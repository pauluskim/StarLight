from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.utils import timezone

class ScoreBoard(models.Model):
    user_pk = models.BigIntegerField(db_index=True)
    brandname = models.CharField(max_length=200, db_index=True)
    page_rank = models.DecimalField(max_digits=22, decimal_places=20, null=True)
    graph_type = models.CharField(max_length=10, db_index=True) # hashtag or basic. 
    created_date = models.DateTimeField(default=timezone.now)

class User(models.Model):
    username = models.CharField(max_length=200, db_index=True)
    usertags_count = models.IntegerField(null=True)
    media_count = models.IntegerField(null=True)
    following_count = models.IntegerField(null=True)
    follower_count = models.IntegerField(null=True, db_index=True)
    is_business = models.BooleanField()
    has_chaining = models.BooleanField()
    geo_media_count = models.IntegerField(null=True)
    user_pk = models.BigIntegerField()
    is_verified = models.BooleanField()
    is_private = models.BooleanField()
    is_favorite = models.BooleanField()
    external_url = models.TextField(null=True)
    created_date = models.DateTimeField(default=timezone.now)
    count_DM_sent = models.IntegerField(default=0) 
    
    engagement_rate = models.DecimalField(max_digits=22, decimal_places=20, null=True)
    num_likes = models.IntegerField(null=True)
    num_follower_likes = models.IntegerField(null=True)
    num_commenters = models.IntegerField(null=True)
    num_follower_commenters = models.IntegerField(null=True)
    num_views = models.IntegerField(null=True)
    remark = models.TextField(null=True)
    campaign_kind = models.TextField(null=True)


class Follow(models.Model):
    object_pk = models.BigIntegerField(db_index=True)
    follow_status = models.CharField(max_length=5, db_index=True) # ing or ed.
    username = models.CharField(max_length=200)
    user_pk = models.BigIntegerField(db_index=True)
    is_verified = models.BooleanField()
    is_private = models.BooleanField()
    is_favorite = models.BooleanField()
    
    created_date = models.DateTimeField(default=timezone.now)
class Influencer(models.Model):
    #author = models.ForeignKey('auth.User')
    user_id = models.CharField(max_length=200)
    engagement_rate = models.DecimalField(max_digits=22, decimal_places=20, null=True)
    followers = models.TextField(null=True)
    followings = models.TextField(null=True)
    num_followers = models.IntegerField(null=True)
    num_followings = models.IntegerField(null=True)
    num_posts = models.IntegerField(null=True)
    num_likes = models.IntegerField(null=True)
    num_commenters = models.IntegerField(null=True)
    num_views = models.IntegerField(null=True)
    
    created_date = models.DateTimeField(
            default=timezone.now)
    #published_date = models.DateTimeField(
    #        blank=True, null=True)

    def publish(self):
        #self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.user_id

class Hashtag_Dictionary(models.Model):
    user_pk = models.BigIntegerField(db_index=True)
    hashtag = models.CharField(max_length=200, db_index=True, null=True)
    count = models.IntegerField(null=True)
    code_list = models.TextField(null=True)
    created_date = models.DateTimeField(default=timezone.now)

    def add_count(self, volume, code):
        self.count += 1
        self.code_list += ','+code
        self.save()

    def __str__(self):
        return self.hashtag

class Post(models.Model):
    user_id = models.CharField(max_length=200)
    engagement_rate = models.DecimalField(max_digits=22, decimal_places=20, null=True)
    num_likes = models.IntegerField(null=True)
    num_commenters = models.IntegerField(null=True)
    num_views = models.IntegerField(null=True)
    captions = models.TextField(null=True)
    created_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.user_id+"'s post"
