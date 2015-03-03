import os
import sys
import unicodedata
import pyTagger

RECYCLE_PATH = r'/Volumes/Music/recycle/'

class GenerateYeimiDeleteScript():
    def __init__(self, fileName=r'..\data\delete.sh'):
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
                    fout.writelines('del -f "'+path+'"\n')

    def predicate(self, x):
        return ('root' in x and x['root'] == 'Jen'
                and 'keep' in x and not x['keep']
                and 'strategy' in x and x['strategy'] in ['A','D'])


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
