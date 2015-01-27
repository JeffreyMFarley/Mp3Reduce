import collections
import pyTagger

class ListMissingTags:
    def __init__(self):
        pass

    def generate(self, inFileName, outFileName):
        snapshot = pyTagger.Mp3Snapshot(False)
        columns = pyTagger.mp3_snapshot.Formatter.basic
        columns.append('version')
        tracks = {k: {c: v[c] 
                      for c in columns 
                      if c in v}
                  for k,v in snapshot.load(inFileName).items()
                  if self.hasMissing(k,v)}
        
        ordered = collections.OrderedDict(sorted(tracks.items()))
        snapshot.save(outFileName, ordered)

    # -------------------------------------------------------------------------
    # Relational Algebra
    # -------------------------------------------------------------------------
    def hasMissing(self, path, x):
        test = (#'track' not in x or not x['track'] or
                'title' not in x or not x['title'] or
                'artist' not in x or not x['artist'] or
                'album' not in x or not x['album'])
        return (test and 
                'Podcast' not in path and
                'Ringtone' not in path)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    inFileName = r'..\data\mp3s.json'
    outFileName = r'..\data\missing.json'

    pipeline = ListMissingTags()
    pipeline.generate(inFileName, outFileName)
