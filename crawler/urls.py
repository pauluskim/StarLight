from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.influencer_list, name='influencer_list'),
    url(r'^crawl/user_info$', views.crawl_user_info, name='crawl_user_info'),
    url(r'^crawl/hashtag_posts$', views.crawl_hashtag_posts, name='crawl_hashtag_posts'),
    url(r'^crawl/followers/(?P<target_user_pk>[0-9]+)/$', views.followers, name='followers'),
    url(r'^crawl/manager$', views.crawl_manager, name='crawl_manager'),
    url(r'^crawl/follow_list$', views.follow_list, name='follow_list'),
]