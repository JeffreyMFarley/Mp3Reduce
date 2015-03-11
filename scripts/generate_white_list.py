import os
import sys
import pyTagger

PATH = r'..\data\white_list.txt'

def _load(fileName):
    if not os.path.exists(fileName):
        return set()
    return {x.strip() for x in _iter_load(fileName) if x}

def _iter_load(fileName):
    with open(fileName, 'r', encoding='utf_16_le') as f:
        f.seek(2) # skip BOM
        for row in f:
            yield row

def _save(fileName, theSet):
    with open(fileName, 'w', encoding='utf_16_le') as f:
        f.write(u'\ufeff') # write BOM
        for row in sorted(theSet):
            f.write(row)
            f.write('\n')

class GenerateWhiteList():
    def __init__(self, fileName=PATH):
        self.fileName = fileName

    def __str__(self):
        return 'Updating White List'

    def run(self, tracks):
        # for these albums: we each own some tracks, but there are no overlaps
        partials = ['amorica', 'brand new eyes', 'natural born killers',
                    'greatest hits my prerogative', 'i love rock n roll',
                    'jagged little pill']

        whitelist = _load(self.fileName)
        for k,v in tracks.items():
            if ('keep' in v and v['keep'] == True
                and 'ang' in v and v['ang'] == 1
                and 'aSummary' in v and ',0' in v['aSummary']):
                if 'strategy' in v and v['strategy']:
                    continue
                print('adding', k.encode(errors='replace'))
                whitelist.add(k)

            if 'subdir' in v and ('Podcast' in v['subdir'] 
                                  or 'Ringtones' in v['subdir']):
                print('adding', k.encode(errors='replace'))
                whitelist.add(k)

            if 'n_album' in v and v['n_album'] in partials:
                print('adding', k.encode(errors='replace'))
                whitelist.add(k)

        _save(self.fileName, whitelist)


class FilterWhiteList():
    def __init__(self, fileName=PATH):
        self.fileName = fileName

    def __str__(self):
        return 'Removing White List from Tracks'

    def run(self, tracks):
        whitelist = _load(self.fileName)
        keys = list(tracks.keys())
        for k in keys:
            if k in whitelist:
                del tracks[k]

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s_enh.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]

    pipeline = [FilterWhiteList(), GenerateWhiteList()]

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    for operation in pipeline:
        print(operation)
        operation.run(tracks)
