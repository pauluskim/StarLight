from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.utils import timezone

class User(models.Model):
    username = models.CharField(max_length=200)
    usertags_count = models.IntegerField(null=True)
    media_count = models.IntegerField(null=True)
    following_count = models.IntegerField(null=True)
    is_business = models.BooleanField()
    has_chaining = models.BooleanField()
    geo_media_count = models.IntegerField(null=True)
    full_name = models.TextField(null=True)
    user_pk = models.IntegerField()
    is_verified = models.BooleanField()
    is_private = models.BooleanField()
    is_favorite = models.BooleanField()
    external_url = models.TextField(null=True)
    created_date = models.DateTimeField(default=timezone.now)
    
class Follow(models.Model):
    object_pk = models.BigIntegerField()
    follow_status = models.CharField(max_length=5) # ing or ed.
    username = models.CharField(max_length=200)
    user_pk = models.BigIntegerField()
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