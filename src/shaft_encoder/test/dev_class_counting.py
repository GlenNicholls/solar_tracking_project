from class_counting_draft import Encoder

# Define pin numbers for a and b
se = Encoder(a_pin = 0, b_pin = 0, ppr = 2000)

# Separately rotate shaft and print degrees
while true:
    print se.get_count();
    print se.get_degrees();
    sleep(1)


