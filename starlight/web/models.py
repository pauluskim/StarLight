# -*- coding: utf-8 -*-
import sys, os
reload(sys)
sys.setdefaultencoding('utf-8')

from django.db import models
from django.utils import timezone

from crawler.models import *

class Subscriber(models.Model):
    product = models.CharField(max_length=200)
    email = models.EmailField()
    first_name = models.CharField(max_length=200)
