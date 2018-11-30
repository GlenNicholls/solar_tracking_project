from utils import dataframe

columns = [ "time",
            "value",
            "note"]

fileLoc = './test.pkl'

frame = dataframe( columns = columns,
            file_location = fileLoc)

# build dict with positive intgers
row1 = {}
for i, col in enumerate(columns):
  row1[col] = i

# append row1 to frame
frame.append_row(row1)
print(row1)

#build dict with negative integers
row2 = {}
for i, col in enumerate(columns):
  row2[col] = -i

#append row2 to frame and print
frame.append_row(row2)
print('frame:')
print(frame._frame)

#dump frame to file
frame.dump()

# get newest entry
print('newest entry:\n{}'.format(frame.get_row()))
print('newest entry specific value:\n{}'.format(frame.get_row()["time"]))

# clear frame
frame = None
print('frame:')
print(frame)

# load new frame from file
frame2 = dataframe( columns = None,
              file_location = fileLoc)

print('raw frame2:')
print(frame2.get_keys())

