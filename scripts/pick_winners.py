import os
import sys
import pyTagger


class AlbumGroupForWinners():
    def __init__(self):
        self.tracks = {}

    def add(self, path, track):
        self.tracks[path] = track

    def calculateAggregates(self):
        # gather group statistics
        strategies = {x['strategy'] if 'strategy' in x else '-' for x in self.tracks.values()}
        keepJeff = self.sumKeeps('Jeff')
        keepJen = self.sumKeeps('Jen')

        # record the information
        summary = ','.join(sorted(strategies))
        for t in self.tracks.values():
            t['keepJeff'] = keepJeff
            t['keepJen'] = keepJen
            t['aStrat'] = summary

    def sumKeeps(self, root):
        return sum([1 for x in self.tracks.values() 
                    if 'root' in x and x['root'] == root and 'keep' in x and x['keep']])

class TrackGroupForWinners():
    def __init__(self):
        self.tracks = {}
        self.strategyA2 = [5120, 4768, 7502, 2622, 1238, 11472, 8844, 8288,
                           8286, 10860, 10862, 10998, 12312, 34697]

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
                self.writeStrategy(track0, track1, 'A', keys[0])
            else:
                self.writeStrategy(track1, track0, 'A', keys[1])

        elif self.isStrategyA2(track0):
            self.writeStrategy(track1, track0, 'A', keys[1])
        elif self.isStrategyA2(track1):
            self.writeStrategy(track0, track1, 'A', keys[0])

        elif self.isStrategyB(track0):
            self.writeStrategy(track1, track0, 'B', keys[1])
        elif self.isStrategyB(track1):
            self.writeStrategy(track0, track1, 'B', keys[0])

        elif self.isStrategyC(track0):
            winner, loser = self.strategyCWinner(track0, track1)
            self.writeStrategy(winner, loser, 'C', keys[0] if winner == track0 else keys[1])

        elif self.isStrategyD(track0):
            if keys[1][-5] == '2':
                self.writeStrategy(track0, track1, 'D')
            else:
                self.writeStrategy(track1, track0, 'D')

        elif self.isStrategyCure(track0):
                self.writeStrategy(track0, track1, 'Cure', keys[0])
        elif self.isStrategyCure(track1):
                self.writeStrategy(track1, track0, 'Cure', keys[1])

        elif self.isStrategyE(track0):
            if 'Jen' in track0['root']:
                self.writeStrategy(track0, track1, 'E', keys[0])
            else:
                self.writeStrategy(track1, track0, 'E', keys[1])

    def isStrategyA(self, track):
        a0 = ('ang' in track and track['ang'] == 1 
              and 'gSummary' in track 
              and track['gSummary'] in ['1,2,1,1,2', '1,1,1,1,2'])
        a1 = ('ang' in track and track['ang'] == 1 
              and 'gSummary' in track and track['gSummary'] == '2,1,1,1,2'
              and 'id' in track and track['id'])
        a2 = ('ang' in track and track['ang'] == 2 
              and 'gSummary' in track and track['gSummary'] == '1,1,1,1,2'
              and 'id' in track and track['id'])
        a3 = ('ang' in track and track['ang'] > 1 
              and 'gSummary' in track and track['gSummary'] == '2,1,1,1,2'
              and 'anw' in track and 'any' in track
              and track['anw'] > track['any'])
        return a0 or a1 or a2 or a3

    def isStrategyA2(self, track):
        a0 = 'yeimi_id' in track and track['yeimi_id'] in self.strategyA2
        a1 = ('n_album' in track 
              and track['n_album'] in ['mirror conspiracy', 'moon antarctica', 'broken social scene']
              and track['root'] == 'Jen')
        return a0 or a1

    def isStrategyB(self, track):
        b0 = ('subtitle' in track 
              and track['subtitle'] in ['2007-03-18', '2007-10-14', '2009-07-19'])
        b1 = ('album' in track 
              and track['album'] == 'A Jolly Christmas from Frank Sinatra'
              and track['root'] == 'Jeff')
        return b0 or b1

    def isStrategyC(self, track):
        return 'anz' in track and track['anz']

    def isStrategyD(self, track):
        return ('ang' in track and track['ang'] == 1 
            and 'gSummary' in track 
            and track['gSummary'] in ['1,1,1,1,1'])

    def isStrategyE(self, track):
        return ('anw' in track and 'any' in track
                and track['any'] > track['anw'])

    def isStrategyCure(self, track):
        return ('n3' == 'cure' 
                and 'aSummary' in track and ',0,' in track['aSummary']
                # and track['title'][0] not in ['0', '1']
                )

    def strategyCWinner(self, a, b):
        if a['bitRate'] > b['bitRate']:
            return (a,b)
        if b['bitRate'] > a['bitRate']:
            return (b,a)

        if a['version'] > b['version']:
            return (a,b)
        if b['version'] > a['version']:
            return (b,a)

        return (a,b)

    def writeStrategy(self, winner, loser, strategy, winningFile=None):
        winner['keep'] = True
        winner['strategy'] = strategy
        loser['keep'] = False
        loser['strategy'] = strategy
        if winningFile:
            loser['winner'] = winningFile

class PickWinners():
    def __init__(self):
        pass

    def __str__(self):
        return 'Pick Winners'

    def run(self, tracks):
        self.pickWinnerWithinGroup(tracks)
        self.aggregateByAlbums(tracks)

    def pickWinnerWithinGroup(self, tracks):
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

    def aggregateByAlbums(self, tracks):
        groups = {}

        # build the groups from the albums ids
        for k,v in tracks.items():
            id = v['n_album']
            if id not in groups:
                groups[id] = AlbumGroupForWinners()
            groups[id].add(k,v)

        # grade the groups
        for g in groups.values():
            g.calculateAggregates()

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