# -*- coding: utf-8 -*-
from json import dumps
from logging import getLogger
from os import makedirs
from os.path import exists
from os.path import split
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import BigAutoField
from django.db.models import CASCADE
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import ForeignKey
from django.db.models import Model
from django.db.models import TextField
from django.db.models import UUIDField
from wand.image import Image


_LOG = getLogger(__name__)

CAPTION_MAX_LENGTH = 256


def _delete_image(image):
    if image is None:
        return
    try:
        image.delete()
    except Exception:
        _LOG.warning("Could not delete image %s", image.image_id)


def _create_thumbnail(image, tumbnail_width, thumbnail_height, file_path):
    if image.width > image.height:
        width = tumbnail_width
        height = int(round((width / image.width) * image.height))
    else:
        height = thumbnail_height
        width = int(round((height / image.height) * image.width))
    image.sample(width, height)
    image.compression_quality = 82
    image.format = "jpeg"
    image_file = settings.STATIC_ROOT + "/" + file_path
    path = split(image_file)[0]
    if not exists(path):
        makedirs(path)
    with open(image_file, "wb") as image_file:
        image.save(image_file)


def _generate_static_files(image, image_object):
    with image_object.clone() as cloned_image_object:
        _create_thumbnail(
            cloned_image_object, settings.THUMBNAIL_WIDTH,
            settings.THUMBNAIL_HEIGHT, image.thumbnail_path)
    with image_object.clone() as cloned_image_object:
        _create_thumbnail(
            cloned_image_object, settings.IMAGE_WIDTH, settings.IMAGE_HEIGHT,
            image.image_path)


class Photo(Model):

    photo_id = BigAutoField(primary_key=True)

    created = DateTimeField(auto_now_add=True, editable=False)

    event = ForeignKey("Event")

    slug = UUIDField(default=uuid4, editable=False)

    original = ForeignKey("Image", on_delete=CASCADE)

    enhanced = ForeignKey(
        "Image", related_name="photo_enhanced", null=True, blank=True,
        on_delete=CASCADE)

    caption = CharField(max_length=CAPTION_MAX_LENGTH)

    exif = TextField(null=True, blank=True, editable=False)

    model = TextField(null=True, blank=True, editable=False)

    exposure = TextField(null=True, blank=True, editable=False)

    f_number = TextField(null=True, blank=True, editable=False)

    iso_speed = TextField(null=True, blank=True, editable=False)

    focal_length_35 = TextField(null=True, blank=True, editable=False)

    @property
    def image(self):
        return self.enhanced or self.original

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

    def generate_static_files(self, image_object=None):
        """ Create a thumbnail and a normal (medium size) version of the image
        and place it into the static directory, ready to be served.

        :param: image: Either the original or the enhanced version of this
            photos image, as a wand Image instance.
        :type image: wand.image.Image
        """
        image = self.enhanced or self.original
        if image_object is None:
            with Image(default_storage.path(image.path)) as image_object:
                _generate_static_files(image, image_object)
        else:
            _generate_static_files(image, image_object)
