from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    #(r'^philly_legislative/', include('philly_legislative.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),


    (r'^subs/$', 'phillyleg.views.index'),
    (r'^subs/create/$', 'phillyleg.views.create'),
    (r'^subs/unsubscribe/$', 'phillyleg.views.unsubscribe'),
    #(r'^subs/(?P<subscription_id>\d+)/$', 'phillyleg.views.edit'),
    (r'^subs/delete/$', 'phillyleg.views.delete')
)
