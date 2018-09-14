import sys
import os

def LoadSearchPaths():
    print('-I- configuring system environment...')
    for i,j,y in os.walk(os.getcwd()):
        if(str(i).find('__pycache__') == -1 and str(i).find('.vscode') == -1):
            sys.path.append(i)
    print('-I- the following have been added to the system path:')
    print(sys.path)
