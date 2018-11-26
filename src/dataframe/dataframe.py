import pandas as pd
import pickle

class df:
  
  '''
    create dataframe with given columnn names
    fromPickle: bool, if true make frame from pickle at fileLoc
    columns: array of column names
    fileLoc: string file location for dumps and restores
  '''
  def __init__(self, fromPickle, columns, fileLoc):
    self.fileLoc = fileLoc
    if fromPickle == True:
      self.frame = pd.read_pickle(fileLoc)
    else:
      self.frame = pd.DataFrame(columns=columns)


  '''
    return array of columns names
  '''
  def getColumnNames(self):
    return self.frame.columns.valuess

  
  '''
    push row data into df
    row: dict with keys that match frame column names
  '''
  def addRow(self, row):
    self.frame = self.frame.append(row, ignore_index=True)
    print(self.frame.head())

  
  '''
    change fileLoc
  '''
  def updateFileLoc(self, newFileLoc):
    self.fileLoc = newFileLoc

  
  '''
    dump frame to .pkl file at fileLoc location
  ''' 
  def dump(self):
    self.frame.to_pickle(self.fileLoc)




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

frame = df( fromPickle = False,
            columns = columns,
            fileLoc = fileLoc)

# build dict with positive intgers
row1 = {}
for i, col in enumerate(columns):
  row1[col] = i

# append row1 to frame
frame.addRow(row1)
print(frame.frame.head())

#build dict with negative integers
row2 = {}
for i, col in enumerate(columns):
  row2[col] = -i

#append row2 to frame and print
frame.addRow(row2)
print('frame:')
print(frame.frame.head())

#dump frame to file
frame.dump()

# clear frame
frame = None
print('frame:')
print(frame)

# load new frame from file
frame2 = df(  fromPickle = True,
              columns = None,
              fileLoc = fileLoc)

print('frame2:')
print(frame2.frame.head())