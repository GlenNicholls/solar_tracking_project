import os
import csv

def read_file(filename):
  if not os.path.exists(filename):
    raise ValueError('file {} does not exist'.format(filename))

  with open(filename, mode='r') as fp:
    file = csv.reader(fp)
  return(file)
  
def parse_gpio_file(filename)
  if not os.path.exists(filename):
    raise ValueError('file {} does not exist'.format(filename))
  line_num = 0
  
  with open(filename, mode='r') as fp
    for line in fp.readlines():
      if line_num == 0:
        pass
      elif line.startswith
  

read_file('gpio.csv')
