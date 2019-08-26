"""Establish basic connection to apple music servers."""
import applemusicpy
import re
from converter.models import Song

# kelsey playlist: https://music.apple.com/us/playlist/2019/pl.u-zPyLm03TkWAX30
# k = kels['data'][0]['relationships']['tracks'][0]['attributes']['name']

class AppleMusic:
    """Collection of data and functions regarding apple music."""
    
    def __init__(self, id=None):
        """Initialize an AppleMusic object."""
        self.key_id = 'UL5GUU9TUZ'
        self.team_id = '564AWN3BL5'
        
        # Need to replace this when it goes on to a real hosting site
        with open('/Users/nickpanagakis/Desktop/Music-Project/music_converter/converter/AuthKey_UL5GUU9TUZ.p8', 'r') as key_file:
            self.secret_key = key_file.read()
        self.apple_music = applemusicpy.AppleMusic(self.secret_key, self.key_id, self.team_id)
        self.id = id
        self.playlist_info = []

    def reset(self):
        self.id = None
        self.playlist_info = []
        self.playlist_name = ""

    def set_id(self, id):
        self.id = id

    def search_for_song(self, song_name=None, artist_name=None, album_name=None, isrc=None):
        """Return the isrc of a song based on its name and artist."""
        try:
            song_db = Song.objects.get(isrc=isrc)
            if song_db.apple_music_id:
                return song_db.apple_music_id
            else:
                id_db = True
                raise()
        except:
            results = self.apple_music.search(song_name, types=['songs'], limit=10)

            for song in results['results']['songs']['data']:
                if song['attributes']['artistName'].lower() == artist_name.lower() and song['attributes']['name'].lower() == song_name.lower():
                    return song['attributes']['isrc']

    def pull_playlist_info(self):
        """Get info for all songs in the playlist."""
        offset = 0
        self.__get_name()
        try:
            while True:
                playlist = self.__get_next(offset)
                ids = self.__get_song_info(playlist)
                self.playlist_info.extend(ids)
                offset += 100
        except:
            return {
                'tracks': self.playlist_info,
                'name': self.playlist_name,
                'type': 'Apple Music'
            }


    def __get_song_info(self, playlist):
        """Get a list of song infos for a playlist."""
        track_info = playlist['data']
        track_list = list()
        for x in track_info:
            temp_dict = dict()
            temp_dict['type'] = 'apple-music'
            temp_dict['name'] = x['attributes']['name']
            temp_dict['artists'] = [ name.strip() for name in re.split(', |&', x['attributes']['artistName']) ]
            temp_dict['album'] = x['attributes']['albumName']
            temp_dict['image'] = x['attributes']['artwork']['url'].format(w=64, h=64)
            temp_dict['isrc'] = x['attributes']['isrc']
            temp_dict['id'] = x['attributes']['playParams']['id']
            track_list.append(temp_dict)

            try:
                song = Song.objects.get(isrc=temp_dict['isrc'])
                song.apple_music_id = temp_dict['id']
            except:
                song = Song(isrc=temp_dict['isrc'], apple_music_id=temp_dict['id'])
            song.save()

        return track_list

    def __get_next(self, offset):
        """Get the next 100 tracks in a given playlist."""
        return self.apple_music.playlist_relationship(self.id, 'tracks', offset=offset)

    def __get_name(self):
        """Return the name of the given playlist."""
        playlist = self.apple_music.playlist(self.id)
        self.playlist_name = playlist['data'][0]['attributes']['name']