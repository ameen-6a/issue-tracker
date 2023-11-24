from django.core.exceptions import BadRequest, ViewDoesNotExist
import math
import json
import sqlite3
from django.http import HttpResponse
from django.http import JsonResponse

from .iomodels.request.Validator import validate_not_null
from .models import Detail, Issue, IssueHistory
from .utils import get_request_body, check_post_method, check_get_method, get_top_k_common_words, check_put_method


def post_register_machine(request):
    check_post_method(request)

    body = get_request_body(request)
    if not body['name']:
        raise BadRequest('Missing machine name')

    try:
        machine_detail = Detail(name=body['name'])
        machine_detail.save()
    except ValueError as err:
        print("Cannot register machine: {}".format(err))
        return HttpResponse(status=500)

    return HttpResponse("Successful register machine %s." % body['name'])


def post_create_issue_to_machine(request):
    check_post_method(request)

    body = get_request_body(request)

    if not validate_not_null(body, ['issue', 'machine_id']):
        raise BadRequest('Bad request for adding issue: {}'.format(body))

    try:
        issue_detail = Issue(
            issue=body['issue'],
            machine_id=Detail.objects.get(id=body['machine_id']),
            description=body['description']
        )
        issue_detail.save()

        history = IssueHistory(
            issue_id=Issue.objects.get(id=issue_detail.id)
        )
        history.save()
    except ValueError as err:
        print("Cannot add issue: {}".format(err))
        return HttpResponse(status=500)

    return HttpResponse("Successful add issue to machine ID %s." % body['machine_id'])


def get_all_reported_query(request, sql_statement: str):
    key_list = request.GET.keys()

    if ('limit' not in key_list and len(key_list) > 2) or len(key_list) <= 2:
        sql_statement += "WHERE"

    if 'machine_id' in key_list:
        sql_statement += " md.id = '{}' and".format(request.GET['machine_id'])
    if 'title' in key_list:
        sql_statement += " mi.issue LIKE '%{}%' and".format(request.GET['title'])
    if 'description' in key_list:
        sql_statement += " mi.description LIKE '%{}%' and".format(request.GET['description'])
    if 'start_timestamp' in key_list:
        sql_statement += " mi.timestamp_created > '{}' and".format(request.GET['start_timestamp'])
    if 'end_timestamp' in key_list:
        sql_statement += " mi.timestamp_created < '{}' and".format(request.GET['end_timestamp'])
    if 'status' in key_list:
        sql_statement += " mi.status = '{}' and".format(str.upper(request.GET['status']))

    sql_statement += " 1=1"
    print(sql_statement)
    return sql_statement


def get_all_reported_issues(request):
    check_get_method(request)

    sql_statement = """
    SELECT * FROM machine_detail md
    LEFT JOIN machine_issue mi ON md.id = mi.machine_id_id
    """

    sql_statement = get_all_reported_query(request, sql_statement)

    try:
        count_all_row = Detail.objects.raw(sql_statement.replace("*", "md.id, COUNT(*) as counter"))[0]
        all_row = count_all_row.counter
    except IndexError as err:
        print("cannot retrieve all rows number: {}".format(err))
        all_row = 0

    try:
        if 'page' in request.GET.keys() and 'limit' in request.GET.keys():
            page_number = int(request.GET['page'])
            limit = int(request.GET['limit'])

            offset = (page_number - 1) * limit

            sql_statement = sql_statement + " LIMIT {} OFFSET {}".format(str(limit), str(offset))

            with sqlite3.connect("db.myproject") as conn:
                c = conn.cursor()
                c.execute(sql_statement)
                all_detail = c.fetchall()
                c.close()

            all_detail_list = construct_output(all_detail)

            response = {
                'count': all_row,
                'pageNumber': page_number,
                'contentLength': len(all_detail_list),
                'totalPage': math.ceil(all_row / limit),
                'info': all_detail_list
            }
        else:
            with sqlite3.connect("db.myproject") as conn:
                c = conn.cursor()
                c.execute(sql_statement)
                all_detail = c.fetchall()
                c.close()

            all_detail_list = construct_output(all_detail)

            response = {
                'count': all_row,
                'info': all_detail_list
            }

        return JsonResponse(response, safe=False)
    except ValueError as err:
        print("Cannot get all issues: {}".format(err))
        return HttpResponse(status=500)


