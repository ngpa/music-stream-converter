"""Formulas for working with spotify."""
import json
import spotipy

def print_json(x):
    """Print JSON chunks in a custom format."""
    print(json.dumps(x, sort_keys=True, indent=4))

def print_playlist_names(playlist):
    """Print all playlist names, given a playlist JSON object."""
    for x in playlist:
        print(x['name'])

def get_track_list(tracks, spotify):
    """Get all tracks from a playlist."""
    ret = list()
    t = tracks
    while True:
        for x in t['items']:
            ret.append(x)
        if t['next']:
            t = spotify.next(t)
        else:
            break
    return ret

def create_search_query(track_name=None, artist_name=None, album_name=None):
    """Create search string for spotify."""
    query = ''
    if track_name:
        query += 'track:"{}" '.format(track_name)
    if artist_name:
        query += 'artist:"{}" '.format(artist_name)
    if album_name:
        query += 'album:"{}" '.format(album_name)

    return query

def find_correct_song(track_name, potentials, artist_name, album_name=None):
    """Take a Spotify JSON track and finds Spotify URI for the song given."""
    for potential_song in potentials['tracks']['items']:
        if potential_song['name'].lower() == track_name.lower():
            artist_match = False
            for x in potential_song['artists']:
                if x['name'].lower() == artist_name.lower():
                    artist_match = True
                    break
            if not artist_match:
                continue
            if album_name:
                if potential_song['album']['name'].lower() != album_name.lower():
                    continue
            return potential_song['uri']
    print('Couldnt find song')
    return None

    