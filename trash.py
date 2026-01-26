import os
root_dir = "./"

for root,dirs,files in os.walk(root_dir):
    for file in files:
        print(file)
        if file.endswith("Identifier"):
            path = os.path.join(root,file)
            os.remove(path)