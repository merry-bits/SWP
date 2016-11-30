# -*- coding: utf-8 -*-
from logging import getLogger
from os import makedirs
from os.path import exists
from os.path import split

from django.contrib import messages
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
from django.shortcuts import redirect


_LOG = getLogger(__name__)


_ORIGINAL = "original"  # upload form field name

_ENHANCED = "enhanced"  # upload form field name


class UploadPhotoForm(Form):

    caption = CharField(max_length=CAPTION_MAX_LENGTH, required=True)

    original = FileField(required=True, max_length=(16 * 1024 * 1024))

    enhanced = FileField(required=False, max_length=(16 * 1024 * 1024))


def event(request, slug):
    event = Event.objects.from_slug(slug)
    photos = event.photo_set.order_by('created')
    ctx = {
        "event": event,
        "photos": photos,
    }
    return render(request, "swp/event.html", ctx)


def _save_image_files(file_object, photo, image, extract_meta):
    with Image(blob=file_object.read()) as original_image:
        if extract_meta:
            photo.extract_meta_data(original_image)
            photo.save()
        original_image.auto_orient()
        path = default_storage.path(split(image.path)[0])
        if not exists(path):
            makedirs(path)
        original_image.format = "png"
        with default_storage.open(image.path, "wb") as image_file:
            original_image.save(image_file)
        photo.generate_static_files(original_image)


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
            original_file_name=form.cleaned_data[_ORIGINAL].name)
        enhanced = None
        if form.cleaned_data[_ENHANCED] is not None:
            enhanced = ImageModel.objects.create(
                user=request.user,
                original_file_name=form.cleaned_data[_ENHANCED].name)
        photo = Photo.objects.create(
            event=event, original=original, enhanced=enhanced,
            caption=form.cleaned_data["caption"])
        try:
            _save_image_files(
                form.cleaned_data[_ORIGINAL], photo, original, True)
            if enhanced is not None:
                _save_image_files(
                    form.cleaned_data[_ENHANCED], photo, enhanced, False)
        except Exception:
            _LOG.exception("Creating and storing a photo failed.")
            try:
                default_storage.delete(original.path)
            except Exception:
                import traceback
                traceback.print_exc()
            photo.delete()
            messages.error(
                request,
                "Sorry, this did not work. The photo was not added. You can "
                "try again and see if it was just a temporary hickup.")
        else:
            messages.success(
                request,
                "Your photo was added, you should be able to see it between "
                "the other photos of the event.")
    else:
        messages.warning(
            request,
            "There was not enough information to generate a photo.")
    return redirect("event", slug=event.slug.hex)

    # https://docs.djangoproject.com/en/1.10/topics/http/file-uploads/
    # MEDIA_ROOT https://docs.djangoproject.com/en/1.10/topics/files/
    # https://en.wikipedia.org/wiki/Exif
