"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.contrib import admin
from socialnetwork import views as socialnetwork_views

urlpatterns = [
    url(r'^$', socialnetwork_views.followfeed, name='home'),
    url(r'^writepost/(\d+)$', socialnetwork_views.writepost, name='writepost'),
    url(r'^images/.*$', socialnetwork_views.get_user_photo, name='myphoto'),
    url(r'^globalstream$', socialnetwork_views.globalstream, name='globalstream'),
    url(r'^followfeed$', socialnetwork_views.followfeed, name='followfeed'),
    url(r'^register$', socialnetwork_views.register, name='register'),
    url(r'^profile/(\d+)$', socialnetwork_views.profile, name='profile'),
    url(r'^streamphoto/(\d+)$', socialnetwork_views.get_stream_photo, name='streamphoto'),
    url(r'^photo/(\d+)$', socialnetwork_views.get_any_photo, name='photo'),
    url(r'^editprofile$', socialnetwork_views.editprofile, name='editprofile'),
    url(r'^viewprofile$', socialnetwork_views.viewprofile, name='viewprofile'),
    # Route for built-in authentication with our own custom login page
    url(r'^login$', auth_views.login, {'template_name':'socialnetwork/login.html'}, name='login'),
    # Route to logout a user and send them back to the login page
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
    url(r'^myphoto$', socialnetwork_views.get_user_photo, name='myphoto'),
    url(r'^follows$', socialnetwork_views.follows, name='follows'),
    url(r'^follow/(\d)$', socialnetwork_views.follow, name='follow'),
    url(r'^unfollow/(\d)$', socialnetwork_views.unfollow, name='unfollow'),
    url(r'^get_posts$', socialnetwork_views.get_posts),
    url(r'^get_feed$', socialnetwork_views.get_feed),
    url(r'^add_comment$', socialnetwork_views.add_comment),
     url(r'^get_comments$', socialnetwork_views.get_comments),
    # url(r'^updatecomments$', socialnetwork_views.updateComments),

]
