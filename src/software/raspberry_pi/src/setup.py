import sys
import os
import argparse

# todo: expand function to add to $PYTHONPATH if it is not already there...
# having a long list like 'import module.package.something' is really inconvenient
class PythonFileTreeMaker(object):
    def _recurse_search_paths(self):
        start_path =  os.getcwd()
        added_dir_buf = []

        print('-I- parsing file tree to add unknown python directories to the $PYTHONPATH')
        print('-I starting in: {}'.format(start_path))

        for dir_path,sub_dirs,file_list in os.walk(start_path):
            if str(dir_path).find('__pycache__') == -1 and str(file_list).find('__init__.py') > -1:
                sys.path.append(dir_path)
                added_dir_buf.append(dir_path)
            # print file tree
            if self._verbose:
                level = dir_path.replace(start_path, '').count(os.sep)
                indent = ' ' * 4 * (level)
                subindent = ' ' * 4 * (level + 1)
                if len( str(os.path.basename(dir_path)) ) > 2:
                    print('{}{}/'.format(indent, os.path.basename(dir_path)))
                    for f in file_list:
                        print('{}{}'.format(subindent, f))

        print('-I- the following directories have been added to the system path:')
        for i,j in enumerate(added_dir_buf):
            print('\t' + j)

    def make(self, args):
        self._verbose = args.verbose
        if self._verbose:
            print('-I- parsing file tree with verbose opton')

        self._recurse_search_paths()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="verbose option", action="store_true")
    #parser.add_argument("-o", "--output", help="output file name", default="")
    args = parser.parse_args()

    PythonFileTreeMaker().make(args)
