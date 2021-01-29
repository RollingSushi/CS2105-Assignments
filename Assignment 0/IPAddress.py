import sys

IPinput = str(sys.argv[1])  # Script name is argv[0] so take argv[1]
# Split string from index 0 to 7 (does not inlude 8)
first8 = int(IPinput[0:8], 2)
# convert to binary, base 2 useing int's second argument)
second8 = int(IPinput[8:16], 2)
third8 = int(IPinput[16:24], 2)
fourth8 = int(IPinput[24:32], 2)

# print string using f literals
print(f"{first8}.{second8}.{third8}.{fourth8}")
