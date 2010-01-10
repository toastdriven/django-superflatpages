import datetime
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify


CONTENT_FORMATS = (
    ('txt', 'Plain Text'),
    ('rst', 'ReStructured Text'),
    ('html', 'HTML'),
)


class BaseFlatPage(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    path = models.CharField(max_length=255, default='', blank=True)
    extra_css = models.TextField(blank=True)
    extra_js = models.TextField(blank=True)
    content_format = models.CharField(max_length=16, choices=CONTENT_FORMATS, default='rst')
    content = models.TextField()
    custom_template = models.CharField(max_length=255, blank=True, null=True)
    last_modified_by = models.ForeignKey(User)
    created = models.DateTimeField(default=datetime.datetime.now)
    modified = models.DateTimeField(default=datetime.datetime.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
    
    def unicode(self):
        return u"%s - %s" % (self.title, self.path)


class FlatPageManager(models.Manager):
    def active(self):
        return self.get_query_set().filter(is_active=True)


class FlatPage(BaseFlatPage):
    # Inherit all fields from the ``BaseFlatPage`` but make them concrete.
    parent = models.ForeignKey('self', blank=True, null=True)
    
    objects = FlatPageManager()
    
    def save(self, *args, **kwargs):
        message = kwargs.get('message', 'Auto-saved')
        
        if 'message' in kwargs:
            del(kwargs['message'])
        
        if not self.slug:
            self.slug = slugify(self.title)
            
        if not self.path:
            if self.parent:
                self.path = "/".join([self.parent.path, self.slug])
            else:
                self.path = self.slug
        
        self.modified = datetime.datetime.now()
        super(FlatPage, self).save(*args, **kwargs)
        FlatPageSnapshot.objects.create_snapshot(self, message=message)
        return self
    
    @models.permalink
    def get_absolute_url(self):
        return ('superflatpages_detail', [], {
            'path': self.path,
        })


class FlatPageSnapshotManager(models.Manager):
    def create_snapshot(self, page, message='Auto-saved'):
        """
        Generates a snapshot of the provided page. Optionally accepts a
        message describing the change (think: commit message).
        """
        return FlatPageSnapshot.objects.create(
            title=page.title,
            slug=page.slug,
            path=page.path,
            extra_css=page.extra_css,
            extra_js=page.extra_js,
            content_format=page.content_format,
            content=page.content,
            custom_template=page.custom_template,
            last_modified_by=page.last_modified_by,
            is_active=page.is_active,
            page=page,
            message=message
        )


class FlatPageSnapshot(BaseFlatPage):
    # Inherit all fields from the ``BaseFlatPage`` but make them concrete.
    page = models.ForeignKey(FlatPage, blank=True, null=True)
    message = models.CharField(max_length=1000, default='Auto-saved', blank=True, help_text='A description of what changed and why.')
    snapped_on = models.DateTimeField(default=datetime.datetime.now)
    
    objects = FlatPageSnapshotManager()
