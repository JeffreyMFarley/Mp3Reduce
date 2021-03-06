import os
import sys
from generate_westeros_update import GenerateWesterosUpdate as WU
import pyTagger

PATH = r'..\data\phaseII_updates.json'

class TrackGroupForUpdate():
    def __init__(self, updater, columns):
        self.tracks = {}
        self.updater = updater
        self.columns = columns

    def add(self, path, track):
        self.tracks[path] = track

    def addUpdates(self, snapshot):
        # some easy ones
        l = len(self.tracks)
        if l != 2:
            return

        keys = list(self.tracks.keys())
        track0 = self.tracks[keys[0]]
        track1 = self.tracks[keys[1]]
       
        if WU.predicate(track0):
            self.addUpdate(track0, track1, keys[1], snapshot)
        elif WU.predicate(track1):
            self.addUpdate(track1, track0, keys[0], snapshot)
        elif self.predicate(track0):
            self.addUpdate(track1, track0, keys[0], snapshot)
        elif self.predicate(track1):
            self.addUpdate(track0, track1, keys[1], snapshot)

    def addUpdate(self, a, b, k, snapshot):
        v = self.updater._findDelta(a, b)
        remove = [field for field in v if field not in self.columns or not v[field]]
        for field in remove:
            del v[field]

        snapshot.update({k: v})

    def predicate(self, x):
        return ('strategy' in x and x['strategy'] in ['H'] and
                'root' in x and x['root'] == 'Jen')

class GenerateUpdateSnapshot():
    def __init__(self, outfile=PATH):
        self.outfile = outfile
        self.updater = pyTagger.UpdateFromSnapshot()
        self.columns = set(pyTagger.Formatter.columns) - set(pyTagger.Formatter.mp3Info)
        for t in ['length', 'id']:
            self.columns.remove(t)

    def __str__(self):
        return 'Generating Update Snapshot'

    def run(self, tracks):
        groups = {}

        # build the groups from the duplcate ids
        for k,v in tracks.items():
            id = v['groupID']
            if id not in groups:
                groups[id] = TrackGroupForUpdate(self.updater, self.columns)
            groups[id].add(k,v)

        # process the groups
        output = {}
        for g in groups.values():
            g.addUpdates(output)

        # write it out
        writer = pyTagger.Mp3Snapshot(False)
        writer.save(self.outfile, output)


#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s_enh.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]

    pipeline = GenerateUpdateSnapshot()

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    pipeline.run(tracks)
