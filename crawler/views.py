#-*- coding: utf-8 -*-
import sys 
reload(sys)
sys.setdefaultencoding('utf-8')


from django.shortcuts import render
from insta_hashtag_crawler import *
from django.http import JsonResponse
from crawler.models import Influencer, Post, User, Follow
import pdb, datetime
from django.utils import timezone
from django.http import HttpResponseRedirect

api = InstagramAPI('_______jack______', 'ghdlWk37qkqk*')
api.login() # login
    
def save_data(request):
    pass

def influencer_list(request):
    influencers = Influencer.objects.order_by('created_date')
    return render(request, 'crawler/influencer_list.html', {'influencers': influencers})
    
def crawl_user_info(request):
    user_id = request.GET.get('user_id', '')
    num_followers = investigate_user(user_id)
    return JsonResponse({"num_followers":num_followers})
    

def crawl_manager(request):
    max_id = "start"
    # hoyatayo
    target_user_pk = 437374249
    while max_id != "end":
        if max_id == "start":
            response = requests.get("https://starlite-data-1-jaegyunkim25.c9users.io/crawl/followers/"+str(target_user_pk)+"/")
            #response = requests.get("https://starlite-data-1-jaegyunkim25.c9users.io/crawl/hashtag_posts/도시락/")
        else: 
            response = requests.get("https://starlite-data-1-jaegyunkim25.c9users.io/crawl/followers/"+str(target_user_pk)+"/?max+id="+max_id)
            #response = requests.get("https://starlite-data-1-jaegyunkim25.c9users.io/crawl/hashtag_posts/도시락/?max_id="+max_id)
        json_response = json.loads(response.text)
        max_id = json_response["max_id"]
        #api.getHashtagFeed(hashtag, maxid=max_id)    
    
    return HttpResponseRedirect('/crawl/follow_list')

def followers(request, target_user_pk):
    max_id = request.GET.get('max_id', '')
    if max_id == "": api.getUserFollowers(target_user_pk)
    else: api.getUserFollowers(pk, maxid=max_id)
    followers = api.LastJson
    
    for follower in followers["users"]:
        if Follow.objects.filter(user_pk = follower["pk"]).exists(): continue
        follow = Follow(created_date=timezone.now())
        follow.object_pk = target_user_pk
        follow.follow_status = 'ed'
        follow.username = follower["username"]
        follow.full_name = follower["full_name"]
        follow.user_pk = follower["pk"]
        follow.is_verified = follower["is_verified"]
        follow.is_private = follower["is_private"]
        if "is_favorite" in follower: follow.is_favorite = follower["is_favorite"]
        else: follow.is_favorite = False
        follow.save()
        
    return JsonResponse({'max_id': followers["next_max_id"]})

def follow_list(request):
    
    follow_list = Follow.objects.order_by('created_date')
    return render(request, 'crawler/follow_list.html', {'follow_list': follow_list})
    
def crawl_hashtag_posts(request):
    hashtag = request.GET.get("hashtag", '')
    max_id = request.GET.get('max_id', '')
    
    if max_id == "":
        api.getHashtagFeed(hashtag)
    else: api.getHashtagFeed(hashtag, maxid=max_id)

    hashtag_metadata = api.LastJson
    
    if api.LastResponse.status_code != 200:
        print(api.LastJson)
        print "No hashtag info"
        return False

    if "ranked_items" in hashtag_metadata:
        items = hashtag_metadata["ranked_items"]
        parse_item(items)
    if "items" in hashtag_metadata:
        items = hashtag_metadata["items"]
        parse_item(items)

    if "next_max_id" in hashtag_metadata: max_id = hashtag_metadata["next_max_id"]
    else:max_id = "end"
    
    return JsonResponse({'max_id':max_id})

def parse_item(items):
    for item in items:
        payload = {}
        # Only get 2017 data.
        created_at = item['taken_at']
        payload['post_date'] = created_at
        if datetime.datetime.fromtimestamp(created_at).year != 2017 : continue

    
        user_id = item["user"]["username"]
        payload['user_id'] = user_id

        response = requests.get("https://starlite-data-1-jaegyunkim25.c9users.io/crawl/user_info?user_id="+user_id)
        user_info = json.loads(response.text)
        num_followers = user_info['num_followers']
        payload['num_followers'] = num_followers
        
        if num_followers < 1000: continue
        

        if "comment_count" in item: comment_count = item["comment_count"]
        else: comment_count = 0
        if "like_count" in item: like_count = item["like_count"]
        else: like_count = 0
        if "code" in item: url = "https://www.instagram.com/p/"+item["code"]
        else: url =""

        engagement_rate = float(comment_count + like_count) / num_followers
        print engagement_rate
        print 'Am I here?'
        influencer = Influencer(user_id=user_id, created_date=timezone.now())
        influencer.engagement_rate = engagement_rate
        influencer.num_commenters = comment_count
        influencer.num_likes = like_count
        influencer.num_followers = num_followers
        influencer.followers = url
        influencer.save()
        print 'Also Am I here?'
        print influencer.followers
