from django.urls import path

from . import views


urlpatterns = [
    path("register", views.post_register_machine, name="register-machine"),
    path("add-issue", views.post_create_issue_to_machine, name="add-machine-issue"),
    path("all-issue", views.get_all_reported_issues, name="get-all-issue"),
    path("count-issues-report", views.post_count_issues_by_machine, name="count-issues-report"),
    path("get-top-k", views.get_top_k_words, name="get-top-k"),
    path("resolved-issue/<int:id>", views.resolved_issue, name="resolved-issue"),
]
