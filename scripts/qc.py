import csv
import sys
import itertools
import keep_or_delete as Upstream
import curated_updates as Downstream

COLUMNS = ['track', 'title', 'album', 'artist', 'fullPath', 'drive', 'root', 'subdir', 'file']
FILENAME = r'..\data\duplicates.txt'

#-------------------------------------------------------------------------------
# Methods
#-------------------------------------------------------------------------------
def predicateWinner(x):
    return x['action'] != 'remove' 

def buildAggregatedTitle(x):
    track = 0
    try: 
        track = int(x['track'])
    except ValueError:
        track = 0
    return '{0}.{1}.{2:02d}.{3}'.format(x['artist'] or 'None',x['album'] or 'None',track, x['title'] or 'None')

def groupByAggregateTitle(x):
    return x['title']

def projectionOnlyKey(x):
    return x['key']

def findDuplicates(x):
    return 'None' not in x['title'] and len(x['keys']) > 1

def projectionCurated(x):
    return {COLUMNS[i]:x[key] for i, key in enumerate(COLUMNS)}

def save(theList):
    with open(FILENAME, 'w', encoding='utf-8') as fout:
        writer = csv.DictWriter(fout, Downstream.COLUMNS, dialect=csv.excel_tab, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(theList)

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

def main():
    print('Build Winners Map')
    b0 = {x['key']: x for x in filter(predicateWinner, Upstream.iter_load())}
    
    print('Build Track Groups')
    a0 = [{'title':buildAggregatedTitle(x), 'key': x['key']} for x in Upstream.iter_load()]
    a0.sort(key=groupByAggregateTitle)
    a1 = [{'title':k, 'keys':set(map(projectionOnlyKey, g))} for k, g in itertools.groupby(a0, groupByAggregateTitle)]

    print('Looking for duplicates')
    
    c0 = []
    for a in filter(findDuplicates, a1):
        c1 = [b0[ak] for ak in a['keys']]
        c1.sort(key=Upstream.sortWithinGroup)

        new_key = c1[0]['key']
        for c in c1[1:]:
            d = projectionCurated(c)
            d['new_key'] = new_key
            d['old_key'] = c['key']
            c0.append(d)

    save(c0)

if __name__ == '__main__':
    main()
