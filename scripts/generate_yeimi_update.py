import os
import sys
import unicodedata
import pyTagger
        

class GenerateYeimiUpdate():
    def __init__(self, fileName=r'..\data\yeimi_library_updates.txt'):
        self.fileName = fileName

    def __str__(self):
        return "Generating Updates for Jen's Mac"

    def run(self, tracks):
        with open(self.fileName, 'w', encoding='macintosh', newline='') as fout:
            for k,v in sorted(tracks.items()):
                if self.predicate(v):
                    title = v['title'] if 'title' in v else ''
                    oldPath = unicodedata.normalize('NFKC', k)
                    if v['strategy'] == 'A':
                        newPath = unicodedata.normalize('NFKC', v['winner'])
                        action = 'update'
                    else:
                        newPath = ''
                        action = 'delete'
                    row = '\t'.join([title, oldPath, newPath, action, str(v['yeimi_id'])])
                    fout.writelines(row+'\n')

    def predicate(self, x):
        return ('root' in x and x['root'] == 'Jen'
                and 'keep' in x and not x['keep']
                and 'yeimi_id' in x and x['yeimi_id']
                and 'strategy' in x and x['strategy'] in ['A','D'])

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s_enh.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]

    pipeline = GenerateYeimiUpdate()

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    pipeline.run(tracks)
