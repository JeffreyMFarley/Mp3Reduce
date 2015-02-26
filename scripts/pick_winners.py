import os
import sys
import pyTagger


class PickWinners():
    def __init__(self):
        pass

    def __str__(self):
        return 'Pick Winners'

    def run(self, tracks):
        pass

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s_enh.json'
    outFile = r'..\data\mp3s_step2.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]
    if argc > 2:
        outFile = sys.argv[2]

    pipeline = PickWinners()

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    pipeline.run(tracks)
    snapshot.save(outFile, tracks)