# Average lyric search

Small script that finds the average number of words in lyrics for a given artist.   
It uses the musicbrainz api (https://musicbrainz.org/doc/Development/XML_Web_Service/Version_2) 
to retrieve recordings by an artist and a lyrics api (https://lyricsovh.docs.apiary.io/#reference) to retrieve lyrics.   
Not all songs have lyrics in the lyrics api so an average is returned for all songs, and for songs where lyrics are found.   

The lyrics api can be slow so searching for an artist with many tracks can take a long time.   

## Setup
To setup run the following
```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```
It has been developed using python 3.8 but should work on any python3 version > 3.4

## Usage
The script has one paramater -a/--artist that is the artist to search for
```
python3 main.py -a 'nova twins'
python3 main.py --artist 'nova twins'
```

## Tests
To run unit tests use the following after running the setup steps above
```
pytest
```

