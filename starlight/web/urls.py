from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.landing, name='starlight_landing'),
    url(r'^influencers$', views.influencers, name='show_influencers'),
    url(r'^subscriber/add$', views.new_subscriber, name='save_new_subscriber'),
]
