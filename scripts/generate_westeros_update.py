import os
import sys
import unicodedata
import pyTagger
        

class GenerateWesterosUpdate():
    def __init__(self, imagesFileName=r'..\data\extract_images.txt'):
        self.imagesFileName = imagesFileName

    def __str__(self):
        return "Generating Updates for Jeff's iTunes"

    def run(self, tracks):
        with open(self.imagesFileName, 'w', encoding='utf-8', newline='') as fImages:
            for k,v in sorted(tracks.items()):
                if self.predicate(v):
                    fImages.writelines(k+'\n')

    def predicate(self, x):
        a0 = ('root' in x and x['root'] == 'Jeff'
              and 'keep' in x and not x['keep']
              and 'westeros_id' in x and x['westeros_id']
              and 'strategy' in x)
        a1 = a0 and x['strategy'] in ['B','E']
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

    pipeline = [GenerateWesterosUpdate()]

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    for operation in pipeline:
        print(operation)
        operation.run(tracks)
