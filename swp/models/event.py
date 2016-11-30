# -*- coding: utf-8 -*-
from uuid import uuid4

from django.db.models import BigAutoField
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import DateField
from django.db.models import Manager
from django.db.models import Model
from django.db.models import TextField
from django.db.models import UUIDField
from django.http import Http404


class EventManager(Manager):

    def from_slug(self, slug):
        try:
            return self.get(slug=slug, visible=True)
        except Event.DoesNotExist:
            raise Http404()


class Event(Model):

    event_id = BigAutoField(primary_key=True)

    slug = UUIDField(default=uuid4, editable=False)

    title = CharField(max_length=128)

    event_date = DateField()

    description = TextField()

    visible = BooleanField(default=False)

    objects = EventManager()
