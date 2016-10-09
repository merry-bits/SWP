# -*- coding: utf-8 -*-
from logging import getLogger
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db.models import BigAutoField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import ForeignKey
from django.db.models import Model
from django.db.models import UUIDField


_LOG = getLogger(__name__)


class Image(Model):

    image_id = BigAutoField(primary_key=True)

    user = ForeignKey(User)

    slug = UUIDField(default=uuid4, editable=False)

    original_file_name = CharField(max_length=256, editable=False)

    created = DateTimeField(auto_now_add=True, editable=False)

    @property
    def path(self):
        uuid_hex = self.slug.hex
        return "{}/{}.png".format(uuid_hex[:2], uuid_hex)

    def delete(self, using=None, keep_parents=False):
        file_path = self.path
        try:
            default_storage.delete(file_path)
        except Exception:
            _LOG.warning("Could not remove file: %s", file_path)
        return super().delete(using=using, keep_parents=keep_parents)
