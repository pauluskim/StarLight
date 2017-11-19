#-*- coding: utf-8 -*-
import sys 
reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from crawler.models import Influencer, Post, User, Follow, Hashtag_Dictionary
from django.db.models import Q
import pdb, datetime, csv, os, sys, requests, json, time
from django.utils import timezone
from auth import *
from langdetect import *

sys.path.append(os.path.abspath('./crawler/Instagram-API-python'))
from InstagramAPI import InstagramAPI

api = InstagramAPI(api_id, api_pwd)
api.login() # login

host_ip = str(requests.get('http://ip.42.pl/raw').text)
#ip_list = ['http://localhost:8000/']
ip_list = ['http://52.52.196.98/', 'http://13.57.80.18/', 'http://13.56.107.109/', 'http://52.53.201.131/', 'http://54.183.193.51/']
# 2, 1, 3, 5, 4
    
def influencer_list(request):
    influencers = Influencer.objects.order_by('created_date')
    return render(request, 'crawler/influencer_list.html', {'influencers': influencers})
    
def export_hashtag_dic(request):
    target_user_pk= request.GET.get('user_pk', '')
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hashtag_dic.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['user id', 'hashtag', 'count'])
    influ_dic_list = Hashtag_Dictionary.objects.filter(user_pk = target_user_pk).order_by('-count')[:10]
    for dic in influ_dic_list:
        line_list = [dic.user_pk, dic.hashtag, dic.count]
        line_list = [str(ele) for ele in line_list]
        writer.writerow(line_list)
    
    follows = Follow.objects.filter(follow_status='ed', object_pk = target_user_pk)
    follower_pk_list = [follow.user_pk for follow in follows]

    dic_list = Hashtag_Dictionary.objects.filter(user_pk__in=follower_pk_list)
    print "query is finished. size is " + str(len(dic_list))

    user_tag_count = {}
    for dic in dic_list:
        if dic.user_pk in user_tag_count:
            user_tag_count[dic.user_pk][dic.hashtag] = dic.count
        else:
            user_tag_count[dic.user_pk] = {dic.hashtag: dic.count}

    print "Start to write"

    for user, tag_count in user_tag_count.iteritems():
        sorted_tag = sorted(tag_count, key=tag_count.get, reverse=True)[:2]
        for tag in sorted_tag:
            line_list = [user, tag, tag_count[tag]]
            line_list = [str(ele) for ele in line_list]
            writer.writerow(line_list)

    return response

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
    target_user_pk= request.GET.get('target_user_pk', '')
    max_id= request.GET.get('max_id', '')
    next_function= request.GET.get('next_function', '')
    recursive_step= request.GET.get('recursive_step', '1')
    kor_check= request.GET.get('kor_check', 't')
    influ_thresold = int(request.GET.get("influ_thresold", '10000'))

    num_crawler = len(ip_list)
    crawler_index = ip_list.index("http://"+host_ip+"/")
    #crawler_index = 0 
    crawler_domain = ip_list[crawler_index]
    # For develop in local.   

    if target_user_pk == "":
        if target_username == "": return HttpResponseRedirect("/crawl/follow_list")
        target_username_list = target_username.split(",")
        target_user_pk_list = []

        for target_username in target_username_list:
            #target_user_pk = user_by_name(target_username).user_pk
            response = requests.get(crawler_domain+"crawl/user_by_name?recursive=False&username={}&kor_check={}&influ_thresold={}".format(target_username, kor_check, influ_thresold))
            json_response = json.loads(response.text)

            if json_response["success"]: 
                target_user_pk = json_response["target_user_pk"]
                target_user_pk_list.append(target_user_pk)
    else:
        target_user_pk_list = target_user_pk.split(",")
    
    for target_user_pk in target_user_pk_list:
        while max_id != "end":
            while True:
                response = requests.get(crawler_domain+"crawl/followers/"+str(target_user_pk)+"/?max_id={}&recursive_step={}".format(max_id, recursive_step))
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
        max_id = ""

    if next_function=='check_influencer': return HttpResponseRedirect('/crawl/check_influencer?object_pk={}&crawler_index={}&recursive_step={}&kor_check={}&influ_thresold={}'.format(target_user_pk, crawler_index, recursive_step, kor_check, influ_thresold))
    else: return HttpResponseRedirect('/crawl/follow_list')


