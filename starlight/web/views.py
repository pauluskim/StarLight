#-*- coding: utf-8 -*-
import sys , os, pdb
reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
#sys.path.append(os.path.abspath('../crawler'))
from models import *
from .forms import WebForm


def landing(request):
    return render(request, 'web/landing.html', {'influencers': 'nothing'})

def influencers(request):
    company = request.GET.get('company', 'Bottega_Veneta')
    company = company.replace('_', ' ')
    influencers = User.objects.filter(campaign_kind='dog', follower_count__gte=10000)[:5]
    return render(request, 'web/influencers.html', {'influencers': influencers, 'company': company})

def new_subscriber(request):
    form = WebForm(request.POST)
    if form.is_valid(): form.save()
    return HttpResponseRedirect("/")
