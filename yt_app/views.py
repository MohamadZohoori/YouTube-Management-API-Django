from django.shortcuts import render
from googleapiclient.discovery import build
import googleapiclient.discovery
from django.http import HttpResponse,JsonResponse
from django.views.decorators.cache import cache_page
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.tools import argparser, run_flow
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from pathlib import Path
from os.path import exists
from django.core.cache import cache,caches
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialAccount
import http.client
import httplib2
import re
import os
import pickle
import json
import requests
import sys
import logging


def home(request):
    return HttpResponse('Welcome to homepage')


def search_results(request):
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = 'AIzaSyAB3st3uGd31sAh7frzO1fgsSM3n0nu22o'
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = DEVELOPER_KEY)
    # Request body
    request = youtube.search().list(
        part="id,snippet",
        type='video',
        q="Spider-Man",
        videoDuration='short',
        videoDefinition='high',
        maxResults=1
    )
    # Request execution
    response = request.execute()
    return JsonResponse(response)




def login(request):
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent
    CLIENT_SECRETS_FILE = os.path.join(BASE_DIR,'client_secret.json')

    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

    # Set up the OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8888)
    api_service_name = "youtube"
    api_version = "v3"

    #requests.post('https://accounts.google.com/o/oauth2/revoke', params={'token': credentials.token}, headers = {'content-type': 'application/x-www-form-urlencoded'})
    uid = request.user.id
    path = os.path.join(BASE_DIR,"temp/login%s.pickle"%uid)
    if exists(os.path.join(BASE_DIR,"temp/login%s.pickle"%uid)):
        os.remove(path) 

    # Set the credentials and create a YouTube Data API client
    youtube = build('youtube', 'v3', credentials=credentials)

    with open("temp/login%s.pickle"%uid, "wb") as token:
        pickle.dump(youtube, token)
        
    return HttpResponse({'Now, you are logged in'})


def logout(request):
    BASE_DIR = Path(__file__).resolve().parent.parent
    CLIENT_SECRETS_FILE = os.path.join(BASE_DIR,'client_secret.json')

    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

    # Set up the OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8888)
    requests.post('https://accounts.google.com/o/oauth2/revoke', params={'token': credentials.token}, headers = {'content-type': 'application/x-www-form-urlencoded'})
    return HttpResponse('logged out')




def subscribeList(request):
    if request.user.is_authenticated:
        BASE_DIR = Path(__file__).resolve().parent.parent  
        uid = request.user.id
        if exists(os.path.join(BASE_DIR,"temp/login%s.pickle"%uid)):
            with open("temp/login%s.pickle"%uid, "rb") as token:
                unpickler = pickle.Unpickler(token)
                youtube = pickle.load(token)
            
            channel_id_cache = 'User%s'%uid
            if (channel_id_cache in cache or channel_id_cache in cache == True or channel_id_cache in cache == 'true'):
                channel_list = get_subscribe_List(uid, youtube)

                if channel_list != 'error':
                    return JsonResponse({'subscribe_List': channel_list}, safe=False)
                else:
                    return HttpResponse('Token expired! Please log in again!')
            else:
                channel_id_data = get_channel_id(uid,youtube)
                if channel_id_data == 'error':
                    return HttpResponse('Token expired! Please log in again!')
                else:
                    channel_list = get_subscribe_List(uid, youtube)
                    if channel_list != 'error':
                        return JsonResponse({'subscribe_List': channel_list}, safe=False)
                    else:
                        return HttpResponse('Token expired! Please log in again!')
        else:
            return HttpResponse('please login first!')
    else:
        return HttpResponse('Please authenticate first!')




def get_channel_id(uid, youtube):
    BASE_DIR = Path(__file__).resolve().parent.parent   
    cache_key = 'User%s'%uid
    if (cache_key in cache == True or cache_key in cache == 'true' or cache_key in cache):
        data = cache.get(cache_key)
        return data
    else: 
        request = youtube.channels().list(
            part="id,status,snippet,statistics",
            mine=True
        )
        try:
            response = request.execute()
            channel_id = response['items'][0]['id']
            cache.set(cache_key, channel_id)
            return channel_id
        except:
            return 'error'