def check_influencer(request):
    global host_ip
    global ip_list
    num_crawler = len(ip_list)
    object_pk= request.GET.get('object_pk', '')
    recursive_step = request.GET.get('recursive_step', '1')
    crawler_index= int(request.GET.get('crawler_index', '0'))
    last_user_pk= request.GET.get('last_user_pk', '')
    kor_check= request.GET.get('kor_check', 't')
    influ_thresold = int(request.GET.get("influ_thresold", '10000'))
    skip_flag = False
    if last_user_pk != '': skip_flag = True

    followers = Follow.objects.filter(follow_status='ed', object_pk =object_pk)

    num_followers = followers.count()

    for index, follower in enumerate(followers):
        if skip_flag:
            if follower.user_pk == int(last_user_pk): 
                skip_flag = False
                print follower.username
            continue

        crawler_domain = ip_list[crawler_index]
        
        request_counter = 0 
        while True:
            response = requests.get(crawler_domain+"crawl/user_by_name?recursive_step={}&recursive={}&username={}&kor_check={}&influ_thresold={}".format(recursive_step, 'True',follower.username, kor_check, influ_thresold))
            try:
                json_response = json.loads(response.text)
                break
            except:
                request_counter += 1
                if request_counter > 5: break
                print "Some json data is wrong."
                print response.text
                crawler_index = (crawler_index + 1) % num_crawler
                crawler_domain = ip_list[crawler_index]
                continue

        if request_counter > 5: continue
        print str(index)+ " / " + str(num_followers)
        crawler_index = (crawler_index + 1) % num_crawler
        if json_response["success"] == False: 
            if json_response["target_user_pk"] == "Not Influencer": follower.delete()
            continue 
        else:
            print "Caught Influencer."
            crawler_domain = ip_list[crawler_index]
            if recursive_step == '2': continue 
            recursive_step = str(int(recursive_step)+1)
            requests.get(crawler_domain+"crawl/user_follow?next_function={}&target_user_pk={}&recursive_step={}&kor_check={}&influ_thresold={}".format("check_influencer", str(json_response["target_user_pk"]), recursive_step, kor_check, influ_thresold))
            recursive_step = str(int(recursive_step)-1)
            crawler_index = (crawler_index + 1) % num_crawler

    return JsonResponse({'success': True})

def start_hashtag_dictionary(request):
    username = request.GET.get('username', '')
    influencer = user_by_name(username)
    hashtag_dictionary(username, influencer.user_pk)

    curl_url = "https://www.instagram.com/"+username+"/?__a=1"
    response = requests.get(curl_url)
    media_json = response.json()["user"]["media"]

    follower_set = set()
    followers = Follow.objects.filter(follow_status='ed', object_pk = influencer.user_pk)
    for follower in followers:
        follower_set.add(follower.user_pk)

    likers = set()
    for node in media_json["nodes"]:
        media_id = node["id"]
        api.getMediaLikers(media_id)
        response_json = api.LastJson
        for user in response_json['users']:
            if user['pk'] in follower_set: likers.add((user['username'], user['pk']))

    total_liker_number = len(likers)
    for num, liker in enumerate(likers):
        print "/".join((str(num), str(total_liker_number)))
        hashtag_dictionary(liker[0], liker[1])
        

    # Take a follower to get hashtag list.

def hashtag_dictionary(username, user_pk):
    global ip_list
    num_crawler = len(ip_list)
    crawler_index = 0

    curl_url = "https://www.instagram.com/"+username+"/?__a=1"
    response = requests.get(curl_url)
    try:
        media_json = response.json()["user"]["media"]
    except:
        print response
        return True
        # It should be fixed if these code is very necessary.

    for node in media_json["nodes"]:
        media_id = node["id"]
        url_code = node["code"]

        #if "caption" in node: hash_tag_count = node["caption"].count("#")
        if "caption" in node:
            caption_hashtag_list = extract_hash_tags(node["caption"])
            for hashtag in caption_hashtag_list:
                save_hashtag_dic(user_pk, hashtag, url_code)

        crawler_domain = ip_list[crawler_index]
        requests.get("{crawler_domain}crawl/api_hashtag_dic?media_id={media_id}&user_pk={user_pk}&url_code={url_code}".format(crawler_domain=crawler_domain, media_id=media_id, user_pk=user_pk, url_code=url_code))
        crawler_index = (crawler_index + 1) % num_crawler


