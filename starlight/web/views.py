#-*- coding: utf-8 -*-
import sys , os
reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render
#sys.path.append(os.path.abspath('../crawler'))
from models import *


def landing(request):
    return render(request, 'web/landing.html', {'influencers': 'nothing'})

def influencers(request):
    company = request.GET.get('company', 'Bottega_Veneta')
    company = company.replace('_', ' ')
    influencers = User.objects.filter(campaign_kind='dog', follower_count__gte=10000)[:5]
    return render(request, 'web/influencers.html', {'influencers': influencers, 'company': company})
