# Using YouTube OAuth2.0 to fetch Comments (Good for customization)

'''
SOURCE
# https://www.analyticssteps.com/blogs/extracting-pre-processing-youtube-comments (Setting up OAuth 2.0)
# https://github.com/ripulagrawal98/Analytic_Steps/tree/master/Extract%20%26%20Pre-process%20-YouTube-Comments

NOTE: Delete the token.pickle file and rerun the code if you get 'Request not identified' error
'''

#!pip install google-api-python-client
#!pip install google-auth google-auth-oauthlib google-auth-httplib2
#!pip install pickle-mixin

import csv
import os
import pickle
import demoji
from langdetect import detect
import re

import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    #  Check if the credentials are invalid or do not exist
    if not credentials or not credentials.valid:
        # Check if the credentials have expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_console()

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
service = get_authenticated_service()


'''
Your request can also use the Boolean NOT (-) and OR (|) operators to exclude videos or to 
find videos that are associated with one of several search terms. For example, to search for 
videos matching either "boating" or "sailing", set the q parameter value to boating|sailing. 
Similarly, to search for videos matching either "boating" or "sailing" but not "fishing", set 
the q parameter value to boating|sailing -fishing. Note that the pipe character must be 
URL-escaped when it is sent in your API request. The URL-escaped value for the pipe character is %7C.

'''
# FETCHING VIDEOS MATCHING THE SEARCH CRITERIA
# https://developers.google.com/youtube/v3/docs/search/list

query = "Royal Enfield Himalayan"

# Default value of maxResults is 5 (Range: 0 to 50 inclusive)


query_results = service.search().list(part = 'snippet',
                                      q = query,
                                      order = 'relevance', 
                                      type = 'video',
                                      relevanceLanguage = 'en',
                                      maxResults=5,
                                      safeSearch = 'moderate').execute()

video_id = []
channel = []
video_title = []
video_desc = []

for item in query_results['items']:
    
    video_id.append(item['id']['videoId'])
    channel.append(item['snippet']['channelTitle'])
    video_title.append(item['snippet']['title'])
    video_desc.append(item['snippet']['description'])

#----------------------------------------------------------------------------------------------------
query_results['items']

video_id = video_id[0]
channel = channel[0]
video_title = video_title[0]
video_desc = video_desc[0]

video_id = 'qhlMLVRpupo'

video_id_pop = []
channel_pop = []
video_title_pop = []
video_desc_pop = []
comments_pop = []
comment_id_pop = []
reply_count_pop = []
like_count_pop = []
comment_date_pop = []

comments_temp = []
comment_id_temp = []
reply_count_temp = []
like_count_temp = []
comment_date_temp = []

#-----------------------------------------------------------------------------------------------------
# RETRIEVING ALL COMMENT THREADS ASSOCIATED WITH A PARTICULAR VIDEO
# https://developers.google.com/youtube/v3/docs/commentThreads/list

# maxResults specifies the maximum number of items that should be returned in the result set
# default: 20, range: 1 to 100, inclusive

nextPage_token = None

while 1:
    response = service.commentThreads().list(
                    part = 'snippet',
                    videoId = video_id,
                    maxResults = 100, 
                    order = 'time', 
                    textFormat = 'plainText',
                    pageToken = nextPage_token
                    ).execute()

    nextPage_token = response.get('nextPageToken')
    
    for item in response['items']:
        comments_temp.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
        comment_id_temp.append(item['snippet']['topLevelComment']['id'])
        reply_count_temp.append(item['snippet']['totalReplyCount'])
        like_count_temp.append(item['snippet']['topLevelComment']['snippet']['likeCount'])
        comment_date_temp.append(item['snippet']['topLevelComment']['snippet']['publishedAt'])
        
        comments_pop.extend(comments_temp)
        comment_id_pop.extend(comment_id_temp)
        reply_count_pop.extend(reply_count_temp)
        like_count_pop.extend(like_count_temp)
        comment_date_pop.extend(comment_date_temp)

        video_id_pop.extend([video_id]*len(comments_temp))
        channel_pop.extend([channel]*len(comments_temp))
        video_title_pop.extend([video_title]*len(comments_temp))
        video_desc_pop.extend([video_desc]*len(comments_temp))

    if nextPage_token is  None:
        break

# print(allVideos)
#

#------------------------------------------------------------------------------------------------
response['items']

output_dict = {
        'Channel': channel_pop,
        'Video Title': video_title_pop,
        'Video Description': video_desc_pop,
        'Video ID': video_id_pop,
        'Date': comment_date_pop,
        'Comment': comments_pop,
        'Comment ID': comment_id_pop,
        'Replies': reply_count_pop,
        'Likes': like_count_pop}

output_df = pd.DataFrame(output_dict, columns = output_dict.keys())

output_df[output_df['Comment']=="Indian made"]

unique_df = output_df.drop_duplicates(subset=['Comment ID'])
unique_df

unique_df.to_csv("yt_comments.csv",index = False)