#  vim: set ts=4 sw=4 tw=0 et ft=python :
import os
import sys

'''
Update the system path to include your testing application directory
'''
from app.MainWindowControl import start

print()
msg = 'Hello from %s'%(os.path.abspath(__file__))
print(msg)
print()

print("SystemPaths:")
for path in sys.path:
    print('>', path)

#os.MessageBox(msg)

# Enter Point
if __name__ == "__main__":
    start()
    # test/cmd style

