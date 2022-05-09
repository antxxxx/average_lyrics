import json

import pytest
from requests_mock.mocker import Mocker

import main
from main import find_mbid, get_recordings

good_artist_musicbrainz_response = """
{
    "created": "2022-05-08T09:09:58.496Z",
    "count": 2772,
    "offset": 0,
    "artists": [
        {
            "id": "6a81fbbc-acea-4221-9199-957842125078",
            "type": "Group",
            "type-id": "e431f5f6-b5d2-343d-8b36-72607fffb74b",
            "score": 100,
            "name": "Nova Twins",
            "sort-name": "Nova Twins",
            "country": "GB",
            "area": {
                "id": "8a754a16-0027-3a29-b6d7-2b40ea0481ed",
                "type": "Country",
                "type-id": "06dd0ae4-8c74-30bb-b43d-95dcedf961de",
                "name": "United Kingdom",
                "sort-name": "United Kingdom",
                "life-span": {
                    "ended": null
                }
            },
            "begin-area": {
                "id": "f03d09b3-39dc-4083-afd6-159e3f0d462f",
                "type": "City",
                "type-id": "6fd8f29a-3d0a-32fc-980d-ea697b69da78",
                "name": "London",
                "sort-name": "London",
                "life-span": {
                    "ended": null
                }
            },
            "life-span": {
                "begin": "2014",
                "ended": null
            },
            "tags": [
                {
                    "count": 1,
                    "name": "rock"
                },
                {
                    "count": 1,
                    "name": "alternative rock"
                },
                {
                    "count": 1,
                    "name": "punk"
                },
                {
                    "count": 1,
                    "name": "punk rock"
                },
                {
                    "count": 1,
                    "name": "hip hop"
                },
                {
                    "count": 1,
                    "name": "nu metal"
                },
                {
                    "count": 1,
                    "name": "pop rock"
                },
                {
                    "count": 1,
                    "name": "rapcore"
                }
            ]
        },
        {
            "id": "26fbfbc3-64ec-4641-a92a-92ef73f220e5",
            "type": "Person",
            "type-id": "b6e035f4-3ce9-331c-97df-83397230b0df",
            "score": 53,
            "gender-id": "93452b5a-a947-30c8-934f-6a4056b151c2",
            "name": "Georgia South",
            "sort-name": "South, Georgia",
            "gender": "female",
            "country": "GB",
            "area": {
                "id": "8a754a16-0027-3a29-b6d7-2b40ea0481ed",
                "type": "Country",
                "type-id": "06dd0ae4-8c74-30bb-b43d-95dcedf961de",
                "name": "United Kingdom",
                "sort-name": "United Kingdom",
                "life-span": {
                    "ended": null
                }
            },
            "disambiguation": "Nova Twins member",
            "ipis": [
                "00650316670"
            ],
            "life-span": {
                "ended": null
            }
        }
    ]
}"""

empty_artist_musicbrainz_response = """
{
    "created": "2022-05-08T09:12:16.770Z",
    "count": 0,
    "offset": 0,
    "artists": []
}
"""

good_recordings_musicbrainz_response_1 = """
{
    "recordings": [
        {
            "length": 138000,
            "title": "Ivory Tower",
            "id": "052e1145-af9d-4bca-a35d-3be126230c0f",
            "video": false,
            "first-release-date": "2020-02-28",
            "disambiguation": ""
        },
        {
            "title": "Vortex",
            "length": 189000,
            "disambiguation": "",
            "first-release-date": "2020-02-28",
            "video": false,
            "id": "06bf478d-7234-48ca-8499-21f35150723c"
        }
    ],
    "recording-count": 4,
    "recording-offset": 0
}"""

