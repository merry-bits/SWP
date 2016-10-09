# -*- coding: utf-8 -*-
from logging import getLogger
from os import mkdir
from os.path import exists
from os.path import split

from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.forms import CharField
from django.forms import FileField
from django.forms import Form
from django.http.response import Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from wand.image import Image

from swp.models import CAPTION_MAX_LENGTH
from swp.models import Event
from swp.models import Image as ImageModel
from swp.models import Photo


_LOG = getLogger(__name__)


class UploadPhotoForm(Form):

    caption = CharField(max_length=CAPTION_MAX_LENGTH, required=True)

    original = FileField(required=True, max_length=(16 * 1024 * 1024))


def event(request, slug):
    event = Event.objects.from_slug(slug)
    return render(request, "swp/event.html", {"event": event})


@csrf_protect
@login_required
def new_event(request, slug):
    """
    :type request: django.http.HttpRequest
    :type slug: string
    """
    if request.method != "POST":
        raise Http404()
    event = Event.objects.from_slug(slug)
    form = UploadPhotoForm(request.POST, request.FILES)
    if form.is_valid():
        original = ImageModel.objects.create(
            user=request.user,
            original_file_name=form.cleaned_data["original"].name)
        photo = Photo.objects.create(
            event=event, original=original,
            caption=form.cleaned_data["caption"], visible=False)
        try:
            with Image(
                    blob=form.cleaned_data["original"].read()
                    ) as original_image:
                photo.extract_meta_data(original_image)
                photo.save()
                path = default_storage.path(split(original.path)[0])
                if not exists(path):
                    mkdir(path)
                with default_storage.open(original.path, "wb") as image_file:
                    original_image.format = "png"
                    original_image.save(image_file)
        except Exception:
            _LOG.exception("Creating and storing a photo failed.")
            try:
                default_storage.delete(original.path)
            except Exception:
                import traceback
                traceback.print_exc()
            photo.delete()
            original.delete()

        # https://docs.djangoproject.com/en/1.10/topics/http/file-uploads/
        # MEDIA_ROOT https://docs.djangoproject.com/en/1.10/topics/files/
        # https://en.wikipedia.org/wiki/Exif
