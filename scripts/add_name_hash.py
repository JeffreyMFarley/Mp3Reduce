from __future__ import print_function
import os
import sys
import csv
import binascii
import hashlib
import generate_normalization_maps as Maps
from generate_normalization_maps import *
import list_mp3s as Source

COLUMNS = Source.COLUMNS + ['NameHash']

class AddNameHash:
    def __init__(self):
        pass

    def run(self, inFile, outFile):
        # Load the curated album and artist dictionaries
        maps = GenerateNormalizationMaps()
        self.albums = maps.load(Maps.FILENAME_ALBUM)
        self.artists = maps.load(Maps.FILENAME_ARTIST)

        # Load the scanned list of tracks & enrich
        self.tracks = map(self.enrich, Source.load(inFile))

        # Save
        self.save(outFile, self.tracks)


    #------------------------------------------------- ------------------------------
    # Relational Algebra
    #-------------------------------------------------------------------------------
    def outputSort(self, x):
        track = 0
        try: 
            track = int(x['Track'])
        except ValueError:
            pass
        
        return (x['Artist'], x['Album'], track, x['Title'])

    #-------------------------------------------------------------------------------
    # Functional
    #-------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------
    # Name hashing
    #-------------------------------------------------------------------------------
    def enrich(self, x):
        shaAccum = hashlib.sha1()

        shaAccum.update(self.getTrack(x).encode())
        shaAccum.update(x['Title'].encode())
        shaAccum.update(self.getArtist(x).encode())
        shaAccum.update(self.getAlbum(x).encode())

        hash = shaAccum.digest();
        b2a = binascii.b2a_base64(hash).decode('ascii')
        x['NameHash'] = b2a.strip()

        return x

    def getTrack(self, x):
        track = 0
        try: 
            track = int(x['Track'])
        except ValueError:
            pass

        a = "%02d" % track
        return a

    def getArtist(self, x):
        a = x['Artist'] if 'Artist' in x else ''
        if not a: return ''

        na = self.artists[a] if a in self.artists else a
        if a not in self.artists:
            print(a.encode(), 'Not Found', file=sys.stderr)
        return na

    def getAlbum(self, x):
        a = x['Album'] if 'Album' in x else ''
        if not a: return ''

        na = self.albums[a] if a in self.albums else a
        if a not in self.albums:
            print(a.encode(), 'Not Found', file=sys.stderr)
        return na

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

    #def dump(self, theSet, fileName):
    #    theList = list(theSet)
    #    theList.sort()
    #    with open(fileName, 'w', encoding='utf-8') as f:
    #        for l in theList:
    #            f.writelines([l, os.linesep])

    def save(self, fileName, theList):
        with open(fileName, 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, COLUMNS, dialect=csv.excel_tab, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(sorted(theList, key=self.outputSort))
    
#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\kira_mp3s.txt'
    outFile = r'..\data\kira_mp3s_enh.txt'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]
    if argc > 2:
        outFile = sys.argv[2]

    pipeline = AddNameHash()
    pipeline.run(inFile, outFile)
