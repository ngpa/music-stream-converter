"""Helper formulas for apple music."""
import applemusicpy
import json

def print_json(x):
    """Print JSON chunks in a custom format."""
    print(json.dumps(x, sort_keys=True, indent=4))

def has_next(json_dict):
    """Determine whether there are more songs to fetch in the playlist."""
    return 'next' in json_dict.keys()

def get_next(apple_music, playlist_id, offset):
    """Get the next 100 tracks in a given playlist."""
    return apple_music.playlist_relationship(playlist_id, 'tracks', offset=100)

def get_playlist_id(url):
    """Parse out the playlist id from a url."""
    url_list = url.split('/')
    return url_list[len(url_list) - 1]


def get_isrcs(playlist, tracks=None):
    """Get a list of song infos for a playlist."""
    if len(playlist['data']) > 1:
        print('Oops! Length is greater than 1')
    track_info = playlist['data'][0]['relationships']['tracks']['data']

    if tracks:
        track_list = tracks
    else:
        track_list = list()

    for x in track_info:
        temp_dict = dict()
        temp_dict['name'] = x['name']
        temp_dict['artist'] = x['artist']
        temp_dict['album'] = x['album']
        temp_dict['isrc'] = x['isrc']
        track_list.append(temp_dict)

    return track_list

def search_for_song(apple_music, song_name, artist_name, album_name=None):
    """Return the isrc of a song based on its name and artist."""
    results = apple_music.search(song_name, types=['songs'], limit=10)

    for song in results['results']['songs']['data']:
        if song['attributes']['artistName'].lower() == artist_name.lower() and song['attributes']['name'].lower() == song_name.lower():
            return song['attributes']['isrc']