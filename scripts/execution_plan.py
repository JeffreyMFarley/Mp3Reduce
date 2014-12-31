# -*- coding: utf-8 -*

import sys
import csv
import math
import keep_or_delete as Upstream
import iTunes
import Levenshtein as DL

LIBRARY_COLUMNS = ['Track ID', 'Track Number', 'Name', 'Album', 'Artist', 'Location']
LIBRARY_FILE = r'..\data\iTunes Music Library.xml'
LIBRARY_CORRECT_ROOT_ALIAS = '/Users/yeimi/Music/iTunes/iTunes Media'

COLUMNS = Upstream.COLUMNS + ['strategy', 'newPath']
KEY = Upstream.KEY
FILENAME = r'..\data\plan.txt'

CORRECT_ROOT = '/Volumes/Music/Jennifer Music'

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------
class ExecutionPlan:
    def __init__(self):
        self.plan = []
    
    def generate(self):
        # load the decisions
        print('Loading the decisions')
        self.decisions = Upstream.load()
        print(len(self.decisions),'files')
        
        # load the library
        print('Loading the library')
        self.tracks = self.loadLibrary()
        print(len(self.tracks),'library tracks')

        # get the track details
        print('Generating the strategy')
        self.route()
        
        # update the targeted names
        print('Fixing the paths')
        self.enrich()

        # write out the results
        self.save();

    def loadLibrary(self):
        library = iTunes.Library(LIBRARY_FILE, LIBRARY_COLUMNS)
        return {library.decodeFileLocation(track['Location']) for track in library.trackIterator()}

    def route(self):
        #file://localhost/Volumes/Music/Jennifer Music/ = J:
        #file://localhost/Users/yeimi/Music/iTunes/iTunes Media/ = J:
        for t in self.decisions:
            # determine alias
            location = t[Upstream.KEY]
            isRenaming = 'Unknown Album' in t[Upstream.KEY] and (t['album'] or '') != ''
            isCorrect = CORRECT_ROOT == t['root']
            alias = location.replace(CORRECT_ROOT, LIBRARY_CORRECT_ROOT_ALIAS) if isCorrect else ''

            # determine the strategy
            strategy = ''
            if t['action'] == 'keep':
                if location in self.tracks:
                    strategy = 'B' if isCorrect and not isRenaming else 'D'
                elif alias in self.tracks:
                    strategy = 'B' if not isRenaming else 'D'
                else:
                    strategy = 'A' if isCorrect and not isRenaming else 'C'
            elif t['action'] == 'remove':
                if location in self.tracks:
                    strategy = 'F' if isCorrect and not isRenaming else 'H'
                elif alias in self.tracks:
                    strategy = 'F' if not isRenaming else 'H'
                else:
                    strategy = 'E' if isCorrect and not isRenaming  else 'G'
            elif t['action'] == 'use_jeff':
                strategy = 'J' if isCorrect and not isRenaming else 'K'
            else:
                raise ValueError

            # save the record
            t['strategy'] = strategy
            self.plan.append(t)

    def predicateMoveFiles(self, x):
        return x['strategy'] in ['C', 'D', 'K']

    def predicateUpdateLibrary(self, x):
        return x['strategy'] in ['F', 'H']

    def predicateWinner(self, x):
        return x['action'] != 'remove' 

    def enrich(self):
        for row in filter(self.predicateMoveFiles, self.plan):
            row['newPath'] = self.buildTargetName(row)

        b0 = {x['key']: {Upstream.KEY: x[Upstream.KEY], 'newPath': x['newPath'] if 'newPath' in x else '', 'strategy': x['strategy']} for x in filter(self.predicateWinner, self.plan)}
        for row in filter(self.predicateUpdateLibrary, self.plan):
            winner = b0[row['key']]
            if winner['strategy'] == 'B':
                print('Library already has this song', row[Upstream.KEY], file=sys.stderr)
            elif self.predicateMoveFiles(winner):
                print('Winner is moving', winner[Upstream.KEY], winner['strategy'], file=sys.stderr)
                row['newPath'] = winner['newPath']
            else:
                row['newPath'] = winner[Upstream.KEY]


    def buildTargetName(self, x):
        artist = x['artist'] or ''
        if artist == '':
            artist = 'Unknown Artist'
        artistSplit = artist.partition('/')
        artist = artistSplit[0] if 'Nine Inch' not in artistSplit[2] else artistSplit[2]  # fix up YEARZEROREMIX

        album = x['album'] or ''
        if album == '':
            album = 'Unknown Album'
        if artist == 'Phish' and '2009' in album:       # Use shorter live title
            album = album.partition(' ')[0]

        # fix bad characters 
        artist = self.fixBadCharacters(artist)
        album = self.fixBadCharacters(album)

        canonSubdir = artist+'/'+album
        subdir = x['subdir']
        distance = math.trunc((100 * DL.distance(canonSubdir, subdir)) / max(len(canonSubdir),len(subdir)))

        if 'Podcast' in subdir or 'Ringtone' in subdir:
            canonSubdir = subdir
        elif distance != 0:
            #print(str(distance), canonSubdir,'vs',subdir, file=sys.stderr)
            pass

        return CORRECT_ROOT+'/'+canonSubdir+'/'+x['file']

    def fixBadCharacters(self, x):
        result = x.replace('/', '-')
        result = result.replace('\\', '-')
        result = result.replace(':', '_')
        if result[-1] == '.':
            result = result[:-1] + '_'
        return result

    def load(self):
        return list(self.iter_load())

    def iter_load(self):
        with open(FILENAME, 'r', encoding='utf-8') as fin:
            reader = csv.DictReader(fin, dialect=csv.excel_tab)
            for row in reader:
                yield row

    def save(self):
        with open(FILENAME, 'w', encoding='utf-8') as fout:
            writer = csv.DictWriter(fout, COLUMNS, dialect=csv.excel_tab, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(sorted(self.plan, key=Upstream.outputSort))

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

def main():
    pipeline = ExecutionPlan()
    pipeline.generate()
    
if __name__ == '__main__':
    main()



