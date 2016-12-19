import os
from PyQt5.QtCore import Qt

try:
    HOMEDIR = os.environ['HOME']
    APPDIR = HOMEDIR + "/.imotion"
except KeyError:
    HOMEDIR = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    APPDIR = HOMEDIR + "\\.imotion"

DEBUG = True

APPNAME = "I-Motion IM Client"
VERSION = "1.0.1"
TRUNK = "Alpha"

KEYENTER = [Qt.Key_Enter, Qt.Key_Return]

# IRC Colors
# Value 	   Name 	      RGB 	           HTML
# 0 	       White 	      255,255,255 	   #FFFFFF
# 1 	       Black 	      0,0,0 	       #000000
# 2 	       Navy 	      0,0,127 	       #00007F
# 3 	       Green 	      0,147,0 	       #009300
# 4 	       Red 	          255,0,0 	       #FF0000
# 5 	       Maroon 	      127,0,0 	       #7F0000
# 6 	       Purple 	      156,0,156 	   #9C009C
# 7 	       Olive 	      252,127,0 	   #FC7F00
# 8 	       Yellow 	      255,255,0 	   #FFFF00
# 9 	       Light Green 	  0,252,0 	       #00FC00
# 10 	       Teal 	      0,147,147 	   #009393
# 11 	       Cyan 	      0,255,255 	   #00FFFF
# 12 	       Royal blue 	  0,0,252 	       #0000FC
# 13 	       Magenta 	      255,0,255 	   #FF00FF
# 14 	       Gray 	      127,127,127 	   #7F7F7F
# 15 	       Light Gray 	  210,210,210 	   #D2D2D2
COLORS = ["#FFFFFF", "#000000", "#00007F", "#009300",
          "#FF0000", "#7F0000", "#9C009C", "#FC7F00", "#FFFF00", "#00FC00", "#009393", "#00FFFF", "#0000FC", "#FF00FF", "#7F7F7F", "#D2D2D2"]
