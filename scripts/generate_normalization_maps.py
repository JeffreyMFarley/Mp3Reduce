from __future__ import print_function
import os
import sys
import csv
import list_mp3s as Upstream
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

FILENAME_ARTIST = r'..\data\artist_map.txt'
FILENAME_ALBUM = r'..\data\album_map.txt'
COLUMNS = ['key', 'value']
KEY = 'key'

class GenerateNormalizationMaps:
    def __init__(self):
        self.artists = set()
        self.albums = set()

    def generate(self, fileName):
        tracks = Upstream.load(fileName)

        # Initialize the two sets with the directory names
        for track in filter(self.hasRightRoot, tracks):
            artist, album = track['Subdir'].split('/')
            self.artists.add(self.normalize(artist))
            self.albums.add(self.normalize(album))

        #self.dump(self.artists, r'..\data\artist_set.txt')
        #self.dump(self.albums, r'..\data\album_set.txt') 

        artistSet = {x['Artist'] for x in filter(self.hasArtist, tracks) }
        artistMap = self.enrichAndMap(artistSet, self.artists)
        self.save(FILENAME_ARTIST, artistMap)

        albumSet = {x['Album'] for x in filter(self.hasAlbum, tracks) }
        albumMap = self.enrichAndMap(albumSet, self.albums)
        self.save(FILENAME_ALBUM, albumMap)

    #------------------------------------------------- ------------------------------
    # Relational Algebra
    #-------------------------------------------------------------------------------
    def hasArtist(self, x):
        return 'Artist' in x and x['Artist'] != '' and x['Artist'] != None

    def hasAlbum(self, x):
        return 'Album' in x and x['Album'] != '' and x['Album'] != None

    def hasRightRoot(self, x):
        return 'Root' in x and x['Root'] in ['/Volumes/Music/Jeff Music/Music', '/Volumes/Music/Jennifer Music']

    def outputSort(self, x):
        return x['key'].lower(), x['value'] if 'value' in x else ''

    #-------------------------------------------------------------------------------
    # Functional
    #-------------------------------------------------------------------------------
    def enrichAndMap(self, a, b):
        result = []

        j = 0
        update = len(a) / 20
        sys.stderr.write(' 1  2    5    7  9 |\n')
        sys.stderr.write('-0--5----0----5--0-|\n')

        for x in sorted(a):
            j += 1
            if j > update:
                sys.stderr.write('#')
                sys.stderr.flush()
                j = 0

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

        return result

    #-------------------------------------------------------------------------------
    # Name hashing
    #-------------------------------------------------------------------------------
    def normalize(self, s):
        s0 = s.lower()
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
        return list(self.iter_load(fileName))

    def iter_load(self, fileName):
         with open(fileName, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, dialect=csv.excel_tab)
            for row in reader:
                yield row

    def dump(self, theSet, fileName):
        theList = list(theSet)
        theList.sort()
        with open(fileName, 'w', encoding='utf-8') as f:
            for l in theList:
                f.writelines([l, os.linesep])

    def save(self, fileName, theList):
        with open(fileName, 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, COLUMNS, dialect=csv.excel_tab, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(sorted(theList, key=self.outputSort))

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    fileName = r'..\data\kira_mp3s.txt'
    argc = len(sys.argv)
    if argc > 1:
        fileName = sys.argv[1]

    pipeline = GenerateNormalizationMaps()
    pipeline.generate(fileName)
