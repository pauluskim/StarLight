#-*- coding: utf-8 -*-
import sys 
reload(sys)
sys.setdefaultencoding('utf-8')


from django.shortcuts import render
from insta_hashtag_crawler import *
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from crawler.models import Influencer, Post, User, Follow
import pdb, datetime, csv
from django.utils import timezone

id_pwd = [["_______jack______", "ghdlWk37qkqk*"], ["hwangba8959", "ghkdqk^*"], ["sunbum7661", "tnsqjadl^*"], ['guha1770', 'rbgk^*'], ['changwook4950', 'ckddnrdl^*'], ['jaehyung2644', 'woguddl^*'], ['minvirus716', 'als951753'], ["hongsik1403", "ghdtlrdl^*"], ["sicily_hongdae", "CKo3umV0WG1Q"]]

api = InstagramAPI(id_pwd[0][0], id_pwd[0][1])
api.login() # login
    
def influencer_list(request):
    influencers = Influencer.objects.order_by('created_date')
    return render(request, 'crawler/influencer_list.html', {'influencers': influencers})
    
def export_follow_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="follow.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['target user pk', 'ing/ed', 'by username', 'user pk', 'is verified', 'is private', 'is favorite'])
    
    follows = Follow.objects.all()
    for follow in follows:
        line_list = [follow.object_pk, follow.follow_status, follow.username, follow.user_pk, follow.is_verified, follow.is_private, follow.is_favorite]
        line_list = [str(ele) for ele in line_list]
        writer.writerow(line_list)

    return response    
    

def user_follow(request):
    target_username= request.GET.get('username', '')
    if target_username == "": return HttpResponseRedirect("/crawl/follow_list")
    
    target_user_pk = user_by_name(target_username).user_pk
    
    num_crawler = 3
    crawler_index = 0
    
    max_id = "start"
    while max_id != "end":
        crawler_domain = "https://starlite-data-"+str(crawler_index)+"-jaegyunkim25.c9users.io"
        if max_id == "start": response = requests.get(crawler_domain+"/crawl/followers/"+str(target_user_pk)+"/")
        else: response = requests.get(crawler_domain+"/crawl/followers/"+str(target_user_pk)+"/?max+id="+max_id)
        
        json_response = json.loads(response.text)
        max_id = json_response["max_id"]
        crawler_index = (crawler_index + 1) % num_crawler
        time.sleep(5)
    
    return HttpResponseRedirect('/crawl/follow_list')
    
def user_by_name(username):
    if User.objects.filter(username = username).exists():
        return User.objects.get(username = username)
    else:
        api.searchUsername(username)
        user_info = api.LastJson["user"]
        user = User(created_date=timezone.now())
        user.username = user_info["username"]
        user.usertags_count = user_info["usertags_count"]
        user.media_count = user_info["media_count"]
        user.following_count = user_info["following_count"]
        user.follower_count = user_info["follower_count"]
        user.is_business = user_info["is_business"]
        user.has_chaining = user_info["has_chaining"]
        user.geo_media_count = user_info["geo_media_count"]
        user.user_pk = user_info["pk"]
        user.is_verified = user_info["is_verified"]
        user.is_private = user_info["is_private"]
        user.is_favorite = user_info["is_favorite"]
        user.external_url = user_info["external_url"]
        user.save()
        return user

def followers(request, target_user_pk):
    max_id = request.GET.get('max_id', '')
    
    for i in range(50):
        print i
        if max_id == "": api.getUserFollowers(target_user_pk)
        else: api.getUserFollowers(target_user_pk, maxid=max_id)
        followers = api.LastJson
        
        for follower in followers["users"]:
            if Follow.objects.filter(user_pk = follower["pk"], object_pk = target_user_pk).exists(): continue
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
