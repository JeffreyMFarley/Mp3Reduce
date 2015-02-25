import os
import sys
import pyTagger
import itertools

class AlbumGroup():
    def __init__(self):
        self.tracks = {}

    def add(self, path, track):
        self.tracks[path] = track

    def grade(self):
        # gather group statistics
        groups = {x['gSummary'] if 'gSummary' in x else '' for x in self.tracks.values()}
        westerosi = sum([1 if x['root'] == 'Jeff' else 0 for x in self.tracks.values()])
        yeimi = sum([1 if x['root'] == 'Jen' else 0 for x in self.tracks.values()])

        # record the information
        summary = '{0},{1},{2}'.format(len(groups), westerosi, yeimi)
        for t in self.tracks.values():
            t['ang'] = len(groups)
            t['anw'] = westerosi
            t['any'] = yeimi
            t['aSummary'] = summary

class TrackGroup:
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

        # investigate 'lengths' a little deeper
        if len(lengths) == 2:
            asList = list(lengths) 
            diff = abs(asList[0] - asList[1])
            if diff <= 2:
                lengths.pop()

        summary = self.enrich(ids, fileHashes, nameHashes, roots, lengths)
        if len(ids) == 1 and len(fileHashes) == 1 and len(roots) == 2:
            self.markAllKeep('A')

    def markAllKeep(self, v):
        for t in self.tracks.values():
            t['keep'] = v

    def enrich(self, ids, fileHashes, nameHashes, roots, lengths):
        summary = '{0},{1},{2},{3},{4}'.format(len(fileHashes), len(ids), len(nameHashes), len(lengths), len(roots))
        for t in self.tracks.values():
            t['gnf'] = len(fileHashes)
            t['gni'] = len(ids)
            t['gnn'] = len(nameHashes)
            t['gnl'] = len(lengths)
            t['gnr'] = len(roots)
            t['gSummary'] = summary

        return summary


class GradeDuplicates():
    def __init__(self):
        pass

    def run(self, tracks):
        self.scoreAsGroups(tracks)
        self.scoreAsAlbums(tracks)

    def scoreAsGroups(self, tracks):
        groups = {}

        # build the groups from the duplcate ids
        for k,v in tracks.items():
            id = v['groupID']
            if id not in groups:
                groups[id] = TrackGroup()
            groups[id].add(k,v)

        # grade the groups
        for g in groups.values():
            g.grade()

    def scoreAsAlbums(self, tracks):
        groups = {}

        # build the groups from the duplcate ids
        for k,v in tracks.items():
            id = v['n_album']
            if id not in groups:
                groups[id] = AlbumGroup()
            groups[id].add(k,v)

        # grade the groups
        for g in groups.values():
            g.grade()

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