def construct_output(all_detail):
    all_detail_list = []
    for output_obj in all_detail:
        all_detail_list.append({
            'id': output_obj[0],
            'name': output_obj[1],
            'issue_id': output_obj[2],
            'description': output_obj[3],
            'status': output_obj[4],
            'title': output_obj[6],
            'timestamp_created': output_obj[7],
        })
    return all_detail_list


def get_count_issues_by_machine(request):
    check_post_method(request)

    body = get_request_body(request)

    if not validate_not_null(body, ['input_ids']):
        raise BadRequest('Bad request for query issue counts: {}'.format(body))

    sql_statement = """
        SELECT md.id as out_machine_id, COUNT(md.id) as out_counter FROM machine_detail md
        LEFT JOIN machine_issue mi ON md.id = mi.machine_id_id
        WHERE md.id IN {}
        GROUP BY md.id
        ORDER BY out_counter DESC;
    """.format(str(body['input_ids']).replace('[', '(').replace(']', ')'))

    try:
        with sqlite3.connect("db.myproject") as conn:
            c = conn.cursor()
            c.execute(sql_statement)
            all_detail = c.fetchall()
            c.close()

        output = []
        for obj in all_detail:
            output.append({
                'machine_id': obj[0],
                'issue_count': obj[1]
            })

        return JsonResponse(output, safe=False)
    except ValueError as err:
        print("Error while trying to retrieve count issue by machine: {}".format(err))


def get_top_k_words(request):
    check_get_method(request)

    top_k = int(request.GET.get('top_k', 5)) or 5

    output = get_all_reported_issues(request)

    result_dict = json.loads(output.content.decode('utf-8'))

    long_text = ''
    for obj in result_dict['info']:
        if obj['title'] is not None and obj['description'] is not None:
            long_text += obj['title'] + " " + obj['description'] + " "
        elif obj['description'] is not None:
            long_text += obj['description'] + " "
        elif obj['title'] is not None:
            long_text += obj['title'] + " "

    top_k_words = get_top_k_common_words(long_text, top_k)
    output = []
    for word, freq in top_k_words:
        output.append({
            "word": word,
            "frequency": freq
        })

    return JsonResponse(output, safe=False)


def resolved_issue(request, id):
    if request.method == 'PUT':
        # Upsert function if issue resolved already it will be skipped
        try:
            history, create = IssueHistory.objects.update_or_create(id=id)
            if create:
                create.save()
        except ValueError as err:
            print("Error while put resolved issue: {}".format(err))

        return get_history(id)
    elif request.method == 'GET':
        return get_history(id)
    else:
        raise ViewDoesNotExist("This method have not been implemented yet")


def get_history(id):
    try:
        sql_statement = """ 
                SELECT * FROM machine_detail md
                LEFT JOIN machine_issue mi ON md.id = mi.machine_id_id
                WHERE mi.id = '{}'
            """.format(str(id))
        with sqlite3.connect("db.myproject") as conn:
            c = conn.cursor()
            c.execute(sql_statement)
            all_detail = c.fetchall()
            c.close()
        output_machine_and_issue = construct_output(all_detail)[0]
        output_machine_and_issue['history'] = []
        histories = IssueHistory.objects.filter(issue_id=output_machine_and_issue['issue_id']).values('status', 'timestamp',
                                                                                                      'comment')
        output_machine_and_issue['history'].extend([hist for hist in histories])
        return JsonResponse(output_machine_and_issue, safe=False)
    except ValueError as err:
        print("Error while trying to get history of resolved issue: {}".format(err))
