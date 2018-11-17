import os
import itertools

  
def parse_gpio_file(filename):
  if not os.path.exists(filename):
    raise ValueError('file {} does not exist in {}'.format(filename, os.getcwd()))
  
  line_num  = 0
  dict_keys = []
  dict_vals = []
  with open(filename, mode='r') as fp:
    lines = (line.rstrip() for line in fp)
    lines = [line for line in lines if line]
    for line in lines:
      #print(line)
      if line.startswith('#'):
        pass
      elif line_num == 0:
        dict_keys.append( line.strip(',') )
      else:
        dict_vals.append( [x.lstrip() for x in line.split(',')] )
      line_num += 1
  print(dict_keys)
  print(dict_vals)
  

parse_gpio_file('gpio.csv')
