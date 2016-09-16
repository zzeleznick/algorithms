"""
Fix path at runtime to allow for TimeUtils
"""

import sys
import os

FILENAME = "TimeUtils.py"
cur = os.getcwd()
parent = os.pardir

if FILENAME in os.listdir(cur):
     sys.path.append(cur)
elif FILENAME in os.listdir(parent):
     sys.path.append(parent)
