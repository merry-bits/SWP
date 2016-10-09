# -*- coding: utf-8 -*-
from django.contrib import admin

from swp.models import Event
from swp.models import Image
from swp.models import Photo
from django.contrib.admin import ModelAdmin


class ImageAdmin(ModelAdmin):

    list_display = ("image_id", "user_name", "original_file_name")

    def user_name(self, obj):
        return obj.user.username
    user_name.admin_order_field = "user__username"


class PhotoAdmin(ModelAdmin):

    list_display = (
        "photo_id", "event_title", "original", "image", "caption", "model",
        "exposure", "f_number", "iso_speed", "focal_length_35")

    def event_title(self, obj):
        return obj.event.title
    event_title.admin_order_field = "event__title"


admin.site.site_header = "SWP admin"
admin.site.site_title = "SWP admin"
admin.site.register(Event)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Image, ImageAdmin)
