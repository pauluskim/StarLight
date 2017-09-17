from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.utils import timezone

class Influencer(models.Model):
    #author = models.ForeignKey('auth.User')
    user_id = models.CharField(max_length=200)
    engagement_rate = models.DecimalField(max_digits=22, decimal_places=20)
    followers = models.TextField()
    followings = models.TextField()
    num_followers = models.IntegerField()
    num_followings = models.IntegerField()
    num_posts = models.IntegerField()
    num_likes = models.IntegerField()
    num_commenters = models.IntegerField()
    num_views = models.IntegerField()
    
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)

    #def publish(self):
    #    self.published_date = timezone.now()
    #    self.save()

    def __str__(self):
        return self.user_id







[]