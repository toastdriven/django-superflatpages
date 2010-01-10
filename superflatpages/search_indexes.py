from haystack import indexes
from haystack import site
from superflatpages.models import FlatPage


class FlatPageIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    author = indexes.CharField(model_attr='last_modified_by__username')
    pub_date = indexes.DateTimeField(model_attr='created')


site.register(FlatPage, FlatPageIndex)
