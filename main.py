import sys

import omr

# Generating the answer key
akey = {}
for i in range(1, 121):
    akey[i] = chr(ord("A") + i % 4)

if sys.argv[1] == "gen-aruco":
    omr.generate_aruco(int(sys.argv[2]), sys.argv[3])
elif sys.argv[1] == "parse":
    omr.omr(sys.argv[3], sys.argv[2], "temp/", akey)
elif sys.argv[1] == "template":
    omr.template(sys.argv[2], sys.argv[3])
elif sys.argv[1] == "svg":
    omr.generate_qrcode(sys.argv[2], sys.argv[3])
