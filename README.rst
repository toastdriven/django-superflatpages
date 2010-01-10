==============
superflatpages
==============

An alternative to ``django.contrib.flatpages`` with more structure, metadata and
limited versioning support.

Comes with optional Haystack support.

Install
=======

#. Add 'superflatpages' to INSTALLED_APPS.
#. At the bottom of your ``ROOT_URLCONF``, add ``(r'^', include('superflatpages.urls')),``.
   It **MUST** be the last entry, as it will gobble up any path it sees.
#. Syncdb.

Dependencies
============

* Django 1.1.X+
* (Optional) Haystack 1.X (http://github.com/toastdriven/django-haystack)
