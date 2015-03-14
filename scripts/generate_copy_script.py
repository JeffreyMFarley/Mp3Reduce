import os
import sys
import unicodedata
import pyTagger

PATH = r'..\data\copy.sh'

class GenerateCopyScript():
    def __init__(self, fileName=PATH):
        self.fileName = fileName

    def __str__(self):
        return "Generating Copy Script"

    def run(self, tracks):
        with open(self.fileName, 'w', encoding='utf-8', newline='') as fout:
            fout.writelines('#!/bin/bash\n\n')
            for k,v in sorted(tracks.items()):
                if self.predicate(v):
                    oldPath = unicodedata.normalize('NFKC', k)
                    newPath = unicodedata.normalize('NFKC', v['winner'])
                    if '"' in oldPath:
                        oldPath = oldPath.replace('"', '""')
                    if '"' in newPath:
                        newPath = newPath.replace('"', '""')
                    fout.writelines('cp -f "'+oldPath+'" "'+newPath+'"\n')

    def predicate(self, x):
        a0 = ('keep' in x and not x['keep']
              and 'strategy' in x)
        a1 = a0 and x['strategy'] in ['G']
        return a1


#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s_enh.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]

    pipeline = GenerateCopyScript()

    # Generate the delete list
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    pipeline.run(tracks)
