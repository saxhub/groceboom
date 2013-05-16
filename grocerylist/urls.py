from django.conf.urls import patterns, url

from grocerylist import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^list/(?P<glist_id>\d+)/$', views.list_detail, name='list_detail'),
    url(r'^list/(?P<glist_id>\d+)/save/$', views.save_list, name='save_list'),
    url(r'^item-check/$', views.check_item, name='check_item'),
    url(r'^serialize-aisles/$', views.serialize_aisles, name='serialize-aisles'),
    url(r'^get-items/(?P<glist_id>\d+)/$', views.get_items, name="get-items"),
    url(r'^get-aisles/(?P<store_id>\d+)/$', views.get_aisles, name="get-aisles"),
    url(r'^login/$', views.login_page, name='login_page'),
    url(r'^do-login/$', views.do_login, name='do-login'),
    url(r'^add-list/$', views.add_list, name='add_list'),
)		