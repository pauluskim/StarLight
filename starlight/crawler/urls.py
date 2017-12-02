from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.influencer_list, name='influencer_list'),
    url(r'^crawl/hashtag_posts$', views.crawl_hashtag_posts, name='crawl_hashtag_posts'),
    url(r'^crawl/start_hashtag_posts$', views.start_hashtag_posts, name='start_hashtag_posts'),
    
    url(r'^crawl/user_follow$', views.user_follow, name='user_follow'),
    url(r'^crawl/followers/(?P<target_user_pk>[0-9]+)/$', views.followers, name='followers'),
    url(r'^crawl/following$', views.following, name='crawl_following'),
    url(r'^crawl/api_following/(?P<target_user_pk>[0-9]+)/$', views.api_following, name='following'),
    url(r'^crawl/from_file_user_by_name$', views.from_file_user_by_name, name='crawl_from_file'),
    url(r'^crawl/calculate_engagement$', views.calculate_engagement, name='calculate_engagement'),
    url(r'^crawl/__a_engagement$', views.__a_engagement, name='__a_engagement'),
    url(r'^crawl/posts$', views.posts, name='posts'),
    url(r'^crawl/SendDM$', views.SendDM, name='SendDM'),
    url(r'^crawl/pagerank$', views.pagerank, name='pagerank'),
    #url(r'^crawl/manager$', views.crawl_manager, name='crawl_manager'),
    url(r'^crawl/follow_list$', views.follow_list, name='follow_list'),
    url(r'^crawl/export_follow_csv$', views.export_follow_csv, name='export_follow_csv'),
    url(r'^crawl/hashtag_dic$', views.start_hashtag_dictionary, name='hashtag_dictionary'),
    url(r'^crawl/api_hashtag_dic$', views.api_hashtag_dic, name='api_hashtag_dictionary'),
    url(r'^crawl/export_hashtag_dic$', views.export_hashtag_dic, name='export_hashtag_dic'),
    url(r'^crawl/check_influencer$', views.check_influencer, name='export_hashtag_dic'),
    url(r'^crawl/user_by_name$', views.user_by_name, name='user_by_name'),
]
