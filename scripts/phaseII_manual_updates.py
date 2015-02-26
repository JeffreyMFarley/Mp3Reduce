from __future__ import print_function
import os
import sys
import pyTagger

FILENAME_PREHASHUPDATES = r'..\data\phaseII_prehash_updates.json'

class PhaseII_PreHashUpdates():
    def __init__(self):
        pass

    def __str__(self):
        return 'Applying Pending Updates'

    def run(self, tracks):
        snapshot = pyTagger.Mp3Snapshot(True)
        updates = snapshot.load(FILENAME_PREHASHUPDATES)
        for k,v in updates.items():
            if k and k not in tracks:
                print(k, 'not found in track list', file=sys.stderr)
            else:
                track = tracks[k]
                track.update(v)

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s.json'
    outFile = r'..\data\mp3s_upd.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]
    if argc > 2:
        outFile = sys.argv[2]

    pipeline = PhaseII_PreHashUpdates()

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    pipeline.run(tracks)
    snapshot.save(outFile, tracks)

