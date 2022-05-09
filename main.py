import argparse
from statistics import mean
from time import sleep
import requests
import json
from typing import Tuple

"""
Small script used to find the average number of words in lyrics of songs by a given artist
"""

BASE_MUSICBRAINZ_URL = 'https://musicbrainz.org/ws/2'
MUSICBRAINZ_HEADERS = {'Accept': 'application/json'}
MUSICBRAINZ_LIMIT = 100
BASE_LYRICS_URL = 'https://api.lyrics.ovh/v1'


def find_mbid(artist: str) -> Tuple[str, int, str]:
    """
    Function which looks up the musicbrainzid (mb_id) for the given artist.
    It only returns the first value found for multiple matches,
    but it includes the score indicating how good a match it is

    Args:
        artist: The name of the artist to search for

    Returns:
        str: The musicbrainzid found
        int: The score returned for this artist
        str: The name of the artist found
    """
    target_url = f'{BASE_MUSICBRAINZ_URL}/artist/'
    query = {'query': artist}
    response = requests.get(target_url, params=query, headers=MUSICBRAINZ_HEADERS)
    if response.status_code != 200:
        return '', 0, ''
    json_response = json.loads(response.text)
    if json_response.get('count', 0) == 0:
        return '', 0, ''
    mb_id = json_response['artists'][0]['id']
    score = json_response['artists'][0]['score']
    found_artist_name = json_response['artists'][0]['name']
    return mb_id, score, found_artist_name


def get_recordings(mb_id: str, offset: int, recordings: list) -> list:
    """
    Function which gets the recordings based on a musicbrainzid.
    It uses recursion to get all recordings as only 100 records are returned from the api

    Args:
        mb_id: The musicbrainzid to search for
        offset: The offset to return values from
        recordings: A list of recordings to append to. Used by recursion - an empty list should be passed in initially

    Returns:
        list: A list of recordings found
    """
    target_url = f'{BASE_MUSICBRAINZ_URL}/recording/'
    query = {'artist': mb_id, 'offset': offset, 'limit': MUSICBRAINZ_LIMIT}
    response = requests.get(target_url, params=query, headers=MUSICBRAINZ_HEADERS)
    if response.status_code != 200:
        return recordings
    json_response = json.loads(response.text)
    recording_count = json_response['recording-count']
    response_recordings = json_response['recordings']
    recordings.extend(response_recordings)
    if offset + MUSICBRAINZ_LIMIT < recording_count:
        # put a sleep in here to avoid hitting rate limits on musicbrainz api
        sleep(2)
        recordings = get_recordings(mb_id, offset+MUSICBRAINZ_LIMIT, recordings)
    return recordings


def get_lyrics(artist: str, title: str) -> Tuple[str, bool]:
    """
    Function which gets the lyrics for a song

    Args:
        artist: The artist to search for
        title: The title to search fo

    Returns:
        str: lyrics found
        bool: flag indicating if lyrics were found
    """
    target_url = f'{BASE_LYRICS_URL}/{artist}/{title}'
    response = requests.get(target_url)
    if response.status_code != 200:
        return '', False
    json_response = json.loads(response.text)
    lyrics = json_response.get('lyrics', '')
    return lyrics, True


def get_all_lyrics(artist: str, titles: list) -> Tuple[list, list, list]:
    """
    Function which gets the lyrics for a list of songs

    Args:
        artist: The artist to search for
        titles: A list of titles to search fo

    Returns:
        list: list of details of songs found - title, number of words, if lyrics were found
        list: list of just numbers showing the number of words in every song
        list: list of just numbers showing the number of words where lyrics were found
    """
    all_details = []
    all_song_lengths = []
    found_song_lengths = []
    for title in titles:
        lyrics, found_lyrics = get_lyrics(artist, title)
        if lyrics != '':
            number_of_words = len(lyrics.replace('\n', ' ').split())
        else:
            number_of_words = 0
        all_details.append({'title': title, 'number_of_words': number_of_words, 'found_lyrics': found_lyrics})
        all_song_lengths.append(number_of_words)
        if found_lyrics:
            found_song_lengths.append(number_of_words)
        sleep(1)
    return all_details, all_song_lengths, found_song_lengths


def main():
    parser = argparse.ArgumentParser(description='Find average number of words in songs by an artist')
    parser.add_argument('-a', '--artist', dest='artist', type=str, help='the artist to search for', required=True)
    args = parser.parse_args()
    artist = args.artist
    print(f'artist searching for is {artist}')

    mb_id, score, found_artist_name = find_mbid(artist)
    if score == 0:
        print('could not find a good match. Exiting')
        return
    print(f'found artist {found_artist_name} with a score of {score}')

    recordings = []
    recordings = get_recordings(mb_id, 0, recordings)
    print(f'found {len(recordings)} total recordings')

    # there may be the same title returned multiple times, so de-dupe the list
    just_titles = []
    for x in recordings: just_titles.append(x['title'])
    just_titles = list(dict.fromkeys(just_titles))
    print(f'found {len(just_titles)} distinct titles')
    if len(just_titles) == 0:
        print('Could not find any titles. Exiting')
        return

    print('retrieving lyrics. This may take some time...')
    all_details, all_song_lengths, found_song_lengths = get_all_lyrics(artist, just_titles)
    mean_of_all_songs = mean(all_song_lengths)
    if len(found_song_lengths) == 0:
        print('Could not find any lyrics for artist')
        mean_of_found_songs = 0
    else:
        mean_of_found_songs = mean(found_song_lengths)

    print()
    print(f'found lyrics for {len(found_song_lengths)} songs')
    print(f'mean number of words of all songs: {mean_of_all_songs}')
    print(f'mean number of words of found songs: {mean_of_found_songs}')


if __name__ == '__main__':
    main()