good_recordings_musicbrainz_response_2 = """
{
    "recordings": [
        {
            "title": "Enemy",
            "length": 171000,
            "first-release-date": "2022-06-17",
            "disambiguation": "",
            "video": false,
            "id": "15319304-b815-4e87-a316-1030b1a8ed4e"
        },
        {
            "id": "15954c3b-7d68-4ab9-8233-e433fcb54e66",
            "disambiguation": "",
            "first-release-date": "2022-03-15",
            "video": false,
            "length": 210000,
            "title": "Cleopatra"
        }
    ],
    "recording-count": 4,
    "recording-offset": 2
}"""

good_lyric_response_1 = """
{
    "lyrics": "The type of girl\\n\\nAh, Cleopatra\\n\\n\\n\\nAh\\n\\nAh"
}
"""

good_lyric_response_2 = """
{
    "lyrics": "Ah, Cleopatra\\n\\n\\n\\nAh\\n\\nAh"
}
"""


def test_find_mbid_success(requests_mock: Mocker):
    requests_mock.get(f'https://musicbrainz.org/ws/2/artist/?query=nova+twins',
                      json=json.loads(good_artist_musicbrainz_response))
    mb_id, score, found_artist_name = find_mbid('nova twins')
    assert mb_id == '6a81fbbc-acea-4221-9199-957842125078'
    assert score == 100
    assert found_artist_name == 'Nova Twins'


def test_find_mbid_no_results(requests_mock: Mocker):
    requests_mock.get(f'https://musicbrainz.org/ws/2/artist/?query=nothing',
                      json=json.loads(empty_artist_musicbrainz_response))
    mb_id, score, found_artist_name = find_mbid('nothing')
    assert mb_id == ''
    assert score == 0
    assert found_artist_name == ''


def test_find_mbid_bad_response(requests_mock: Mocker):
    requests_mock.get(f'https://musicbrainz.org/ws/2/artist/?query=bad_response',
                      status_code=500)
    mb_id, score, found_artist_name = find_mbid('bad_response')
    assert mb_id == ''
    assert score == 0
    assert found_artist_name == ''


def test_get_recordings_single_response(requests_mock: Mocker):
    requests_mock.get(f'https://musicbrainz.org/ws/2/recording/?artist=6a81fbbc-acea-4221-9199-957842125078&offset=0'
                      f'&limit=100',
                      json=json.loads(good_recordings_musicbrainz_response_1))
    recordings = []
    recordings = get_recordings('6a81fbbc-acea-4221-9199-957842125078', 0, recordings)
    assert len(recordings) == 2
    assert recordings[0]['title'] == 'Ivory Tower'
    assert recordings[1]['title'] == 'Vortex'


def test_get_recordings_multiple_response(requests_mock: Mocker, monkeypatch):
    monkeypatch.setattr(main, "MUSICBRAINZ_LIMIT", 2)
    requests_mock.get(f'https://musicbrainz.org/ws/2/recording/?artist=6a81fbbc-acea-4221-9199-957842125078&offset=0'
                      f'&limit=2',
                      json=json.loads(good_recordings_musicbrainz_response_1))
    requests_mock.get(f'https://musicbrainz.org/ws/2/recording/?artist=6a81fbbc-acea-4221-9199-957842125078&offset=2'
                      f'&limit=2',
                      json=json.loads(good_recordings_musicbrainz_response_2))
    recordings = []
    recordings = get_recordings('6a81fbbc-acea-4221-9199-957842125078', 0, recordings)
    assert len(recordings) == 4
    assert recordings[0]['title'] == 'Ivory Tower'
    assert recordings[1]['title'] == 'Vortex'
    assert recordings[2]['title'] == 'Enemy'
    assert recordings[3]['title'] == 'Cleopatra'


def test_get_recordings_bad_response(requests_mock: Mocker):
    requests_mock.get(
        f'https://musicbrainz.org/ws/2/recording/?artist=6a81fbbc-acea-4221-9199-957842125078&offset=0&limit=100',
        status_code=500)
    recordings = []
    recordings = get_recordings('6a81fbbc-acea-4221-9199-957842125078', 0, recordings)
    assert len(recordings) == 0


