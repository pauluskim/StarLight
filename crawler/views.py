from django.shortcuts import render

# Create your views here.

def influencer_list(request):
    return render(request, 'crawler/influencer_list.html', {})