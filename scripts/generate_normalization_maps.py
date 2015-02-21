from __future__ import print_function
import os
import sys
import csv
import pyTagger
import unicodedata
try:
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
except ImportError:
    print('Only loading of normalized files will be supported', file=sys.stderr)

FILENAME_ARTIST = r'..\data\artist_map.txt'
FILENAME_ALBUM = r'..\data\album_map.txt'
COLUMNS = ['key', 'value']
KEY = 'key'

class GenerateNormalizationMaps:
    def __init__(self):
        self.artists = set()
        self.albums = set()
        self.snapshot = pyTagger.Mp3Snapshot()
        self.translateTable = self.buildTranslateTable()

    @classmethod
    def buildTranslateTable(cls):
        if sys.version >= '3':
            return dict.fromkeys(c for c in range(sys.maxunicode)
                                 if unicodedata.combining(chr(c)))
        else:
            return dict.fromkeys(c for c in range(sys.maxunicode)
                                 if unicodedata.combining(unichr(c)))

    def generate(self, fileName, pathSep):
        tracks = self.snapshot.load(fileName)
        segmenter = pyTagger.PathSegmentation(pathSep)

        # Initialize the two sets with the directory names
        for fullPath, track in tracks.items():
            pathInfo = segmenter.split(fullPath)
            if self.hasRightRoot(pathInfo):
                artist, album = pathInfo['subdir'].split(pathSep)
                self.artists.add(self.normalize(artist))
                self.albums.add(self.normalize(album))

        albumSet = {x['album'] for x in filter(self.hasAlbum, tracks.values()) }
        albumMap = self.enrichAndMap(albumSet, self.albums, 'Albums')
        self.save(FILENAME_ALBUM, albumMap)

        artistSet = {x['artist'] for x in filter(self.hasArtist, tracks.values()) }
        artistMap = self.enrichAndMap(artistSet, self.artists, 'Artists')
        self.save(FILENAME_ARTIST, artistMap)


    #------------------------------------------------- ------------------------------
    # Relational Algebra
    #-------------------------------------------------------------------------------
    def hasArtist(self, x):
        return 'artist' in x and x['artist'] != '' and x['artist'] != None

    def hasAlbum(self, x):
        return 'album' in x and x['album'] != '' and x['album'] != None

    def hasRightRoot(self, x):
        return 'root' in x and x['root'] in ['/Volumes/Music/Jeff Music/Music', '/Volumes/Music/Jennifer Music', r'\Jeff Music\Music', r'\Jennifer Music']

    def outputSort(self, x):
        return x['key'].lower(), x['value'] if 'value' in x else ''

    #-------------------------------------------------------------------------------
    # Functional
    #-------------------------------------------------------------------------------
    def enrichAndMap(self, a, b, operation):
        result = []
        progressBar = pyTagger.ProgressBar(a, operation)

        for x in sorted(a):
            progressBar.increment()

            nx = self.normalize(x)
            d = {KEY: x}

            if nx in b:
                d['value'] = nx
            else:
                match, score = process.extractOne(nx, b)
                if 0 < score < 90:
                    b.add(nx)
                    d['value'] = nx
                elif 90 <= score < 100 and len(match) > 3 and len(nx) > 3:
                    d['value'] = match
                elif 90 <= score < 100:
                    b.add(nx)
                    d['value'] = nx

            result.append(d)

        progressBar.finish()
        return result

    #-------------------------------------------------------------------------------
    # Name hashing
    #-------------------------------------------------------------------------------
    def normalize(self, s):
        b = unicodedata.normalize('NFKD', s.lower())
        s0 = b.translate(self.translateTable)
        s1 = self.filterArticles(s0)
        s2 = self.filterCharacters(s1)
        return s2

    def filterCharacters(self, s):
        s0 = ''.join( c for c in s if c not in '.<>?\':"[]{}|`~!@#$%^&*()-_=+' )  # Remove punctuation
        s1 = ''.join( c if c not in ',/\\;' else ' ' for c in s0 ) # replace these with spaces
        s2 = ' '.join(s1.split()) # remove multiple spaces
        return s2

    def filterArticles(self, s):
        if s.startswith('the '):
            return s[4:]
        elif s.startswith('a '):
            return s[2:]
        elif s.startswith('an '):
            return s[3:]
        return s

    #-------------------------------------------------------------------------------
    # I/O
    #-------------------------------------------------------------------------------
    
    def load(self, fileName):
        return {x[KEY]:x['value'] for x in self.iter_load(fileName)}

    def iter_load(self, fileName):
         with open(fileName, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, dialect=csv.excel_tab)
            for row in reader:
                yield row

    def save(self, fileName, theList):
        with open(fileName, 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, COLUMNS, dialect=csv.excel_tab, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(sorted(theList, key=self.outputSort))

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    fileName = r'..\data\mp3s.json'
    argc = len(sys.argv)
    if argc > 1:
        fileName = sys.argv[1]

    pipeline = GenerateNormalizationMaps()
    pipeline.generate(fileName, '/')