def get_subscribe_List(uid, youtube):
    channel_id_cache = 'User%s'%uid
    channel_id_data = cache.get(channel_id_cache)
    sub_cache_key = 'subList%s'%uid 
    if (sub_cache_key in cache == True or sub_cache_key in cache == 'true' or sub_cache_key in cache):
        channel_list = cache.get(sub_cache_key)
        return channel_list
    else:
        # Continue with your API request using the authenticated YouTube object
        request = youtube.subscriptions().list(
            part="snippet,contentDetails",
            channelId = channel_id_data
        )
        try:
            response = request.execute()
            channel_list = []
            for i in range(int(response['pageInfo']['totalResults'])):
                channel_list.append(response['items'][i]['snippet']['title'])
            cache.set(sub_cache_key, channel_list)
            return channel_list
        except:
            return 'error'



def find_channel_id(request):
    if request.user.is_authenticated:
        BASE_DIR = Path(__file__).resolve().parent.parent   
        uid = request.user.id 
        if exists(os.path.join(BASE_DIR,"temp/login%s.pickle"%uid)):
            with open("temp/login%s.pickle"%uid, "rb") as token:
                unpickler = pickle.Unpickler(token)
                youtube = pickle.load(token)

            #cache.delete(cache_key)
            cache_key = 'User%s'%uid
            if (cache_key in cache == True or cache_key in cache == 'true' or cache_key in cache):
                print('here')
                data = cache.get(cache_key)
                return JsonResponse({'cache':'True', 'channel_id': data}, safe=False)

            else:
                print('caching again!')   
                request = youtube.channels().list(
                    part="id,status,snippet,statistics",
                    mine=True
                )
                try:
                    response = request.execute()
                    channel_id = response['items'][0]['id']
                    cache.set(cache_key, channel_id)
                    return JsonResponse({'cache':'False', 'channel_id': channel_id, 'cache_set': cache_key in cache }, safe=False)
                except:
                    return HttpResponse('Token expired! Please log in again!')
        else:
            return JsonResponse({"Please login first!"}, safe = False)
    else:
        return HttpResponse('Please authenticate first!')






def upload_video(request):

    httplib2.RETRIES = 1

    # Maximum number of times to retry before giving up.
    MAX_RETRIES = 10

    # Always retry when these exceptions are raised.
    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
        http.client.IncompleteRead, http.client.ImproperConnectionState,
        http.client.CannotSendRequest, http.client.CannotSendHeader,
        http.client.ResponseNotReady, http.client.BadStatusLine)

    VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

    BASE_DIR = Path(__file__).resolve().parent.parent    
    if exists(os.path.join(BASE_DIR,'temp/login.pickle')):
        with open("temp/login.pickle", "rb") as token:
            unpickler = pickle.Unpickler(token)
            youtube = pickle.load(token)
        try:
          initialize_upload(youtube)
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        
        return HttpResponse('uploading')

    else:
        return HttpResponse('please login first!')   




def initialize_upload(youtube):
    BASE_DIR = Path(__file__).resolve().parent.parent    
    tags = None
    
    '''
    if options.keywords:
      tags = options.keywords.split(",")
    '''

    body=dict(
      snippet=dict(
        title='title',
        description='description',
        tags=tags,
        categoryId='id'
      ),
      status=dict(
        privacyStatus="public"
      )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
      part=",".join(body.keys()),
      body=body,
      media_body=MediaFileUpload(os.path.join(BASE_DIR,'videos/1.mp4'), chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)


def resumable_upload(insert_request):
    import random
    import time
    from googleapiclient.errors import HttpError

    httplib2.RETRIES = 1

    # Maximum number of times to retry before giving up.
    MAX_RETRIES = 10

    # Always retry when these exceptions are raised.
    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
        http.client.IncompleteRead, http.client.ImproperConnectionState,
        http.client.CannotSendRequest, http.client.CannotSendHeader,
        http.client.ResponseNotReady, http.client.BadStatusLine)

    VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." % response['id'])
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content.decode())
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)