def api_hashtag_dic(request):
    media_id = request.GET.get('media_id', '')
    user_pk = request.GET.get('user_pk', '')
    url_code = request.GET.get('url_code', '')

    api.getMediaComments(media_id)
    response_json = api.LastJson

    if not 'comments' in response_json: return JsonResponse({'success': 'no comments'})
    comments = response_json['comments']

    for comment in comments:
        if user_pk == comment['user_id']:
            influ_comments = comment['text']
            comment_hashtag_list = extract_hash_tags(influ_comments)
            for hashtag in comment_hashtag_list:
                save_hashtag_dic(user_pk, hashtag, url_code)

    return JsonResponse({'success': True})

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
    hashtag_set = set()
    word_list = s.split('#')
    for word in word_list:
        raw_hashtag = word.split()
        if len(raw_hashtag) == 0: continue
        hashtag_set.add(raw_hashtag[0])
    return hashtag_set


def user_by_name(request):
    username = request.GET.get("username", "")
    recursive = request.GET.get("recursive", 'False')
    kor_check = request.GET.get("kor_check", 't')
    influ_thresold = int(request.GET.get("influ_thresold", '10000'))
    if User.objects.count() > 400000: return JsonResponse({'success': False, 'target_user_pk':"FULL"})
    if User.objects.filter(username = username).exists():
        if recursive == 'False':
            return JsonResponse({'success': True, 'target_user_pk':User.objects.get(username = username).user_pk})
        else:
            return JsonResponse({'success': False, 'target_user_pk':'already visited'})
    else:
        api.searchUsername(username)
        try:
            user_info = api.LastJson["user"]
        except:
            print api.LastJson
            return JsonResponse({'success': False, 'target_user_pk':"API FAIL"})

        if user_info["follower_count"] >= influ_thresold:
            if kor_check == 't':
                if not is_korean(username): return JsonResponse({'success': False, 'target_user_pk': 'Not korean'})
            user = User(created_date=timezone.now())
            user.username = user_info["username"]
            user.usertags_count = user_info["usertags_count"]
            user.media_count = user_info["media_count"]
            user.following_count = user_info["following_count"]
            user.follower_count = user_info["follower_count"]
            user.is_business = user_info["is_business"]
            user.has_chaining = user_info["has_chaining"]
            if "geo_media_count" in user_info : user.geo_media_count = user_info["geo_media_count"]
            else : user.geo_media_count = 0
            user.user_pk = user_info["pk"]
            user.is_verified = user_info["is_verified"]
            user.is_private = user_info["is_private"]
            if "is_favorite" in user_info: user.is_favorite = user_info["is_favorite"]
            else: user.is_favorite = False
            user.external_url = user_info["external_url"]
            user.save()
            print "Saved"
            return JsonResponse({'success': True, 'target_user_pk':user.user_pk})
        else:
            return JsonResponse({'success': False, 'target_user_pk':"Not Influencer"})


def is_korean(username):
    curl_url = "https://www.instagram.com/"+username+"/?__a=1"
    response = requests.get(curl_url)
    media_json = response.json()["user"]["media"]
    for node in media_json["nodes"]:
        try:
            if detect(node["caption"]) == 'ko': 
                print 'korean'
                return True
        except:
            continue
    print 'not korean'
    return False

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
        if Follow.objects.filter(user_pk = follower["pk"], object_pk = target_user_pk, follow_status='ed').exists(): continue
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

def start_hashtag_posts(request):
    global ip_list
    num_crawler = len(ip_list)

    hashtag = request.GET.get("hashtag", '')
    max_id = request.GET.get('max_id', '')
    crawler_index= int(request.GET.get('crawler_index', '0'))
    kor_check = request.GET.get('kor_check', 't')
    influ_thresold = int(request.GET.get("influ_thresold", '10000'))
    post_count = int(request.GET.get("post_count", '0'))


    hashtag_list = hashtag.split(',')

    for hashtag in hashtag_list:
        while max_id != 'end':
            crawler_domain = ip_list[crawler_index]
            response = requests.get(crawler_domain+"crawl/hashtag_posts?hashtag={}&max_id={}&crawler_index={}&kor_check={}&influ_thresold={}&post_count={}".format(hashtag, max_id, crawler_index, kor_check, influ_thresold, post_count))
            result = json.loads(response.text)
            if result['success']: max_id = result["next_max_id"]
            else: time.sleep(10)
            crawler_index = (crawler_index + 1) % num_crawler
            post_count = result["post_count"]
        print "post_count: ", post_count
        max_id =""
    print "post_count: ", post_count

    return JsonResponse({'success':True})

    
