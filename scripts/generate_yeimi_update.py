import os
import sys
import unicodedata
import pyTagger
from add_library_ids import *
from add_name_hash import *
        

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


class MeantToInclude():
    def __init__(self, fileName=r'..\data\yeimi_library_adds.txt'):
        self.fileName = fileName

    def __str__(self):
        return "Generating List of Missing Albums"

    def run(self, tracks):
        missing = set()
        for k,v in sorted(tracks.items()):
            if self.predicate(v):
                combined = v['n3'] + ' - ' + v['n_album']
                missing.add(combined)
        with open(self.fileName, 'w', encoding='macintosh', newline='') as fout:
            for row in sorted(missing):
                fout.write(row)
                fout.write('\n')

    def predicate(self, x):
        return ('root' in x and x['root'] == 'Jen'
                 and 'yeimi_id' not in x
                )

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
#    inFile = r'..\data\mp3s.json'
    inFile = r'..\data\mp3s_enh.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]

#    pipeline = [AddYeimiLibraryIds(), AddNameHash(), MeantToInclude()]
    pipeline = [MeantToInclude()]

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    for operation in pipeline:
        print(operation)
        operation.run(tracks)
