from __future__ import print_function
import pyTagger
from phaseII_manual_updates import *
from add_name_hash import *
from find_duplicates import *
from grade_duplicates import *

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s.json'
    outFile = r'..\data\mp3s_enh.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]
    if argc > 2:
        outFile = sys.argv[2]

    pipeline = [PhaseII_PreHashUpdates(), AddNameHash(), FindDuplicates(), GradeDuplicates()]

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    for operation in pipeline:
        operation.run(tracks)
    snapshot.save(outFile, tracks)
