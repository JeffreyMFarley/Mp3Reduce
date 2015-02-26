import os
import sys
import pyTagger


class TrackGroupForUpdate():
    def __init__(self):
        self.tracks = {}

    def add(self, path, track):
        self.tracks[path] = track

    def addUpdates(self, snapshot):
        # some easy ones
        l = len(self.tracks)
        if l != 2:
            return

        keys = list(self.tracks.keys())
        track0 = self.tracks[keys[0]]
        if 'keep' in track0 and track0['keep'] == True:
            return

        track1 = self.tracks[keys[1]]
        if not track0['track'] and track1['track']:
            snapshot.update({keys[0]: {'track': track1['track'] }})
        if track0['track'] and not track1['track']:
            snapshot.update({keys[1]: {'track': track0['track'] }})
        

class GenerateUpdateSnapshot():
    def __init__(self, outfile=r'..\data\phaseII_updates.json'):
        self.outfile = outfile

    def __str__(self):
        return 'Generating Update Snapshot'

    def run(self, tracks):
        groups = {}

        ## build the groups from the duplcate ids
        #for k,v in tracks.items():
        #    id = v['groupID']
        #    if id not in groups:
        #        groups[id] = TrackGroupForUpdate()
        #    groups[id].add(k,v)

        ## process the groups
        #output = {}
        #for g in groups.values():
        #    g.addUpdates(output)

        ## write it out
        #writer = pyTagger.Mp3Snapshot(False)
        #writer.save(self.outfile, output)


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
