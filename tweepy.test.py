import tweepy
import webbrowser
import pickle
import os
import sys
import csv
import StringIO

# this assumes the existence of a credentials.py in your sys.path holding key/secret for Twitter application
# https://dev.twitter.com/apps -- e.g., one of @rdhyee's: https://dev.twitter.com/apps/171403/show

from credentials import consumer_key, consumer_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

# set the cache_dir to the "cache" dir in the same directory as this script
file_cache = tweepy.FileCache(cache_dir=os.path.join(os.path.split(sys.argv[0])[0], "cache"))

def get_user_followers(api, user_id):
    user = api.get_user("rdhyee")
    print user.screen_name
    print user.followers_count
    for friend in tweepy.Cursor(api.followers, screen_name=user.screen_name).items():
       print friend.screen_name

# if auth.dat exists, read in the auth token, else do the authn dance

tweepy_config_path = os.path.join(os.path.expanduser("~"), ".tweepyauth")

try:
    auth_file = open(tweepy_config_path)
    auth = pickle.load(auth_file)
    auth_file.close()
    api = tweepy.API(auth,cache=file_cache)
except:
    try:
        redirect_url = auth.get_authorization_url()
        webbrowser.open_new_tab(redirect_url)
        # Example w/o callback (desktop)
        verifier = raw_input('Verifier:')
        # Get access token
        auth.get_access_token(verifier)
        api = tweepy.API(auth,cache=file_cache)
        # auth succeeded -- print out access key, secret
        print "auth succeeded"
        print "auth token key, secret", auth.access_token.key, auth.access_token.secret
        auth_file = open(tweepy_config_path ,"w")
        pickle.dump(auth,auth_file)
        auth_file.close()
    
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'
    
    
# now let's download all my status updates

# status: ['author', 'contributors', 'coordinates', 'created_at', 'destroy', 'favorite', 'favorited', 'geo', 'id', 'in_reply_to_screen_name', 'in_reply_to_status_id', 'in_reply_to_user_id', 'parse', 'parse_list', 'place', 'retweet', 'retweets', 'source', 'text', 'truncated', 'user']
# author: [ 'contributors_enabled', 'created_at', 'description', 'favourites_count', 'follow', 'followers', 'followers_count', 'followers_ids', 'following', 'friends', 'friends_count', 'geo_enabled', 'id', 'lang', 'lists', 'lists_memberships', 'lists_subscriptions', 'location', 'name', 'notifications', 'parse', 'parse_list', 'profile_background_color', 'profile_background_image_url', 'profile_background_tile', 'profile_image_url', 'profile_link_color', 'profile_sidebar_border_color', 'profile_sidebar_fill_color', 'profile_text_color', 'protected', 'screen_name', 'statuses_count', 'time_zone', 'timeline', 'unfollow', 'url', 'utc_offset', 'verified']

output_file = StringIO.StringIO()
fieldnames = ['status_id', 'status_text', 'status_created_at', 'author_screen_name', 'author_id', 'status_favorited', 'status_in_reply_to_screen_name', 'status_in_reply_to_status_id', 'status.in_reply_to_user_id', 'status_geo']

c_writer = csv.DictWriter(output_file,fieldnames=fieldnames)
c_writer.writerow(dict([(h,h) for h in fieldnames]))


# HAVE TO HANDLE unicode ENCODING PROPERLY
for i, status in enumerate(tweepy.Cursor(api.user_timeline, count=100, include_rts=True).items()):
    text = status.text.encode("UTF-8")
    print i, text, type(text)
    author = status.author
    #print status.id, status.text, status.created_at, status.favorited, status.in_reply_to_screen_name, status.in_reply_to_status_id, status.in_reply_to_user_id
    #print status.geo
    #print author.screen_name, author.id
    status_data = {'status_id':status.id, 'status_text':text, 'status_created_at':status.created_at, \
                   'author_screen_name':author.screen_name, 'author_id':author.id, 'status_favorited':status.favorited, \
                   'status_in_reply_to_screen_name':status.in_reply_to_screen_name, 'status_in_reply_to_status_id':status.in_reply_to_status_id, \
                   'status.in_reply_to_user_id':status.in_reply_to_user_id, 'status_geo':status.geo}
    c_writer.writerow(status_data)
    
out_file = open("mytweets.csv","w")
out_file.write(output_file.getvalue())
out_file.close()

# to refresh to get the latest tweets, what are the options.  One can grab tweets later than a certain time -- though that won't deal with the case of some tweets having been deleted
# in the meantime.



