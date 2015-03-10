from __future__ import print_function
import os
import sys
import csv
import binascii
import hashlib
import generate_normalization_maps as Maps
from generate_normalization_maps import *
import pyTagger

class AddNameHash:
    def __init__(self):
        self.maps = GenerateNormalizationMaps()
        self.segmenter = pyTagger.PathSegmentation('/')
        self.commonAlbumNames = ['greatest hits', 'greatest', 'singles', 'live', 'substance']

    def __str__(self):
        return 'Add Name Hash'

    def run(self, tracks):
        # Load the curated album and artist dictionaries
        self.albums = self.maps.load(Maps.FILENAME_ALBUM)
        self.artists = self.maps.load(Maps.FILENAME_ARTIST)

        # Load the scanned list of tracks & enrich
        for k,v in tracks.items():
            tracks[k] = self.enrich(v, k)

    #--------------------------------------------------------------------------
    # Name hashing
    #--------------------------------------------------------------------------
    def enrich(self, x, fullPath):
        shaAccum = hashlib.sha1()

        parts = [self.getTrack(x), self.getTitle(x), self.getArtist(x), self.getAlbum(x)]
        fields = ['n1', 'n2', 'n3', 'n_album']
        for i, n in enumerate(parts):
            shaAccum.update(n.encode())
            x[fields[i]] = n;

        hash = shaAccum.digest();
        b2a = binascii.b2a_base64(hash).decode('ascii')
        x['nameHash'] = b2a.strip()

        pathInfo = self.segmenter.split(fullPath)
        if 'root' not in pathInfo:
            x['root'] = ''
        elif pathInfo['root'] in ['/Volumes/Music/Jeff Music/Music', r'\Jeff Music\Music']:
            x['root'] = 'Jeff'
        elif pathInfo['root'] in ['/Volumes/Music/Jennifer Music', r'\Jennifer Music']:
            x['root'] = 'Jen'
        else:
            x['root'] = ''

        x['subdir'] = pathInfo['subdir'] if 'subdir' in pathInfo else ''

        lc = 0
        if 'yeimi_id' in x and x['yeimi_id'] > 0:
            lc += 1
        if 'westeros_idh' in x and x['westeros_idh'] != 0:
            lc += 1
        x['lib_count'] = lc

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
        if not a:
            return ''

        na = self.artists[a] if a in self.artists else a
        if a not in self.artists:
            print('getArtist', a.encode(), 'Not Found', file=sys.stderr)
        return na

    def getAlbum(self, x):
        a = x['album'] if 'album' in x else ''
        if not a:
            return ''

        na = self.albums[a] if a in self.albums else a

        # a pretty common name, append the artist
        if na in self.commonAlbumNames:
            na = na + '-' + self.getArtist(x)

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