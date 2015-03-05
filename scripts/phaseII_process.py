from __future__ import print_function
import pyTagger
from phaseII_manual_updates import *
from add_name_hash import *
from add_library_ids import *
from find_duplicates import *
from grade_duplicates import *
from pick_winners import *
from generate_delete_script import *
from generate_update_snapshot import *
from generate_white_list import *
from generate_yeimi_update import *

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

    pipeline = [AddYeimiLibraryIds(), AddWesterosLibraryIds(), 
                PhaseII_PreHashUpdates(), FilterWhiteList(), 
                AddNameHash(), 
                FindDuplicates(), GradeDuplicates(), PickWinners(), 
                GenerateUpdateSnapshot(), GenerateWhiteList(),
                GenerateYeimiDeleteScript(), GenerateYeimiUpdate()]

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    for operation in pipeline:
        print(operation)
        operation.run(tracks)
        snapshot.save(outFile, tracks)
