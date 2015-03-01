import os
import sys
import pyTagger


class TrackGroupForWinners():
    def __init__(self):
        self.tracks = {}

    def add(self, path, track):
        self.tracks[path] = track

    def pickWinner(self):
        # is this  winner?
        if len(self.tracks) != 2:
            return

        keys = list(self.tracks.keys())
        track0 = self.tracks[keys[0]]
        track1 = self.tracks[keys[1]]

        # strategies
        if self.isStrategyA(track0):
            if 'Jeff' in track0['root']:
                self.writeStrategy(track0, track1, 'A')
            else:
                self.writeStrategy(track1, track0, 'A')

        elif self.isStrategyB(track0):
            self.writeStrategy(track1, track0, 'B')

        elif self.isStrategyB(track1):
            self.writeStrategy(track0, track1, 'B')

        elif self.isStrategyD(track0):
            if keys[1][-5] == '2':
                self.writeStrategy(track0, track1, 'D')
            else:
                self.writeStrategy(track1, track0, 'D')

    def isStrategyA(self, track):
        a0 = ('ang' in track and track['ang'] == 1 
              and 'gSummary' in track 
              and track['gSummary'] in ['1,2,1,1,2', '1,1,1,1,2'])
        a1 = ('ang' in track and track['ang'] == 1 
              and 'gSummary' in track and track['gSummary'] == '2,1,1,1,2'
              and 'id' in track and track['id'])
        a2 = ('ang' in track and track['ang'] > 1 
              and 'gSummary' in track and track['gSummary'] == '1,1,1,1,2'
              and 'id' in track and track['id'])
        return a0 or a1 or a2

    def isStrategyB(self, track):
        return ('subtitle' in track 
            and track['subtitle'] in ['2007-03-18', '2009-07-19'])

    def isStrategyD(self, track):
        return ('ang' in track and track['ang'] == 1 
            and 'gSummary' in track 
            and track['gSummary'] in ['1,1,1,1,1'])

    def writeStrategy(self, winner, loser, strategy):
        winner['keep'] = True
        winner['strategy'] = strategy
        loser['keep'] = False
        loser['strategy'] = strategy

class PickWinners():
    def __init__(self):
        pass

    def __str__(self):
        return 'Pick Winners'

    def run(self, tracks):
        groups = {}

        # build the groups from the duplcate ids
        for k,v in tracks.items():
            id = v['groupID']
            if id not in groups:
                groups[id] = TrackGroupForWinners()
            groups[id].add(k,v)

        # process the groups
        for g in groups.values():
            g.pickWinner()

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