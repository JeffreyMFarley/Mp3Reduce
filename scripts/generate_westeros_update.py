import os
import sys
import unicodedata
import pyTagger
        

class GenerateWesterosUpdate():
    def __init__(self, 
                 imagesFileName=r'..\data\extract_images.txt', 
                 libraryUpdateFileName=r'..\data\westeros_library_update.txt'):
        self.imagesFileName = imagesFileName
        self.libraryUpdateFileName = libraryUpdateFileName

    def __str__(self):
        return "Generating Updates for Jeff's iTunes"

    def run(self, tracks):
        fImages = open(self.imagesFileName, 'w', encoding='utf-8', newline='')
        fUpdates = open(self.libraryUpdateFileName, 'w', encoding='utf-8', newline='')

        for k,v in sorted(tracks.items()):
            if self.predicate(v):
                fImages.writelines(k+'\n')
                title = v['title'] if 'title' in v else ''
                oldPath = unicodedata.normalize('NFKC', k)
                if v['strategy'] in ['B', 'C']:
                    newPath = unicodedata.normalize('NFKC', v['winner'])
                    action = 'update'
                else:
                    newPath = ''
                    action = 'delete'
                row = '\t'.join([title, oldPath, newPath, action, str(v['westeros_idh']), str(v['westeros_idl'])])
                fUpdates.writelines(row+'\n')

        fImages.close()
        fUpdates.close()

    @staticmethod
    def predicate(x):
        a0 = ('root' in x and x['root'] == 'Jeff'
              and 'keep' in x and not x['keep']
              and 'westeros_idh' in x and x['westeros_idh']
              and 'strategy' in x)
        a1 = a0 and x['strategy'] in ['B']
        a2 = a0 and (x['strategy'] == 'C'
                     and 'keepJeff' in x and x['keepJeff'] == 0
                     and 'keepJen' in x and x['keepJen'] > 0)
        return a1 or a2


#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    inFile = r'..\data\mp3s_enh.json'
    argc = len(sys.argv)
    if argc > 1:
        inFile = sys.argv[1]

    pipeline = [GenerateWesterosUpdate()]

    # Load the scanned list of tracks & enrich
    snapshot = pyTagger.Mp3Snapshot(True)
    tracks = snapshot.load(inFile)
    for operation in pipeline:
        print(operation)
        operation.run(tracks)
