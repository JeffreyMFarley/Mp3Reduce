import os
import sys
import unicodedata
import pyTagger
from add_library_ids import *
from add_name_hash import *
      
PATH = r'..\data\yeimi_library_updates.txt'  

class GenerateYeimiUpdate():
    def __init__(self, fileName=PATH):
        self.fileName = fileName

    def __str__(self):
        return "Generating Updates for Jen's Mac"

    def run(self, tracks):
        with open(self.fileName, 'w', encoding='macintosh', newline='') as fout:
            for k,v in sorted(tracks.items()):
                if self.predicate(v):
                    title = v['title'] if 'title' in v else ''
                    oldPath = unicodedata.normalize('NFKC', k)
                    if v['strategy'] in ['A', 'C', 'F', 'H']:
                        newPath = unicodedata.normalize('NFKC', v['winner'])
                        action = 'update'
                    else:
                        newPath = ''
                        action = 'delete'
                    row = '\t'.join([title, oldPath, newPath, action, str(v['yeimi_id'])])
                    fout.writelines(row+'\n')

    def predicate(self, x):
        a0 = ('root' in x and x['root'] == 'Jen'
              and 'keep' in x and not x['keep']
              and 'yeimi_id' in x and x['yeimi_id']
              and 'strategy' in x)
        a1 = a0 and x['strategy'] in ['A','D','F','H']
        a2 = a0 and (x['strategy'] == 'C'
                     and 'keepJeff' in x and x['keepJeff'] > 0
                     and 'keepJen' in x and x['keepJen'] == 0)
        return a1 or a2

class MeantToInclude():
    def __init__(self, outFileName=r'..\data\yeimi_library_adds.txt', 
                 absencesFileName=r'..\data\yeimi_library_absences.txt'):
        self.outFileName = outFileName
        with open(absencesFileName, 'r', encoding='macintosh', newline='\n') as f:
            self.origAbsences = {x.strip() for x in f}

    def __str__(self):
        return "Generating List of Missing Albums"

    def run(self, tracks):
        folders = {}
        missing = {}

        for k,v in sorted(tracks.items()):
            combined = v['n3'] + ' - ' + v['n_album']
            if combined not in folders and 'root' in v:
                folders[combined] = v['root']
            if self.predicate(v, combined):
                missing[combined] = v['root']

        with open(self.outFileName, 'w', encoding='macintosh', newline='') as fout:
            for k in sorted(missing):
                fout.write(k)
                fout.write('\t')
                fout.write(missing[k])
                fout.write('\n')

    def predicate(self, x, combined):
        a0 = 'yeimi_id' not in x and 'root' in x
        a1 = a0 and x['root'] == 'Jen'
        a2 = a0 and combined in self.origAbsences and x['root'] == 'Jeff'
        return a1 or a2

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s.json'
#    inFile = r'..\data\mp3s_enh.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]

    pipeline = [AddYeimiLibraryIds(performQA=True), AddNameHash(), MeantToInclude()]
#    pipeline = [MeantToInclude()]

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    for operation in pipeline:
        print(operation)
        operation.run(tracks)
