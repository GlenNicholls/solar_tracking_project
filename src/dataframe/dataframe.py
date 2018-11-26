import os
import logging
import pandas as pd
import pickle

class dataframe:
  
  '''
    create dataframe with given columnn names
    fromPickle: bool, if true make frame from pickle at fileLoc
    columns: array of column names
    fileLoc: string file location for dumps and restores
  '''
  def __init__(self, logger_name        = 'main_logger', 
                     logger_module_name = 'dataframe',
                     columns            = None, 
                     file_location      = ''
               ):
    self.logger = logging.getLogger(logger_name + '.' + logger_module_name)
    self.logger.info('creating an instance of the ' + __name__ + ' with the alias {}'.format(logger_module_name))

    self.pd = pd

    # dataframe
    self.column_names = columns
    if self.column_names == None:
      raise ValueError('Invalud column names, must be list of strings: [\'str1\', \'str2\',...]')
    self.df = self.pd.DataFrame(columns=columns)
    print('frame: {}'.format(self.df))

    # file location
    self.fileLoc = file_location
    if self.fileLoc == '':
      raise ValueError('Invalid file location, must be valid string')
    if os.path.isfile(self.fileLoc):
      self.pickle = self.pd.read_pickle(self.fileLoc)
    else:
      self.logger.warning('Pickle file location does not exist! Creating file now: {}'.format(self.fileLoc))
      self.df.to_pickle(self.fileLoc)
      self.pickle = self.pd.read_pickle(self.fileLoc)
    print('pickle: {}'.format(self.pickle))



  '''
    return array of columns names
  '''
  def get_keys(self):
    column_names = self.df.columns.values
    self.logger.debug('Column Names: {}'.format(column_names))
    return column_names

  
  '''
    push row data into df
    row: dict with keys that match frame column names
  '''
  def set_row(self, row):
    self.pickle = self.pickle.append(row, ignore_index=True)
    new_row = self.pickle.head()
    self.logger.debug('Added row: {}'.format(row))


  '''
    pop row data into df
    row: dict with keys that match frame column names
  '''
  def get_row(self, row=1):
    tail = self.pickle.tail(row)
    self.logger.info('Popped {} rows from the end: {}'.format(row, tail))
    return tail
    
  
  '''
    change fileLoc
  '''
  def set_file_location(self, newFileLoc):
    self.logger.debug('Changing pickle file location to: {}'.format(newFileLoc))
    self.fileLoc = newFileLoc
    self.pickle  = pd.read_pickle(self.fileLoc)

  
  '''
    dump frame to .pkl file at fileLoc location
  ''' 
  def dump(self):
    self.logger.debug('Dumping dataframe to: {}'.format(self.fileLoc))
    self.pickle.to_pickle(self.fileLoc)




###### Usage

columns = [ "time",
            "latitude",
            "longitude",
            "azimuth",
            "elevation",
            "panelVoltage",
            "batteryVoltage",
            "current",
            "power",
            "energy"]

fileLoc = './test.pkl'

frame = dataframe( columns = columns,
            file_location = fileLoc)

# build dict with positive intgers
row1 = {}
for i, col in enumerate(columns):
  row1[col] = i

# append row1 to frame
frame.set_row(row1)
print(row1)

#build dict with negative integers
row2 = {}
for i, col in enumerate(columns):
  row2[col] = -i

#append row2 to frame and print
frame.set_row(row2)
print('frame:')
print(frame.pickle)

#dump frame to file
frame.dump()

# get newest entry
tail = frame.get_row()
print('frame end:\n{}'.format(tail))

# clear frame
frame = None
print('frame:')
print(frame)


# # load new frame from file
# frame2 = dataframe( columns = None,
#               file_location = fileLoc)
# 
# print('frame2:')
# print(frame2.frame[-1])
# 
# print('raw frame2:')
# print(frame2.get_keys())
