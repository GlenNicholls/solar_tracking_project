import sys
import os
import argparse

# todo: expand function to add to $PYTHONPATH if it is not already there...
# having a long list like 'import module.package.something' is really inconvenient
class PythonFileTreeMaker(object):
    def _recurse_search_paths(self):
        print('-I- parsing file tree to add unknown python directories to the $PYTHONPATH')

        added_dir_buf = []

        for dir_path,sub_dirs,file_list in os.walk(os.getcwd()):
            if self._verbose:
                print('-I- the following files have been found in {}'.format(dir_path))
                for i,file in enumerate(file_list):
                    print('\t' + file)

                print('-I- the following subdirectories have been found in {}'.format(dir_path))
                for i,sub_dir in enumerate(sub_dirs):
                    print('\t' + sub_dir)

            if str(dir_path).find('__pycache__') == -1 and str(file_list).find('__init__.py') > -1:
                sys.path.append(dir_path)
                added_dir_buf.append(dir_path)
        print('-I- the following directories have been added to the system path:')
        for i,j in enumerate(added_dir_buf):
            print('\t' + j)

    def make(self, args):
        self._verbose = args.verbose
        if self._verbose:
            print('-I- parsing file tree with verbose opton')
        #self._output = args.output
        #print("root:%s" % self.root)

        self._recurse_search_paths()

        #buf = []
        #path_parts = self.root.rsplit(os.path.sep, 1)
        #buf.append("[%s]" % (path_parts[-1],))
        #self._recurse(self.root, os.listdir(self.root), "", buf, 0)
        #
        #output_str = "\n".join(buf)
        #if len(args.output) != 0:
        #    with open(self._output, 'w') as of:
        #        of.write(output_str)
        #return output_str

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="verbose option", action="store_true")
    #parser.add_argument("-o", "--output", help="output file name", default="")
    args = parser.parse_args()

    PythonFileTreeMaker().make(args)
