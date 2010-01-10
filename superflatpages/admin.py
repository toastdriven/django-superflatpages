from django.contrib import admin
from django import forms
from superflatpages.models import FlatPage, FlatPageSnapshot


class FlatPageAdminForm(forms.ModelForm):
    message = forms.CharField(required='False', widget=forms.Textarea)
    
    class Meta:
        model = FlatPage
    
    def save(self, *args, **kwargs):
        flatpage = super(FlatPageAdminForm, self).save(commit=False)
        return flatpage.save(message=self.cleaned_data['message'])


class FlatPageAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    fieldsets = (
        (None, {
            'fields': ('title', 'content_format', 'content', 'last_modified_by', 'parent'),
        }),
        ('Additional Page Data', {
            'classes': ('collapse',),
            'fields': ('extra_js', 'extra_css', 'custom_template', 'slug', 'path'),
        }),
        ('Meta', {
            'classes': ('collapse',),
            'fields': ('created', 'modified', 'is_active'),
        })
    )
    # form = FlatPageAdminForm
    list_display = ('title', 'path', 'content_format', 'last_modified_by', 'is_active', 'modified')
    list_filter = ('is_active',)
    raw_id_fields = ('parent', 'last_modified_by')
    search_fields = ('title', )


class FlatPageSnapshotAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'message', 'content_format', 'content', 'last_modified_by', 'page'),
        }),
        ('Additional Page Data', {
            'classes': ('collapse'),
            'fields': ('extra_js', 'extra_css', 'custom_template', 'slug', 'path'),
        }),
        ('Meta', {
            'classes': ('collapse'),
            'fields': ('created', 'modified', 'is_active'),
        })
    )
    raw_id_fields = ('page', 'last_modified_by')


admin.site.register(FlatPage, FlatPageAdmin)
admin.site.register(FlatPageSnapshot, FlatPageSnapshotAdmin)
