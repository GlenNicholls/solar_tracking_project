from utils import dataframe

columns = [ "value",
            "note",
            "time",]

dict_dat = dict.fromkeys(columns)
print('init dictionary data: {}'.format(dict_dat))

fileLoc = './test.pkl'

# create frame
frame = dataframe( columns = columns,
            file_location = fileLoc)

# build dict with positive intgers
i = 0
for key, val in dict_dat.items():
  dict_dat[key] = i
  i += 1

# append row1 to frame
frame.append_row(dict_dat)
print('frame:')
print(frame._frame)

#build dict with negative integers
for key, val in dict_dat.items():
  dict_dat[key] = -i
  i += 1

#append row2 to frame and print
frame.append_row(dict_dat)
print('frame:')
print(frame._frame)

#dump frame to file
frame.dump_pickle()

# get newest entry
print('newest entry:\n{}'.format(frame.get_row()))
print('newest entry info:\n{}'.format(frame.get_row()['time']))
print('newest entry value:\n{}'.format(frame.get_row().iloc[0]['time']))
print('newest entry value type:\n{}'.format(type(frame.get_row().iloc[0]['time'])))

# clear frame
frame = None
print('frame:')
print(frame)

# load new frame from file
frame2 = dataframe( columns = None,
              file_location = fileLoc)

print('raw frame2:')
print(frame2.get_keys())

