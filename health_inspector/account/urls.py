from django.conf.urls import url
from .views import home, login, signup_doctor, signup_parent, signup_child, logout

urlpatterns = [
    url(r'^$', home, name = "home"),
    url(r'^login/$', login, name = "login"),
    url(r'^logout/$', logout, name = "logout"),
    url(r'^signup-doctor/$', signup_doctor, name ="signup-doctor" ),
    url(r'^signup-parent/$', signup_parent, name ="signup-parent" ),
    url(r'^signup-child/$', signup_child, name ="signup-child" ),
]