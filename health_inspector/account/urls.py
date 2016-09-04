from django.conf.urls import url
from .views import home, login, signup_doctor, signup_parent, signup_child, logout, edit_profile, search_child, home_child, create_task, edit_task

urlpatterns = [
    url(r'^$', home, name = "home"),
    url(r'^login/$', login, name = "login"),
    url(r'^logout/$', logout, name = "logout"),
    url(r'^signup-doctor/$', signup_doctor, name ="signup-doctor" ),
    url(r'^signup-parent/$', signup_parent, name ="signup-parent" ),
    url(r'^signup-child/$', signup_child, name ="signup-child" ),
    url(r'^edit-profile/$', edit_profile, name ="edit-profile" ),
    url(r'^search-child/$', search_child, name ="search-child" ),
    url(r'^(?P<id>\d+)/$', home_child, name="home-child"),
    url(r'^(?P<id>\d+)/create-task/$', create_task, name="create-task"),
    url(r'^(?P<id>\d+)/(?P<t_id>\d+)/edit-task/$', edit_task, name="edit-task")
]