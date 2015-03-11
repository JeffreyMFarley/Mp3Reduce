import sys
import os
import unicodedata
import win32com.client

#The ITTrackKindFile value will be use to check if a track is a physical file
ITTrackKindFile=1

class iTunesUpdateRow:
    def __init__(self, row):
        cells = row.strip().split('\t')
        self.title = unicodedata.normalize('NFKC', cells[0]) 
        self.oldPath = unicodedata.normalize('NFKC', cells[1])
        self.newPath = unicodedata.normalize('NFKC', cells[2])
        self.action = cells[3]
        self.idHigh = int(cells[4])
        self.idLow = int(cells[5])

class iTunesOnWindows():
    def __init__(self, asPosix=True):
        self.asPosix = asPosix
        self.itunes= win32com.client.Dispatch("iTunes.Application")
        self.library = self.itunes.LibraryPlaylist
        self.tracks = self.library.Tracks

    def toPosix(self, n):
        n = n.replace('J:', '/Volumes/Music')
        n = n.replace('\\', '/')
        return n

    def toWindows(self, n):
        n = n.replace('/Volumes/Music', 'J:')
        n = n.replace('/', '\\') 
        return n

    def scan(self, fileName=r'..\data\westeros_library.txt'):
        with open(fileName, "w", encoding='utf-8') as f:
          for i in range(1, self.tracks.Count): 
            track = self.tracks.Item(i)
            if track.Kind == ITTrackKindFile:
                location = track.Location
                if self.asPosix:
                    location = self.toPosix(location)

                highID = self.itunes.ITObjectPersistentIDHigh(track)
                lowID = self.itunes.ITObjectPersistentIDLow(track)
                row = '\t'.join([track.Name, location, str(highID), str(lowID)])
                f.write(row)
                f.write('\n')

    def update(self, fileName=r'..\data\westeros_library_update.txt'):
        with open(fileName, "r", encoding='utf-8') as f:
            for row in f:
                t = iTunesUpdateRow(row)
                if self.asPosix:
                    t.oldPath = self.toWindows(t.oldPath)
                    t.newPath = self.toWindows(t.newPath)

                track = self.tracks.ItemByPersistentID(t.idHigh, t.idLow)
                nloc = unicodedata.normalize('NFKC', track.location).lower()
                if nloc == t.oldPath.lower():
                    track.location = t.newPath
                else:
                    print('Not Found!', t.oldPath.encode(errors='ignore'))

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    pipeline = iTunesOnWindows()
    pipeline.update()


