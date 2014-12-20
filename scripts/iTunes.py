import plistlib
import sys
import urllib.parse as urlEscaper
import unicodedata

TRACK_COLUMNS = ['Bit Rate', 'Play Date', 'Sort Album', 'Normalization', \
                    'Play Count', 'Genre', 'Album', 'Grouping', 'Sort Artist', \
                    'Album Artist', 'Rating', 'Size', 'File Folder Count',
                    'Track ID', 'Total Time', 'BPM', 'Year', \
                    'Library Folder Count', 'Sample Rate', 'Album Rating', \
                    'Album Rating Computed', 'Artist', 'Date Added', 'Kind', \
                    'Play Date UTC', 'Track Type', 'Date Modified', 'Comments', \
                    'Artwork Count', 'Track Number', 'Persistent ID', 'Location', \
                    'Composer', 'Name']
PLAYLIST_COLUMNS = ['Master', 'Playlist ID', 'Playlist Persistent ID', 'All Items', \
                    'Visible', 'Name', 'Playlist Items']

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------
class Library:
    def __init__(self, libraryPath, trackProjectionColumns=TRACK_COLUMNS):
        self.libraryPath = libraryPath
        self.trackProjectionColumns = trackProjectionColumns
        self._root = None

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        self._root = value

    def trackIterator(self):
        self.root = plistlib.readPlist(self.libraryPath)
        tracks = self.root['Tracks']
        for track_id in tracks:
            yield self.trackProjection(tracks[track_id])
            
    def playlistIterator(self):
        for x in l:
            name = x['Name']
            tracks = x['Playlist Items'] if 'Playlist Items' in x else []
            for t in tracks:
                yield {'Playlist':name, 'Track ID': t['Track ID']}

    def trackProjection(self, x):
        result = {}
        for i, key in enumerate(self.trackProjectionColumns):
            try:
                value = x[key]
                if isinstance(value, str):
                    result[key] = unicodedata.normalize('NFC',x[key])
                else:
                    result[key] = value
            except KeyError:
                result[key] = None

        return result

    def decodeFileLocation(self, f):
        f = urlEscaper.unquote(f)
        f = f.replace('file://localhost', '')
        # normalize here because the 'unquote' operation above may have uncovered different code-points
        return unicodedata.normalize('NFC',f) 

    def encodeFileLocation(self, f):
        return 'file://localhost' + urlEscaper.quote(f)
    
# flatten the playlist hierarchy
# print('Loading the playlists')
# plist_playlists = library['Playlists']
# playlists = list(playlistIterator(plist_playlists))

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

def debugging():
    library = Library(r'..\data\yeimi_library.xml')
    for t in library.trackIterator():
        print(t)
    
if __name__ == '__main__':
    print('this is intended to be used as a helper class and not a free-executing script')
