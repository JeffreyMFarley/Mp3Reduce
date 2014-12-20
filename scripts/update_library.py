import sys
import execution_plan as Upstream
import iTunes
import plistlib

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------
class UpdateLibrary:
    def __init__(self):
        self.plan = Upstream.ExecutionPlan()
        self.library = None
        self.tracks = []
        self._root = None

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        self._root = value
            
    def update(self, targetStrategies, inFile, outFile):
        self.targetStrategies = targetStrategies

        print('Loading Current Library')
        self.tracks = self.loadLibrary(inFile)

        print('Updating values')
        for row, track in map(self.projection, filter(self.predicate, self.plan.iter_load())):
            self.updateTrack(row, track)

        print('Saving Library')
        plistlib.writePlist(self.root, outFile)
    
    def predicate(self, x):
        return x['strategy'] in self.targetStrategies

    def projection(self, x):
        location = x[Upstream.KEY]
        alias = location.replace(Upstream.CORRECT_ROOT, Upstream.LIBRARY_CORRECT_ROOT_ALIAS)
        if location in self.tracks:
            return (x, self.tracks[location])
        elif alias in self.tracks:
            return (x, self.tracks[alias])
        else:
            return (x, {})

    def loadLibrary(self, inFile):
        self.library = iTunes.Library(inFile)
        self.root = plistlib.readPlist(inFile)
        tracks = self.root['Tracks']
        return {self.library.decodeFileLocation(tracks[track_id]['Location']) : tracks[track_id] for track_id in tracks}

    def updateTrack(self, x, t):
        if len(t) == 0:
            print(x['strategy'], 'Not found in library, no update:', x[Upstream.KEY], file=sys.stderr)
            return

        if (x['newPath'] or '') == '':
            print(x['strategy'], 'Remove from library manually:',x[Upstream.KEY], file=sys.stderr)
            return

        t['Location'] = self.library.encodeFileLocation(x['newPath'])

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

def main():
    pipeline = UpdateLibrary()
    pipeline.update(['D', 'F', 'H'], r'J:\iTunes Music Library.xml', r'J:\iTunes Music Library (new).xml')
    
if __name__ == '__main__':
    main()



