from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader, RequestContext
from django.views.decorators.cache import cache_page
from superflatpages.models import FlatPage


CACHE_EXPIRE = getattr(settings, 'SUPERFLATPAGES_CACHE_EXPIRE', 60)


@cache_page(CACHE_EXPIRE)
def detail(request, path):
    """
    Displays a flat page if found.
    
    Only pulls from FlatPage objects that are active and match the path
    passed in, returning a 404 if not found.
    
    Templates::
        ``[flatpage.custom_template (if present), 'superflatpages/detail.html']``
    
    Context::
        ``flatpage``:
            The requested FlatPage object.
    """
    template_names = ['superflatpages/detail.html']
    
    # Look only within active pages.
    flatpage = get_object_or_404(FlatPage.objects.active(), path=path)
    
    if flatpage.custom_template:
        # Try to use the custom template, falling back on the default.
        template_names = [flatpage.custom_template] + template_names
    
    template = loader.select_template(template_names)
    context = RequestContext(request, {
        'flatpage': flatpage,
    })
    return HttpResponse(template.render(context))
