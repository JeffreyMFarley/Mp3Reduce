from __future__ import print_function
import sys
import os
import socket
import shutil
import pyTagger
import add_library_ids as O1
import phaseII_manual_updates as O2
import add_name_hash as O3
import find_duplicates as O4
import grade_duplicates as O5
import pick_winners as O6
import generate_update_snapshot as O7
import generate_delete_script as O8
import generate_white_list as WL
import generate_yeimi_update as O9
import generate_westeros_update as O10

PATH_INPUT = r'..\data\mp3s.json'
PATH_OUTPUT_JSON = r'..\data\mp3s_enh.json'
PATH_OUTPUT_CSV = r'..\data\mp3s_enh.txt'

def KiraPath(p):
    path, fileName = os.path.split(p)
    return os.path.join('J:', fileName)

def import_files():
    files = [PATH_INPUT, O1.PATH_YEIMI]
    for file in files:
        kira = KiraPath(file)
        shutil.copy(kira, file)
       
def export_files():
    files = [O2.PATH_MANUAL, O7.PATH, O8.PATH_WESTEROS, O8.PATH_YEIMI, O9.PATH, O10.PATH_IMAGES]
    for file in files:
        kira = KiraPath(file)
        shutil.copy(file, kira)


#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = PATH_INPUT
    outFile = PATH_OUTPUT_JSON
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]
    if argc > 2:
        outFile = sys.argv[2]

    hostName = socket.gethostname()
    isWesteros = hostName == 'Westeros'

    pipeline = [O1.AddYeimiLibraryIds(), O1.AddWesterosLibraryIds(), 
                O2.PhaseII_PreHashUpdates(), WL.FilterWhiteList(), 
                O3.AddNameHash(), 
                O4.FindDuplicates(), O5.GradeDuplicates(), O6.PickWinners(), 
                O7.GenerateUpdateSnapshot(), WL.GenerateWhiteList(),
                O8.GenerateYeimiDeleteScript(), O8.GenerateWesterosDeleteScript(), 
                O9.GenerateYeimiUpdate(), O10.GenerateWesterosUpdate()]

    if isWesteros:
        print('Importing from KIRA')
        import_files()

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    for operation in pipeline:
        print(operation)
        operation.run(tracks)
        snapshot.save(outFile, tracks)

    if isWesteros:
        print('Exporting to KIRA')
        export_files()

    print('Convert to CSV')
    converter = pyTagger.SnapshotConverter()
    converter.convert(outFile, PATH_OUTPUT_CSV)