def crawl_hashtag_posts(request):
    global ip_list
    num_crawler = len(ip_list)
    
    hashtag = request.GET.get("hashtag", '')
    max_id = request.GET.get('max_id', '')
    kor_check = request.GET.get('kor_check', 't')
    influ_thresold = int(request.GET.get("influ_thresold", '10000'))
    crawler_index= int(request.GET.get('crawler_index', '0'))
    post_count = int(request.GET.get("post_count", '0'))
    
    if max_id == "":
        api.getHashtagFeed(hashtag)
    else: api.getHashtagFeed(hashtag, maxid=max_id)

    hashtag_metadata = api.LastJson
    
    if api.LastResponse.status_code != 200:
        return JsonResponse({'success':False, 'post_count': post_count})

    if "ranked_items" in hashtag_metadata:
        items = hashtag_metadata["ranked_items"]
        post_count = parse_item(items, crawler_index, kor_check, influ_thresold, post_count)
    if "items" in hashtag_metadata:
        items = hashtag_metadata["items"]
        post_count = parse_item(items, crawler_index, kor_check, influ_thresold, post_count)

    if "next_max_id" in hashtag_metadata: 
        max_id = hashtag_metadata["next_max_id"]
        return JsonResponse({'success':True, 'next_max_id': max_id, 'post_count': post_count})
    else:
        return JsonResponse({'success':True, 'next_max_id': 'end', 'post_count': post_count})


def parse_item(items, crawler_index, kor_check, influ_thresold, post_count):
    global ip_list
    num_crawler = len(ip_list)

    for item in items:
        # Only get 2017 data.
        created_at = item['taken_at']
        if datetime.datetime.fromtimestamp(created_at).year != 2017 : 
            print 'not in 2017, created_at: ',created_at
            continue
        post_count += 1
    
        user_id = item["user"]["username"]

        crawler_index = (crawler_index + 1) % num_crawler
        crawler_domain = ip_list[crawler_index]
        response = requests.get(crawler_domain+"crawl/user_by_name?recursive=False&username={}&kor_check={}&influ_thresold={}".format(user_id, kor_check, influ_thresold))
        user_info = json.loads(response.text)
        if not user_info["success"] : continue

        if "comment_count" in item: comment_count = item["comment_count"]
        else: comment_count = 0
        if "view_count" in item: view_count = item["view_count"]
        else: view_count = 0
        if "like_count" in item: like_count = item["like_count"]
        else: like_count = 0
        if "code" in item: url = "https://www.instagram.com/p/"+item["code"]
        else: url =""

        
        influencer = User.objects.get(user_pk = user_info['target_user_pk'])
        engagement_rate = float(comment_count + like_count) / influencer.follower_count
        if engagement_rate > influencer.engagement_rate:
            influencer.engagement_rate = engagement_rate
            influencer.num_commenters = comment_count
            influencer.num_views = view_count
            influencer.num_likes = like_count
            influencer.remark = url
            influencer.save()
    return post_count

def following(request):
    global host_ip
    global ip_list

    username= request.GET.get('username', '')
    target_user_pk= request.GET.get('target_user_pk', '')
    max_id= request.GET.get('max_id', '')
    kor_check= request.GET.get('kor_check', 't')
    influ_thresold = int(request.GET.get("influ_thresold", '0'))

    num_crawler = len(ip_list)
    crawler_index = ip_list.index("http://"+host_ip+"/")
    #crawler_index = 0 
    crawler_domain = ip_list[crawler_index]
    # For develop in local.   

    if target_user_pk == "":
        if username == "": return JsonResponse({'success': False})
        username_list = username.split(",")
        target_user_pk_list = []
        for username in username_list:
            while True:
                response = requests.get(crawler_domain+"crawl/user_by_name?recursive=False&username={}&kor_check={}&influ_thresold={}".format(username, kor_check, influ_thresold))
                json_response = json.loads(response.text)

                if json_response["success"]: 
                    target_user_pk = json_response["target_user_pk"]
                    target_user_pk_list.append(target_user_pk)
                    break
                else:
                    crawler_index = (crawler_index + 1) % num_crawler
                    crawler_domain = ip_list[crawler_index]
    else:
        target_user_pk_list = target_user_pk.split(",")

    num_target_users = len(target_user_pk_list)
    counter = 0
    for target_user_pk in target_user_pk_list:
        counter += 1
        print counter, ' : ', num_target_users
        while max_id != "end":
            while True:
                response = requests.get(crawler_domain+"crawl/api_following/"+str(target_user_pk)+"/?max_id={}".format(max_id))
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
        max_id = ''

    return JsonResponse({"success": True})

