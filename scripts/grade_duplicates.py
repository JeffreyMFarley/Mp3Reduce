import os
import sys
import pyTagger
import itertools

class Group:
    def __init__(self):
        self.tracks = {}

    def add(self, path, track):
        self.tracks[path] = track

    def grade(self):
        # some easy ones
        l = len(self.tracks)
        if l > 10 or l < 2:
            self.markAllKeep(True)
            return

        # gather group statistics
        lengths = {x['length'] for x in self.tracks.values()}
        ids = {x['id'] for x in self.tracks.values()}
        fileHashes = {x['fileHash'] for x in self.tracks.values()}
        roots = {x['root'] for x in self.tracks.values()}
        nameHashes = {x['nameHash'] for x in self.tracks.values()}

        summary = self.enrich(ids, fileHashes, nameHashes, roots, lengths)
        if len(ids) == 1 and len(fileHashes) == 1 and len(roots) == 2:
            self.markAllKeep('A')

    def markAllKeep(self, v):
        for t in self.tracks.values():
            t['keep'] = v

    def enrich(self, ids, fileHashes, nameHashes, roots, lengths):
        summary = '{0},{1},{2},{3},{4}'.format(len(ids), len(fileHashes), len(nameHashes), len(roots), len(lengths))
        for t in self.tracks.values():
            t['gni'] = len(ids)
            t['gnf'] = len(fileHashes)
            t['gnn'] = len(nameHashes)
            t['gnr'] = len(roots)
            t['gnl'] = len(lengths)
            t['gSummary'] = summary

        return summary


class GradeDuplicates():
    def __init__(self):
        pass

    def run(self, tracks):
        groups = {}

        # build the group set
        for k,v in tracks.items():
            id = v['groupID']
            if id not in groups:
                groups[id] = Group()
            groups[id].add(k,v)

        # grade the groups
        for g in groups.values():
            g.grade()

    # -------------------------------------------------------------------------
    # Relational Algebra
    # -------------------------------------------------------------------------
    def groupByKey(self, x):
        return x['groupID']

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

    pipeline = GradeDuplicates()

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    pipeline.run(tracks)
    snapshot.save(outFile, tracks)

