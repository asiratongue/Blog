import os

for root, dirs, files in os.walk(r'G:\\01101000111101\\Programming\\Projects\\Backend Projects\\Personal Blog\\articles'):
    print(f"Root: {root}, Files: {files}")