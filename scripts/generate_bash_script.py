import sys
import execution_plan as Upstream

RECYCLE_PATH = r'/Volumes/Music/recycle/'

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------
class BashScriptGenerator:
    def __init__(self):
        self.plan = Upstream.ExecutionPlan()
    
    def generateDelete(self, targetStrategies, fileName='delete.sh'):
        self.targetStrategies = targetStrategies

        print('Generating',fileName)
        with open(fileName, 'w', encoding='utf-8', newline='') as fout:
            fout.writelines('#!/bin/bash\n\n')
            for row in filter(self.predicate, self.plan.iter_load()):
                fout.writelines('mv -f "'+row[Upstream.KEY]+'" "'+RECYCLE_PATH+row['file']+'"\n')
    
    def generateMove(self, targetStrategies, fileName='move.sh'):
        self.targetStrategies = targetStrategies

        print('Generating',fileName)
        with open(fileName, 'w', encoding='utf-8', newline='') as fout:
            fout.writelines('#!/bin/bash\n\n')
            for row in filter(self.predicate, self.plan.iter_load()):
                fout.writelines('mv -f "'+row[Upstream.KEY]+'" "'+row['newPath']+'"\n')

    def generateCopy(self, targetStrategies, fileName='copy.sh'):
        self.targetStrategies = targetStrategies

        print('Generating',fileName)
        with open(fileName, 'w', encoding='utf-8', newline='') as fout:
            fout.writelines('#!/bin/bash\n\n')
            for row in filter(self.predicate, self.plan.iter_load()):
                fout.writelines('cp -f "'+row[Upstream.KEY]+'" "'+row['newPath']+'"\n')

    def predicate(self, x):
        return x['strategy'] in self.targetStrategies
        
#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

def main():
    pipeline = BashScriptGenerator()
    pipeline.generateDelete(['E', 'G'], r'J:\step1_delete.sh')
    pipeline.generateMove(['C', 'K'], r'J:\step1_move.sh')
    pipeline.generateCopy(['D'], r'J:\step1_copy.sh')
    pipeline.generateDelete(['D', 'F', 'H'], r'J:\step2_delete.sh') 
    
if __name__ == '__main__':
    main()



