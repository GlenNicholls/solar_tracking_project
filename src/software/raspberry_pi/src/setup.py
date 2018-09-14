import sys
import os

# todo: expand function to add to $PYTHONPATH if it is not already there...
# having a long list like 'import module.package.something' is really inconvenient
def load_search_paths():
    print('-I- configuring system environment...')
    print('-I- the following have been added to the system path:')
    for i,j,y in os.walk(os.getcwd()):
        if(str(i).find('__pycache__') == -1 and str(i).find('.vscode') == -1):
            sys.path.append(i)
            print(i)


if __name__ == "__main__":
    load_search_paths()
