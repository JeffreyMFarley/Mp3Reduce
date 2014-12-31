from __future__ import print_function
import os
import sys
import csv
import itertools
import unicodedata
import codecs
import Levenshtein as DL
import list_mp3s as Upstream

projectionColumns = ['Track','Title','Album','Artist','Full Path','Drive', 'Root', 'Subdir', 'File', 'Hash', 'DJTagger','Bit Rate','VBR']

COLUMNS = ['track', 'title', 'album', 'artist', 'fullPath', 'drive', 'root', 'subdir', 'file', 'key', 'ufid', 'bitRate', 'vbr', 'fileDistance', 'pathDistance', 'action']
KEY = 'fullPath'
FILENAME = r'..\data\keep_or_delete.txt'

#-------------------------------------------------------------------------------
# Methods
#-------------------------------------------------------------------------------

def groupByKey(x):
    return x['Hash']

def sortWithinGroup(x):
    c0 = 99
    if '/Volumes/Music/' in x['fullPath']:
        c0 = 1
    elif '/Volumes/Jen/' in x['fullPath']:
        c0 = 2
    elif '/Users/yeimi/' in x['fullPath']:
        c0 = 3
    return (c0, x['fileDistance'], x['pathDistance'], x['fullPath'])

def outputSort(x):
    track = 0
    try: 
        track = int(x['track'])
    except ValueError:
        pass
        
    return (x['artist'], x['album'], track, x['action'], x['fullPath'])

def projection(x):
    return {COLUMNS[i]:unicodedata.normalize('NFC',x[key]) for i, key in enumerate(projectionColumns)}

def makeGroups(theList):
    theList.sort(key=groupByKey) # groupby doesn't work with an unsorted list
    return [{'key':k, 'files':list(map(projection, g))} for k, g in itertools.groupby(theList, groupByKey)]

def getCanonical(column, group):
    uniqueVals = {x[column] for x in group['files']}
    if len(uniqueVals) > 1:
        print('collision! : ', uniqueVals, file=sys.stderr)
    group[column] = next(itertools.islice(uniqueVals, 1))

def enrich(group):
    getCanonical('track', group)
    getCanonical('title', group)
    getCanonical('album', group)
    getCanonical('artist', group)

    #convert the canonical track to a number
    try:
        trackNumber = int(group['track'])
    except ValueError:
        trackNumber = 0
    
    group['canonicalFileName'] = '{0:02d} {1}.mp3'.format(trackNumber, group['title'].lower())
    group['canonicalSubdir'] = r'{0}\{1}'.format(group['artist'].lower(), group['album'].lower())

def score(group):
    for f in group['files']:
        f['fileDistance'] = DL.distance(f['file'], group['canonicalFileName'])
        f['pathDistance'] = DL.distance(f['subdir'], group['canonicalSubdir'])
    
def reduce_keep(theGroups):
    return [g['files'][0] for g in groups]

def reduce_delete(theGroups):
    return [k for g in groups for k in g['files'][1:]]
    
def load():
    return list(iter_load())

def iter_load():
    fin = codecs.open(FILENAME, 'r', encoding='utf-8')
    reader = csv.DictReader(fin, dialect=csv.excel_tab)
    for row in reader:
        yield row
    fin.close()

def save(theList, fileName=FILENAME):
    fout = codecs.open(fileName, 'w', encoding='utf-8')
    writer = csv.DictWriter(fout, COLUMNS, dialect=csv.excel_tab, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(sorted(theList, key=outputSort))
    fout.close()

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    #combine
    fullList = []
    fullList += Upstream.load(r'..\data\jdrive_mp3s.txt')
    fullList += Upstream.load(r'..\data\zdrive_mp3s.txt')
    fullList += filter(lambda x: '.Trash' not in x['Full Path'], Upstream.load(r'..\data\yeimi_mp3s.txt'))

    # map fullList => {hash, [list of files]}
    groups = makeGroups(fullList)

    j = 0
    update = len(groups) / 20
    sys.stderr.write(' 1  2    5    7  9 |\n')
    sys.stderr.write('-0--5----0----5--0-|\n')
    
    for g in groups:
        j += 1
        if j > update:
            sys.stderr.write('#')
            sys.stderr.flush()
            j = 0
        
        enrich(g)  # add other columns to help with making decisions
        score(g)   # score the files with a group
        g['files'].sort(key=sortWithinGroup) # perform final sort

    # reduce => {hash, one file}
    keep = reduce_keep(groups)
    for k in keep:
        k['action'] = 'keep' if k['ufid'] == '' else 'use_jeff'

    # remainder of reduce operation
    toDelete = reduce_delete(groups)
    for d in toDelete:
        d['action'] = 'remove'

    save(keep + toDelete)




