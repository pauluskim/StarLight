#-*- coding: utf-8 -*-
import sys 
reload(sys)
sys.setdefaultencoding('utf-8')

import argparse, json, os, re, sys, time, datetime, requests
import pdb

sys.path.append('/home/ubuntu/Instagram-API-python')
sys.path.append('/home/ubuntu/Instagram-API-python/insta_crawl/lib/python2.7/site-packages/')
from InstagramAPI import InstagramAPI
#from crawl_followers import *

#api = InstagramAPI("mikecoolboy9840", "dkflrktEh1!*")
#api = InstagramAPI("minvirus716", "als951753")
#api.login() # login

def visted(result_file, progress_file):
    influ_set = set()
    num_posts = 0 
    with open(result_file, 'r') as result_file:
        for line in result_file:
            line_list = line.strip().split('\t')
            influ = line_list[0]
            influ_set.add(influ)
    with open(progress_file, 'r') as progress:
        num_posts = int(progress.readline().strip())
    return influ_set, num_posts

def investigate_user(user_id):
    #if user_id in visited_influ_set: 
    print user_id
    api.searchUsername(user_id)
    print api.LastJson
    print api.LastResponse
    if "user" in api.LastJson:
        num_followers = api.LastJson['user']['follower_count']
        return num_followers
    else: return "Wrong status code"
    
    
def main():

    parser = argparse.ArgumentParser(description='Instagram Crawler')
    parser.add_argument('-t', '--hashtag', type=str, default='도시락', help = 'Hashtag you want to crawl.')
    args = parser.parse_args()
    query = args.hashtag

    dir_path = "./api_influ_with_engagement_rate_min/"
    result_file = dir_path+query+".txt"
    progress_file = dir_path+query+"_progress.txt"
    if os.path.isfile(result_file): visited_influ_set, num_posts =  visted(result_file, progress_file)
    else:
        visited_influ_set = set()
        num_posts = 0


    max_id = "start"
    while max_id != "end":
        if max_id == "start":
            api.getHashtagFeed(query)
        elif max_id == "end":
            break
        else: api.getHashtagFeed(query, maxid=max_id)

        hashtag_metadata = api.LastJson
        if api.LastResponse.status_code != 200:
            print(api.LastJson)
            print "No hashtag info"
            time.sleep(200)
            continue

        if "ranked_items" in hashtag_metadata:
            items = hashtag_metadata["ranked_items"]
            visited_influ_set, num_posts = parse_item(items, visited_influ_set, query, num_posts)
        if "items" in hashtag_metadata:
            items = hashtag_metadata["items"]
            visited_influ_set, num_posts = parse_item(items, visited_influ_set, query, num_posts)
        if "next_max_id" in hashtag_metadata:max_id = hashtag_metadata["next_max_id"]
        else:max_id = "end"

if __name__ == "__main__":
    main()



