import csv
import keep_or_delete as Upstream

COLUMNS = ['track', 'title', 'album', 'artist', 'fullPath', 'drive', 'root', 'subdir', 'file', 'old_key', 'new_key']
FILENAME_KEYS = r'..\data\curated_keys.txt'
FILENAME_NAMES = r'..\data\curated_names.txt'

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class UpdateKeys:
    def __init__(self):
        self.updates = {}

    def run(self):
        self.loadUpdates()
        l = Upstream.load()
        for r in filter(self.predicate, l):
            r['action'] = 'remove'
            r['key'] = self.updates[r['key']]
        Upstream.save(l)

    def loadUpdates(self):
        with open(FILENAME_KEYS, encoding='utf-8') as f:
            self.updates = {x['old_key']: x['new_key'] for x in csv.DictReader(f, dialect=csv.excel_tab)}

    def predicate(self, x):
        return x['key'] in self.updates
 
class UpdateNames:
    def __init__(self):
        self.updates = {}

    def run(self):
        self.loadUpdates()
        l = Upstream.load()
        for target in filter(self.predicate, l):
            source = self.updates[target[Upstream.KEY]]
            self.updateField(source, target, 'track')
            self.updateField(source, target, 'title')
            self.updateField(source, target, 'artist')
            self.updateField(source, target, 'album')
        Upstream.save(l)

    def loadUpdates(self):
        with open(FILENAME_NAMES, encoding='utf-8') as f:
            self.updates = {x[Upstream.KEY]: x for x in csv.DictReader(f, dialect=csv.excel_tab)}

    def predicate(self, x):
        return x[Upstream.KEY] in self.updates

    def updateField(self, x, y, field):
        if y[field] != x[field]:
            y[field] = x[field]

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

def main():
    pipeline = [UpdateKeys(), UpdateNames()]
    for p in pipeline:
        p.run()
    
if __name__ == '__main__':
    main()
