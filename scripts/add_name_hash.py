from __future__ import print_function
import os
import sys
import csv
import binascii
import hashlib
import generate_normalization_maps as Maps
from generate_normalization_maps import *

class AddNameHash:
    def __init__(self):
        self.maps = GenerateNormalizationMaps()

    def run(self, tracks):
        # Load the curated album and artist dictionaries
        self.albums = self.maps.load(Maps.FILENAME_ALBUM)
        self.artists = self.maps.load(Maps.FILENAME_ARTIST)

        # Load the scanned list of tracks & enrich
        for k,v in tracks.items():
            tracks[k] = self.enrich(v)

    #--------------------------------------------------------------------------
    # Name hashing
    #--------------------------------------------------------------------------
    def enrich(self, x):
        shaAccum = hashlib.sha1()

        #shaAccum.update(self.getTrack(x).encode())  # not everyone uses track#
        shaAccum.update(self.getTitle(x).encode())
        shaAccum.update(self.getArtist(x).encode())
        shaAccum.update(self.getAlbum(x).encode())

        hash = shaAccum.digest();
        b2a = binascii.b2a_base64(hash).decode('ascii')
        x['nameHash'] = b2a.strip()

        return x

    def getTrack(self, x):
        track = 0
        try: 
            track = int(x['track'])
        except (ValueError, TypeError, KeyError):
            pass

        a = "%02d" % track
        return a

    def getTitle(self, x):
        a = x['title'] if 'title' in x else ''
        na = self.maps.normalize(a) if a else ''
        return na

    def getArtist(self, x):
        a = x['artist'] if 'artist' in x else ''
        if not a: return ''

        na = self.artists[a] if a in self.artists else a
        if a not in self.artists:
            print('getArtist', a.encode(), 'Not Found', file=sys.stderr)
        return na

    def getAlbum(self, x):
        a = x['album'] if 'album' in x else ''
        if not a: return ''

        na = self.albums[a] if a in self.albums else a
        if a not in self.albums:
            print('getAlbum', a.encode(), 'Not Found', file=sys.stderr)
        return na
    
#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s.json'
    outFile = r'..\data\mp3s_enh.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]
    if argc > 2:
        outFile = sys.argv[2]

    pipeline = AddNameHash()

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    pipeline.run(tracks)
    snapshot.save(outFile, tracks)