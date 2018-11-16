import os
import csv

def read_file_dict(filename):
  if not os.path.exists(filename):
    raise ValueError('file {} does not exist'.format(filename))

  with open(filename, mode='r') as fp:
    file = csv.DictReader(fp)
    #for line in file:
        #print(line)
  print(file)

read_file_dict('gpio.csv')
