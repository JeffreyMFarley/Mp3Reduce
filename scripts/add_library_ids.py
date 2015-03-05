import os
import sys
import pyTagger
import urllib
import unicodedata

class AddYeimiLibraryIds():
    def __init__(self, fileName=r'..\data\yeimi_library.txt'):
        self.fileName = fileName

    def __str__(self):
        return "Adding IDs from Jen's iTunes Library"

    def run(self, tracks):
        if not os.path.exists(self.fileName):
            return
        with open(self.fileName, 'r', encoding='macintosh') as f:
            for row in f:
                cells = row.strip().split('\t')
                t = {'title': unicodedata.normalize('NFKD', cells[0]), 
                     'path': unicodedata.normalize('NFKD', cells[1]), 
                     'id': int(cells[2])}

                if 'Sigur' in t['path']:
                    t['path'] = t['path'].replace('<eth>', chr(240))

                if t['path'] in tracks:
                    tracks[t['path']]['yeimi_id'] = t['id']
                elif t['path'][-3:] == 'mp3':
                    print('  ', t['path'].encode(errors='ignore'), 'not found')

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s.json'
    outFile = r'..\data\mp3s_step2.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]
    if argc > 2:
        outFile = sys.argv[2]

    pipeline = [AddYeimiLibraryIds()]

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    for operation in pipeline:
        print(operation)
        operation.run(tracks)
        snapshot.save(outFile, tracks)