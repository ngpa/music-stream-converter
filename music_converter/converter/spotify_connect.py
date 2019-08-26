"""Establish basic connection to spotify servers."""
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import os
import urllib.parse
from converter.models import Song
from converter.general import clean_album, clean_song
# from spotify_formulas import *

class Spotify:
    """Collection of data and functions regarding Spotify."""

    def __init__(self, id=None, token=None):
        """Initialize a Spotify Object."""
        self.cid ="57fb8390315249aeafcd15d177111c69" 
        self.secret = "a525345d30b64f2d999679e40156462e"
        self.scope = 'playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'
        self.redirect_url = 'http://localhost:8000/converter/authorize-spotify/'
        

        if token:
            self.token = token
            self.spotify = spotipy.Spotify(auth=token)
            self.username = self.spotify.me()['id']
        else:
            self.username = 'nickpanagakis'
            client_credentials_manager = SpotifyClientCredentials(client_id=self.cid, client_secret=self.secret)
            self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.id = id
        self.playlist_info = []
        self.playlist_name = ""
    
    def reset(self):
        """Reset the id and playlist_info variables."""
        self.id = None
        self.playlist_info = []

    def set_id(self, id):
        """Set new id."""
        self.id = id

    def __create_search_query(self, isrc=None, **kwargs):
        """Create search string for spotify."""
        query_list = list()
        if isrc:
            query = 'isrc:{}'.format(isrc)
        else:
            if 'track_name' in kwargs.keys():
                query_list.append('''track:"{}"'''.format(kwargs['track_name']).replace("'", ""))
            if 'artist_name' in kwargs.keys():
                query_list.append('''artist:"{}"'''.format(kwargs['artist_name']).replace("'", ""))
            if 'album_name' in kwargs.keys():
                query_list.append('''album:"{}"'''.format(kwargs['album_name']).replace("'", ""))

            if len(kwargs.keys()) > 1:
                query = ' AND '.join(query_list)
            else:
                query = ' '.join(query_list)
        return query

    def __find_correct_song(self, potentials, track_name=None, artist_name=None, album_name=None, isrc=None, db_obj=None, clean_inputs=False):
        """Take a Spotify JSON track and finds Spotify ID for the song given."""
        for potential_song in potentials['tracks']['items']:
            if isrc:
                if potential_song['external_ids']['isrc'] == isrc:
                    if db_obj:
                        db_obj.spotify_id = potential_song['id']
                    else:
                        db_obj = Song(isrc=isrc, spotify_id=potential_song['id'])
                    db_obj.save()                    
                    return potential_song['id']
            if clean_inputs:
                track_name, query_artists = clean_song(track_name)
                potential_song_name, potential_artists = clean_song(potential_song['name'])
                if album_name:
                    album_name = clean_album(album_name)
                    potential_album_name = clean_album(potential_song['album']['name'])
            else:
                track_name = track_name
                album_name = album_name
                potential_song_name = potential_song['name']
                potential_album_name = potential_song['album']['name']

            if potential_song_name.lower() == track_name.lower():
                if artist_name:
                    query_set = list(artist_name)
                    result_set = [ artist['name'].lower() for artist in potential_song['artists'] ]
                    if clean_inputs:
                        result_set.extend(potential_artists)
                        query_set.extend(query_artists)
                    if len(query_set) < len(result_set):
                        smaller = {} x.lower() for x in query_set }
                        larger = { x.lower() for x in result_set }
                    else:
                        smaller = { x.lower() for x in result_set }
                        larger = { x.lower() for x in query_set }
                    inside = 0
                    for x in smaller:
                        if x in larger:
                            inside += 1
                    if inside < .4 * len(larger):
                        continue
                        
                if album_name:
                    if potential_song_album.lower() != album_name.lower():
                        continue
                return potential_song['id']
        print('Couldnt find song {}'.format(isrc))
        return None
    
    def search_for_song(self, song_name=None, artist_name=None, album_name=None, isrc=None):
        """Return the uri of a song based on its name and artist."""
        try:
            song_db = Song.objects.get(isrc=isrc)
            if song_db.spotify_id:
                return song_db.spotify_id
            else:
                in_db = True
                raise()
        except:
            if not in_db:
                song_db = None
            query = self.__create_search_query(track_name=song_name, artist_name=artist_name, album_name=album_name, isrc=isrc)
            raw_output = self.spotify.search(query, type='track')
            song = self.__find_correct_song(raw_output, track_name=song_name, artist_name=artist_name, album_name=album_name, isrc=isrc, db_obj=song_db)
        return song

    def pull_playlist_info(self):
        """Get info for all songs in the playlist."""
        playlist = self.spotify.user_playlist(self.username, playlist_id=self.id)
        self.playlist_name = playlist['name']
        playlist = playlist['tracks']

        try:
            while True:
                ids = self.__get_song_info(playlist)
                self.playlist_info.extend(ids)
                playlist = self.spotify.next(playlist)
        except:
            return {
                'tracks': self.playlist_info,
                'name': self.playlist_name,
                'type': 'Spotify'
                }

    def __get_song_info(self, playlist):
        """Return the song info for all songs in a playlist."""
        track_info = playlist['items']
        track_list = list()
        for x in track_info:
            temp_dict = dict()
            temp_dict['type'] = 'spotify'
            temp_dict['name'] = x['track']['name']
            temp_dict['artists'] = [ name['name'] for name in x['track']['artists'] ]
            temp_dict['album'] = x['track']['album']['name']
            temp_dict['image'] = x['track']['album']['images'][2]['url']
            temp_dict['isrc'] = x['track']['external_ids']['isrc']
            temp_dict['id'] = x['track']['id']
            track_list.append(temp_dict)

            try:
                song = Song.objects.get(isrc=temp_dict['isrc'])
                song.spotify_id = temp_dict['id']
            except:
                song = Song(isrc=temp_dict['isrc'], spotify_id=temp_dict['id'])
            song.save()
        return track_list


    def find_ids_from_isrcs(self, isrc_list, duplicates_allowed=True):
        ids = list() if duplicates_allowed else set()
        missed = set()
        for track in isrc_list:
            isrc = track['isrc']
            try:
                db_item = Song.objects.get(isrc=isrc)
                if db_item.spotify_id:
                    id = db_item.spotify_id
                else:
                    raise()
            except:
                isrc_query = self.__create_search_query(isrc=isrc)
                data_query = self.__create_search_query(track_name=track['track_name'], album_name=track['album'])
                cleaned_query = self.__create_search_query(track_name=clean_song(track['track_name']), album_name=clean_album(track['album']))
                isrc_output = self.spotify.search(isrc_query, type='track')
                temp = self.__find_correct_song(isrc_output, isrc=isrc, db_obj=db_item)
                if temp:
                    id = temp
                else:
                    data_output = self.spotify.search(data_query, type='track')
                    temp = self.__find_correct_song(data_output, artist_name=track['artists'], track_name=track['track_name'])
                    if temp:
                        id = temp
                    else:
                        cleaned_output = self.spotify.search(cleaned_query, type='track')
                        id = self.__find_correct_song(cleaned_output, artist_name=track['artists'], track_name=track['track_name'], clean_inputs=True)
            if id:
                db_item.spotify_id = id
                db_item.save()
                if duplicates_allowed:
                    ids.append(id)
                else:
                    ids.add(id)
            else:
                missed.add(isrc)
        return ids, missed

    def create_and_fill_playlist(self, **kwargs):
        name = kwargs['name']
        origin = kwargs['origin']
        spotify_ids = kwargs['id_list']

        new_playlist_id = self.__create_playlist(name, origin)
        # Figure out what i meant with this
        for x in range(0, len(spotify_ids), 75):
            temp = spotify_ids[x:x+75]
            _ = self.spotify.user_playlist_add_tracks(self.username, new_playlist_id, temp)

        return new_playlist_id

    def __create_playlist(self, name, origin):
        """Create a new playlist for the user and return the playlist id."""
        new_playlist = self.spotify.user_playlist_create(self.username, name)['id']
        return new_playlist


# country_uri = spotify:user:nickpanagakis:playlist:10I0UHW6HLzErU2bMHLNiJ
# https://open.spotify.com/user/nickpanagakis/playlist/10I0UHW6HLzErU2bMHLNiJ?si=Xh3jpvdfTYmL6CMOzxpw_A

# emmy url = https://open.spotify.com/user/emmypanagakis/playlist/2BoI5znYliukikXZlLyeW3?si=sNysrLtyTZOxk4LQ6xROgw


# Create a spotifyObject 
# spotify = spotipy.Spotify(auth=token)

# current_user = spotify.current_user()
# playlists = spotify.current_user_playlists()['items'] # this returns a list of dictionaries, each describing a type of playlist
# print_json(playlists)
# tracks = spotify.user_playlist_tracks(username, playlist_id="spotify:playlist:10I0UHW6HLzErU2bMHLNiJ") # Eventually replace playlist_id with playlists['id']
# track_list = get_track_list(tracks, spotify)

# query = create_search_query(track_name='Die a Happy Man', artist_name='Thomas Rhett')
# test = spotify.search(query, type='track')
# song = find_correct_song('Die a Happy Man', test, artist_name='Thomas Rhett')