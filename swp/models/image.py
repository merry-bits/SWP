# -*- coding: utf-8 -*-
from logging import getLogger
from uuid import uuid4
from os import remove

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db.models import BigAutoField
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import Model
from django.db.models import UUIDField
from django.conf import settings


_LOG = getLogger(__name__)


def _remove_file(image_file):
    try:
        remove(image_file)
    except Exception:
        _LOG.warning("Could not remove file: %s", image_file, exc_info=True)


class Image(Model):

    image_id = BigAutoField(primary_key=True)

    user = ForeignKey(User)

    slug = UUIDField(default=uuid4, editable=False, db_index=True)

    original_file_name = CharField(max_length=256, editable=False)

    @property
    def path(self):
        uuid_hex = self.slug.hex
        return "{}/{}.png".format(uuid_hex[:2], uuid_hex)

    @property
    def thumbnail_path(self):
        uuid_hex = self.slug.hex
        return "thumbnails/{}/{}_{}.jpeg".format(
            uuid_hex[:2], uuid_hex, settings.THUMBNAIL_WIDTH)

    @property
    def image_path(self):
        uuid_hex = self.slug.hex
        return "thumbnails/{}/{}_{}.jpeg".format(
            uuid_hex[:2], uuid_hex, settings.IMAGE_WIDTH)

    def delete(self, using=None, keep_parents=False):
        # Delete original size file.
        file_path = self.path
        try:
            default_storage.delete(file_path)
        except Exception:
            _LOG.warning("Could not delete file: %s", file_path)
        # Delete static files.
        _remove_file(settings.STATIC_ROOT + "/" + self.thumbnail_path)
        _remove_file(settings.STATIC_ROOT + "/" + self.image_path)
        return super().delete(using=using, keep_parents=keep_parents)
