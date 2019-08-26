from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.utils.http import urlencode
from django.template import loader
from converter.general import parse_url, date_to_string, string_to_date
from converter.apple_music_connect import AppleMusic
from converter.spotify_connect import Spotify
from spotipy.oauth2 import SpotifyOAuth
from converter.models import Song
from json import loads, dumps
from datetime import datetime, timedelta

# Create your views here.

def route_type(type, id=None):
    """Return the proper object given the url type."""
    if type == 'spotify':
        return Spotify(id=id)
    elif type == 'apple-music':
        return AppleMusic(id)
    else:
        raise Exception('Invalid route sent.')

def index(request, context={}):
    context['spotify_logged_in'] = verify_spotify_token(request)

    # playlist = obj.pull_playlist_info()
    # isrcs = [ {'isrc':song['isrc'], 'track_name':song['name'], 'artist_name':song['artists']} for song in playlist['tracks'] ]
    # searched_set = set([ obj.search_for_song(isrc=x['isrc'], song_name=x['track_name'], artist_name=x['artist_name']) for x in isrcs ])
    # isrc_list = [isrc['isrc'] for isrc in isrcs]
    # count_dict = {x:isrc_list.count(x) for x in isrc_list}
    # total = 0
    # for x in count_dict.values():
    #     total += x
    # print(total)
    return render(request, 'converter/index.html', context)

def enter_url(request):
    context = {}
    try:
        url = request.POST['url']
    except:
        print('Error in the post request')
    try:
        print('got POST request; url = {}'.format(url))
        type, id, other = parse_url(url)
        music_handler = route_type(type, id)
        context = music_handler.pull_playlist_info()
    except:
        print('Error handling url')

    context['spotify_logged_in'] = verify_spotify_token(request)
    temp = context
    context['last_playlist_search'] = dumps(temp)
    return render(request, 'converter/enter-url.html', context)

import spotipy
from spotipy import oauth2

cid ="57fb8390315249aeafcd15d177111c69" 
secret = "a525345d30b64f2d999679e40156462e"
scope = 'playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'
redirect_url = 'http://localhost:8000/converter/authorize-spotify/'
test_playlist = 'https://open.spotify.com/user/nickpanagakis/playlist/09634SN5Up9L489fxSlelM?si=iNVQDltQS2uawaRAwdUoVw'

sp_oauth = oauth2.SpotifyOAuth(cid, secret, redirect_url, scope=scope, cache_path='.spotipycache')

def authorize_spotify(request):
    """Log a user into Spotify."""
    access_token = ''
    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = str(request).split("'")[1]
        code = sp_oauth.parse_response_code(url)
        if code:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print("Access token available! Trying to get user information...")
        spotify = spotipy.Spotify(access_token)
        request.session['spotify_token'] = token_info
        request.session['spotify_expiration'] = date_to_string(datetime.now() + timedelta(seconds=token_info['expires_in']))
        results = spotify.current_user()
        return index(request, context={'new_spotify': True})
    else:
        return HttpResponse('Didnt work dickhead')

def verify_spotify_token(request):
    """Verifies that spotify is logged in. If it is not, attempts to refresh the token, otherwise returns false."""
    if 'spotify_token' not in request.session.keys():
        return False
    else:    
        expiration = string_to_date(request.session['spotify_expiration'])
        if expiration > datetime.now():
            return True
        else:
            try:
                refresh_token = sp_oauth.refresh_access_token(request.session['spotify_token']['refresh_token'])
                request.session['token'] = refresh_token
                request.session['spotify_expiration'] = date_to_string(datetime.now() + timedelta(seconds=refresh_token['expires_in']))
                return True
            except:
                return False

def login_spotify(request):
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def logout_spotify(request):
    try:
        del(request.session['spotify_token'])
    except:
        print('Session was already deleted')
    return index(request, context={'del_spotify': True})

def login_apple_music(request):
    pass

def logout_apple_music(request):
    pass

def convert_to_spotify(request):
    context = {}
    context['spotify_loged_in'] = verify_spotify_token(request)
    tracks = loads(request.POST['last_playlist_search'])
    output_type = request.GET['output_type']
    isrc_list = [{'isrc':song['isrc'], 'track_name':song['name'], 'artists':song['artists'], 'album':song['album']} for song in tracks['tracks']]
    if output_type == 'spotify':
        auth_token = request.session['spotify_token']['access_token']
        handler = Spotify(token=auth_token)
        if datetime.now() > string_to_date(request.session['spotify_expiration']):
            handler.refresh_token(request.session['spotify_token'])
            request.session['spotify_token'] = new_token
        origin = 'apple-music'
    elif output_type =='apple-music':
        origin = 'spotify'

    found_ids, missed = handler.find_ids_from_isrcs(isrc_list)
    new_playlist = handler.create_and_fill_playlist(name=tracks['name'], origin=origin, id_list=found_ids)
    
    return HttpResponse(dumps(tracks))
    # return HttpResponse('Converting playlist {} (length of {} tracks) to Spotify'.format(request.POST['playlist_name'], len(loads(request.POST['playlist_tracks']))))
1
def convert_to_apple_music(request):
    return HttpResponse('Converting to Apple Music')