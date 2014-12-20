# -*- coding: utf-8 -*

from __future__ import print_function
import csv
import os
import sys
import codecs
if sys.version < '3':
    import eyed3
    from eyed3 import main, id3, core
import binascii
import hashlib

COLUMNS = ['Track','Title','Album','Artist','Full Path','Drive','Directory','Root','Subdir','File','Hash','DJTagger','Bit Rate','VBR']
KEY = 'Full Path'

def splitPath(fullPath):
    drive, path = os.path.splitdrive(fullPath)
    path, filename = os.path.split(path)
    
    result = {'Full Path': fullPath, 'Drive': drive, 'Directory': os.path.join(drive, path), 'File': filename}
    
    dirSplit = path.split(os.sep)
    if len(dirSplit) > 2:
        lastTwoSubdir = dirSplit[-2:]
        headSubdir = dirSplit[:len(dirSplit) - 2]

        result['Root'] = os.sep.join(headSubdir)
        result['Subdir'] = os.sep.join(lastTwoSubdir)

    return result

def extractID3(fullPath):
    try:
        track = eyed3.load(fullPath)
    except IOError:
        print('Cannot Load', fullPath, file=sys.stderr)
        return {}
        
    if track.tag is None:
        track.tag = eyed3.id3.Tag()
        track.tag.file_info = eyed3.id3.FileInfo(fullPath)

    ufid = ''
    for a0 in track.tag.unique_file_ids:
        ufid += binascii.b2a_hex(a0.uniq_id).upper()

    vbr = False
    bitRate = 0
    if track.info != None:
        vbr, bitRate = track.info.bit_rate

    return {'Track': str(track.tag.track_num[0]), 'Title': track.tag.title, \
            'Album': track.tag.album, 'Artist': track.tag.artist, 'DJTagger': str.strip(ufid), \
            'Bit Rate': str(bitRate), 'VBR': str(vbr) }

def calculateHash(fullPath):
    chunk_size = 1024

    shaAccum = hashlib.sha1()
    try:
        with open(fullPath, "rb") as f:
            byte = f.read(chunk_size)
            while byte:
                shaAccum.update(byte)
                byte = f.read(chunk_size)
        f.close()
    except IOError:
        print('Cannot Load', fullPath, file=sys.stderr)
        return ''

    return binascii.b2a_base64(shaAccum.digest());

def writeHeader(f):
    for header in COLUMNS:
        f.write(header)
        f.write('\t')
    f.write(os.linesep)

def writeRow(f, row):
    for header in COLUMNS:
        if header in row:
            safeWrite(f, row[header])
        else:
            f.write('')
        f.write('\t')
    f.write(os.linesep)
    f.flush()

def safeWrite(f, s):
    if s == None:
        f.write('')
    else:
        try:
            f.write(s)
        except UnicodeDecodeError:
            f.write('')
            print('bad char', s, file=sys.stderr)

def scan(f, path):
   for currentDir, subdirs, files in os.walk(path):
        # Get the absolute path of the currentDir parameter
        currentDir = os.path.abspath(currentDir)
     
        # Traverse through all files
        for fileName in files:
            curFile = os.path.join(currentDir, fileName)
            curFile = curFile.decode(sys.getfilesystemencoding())

            fileExtension = curFile[-3:]           

            # Check if the file has an extension of typical music files
            if fileExtension in ['mp3']:
                try:
                    print("Processing", curFile)
                
                    x = splitPath(curFile)
                    y = extractID3(curFile)

                    info = dict(x.items() + y.items())
                    info['Hash'] = str.strip(calculateHash(curFile))
                
                    writeRow(f, info)
                except Exception as ex:
                    print(ex, file=sys.stderr)

def load(dataSetFileName):
    result = []
    f = codecs.open(dataSetFileName, 'rU', encoding='utf-8')
    result = list(csv.DictReader(f, dialect=csv.excel_tab))
    f.close()
    return result

# debugging
#sys.argv = [sys.argv[0], u'J:\\Jennifer Music\\Arcade Fire']

if __name__ == '__main__':
    retval = 1

    path = os.getcwd()
    outFileName = 'mp3s.txt'
    
    argc = len(sys.argv)
    if argc > 2:
        outFileName = sys.argv[2]
    if argc > 1:
        path = sys.argv[1]

    try:
        fout = codecs.open(outFileName, 'w', encoding='utf-8')
        #fout = sys.stdout

        writeHeader(fout)
        scan(fout, path)
    except KeyboardInterrupt:
        retval = 0
    except Exception as ex:
       print(ex, file=sys.stderr)
    finally:
        fout.close()
        sys.exit(retval)
