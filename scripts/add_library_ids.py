import os
import sys
import pyTagger
import urllib
import unicodedata
import generate_normalization_maps as Normalize

PATH_YEIMI = r'..\data\yeimi_library.txt'
PATH_WESTEROS = r'..\data\westeros_library.txt'

class AddYeimiLibraryIds():
    def __init__(self, fileName=PATH_YEIMI, performQA=False):
        self.fileName = fileName
        self.performQA = performQA

    def __str__(self):
        return "Adding IDs from Jen's iTunes Library"

    def run(self, tracks):
        if not os.path.exists(self.fileName):
            return

        normalizer = Normalize.GenerateNormalizationMaps()

        with open(self.fileName, 'r', encoding='macintosh') as f:
            header = f.readline()
            for row in f:
                cells = row.strip().split('\t')
                t = {'title': normalizer.normalize(cells[0]), 
                     'path': unicodedata.normalize('NFKD', cells[1]), 
                     'id': int(cells[2])}

                if '<eth>' in t['path']:
                    t['path'] = t['path'].replace('<eth>', chr(240))

                if 'Pel? Merengue' in t['path']:
                    t['path'] = t['path'].replace('?', chr(12539))

                if 'Lobotomy' in t['path']:
                    t['path'] = t['path'].replace('?', chr(61480))

                if '?' in t['path']:
                    t['path'] = t['path'].replace('?', chr(61477))

                if t['path'] in tracks:
                    track = tracks[t['path']]
                    track['yeimi_id'] = t['id']

                    if self.performQA and 'title' in track and track['title']:
                        nt = normalizer.normalize(track['title'])
                        if (nt != t['title']):
                            print('  QA Issue', 
                                  t['path'].encode(errors='ignore'), 
                                  'title mismatch\t', nt.encode(errors='ignore'), 
                                  '\t', t['title'].encode(errors='ignore'))

                elif t['path'][-3:] == 'mp3':
                    print('  ', t['path'].encode(errors='ignore'), 'not found', file=sys.stderr)

class AddWesterosLibraryIds():
    def __init__(self, fileName=PATH_WESTEROS):
        self.fileName = fileName

    def __str__(self):
        return "Adding IDs from Jeff's iTunes Library"

    def run(self, tracks):
        if not os.path.exists(self.fileName):
            return

        # Windows OS is not case sensitive
        ciTracks = {unicodedata.normalize('NFKD', k).lower():v for k,v in tracks.items() }

        with open(self.fileName, 'r', encoding='utf-8') as f:
            for row in f:
                cells = row.strip().split('\t')
                t = {'title': unicodedata.normalize('NFKD', cells[0]), 
                     'path': unicodedata.normalize('NFKD', cells[1]).lower(), 
                     'idh': int(cells[2]),
                     'idl': int(cells[3])
                     }

                if t['path'] in ciTracks:
                    ciTrack = ciTracks[t['path']]
                    ciTrack['westeros_idh'] = t['idh']
                    ciTrack['westeros_idl'] = t['idl']
                elif t['path'][-3:] == 'mp3' and t['path'][0] not in ['c', 'l']:
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

    pipeline = [AddYeimiLibraryIds(), AddWesterosLibraryIds()]

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    for operation in pipeline:
        print(operation)
        operation.run(tracks)
        # snapshot.save(outFile, tracks)