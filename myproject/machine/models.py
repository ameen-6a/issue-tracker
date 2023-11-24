from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Detail(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=300)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class StatusEnum(models.TextChoices):
    OPEN = 'OPEN', _('Open')
    URGENT = 'URGENT', _('Urgent')
    RESOLVED = 'RESOLVED', _('Resolved')


class Issue(models.Model):
    id = models.AutoField(primary_key=True)
    issue = models.CharField(max_length=300)
    machine_id = models.ForeignKey(Detail, on_delete=models.CASCADE)
    description = models.CharField(max_length=3000)
    timestamp_created = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=8,
        choices=StatusEnum.choices,
        default=StatusEnum.OPEN,
    )

    def serialize(self):
        return {
            "id": self.id,
            "issue": self.issue,
            "machine_id": self.machine_id,
            "description": self.description,
            "timestamp_created": self.timestamp_created,
            "status": self.status,
        }


class IssueHistory(models.Model):
    issue_id = models.ForeignKey(Issue, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=8,
        choices=StatusEnum.choices,
        default=StatusEnum.OPEN,
    )
    timestamp = models.DateTimeField(default=timezone.now)
    comment = models.CharField(max_length=3000, null=True)


