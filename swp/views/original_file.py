from swp.models import Image
from django.http.response import Http404
from django.http.response import FileResponse
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required


@login_required
def original_file(request, slug):
    try:
        image = Image.objects.get(slug=slug)
    except Image.DoesNotExist:
        raise Http404
    response = FileResponse(
        default_storage.open(image.path, "rb"), content_type="image/png")
    return response
