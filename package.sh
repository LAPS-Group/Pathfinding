#!/bin/sh

# Clear build
rm -rf build || echo "Build dir already rip"

#Copy all the root python files to the build folder
echo "Copying root files..."
mkdir -p build
cp *.py build

# Loader.py only has side effects and is only needed for loading .ipynb files.
# Instead just load them directly and throw away the second part of the path.
echo "Making fake loader.py..."
echo "
import types, sys

class Loader(object):
  def __init__(self, path=None):
    pass

  def load_module(self, fullname):
    path = fullname[0:fullname.find(\".\")]
    mod = types.moduleType(fullname)
    mod.__file__ = path
    mod.__loader__ = self
    sys.modules[fullname] = mod

    return mod
" > build/loader.py

# Convert Dijkstra module stuff
## Find the files
echo "Packaging Dijkstra module..."
files=$(find Dijkstra -iname '*.ipynb')
mkdir -p build/Dijkstra
## Convert into .py and copy into the correct folder
jupyter nbconvert --to script $files
mv Dijkstra/*.py build/Dijkstra

## build the docker image for Dijkstra
docker build -t dijkstra -f Dijkstra/Dockerfile .
