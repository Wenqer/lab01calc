from django.conf.urls import patterns, include, url
#from calcapp.views import hello, countera3
from calcapp import views
from django.views.generic import TemplateView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'lab01calc.views.home', name='home'),
    #url(r'^lab01calc/', include('lab01calc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
     url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Home Page -- Replace if you like
    #url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^$', views.start),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),

    #ajax upload
    #( r'^ajax_upload/$', views.ajax_upload),
    #url( r'^$', views.upload_page, name="home" ),


    (r'^recounter/$', views.recounter),
    (r'^digit/$', views.digit),
    (r'^paper-choose/$', views.paper_choose),
    (r'^add-order/$', views.add_order),
    (r'^paper-size/$', views.paper_size),
    (r'^lamin/$', views.lamin),
    (r'^login$', views.login),
    (r'^logout$', views.logout),
    #ajaxuploader
    url(r'start$', views.start, name="start"),
    url(r'ajax-upload$', views.import_uploader, name="my_ajax_upload"),



)
