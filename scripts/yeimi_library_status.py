# -*- coding: utf-8 -*

import sys
import csv
import execution_plan as Upstream
import iTunes

projectionColumns = ['Track ID', 'Track Number', 'Name', 'Album', 'Artist', 'Location']
COLUMNS = ['Playlist', 'Track ID', 'Track Number', 'Name', 'Album', 'Artist', 'Location', 'Alias', 'Action']

inputFileName = r'..\data\iTunes Music Library.xml'
FILENAME = r'..\data\yeimi_library_status.txt'

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------
class ProcessLibraryStatus:
    def __init__(self):
        self.otherFormats = []
        self.podcasts = []
        self.unmatched = []
        self.library = iTunes.Library(inputFileName, projectionColumns)
        self.plan = Upstream.ExecutionPlan()
    
    def run(self):
        # load the decisions
        print('Loading the decisions')
        self.decisions = self.loadDecisions()
        
        # load the library
        print('Loading the library')
        self.tracks = self.loadLibrary()

        # get the track details
        print('Processing the tracks')
        self.enrich()
        self.route()

        # write out the results
        self.save(self.tracks, FILENAME)
        self.save(self.otherFormats, r'..\data\yeimi_library_otherFormats.txt');
        self.save(self.podcasts, r'..\data\yeimi_library_podcasts.txt');
        self.save(self.unmatched, r'..\data\yeimi_library_unmatched.txt');
    
    def predicateDecision(self, x):
        return x[Upstream.KEY] != ''

    def loadDecisions(self):
        return {x[Upstream.KEY]: x['strategy'] for x in filter(self.predicateDecision,self.plan.iter_load())}

    def loadLibrary(self):
        return [track for track in self.library.trackIterator()]

    def enrich(self):
        #file://localhost/Volumes/Music/Jennifer Music/ = J:
        #file://localhost/Users/yeimi/Music/iTunes/iTunes Media/ = J:
        for t in self.tracks:
            t['Playlist'] = ''
            location = self.library.decodeFileLocation(t['Location'])
            t['Location'] = location
            alias = location.replace('/Users/yeimi/Music/iTunes/iTunes Media', '/Volumes/Music/Jennifer Music')

            if location in self.decisions:
                t['Action'] = self.decisions[location]
            elif alias in self.decisions:
                t['Action'] = self.decisions[alias]
                t['Alias'] = True
            elif 'http:' in location:
                t['Action'] = 'keep'
            else:
                t['Action'] = '?'

    def predicateNoAction(self, x):
        return x['Action'] == '?'

    def route(self):
        for t in filter(self.predicateNoAction, self.tracks):
            location = t['Location']

            if 'm4a' in location:
                self.otherFormats.append(t)
            elif 'm4v' in location:
                self.otherFormats.append(t)
            elif 'Podcast' in location:
                self.podcasts.append(t)
            else:
                self.unmatched.append(t)

    def outputSort(self, x):
        return (x['Playlist'], x['Location'])

    def save(self, theList, fileName):
        fout = open(fileName, 'w', encoding='utf-8')
        writer = csv.DictWriter(fout, COLUMNS, dialect=csv.excel_tab, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(sorted(theList, key=self.outputSort))
        fout.close()
        
#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

def main():
    pipeline = ProcessLibraryStatus()
    pipeline.run()
    
if __name__ == '__main__':
    main()
    
    
##def rightJoin(onePlaylist, allTracks):
##    fk = str(onePlaylist['Track ID'])
##    track = projection_libTrack(allTracks[fk]) if fk in allTracks else {}
##    return dict(onePlaylist.items() | track.items())

# right join the track information
#mapfunc = functools.partial(rightJoin, allTracks=plist_tracks)
#playlistTracks = list(map(mapfunc, playlists))


