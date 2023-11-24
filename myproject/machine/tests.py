from django.test import TestCase
from django.test.client import RequestFactory

from .models import Detail, Issue
from .utils import get_response_body
from .views import post_register_machine, post_create_issue_to_machine, get_all_reported_issues, \
    post_count_issues_by_machine, get_top_k_words, resolved_issue


class AllTestCases(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        detail = Detail.objects.create(name="test_mock_1")

        issue = Issue(id='17', issue='mock title 1', machine_id=Detail.objects.get(id=detail.id), description='mock desc 1')
        issue.save()

    def test_post_register_machine_success(self):
        req_body = {
            'name': "machine_test_2"
        }
        request = self.factory.post('/machine-service/register', data=req_body, content_type='application/json')

        response = post_register_machine(request)
        response_body = get_response_body(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response_body['id'], 2)
        self.assertEquals(response_body['name'], 'machine_test_2')

    def test_post_create_issue_to_machine_success(self):
        req_body = {
            'machine_id': 1,
            "issue": "mock_issue",
            "description": "test_mock-issue_1: data success"
        }
        request = self.factory.post('/machine-service/add-issue', data=req_body, content_type='application/json')

        response = post_create_issue_to_machine(request)

        self.assertEquals(response.status_code, 200)

        added_issue = Issue.objects.filter(issue='mock_issue').values()[0]

        self.assertEquals(added_issue['issue'], 'mock_issue')
        self.assertEquals(added_issue['description'], 'test_mock-issue_1: data success')
        self.assertEquals(added_issue['machine_id_id'], 1)

    def test_get_all_service_success(self):
        request = self.factory.get('/machine-service/all-issue?status=OPEn&page=1&limit=1',
                                   content_type='application/json')

        response = get_all_reported_issues(request)
        response_body = get_response_body(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response_body['count'], 5)
        self.assertEquals(response_body['contentLength'], 1)

    def test_count_issues_report_success(self):
        req_body = {
            'input_ids': [6, 7]
        }
        request = self.factory.post('/machine-service/count-issues-report', data=req_body,
                                    content_type='application/json')

        response = post_count_issues_by_machine(request)
        response_body = get_response_body(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response_body[0]['machine_id'], 7)
        self.assertEquals(response_body[0]['issue_count'], 4)

    def test_get_top_k_success(self):
        request = self.factory.get('/machine-service/get-top-k?top_k=2', content_type='application/json')

        response = get_top_k_words(request)
        response_body = get_response_body(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response_body[0]['word'], 'support')
        self.assertEquals(response_body[0]['frequency'], 133)

    def test_put_resolved_issue_success(self):
        req_body = {
            "comment": "Fixed Trump supporter already 2!"
        }
        request = self.factory.put('/machine-service/resolved-issue/17', data=req_body, content_type='application/json')

        response = resolved_issue(request, 17)
        response_body = get_response_body(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response_body['name'], 'machine1')
        self.assertEquals(len(response_body['history']), 1)

    def test_get_resolved_issue_success(self):
        request = self.factory.get('/machine-service/resolved-issue/1', content_type='application/json')

        response = resolved_issue(request, 17)
        response_body = get_response_body(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response_body['name'], 'machine1')
