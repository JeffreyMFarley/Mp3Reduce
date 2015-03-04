import sys
import os
import win32com.client

#The ITTrackKindFile value will be use to check if a track is a physical file
ITTrackKindFile=1

class iTunesOnWindows():
    def __init__(self, asPosix=True):
        self.asPosix = asPosix
        self.itunes= win32com.client.Dispatch("iTunes.Application")
        self.library = self.itunes.LibraryPlaylist
        self.tracks = self.library.Tracks

    def scan(self, fileName=r'..\data\westeros_library.txt'):
        with open(fileName, "w", encoding='utf-8') as f:
          for i in range(1, self.tracks.Count): 
            track = self.tracks.Item(i)
            if track.Kind == ITTrackKindFile:
                location = track.Location
                if self.asPosix:
                    location = location.replace(r'C:\Users\jfarley.15T-5CG3332ZD5\Music\Amazon MP3', '/Volumes/Music/Jeff Music/Music')
                    location = location.replace('\\', '/')

                row = '\t'.join([track.Name, location, str(track.TrackDatabaseID)])
                f.write(row)
                f.write('\n')


#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    pipeline = iTunesOnWindows()
    pipeline.scan()


