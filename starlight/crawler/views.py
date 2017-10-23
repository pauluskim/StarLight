#-*- coding: utf-8 -*-
import sys 
reload(sys)
sys.setdefaultencoding('utf-8')


from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from crawler.models import Influencer, Post, User, Follow, Hashtag_Dictionary
import pdb, datetime, csv, os, sys, requests, json
from django.utils import timezone
from auth import *

sys.path.append(os.path.abspath('./crawler/Instagram-API-python'))
from InstagramAPI import InstagramAPI

api = InstagramAPI(api_id, api_pwd)
api.login() # login

host_ip = str(requests.get('http://ip.42.pl/raw').text)
#ip_list = ['http://13.56.240.85/', 'http://13.57.16.83/']
ip_list = ['http://13.56.240.85/', 'http://13.57.16.83/', 'http://13.57.12.106/', 'http://54.183.65.48/', 'http://52.53.255.11/']
# 2, 1, 3, 5, 4
    
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
    global host_ip
    global ip_list

    target_username= request.GET.get('username', '')
    max_id= request.GET.get('max_id', '')
    
    if target_username == "": return HttpResponseRedirect("/crawl/follow_list")
    
    target_user_pk = user_by_name(target_username).user_pk
    
    crawler_domain = "http://"+host_ip+"/"

    num_crawler = len(ip_list)
    #crawler_index = ip_list.index(crawler_domain)
    crawler_index = 0 
    # For develop in local.
    
    while max_id != "end":
        while True:
            response = requests.get(crawler_domain+"crawl/followers/"+str(target_user_pk)+"/?max_id="+max_id)
            print response
            try:
                json_response = json.loads(response.text)
                break
            except:
                print "Some json data is wrong."
                print response
                print response.text
                crawler_index = (crawler_index + 1) % num_crawler
                crawler_domain = ip_list[crawler_index]
                continue
            
        max_id = json_response["max_id"]
        crawler_index = (crawler_index + 1) % num_crawler
        crawler_domain = ip_list[crawler_index]

        
    
    return HttpResponseRedirect('/crawl/follow_list')

def start_hashtag_dictionary(request):
    username = request.GET.get('username', '')
    influencer = user_by_name(username)
    hashtag_dictionary(username, influencer.user_pk)

    followers = Follow.objects.filter(object_pk=influencer.user_pk, follow_status='ed')
    for follower in followers:
        hashtag_dictionary(follower.username, follower.user_pk)
        

    # Take a follower to get hashtag list.

def hashtag_dictionary(username, user_pk):
    global ip_list
    num_crawler = len(ip_list)
    crawler_index = 0

    curl_url = "https://www.instagram.com/"+username+"/?__a=1"
    response = requests.get(curl_url)
    media_json = response.json()["user"]["media"]

    for node in media_json["nodes"]:
        media_id = node["id"]
        url_code = node["code"]

        #if "caption" in node: hash_tag_count = node["caption"].count("#")
        if "caption" in node:
            caption_hashtag_list = extract_hash_tags(node["caption"])
            for hashtag in caption_hashtag_list:
                save_hashtag_dic(user_pk, hashtag, url_code)

        crawler_domain = ip_list[crawler_index]
        requests.get("{crawler_domain}crawl/api_hashtag_dic/?media_id={media_id}&user_pk={user_pk}&url_code={url_code}".format(crawler_domain=crawler_domain, media_id=media_id, user_pk=user_pk, url_code=url_code))
        crawler_index = (crawler_index + 1) % num_crawler


def api_hashtag_dic(request):
    media_id = request.GET.get('media_id', '')
    user_pk = request.GET.get('user_pk', '')
    url_code = request.GET.get('url_code', '')

    api.getMediaComments(media_id)
    response_json = api.LastJson
    comments = response_json['comments']

    for comment in comments:
        if user_pk == comment['user_id']:
            influ_comments = comment['text']
            comment_hashtag_list = extract_hash_tags(influ_comments)
            for hashtag in comment_hashtag_list:
                save_hashtag_dic(user_pk, hashtag, url_code)

def save_hashtag_dic(user_pk, hashtag, url_code):
    if Hashtag_Dictionary.objects.filter(hashtag = hashtag, user_pk = user_pk).exists():
        hashtag_dic = Hashtag_Dictionary.objects.get(hashtag = hashtag, user_pk = user_pk)
        if not url_code in hashtag_dic.code_list:
            hashtag_dic.add_count(1, url_code)
    else:
        hashtag_dic             = Hashtag_Dictionary(created_date=timezone.now())
        hashtag_dic.user_pk     = user_pk
        hashtag_dic.hashtag     = hashtag
        hashtag_dic.count       = 1 
        hashtag_dic.code_list   = url_code
        try:
            hashtag_dic.save()
        except:
            print '!!!!!!!!!!!!!!!!!!'
            print hashtag
            print '!!!!!!!!!!!!!!!!!!'

def extract_hash_tags(s):
    return set(part[1:] for part in s.split() if part.startswith('#'))


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
        if "is_favorite" in user_info: user.is_favorite = user_info["is_favorite"]
        else: user.is_favorite = False
        user.external_url = user_info["external_url"]
        user.save()
        return user

def followers(request, target_user_pk):
    max_id = request.GET.get('max_id', '')
    try:
        if max_id == "": api.getUserFollowers(target_user_pk)
        else: api.getUserFollowers(target_user_pk, maxid=max_id)
        followers = api.LastJson
    except:
        print "api response is wrong so return."
        return JsonResponse({'max_id': max_id})
        
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
    
    if "next_max_id" in followers:
        max_id = followers["next_max_id"]
    else:
        max_id = "end"
    
    return JsonResponse({'max_id': max_id})

def follow_list(request):
    follow_list = Follow.objects.order_by('created_date')[:10]
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
