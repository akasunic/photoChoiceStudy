from django.conf.urls import include, url
from socialnetwork import views

urlpatterns = [
    url(r'^$', views.followfeed),
    url(r'^socialnetwork/', include('socialnetwork.urls')),
]