def test_get_lyrics_good(requests_mock: Mocker):
    requests_mock.get(f'https://api.lyrics.ovh/v1/Nova Twins/Cleopatra',
                      json=json.loads(good_lyric_response_1))
    lyrics, found_lyrics = main.get_lyrics('Nova Twins', 'Cleopatra')
    assert lyrics == "The type of girl\n\nAh, Cleopatra\n\n\n\nAh\n\nAh"


def test_get_lyrics_no_response(requests_mock: Mocker):
    requests_mock.get(f'https://api.lyrics.ovh/v1/Nova Twins/Cleopatra',
                      status_code=404)
    lyrics, found_lyrics = main.get_lyrics('Nova Twins', 'Cleopatra')
    assert lyrics == ""


def test_get_all_lyrics_one_song(requests_mock: Mocker):
    requests_mock.get(f'https://api.lyrics.ovh/v1/Nova Twins/Cleopatra',
                      json=json.loads(good_lyric_response_1))
    all_details, all_song_lengths, found_song_lengths = main.get_all_lyrics('Nova Twins', ['Cleopatra'])
    assert len(all_details) == 1
    assert all_details[0] == {'found_lyrics': True, 'number_of_words': 8, 'title': 'Cleopatra'}
    assert len(all_song_lengths) == 1
    assert all_song_lengths[0] == 8
    assert len(found_song_lengths) == 1
    assert found_song_lengths[0] == 8


def test_get_all_lyrics_two_songs_one_found(requests_mock: Mocker):
    requests_mock.get(f'https://api.lyrics.ovh/v1/Nova Twins/Cleopatra',
                      json=json.loads(good_lyric_response_1))
    requests_mock.get(f'https://api.lyrics.ovh/v1/Nova Twins/Enemy',
                      status_code=404)
    all_details, all_song_lengths, found_song_lengths = main.get_all_lyrics('Nova Twins', ['Cleopatra', 'Enemy'])
    assert len(all_details) == 2
    assert all_details[0] == {'found_lyrics': True, 'number_of_words': 8, 'title': 'Cleopatra'}
    assert all_details[1] == {'found_lyrics': False, 'number_of_words': 0, 'title': 'Enemy'}
    assert len(all_song_lengths) == 2
    assert all_song_lengths[0] == 8
    assert all_song_lengths[1] == 0
    assert len(found_song_lengths) == 1
    assert found_song_lengths[0] == 8


def test_get_all_lyrics_three_songs_two_found(requests_mock: Mocker):
    requests_mock.get(f'https://api.lyrics.ovh/v1/Nova Twins/Cleopatra',
                      json=json.loads(good_lyric_response_1))
    requests_mock.get(f'https://api.lyrics.ovh/v1/Nova Twins/Enemy',
                      status_code=404)
    requests_mock.get(f'https://api.lyrics.ovh/v1/Nova Twins/Say Something',
                      json=json.loads(good_lyric_response_2))
    all_details, all_song_lengths, found_song_lengths = main.get_all_lyrics('Nova Twins', ['Cleopatra',
                                                                                           'Enemy',
                                                                                           'Say Something'])
    assert len(all_details) == 3
    assert all_details[0] == {'found_lyrics': True, 'number_of_words': 8, 'title': 'Cleopatra'}
    assert all_details[1] == {'found_lyrics': False, 'number_of_words': 0, 'title': 'Enemy'}
    assert all_details[2] == {'found_lyrics': True, 'number_of_words': 4, 'title': 'Say Something'}
    assert len(all_song_lengths) == 3
    assert all_song_lengths[0] == 8
    assert all_song_lengths[1] == 0
    assert all_song_lengths[2] == 4
    assert len(found_song_lengths) == 2
    assert found_song_lengths[0] == 8
    assert found_song_lengths[1] == 4
