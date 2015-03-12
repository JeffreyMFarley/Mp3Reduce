import os
import sys
import unicodedata
import pyTagger

RECYCLE_PATH = r'/Volumes/Music/recycle/'
PATH_YEIMI = r'..\data\delete_jen.sh'
PATH_WESTEROS = r'..\data\delete_jeff.sh'

class GenerateYeimiDeleteScript():
    def __init__(self, fileName=PATH_YEIMI):
        self.fileName = fileName

    def __str__(self):
        return "Generating Jen's Mac Delete Script"

    def run(self, tracks):
        with open(self.fileName, 'w', encoding='utf-8', newline='') as fout:
            fout.writelines('#!/bin/bash\n\n')
            for k,v in sorted(tracks.items()):
                if self.predicate(v):
                    path = unicodedata.normalize('NFKC', k)
                    if '"' in path:
                        path = path.replace('"', '""')
                    fout.writelines('rm -f "'+path+'"\n')

            # manual deletes
            for k in ['/Volumes/Music/Jennifer Music/Portishead/Portishead Assorted/Portishead - Sheared Times (Rare).mp3',
                      '/Volumes/Music/Jeff Music/Music/Compilations/Becoming RemiXed/06 6 Underground (Perfecto Mix).mp3',
                      '/Volumes/Music/Jennifer Music/Talking Heads/Talking Heads Assorted/Talking Heads - Psycho Killer.mp3',
                      '/Volumes/Music/Jennifer Music/Talking Heads/Talking Heads Assorted/Talking Heads - Cities.mp3',
                      '/Volumes/Music/Jennifer Music/Paul Oakenfold/Bunkka/01 Ready Steady go.mp3',
                      '/Volumes/Music/Jennifer Music/Paul Oakenfold/Bunkka/03 Time of Your Life.mp3',
                      '/Volumes/Music/Jennifer Music/Paul Oakenfold/Bunkka/04 Hypnotised.mp3',
                      '/Volumes/Music/Jennifer Music/Paul Oakenfold/Bunkka/10 Motion.mp3',
                      '/Volumes/Music/Jennifer Music/Paul Oakenfold/Bunkka/11 The Harder They Come.mp3',
                      '/Volumes/Music/Jennifer Music/Nine Inch Nails/The Downward Spiral/04 March of the Pigs.mp3',
                      '/Volumes/Music/Jennifer Music/Nine Inch Nails/The Downward Spiral [Explicit]/05 Closer [Explicit].mp3',
                      '/Volumes/Music/Jennifer Music/Nine Inch Nails/The Downward Spiral/09 Big Man With a Gun.mp3'
                      ]:
                path = unicodedata.normalize('NFKC', k)
                if '"' in path:
                    path = path.replace('"', '""')
                fout.writelines('rm -f "'+path+'"\n')


    def predicate(self, x):
        a0 = ('root' in x and x['root'] == 'Jen'
              and 'keep' in x and not x['keep']
              and 'strategy' in x)
        a1 = a0 and x['strategy'] in ['A','D']
        a2 = a0 and (x['strategy'] == 'C'
                     and 'keepJeff' in x and x['keepJeff'] > 0
                     and 'keepJen' in x and x['keepJen'] == 0)
        return a1 or a2

class GenerateWesterosDeleteScript():
    def __init__(self, fileName=PATH_WESTEROS):
        self.fileName = fileName

    def __str__(self):
        return "Generating Jeff's Delete Script"

    def run(self, tracks):
        with open(self.fileName, 'w+', encoding='utf-8', newline='') as fout:
            fout.writelines('#!/bin/bash\n\n')
            for k,v in sorted(tracks.items()):
                if self.predicate(v):
                    path = unicodedata.normalize('NFKC', k)
                    if '"' in path:
                        path = path.replace('"', '""')
                    fout.writelines('rm -f "'+path+'"\n')

    def predicate(self, x):
        a0 = ('root' in x and x['root'] == 'Jeff'
              and 'keep' in x and not x['keep']
              and 'strategy' in x)
        a1 = a0 and x['strategy'] in ['B']
        a2 = a0 and (x['strategy'] == 'C'
                     and 'keepJeff' in x and x['keepJeff'] == 0
                     and 'keepJen' in x and x['keepJen'] > 0)
        return a1 or a2

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s_enh.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]

    pipeline = GenerateYeimiDeleteScript()

    # Generate the delete list
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    pipeline.run(tracks)
