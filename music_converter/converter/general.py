from datetime import datetime
import re

def parse_url(url):
    """Determine the music service provider given the url."""
    url_list = url.split('/')
    id = url_list[len(url_list) - 1]

    if 'spotify' in url_list[2]:
        id = id.split('?')[0]
        return 'spotify', id, 'apple-music'
    elif 'apple' in url_list[2]:
        return 'apple-music', url_list[len(url_list) - 1], 'spotify'
    else:
        raise Exception('Invalid URL entered.')

def date_to_string(date):
    return datetime.strftime(date, "%Y-%m-%d %H:%M:%S")

def string_to_date(string):
    return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

def clean_song(song):
    dash_search = ' - .+'
    feat_search = '\(?feat\.? .+'
    with_search = '\(?with .+'
    artists = list()

    dash_stop = re.search(dash_search, song)
    if dash_stop:
        song = song[:dash_stop.span()[0]]
    feat_stop = re.search(feat_search, song)
    if feat_stop:
        s = re.search('\(feat\. .+\)', song)
        feat = song[s.span()[0] + 7 : s.span()[1] - 1]
        a = re.split(', | & ', feat)
        artists.extend(a)
        song = song[:feat_stop.span()[0]]
    with_stop = re.search(with_search, song)
    if with_stop:
        s = re.search('\(with\. .+\)', song)
        feat = song[s.span()[0] + 7 : s.span()[1] - 1]
        a = re.split(', | & ', feat)
        artists.extend(a)
        song = song[:with_stop.span()[0]]

    return song.rstrip(), artists

def clean_artist(artist):
    pass

def clean_album(album):
    dash_search = ' - .+'
    feat_search = '\(?feat\.? .+'
    with_search = '\(?with .+'

    dash_stop = re.search(dash_search, album)
    if dash_stop:
        d = dash_stop[0]
        album = album[:dash_stop.span()[0]]
    feat_stop = re.search(feat_search, album)
    if feat_stop:
        album = album[:feat_stop.span()[0]]
    with_stop = re.search(with_search, album)
    if with_stop:
        album = album[:with_stop.span()[0]]

    return album.rstrip()