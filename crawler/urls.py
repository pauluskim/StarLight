from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.influencer_list, name='influencer_list'),
]