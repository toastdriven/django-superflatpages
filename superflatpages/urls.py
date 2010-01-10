from django.conf.urls.defaults import *

urlpatterns = patterns('superflatpages.views',
    # Be very greedy.
    url(r'^(?P<path>.*)/$', 'detail', name='superflatpages_detail'),
)