def api_following(request, target_user_pk):
    max_id = request.GET.get('max_id', '')
    try:
        if max_id == "": api.getUserFollowings(target_user_pk)
        else: api.getUserFollowings(target_user_pk, maxid=max_id)
        following = api.LastJson
    except:
        print "api response is wrong so return."
        return JsonResponse({'max_id': max_id})
        
    for each_following in following["users"]:
        if Follow.objects.filter(user_pk = each_following["pk"], object_pk = target_user_pk, follow_status='ing').exists(): continue
        follow = Follow(created_date=timezone.now())
        follow.object_pk = target_user_pk
        follow.follow_status = 'ing'
        follow.username = each_following["username"]
        follow.full_name = each_following["full_name"]
        follow.user_pk = each_following["pk"]
        follow.is_verified = each_following["is_verified"]
        follow.is_private = each_following["is_private"]
        if "is_favorite" in each_following: follow.is_favorite = each_following["is_favorite"]
        else: follow.is_favorite = False
        follow.save()
    
    if "next_max_id" in following:
        max_id = following["next_max_id"]
    else:
        max_id = "end"
    
    return JsonResponse({'max_id': max_id})

def from_file_user_by_name(request):
    global host_ip
    global ip_list
    num_crawler = len(ip_list)
    crawler_index= int(request.GET.get('crawler_index', '0'))
    kor_check= request.GET.get('kor_check', 't')
    influ_thresold = int(request.GET.get("influ_thresold", '1000'))

    file_path = "/Users/jack/roka/starlight/starlight/data/animal_followed_group.sort"
    with open(file_path, 'r') as read_f:
        counter = 0 
        len_file = '209667'
        for line in read_f:
            counter += 1
            print counter, '/ '+len_file
            line_list = line.strip().split(' ')
            if len(line_list) < 2: continue
            following_count = line_list[0]
            username = line_list[1]
            if following_count < 5: continue
            
            crawler_domain = ip_list[crawler_index]
            request_counter = 0 
            while True:
                response = requests.get(crawler_domain+"crawl/user_by_name?username={}&kor_check={}&influ_thresold={}".format(username, kor_check, influ_thresold))
                try:
                    json_response = json.loads(response.text)
                    break
                except:
                    request_counter += 1
                    if request_counter > 5: break
                    print "Some json data is wrong."
                    print response.text
                    crawler_index = (crawler_index + 1) % num_crawler
                    crawler_domain = ip_list[crawler_index]
                    continue
            if request_counter > 5: continue
            crawler_index = (crawler_index + 1) % num_crawler

            if json_response["success"]:
                target_user_pk = json_response["target_user_pk"]
                influencer = User.objects.get(user_pk = target_user_pk)
                influencer.remark = 'animal_followed_influencer'
                influencer.save()

def calculate_engagement(request):
    global host_ip
    global ip_list
    num_crawler = len(ip_list)
    crawler_index= int(request.GET.get('crawler_index', '0'))

    users = User.objects.filter(Q(remark='animal_supporter') | Q(remark='animal_followed_influencer'))
    num_users = users.count()
    counter = 0
    for user in users:
        counter += 1
        print counter , ' / ', num_users
        crawler_domain = ip_list[crawler_index]
        request_counter = 0 
        while True:
            response = requests.get(crawler_domain+"crawl/__a_engagement?user_pk={}".format(user.user_pk))
            try:
                json_response = json.loads(response.text)
                break
            except:
                request_counter += 1
                if request_counter > 5: break
                print "Some json data is wrong."
                print response.text
                crawler_index = (crawler_index + 1) % num_crawler
                crawler_domain = ip_list[crawler_index]
                continue
        if request_counter > 5: continue
        crawler_index = (crawler_index + 1) % num_crawler

    return JsonResponse({"success":True})


def __a_engagement(request):
    user_pk= request.GET.get('user_pk', '')
    user = User.objects.get(user_pk = user_pk)
    curl_url = "https://www.instagram.com/"+user.username+"/?__a=1"
    response = requests.get(curl_url)
    media_json = response.json()["user"]["media"]

    comment_count = 0
    likes_count = 0
    views_count = 0
    video_count = 0
    post_count = 0 

    for node in media_json["nodes"]:
        post_count += 1
        comment_count += node['comments']['count']
        likes_count += node['likes']['count']
        if node['is_video']:
            video_count += 1
            views_count += node['video_views']

    if post_count > 0 :
        num_commenters = float(comment_count) / post_count
        num_likes = float(likes_count) / post_count
    else:
        num_commenters = 0
        num_likes = 0
    if video_count > 0 :
        num_views = float(views_count) / video_count
    else:
        num_views = 0 

    user.num_commenters = num_commenters
    user.num_likes = num_likes
    user.num_views = num_views

    user.engagement_rate = float(num_commenters + num_likes + num_views) / user.follower_count
    user.save()
    return JsonResponse({"success": True})
