import os
import sys
import pyTagger

class UndirectedTrackNode:
    def __init__(self, key, track):
        self.key = key
        self.value = track
        self.relations = set()

    def relate(self, node):
        self.relations.add(node)
        node.relations.add(self)

class UndirectedGraph:
    def __init__(self, tracks):
        self.nodes = set([UndirectedTrackNode(k,v) for k,v in tracks.items()])

class FindDuplicates():
    def __init__(self):
        pass

    def __str__(self):
        return 'Find Duplicates'

    def run(self, tracks):
        graph = UndirectedGraph(tracks)
        self.buildRelations(graph)
        self.extractDisjoints(graph, tracks)

    def buildRelations(self, graph):
        queue = list(graph.nodes)
        l = len(queue)
        progress = pyTagger.ProgressBar((l * (l-1))/2, '  Step 1: Building relations')

        while len(queue) > 0:
            n0 = queue.pop(0)
            for n in queue:
                progress.increment()
                if self.areRelated(n0.value, n.value):
                    n0.relate(n)
        progress.finish()

    def extractDisjoints(self, graph, tracks):
        progress = pyTagger.ProgressBar(graph.nodes, '  Step 2: Extract Disjoints')

        group = 0
        while len(graph.nodes) > 0:
            progress.increment()
            n0 = graph.nodes.pop()
            tracks[n0.key]['groupID'] = group
            for n in n0.relations:
                tracks[n.key]['groupID'] = group
                if n in graph.nodes:
                    progress.increment()
                    graph.nodes.remove(n)
            group += 1
        
        progress.finish()

    def areRelated(self, a, b):
        aid = a['id'] if 'id' in a else ''
        bid = b['id'] if 'id' in b else ''
        r0 = aid == bid and aid and bid
        r1 = a['fileHash'] == b['fileHash']
        r2 = a['nameHash'] == b['nameHash']
        return r0 or r1 or r2

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

    pipeline = FindDuplicates()

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    pipeline.run(tracks)
    snapshot.save(outFile, tracks)

