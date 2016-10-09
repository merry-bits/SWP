# -*- coding: utf-8 -*-
from json import dumps
from logging import getLogger
from uuid import uuid4

from django.db.models import BigAutoField
from django.db.models import BooleanField
from django.db.models import CASCADE
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import Model
from django.db.models import TextField
from django.db.models import UUIDField


_LOG = getLogger(__name__)

CAPTION_MAX_LENGTH = 256


def _delete_image(image):
    if image is None:
        return
    try:
        image.delete()
    except Exception:
        _LOG.warning("Could not delete image %s", image.image_id)


class Photo(Model):

    photo_id = BigAutoField(primary_key=True)

    event = ForeignKey("Event")

    slug = UUIDField(default=uuid4, editable=False)

    original = ForeignKey("Image", on_delete=CASCADE)

    image = ForeignKey(
        "Image", related_name="photo_image", null=True, blank=True,
        on_delete=CASCADE)

    caption = CharField(max_length=CAPTION_MAX_LENGTH)

    exif = TextField(null=True, blank=True, editable=False)

    model = TextField(null=True, blank=True, editable=False)

    exposure = TextField(null=True, blank=True, editable=False)

    f_number = TextField(null=True, blank=True, editable=False)

    iso_speed = TextField(null=True, blank=True, editable=False)

    focal_length_35 = TextField(null=True, blank=True, editable=False)

    visible = BooleanField(default=False)

    def extract_meta_data(self, image):
        """ Try to read EXIF meta data from the image and save the values
        to the fields of this object.

        Does not save the object!
        :type image: wand.image.Image
        """
        # Parse meta data.
        exif = {
            k[5:]: v
            for k, v in image.metadata.items() if k.startswith("exif:")}
        self.exif = dumps(exif)
        # Try to find data.
        self.model = exif.get("Model", "").strip()
        self.exposure = exif.get("ExposureTime", "").strip()
        self.f_number = exif.get("FNumber", "").strip()
        self.iso_speed = exif.get("ISOSpeedRatings", "").strip()
        self.focal_length_35 = exif.get("FocalLengthIn35mmFilm", "").strip()

    def delete(self, using=None, keep_parents=False):
        original = self.original
        image = self.image
        result = super().delete(using=using, keep_parents=keep_parents)
        _delete_image(original)
        _delete_image(image)
        return result
