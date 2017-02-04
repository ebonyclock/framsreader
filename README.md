# Framsreader
Python3 file reader for [Framsticks](http://www.framsticks.com/)

## Installation:

### From [PyPI](https://pypi.python.org/pypi):
```bash
pip3 install framsreader
```
### From repository:
```bash
git clone https://github.com/ebonyclock/framsreader
cd framsreader
pip3 install .
```
or without clonging the repo:
```bash
pip3 install git+https://github.com/ebonyclock/framsreader

```
## Using without pip
Just copy/link framsreader subdirectory where you want to use the package e.g.
```bash
git clone https://github.com/ebonyclock/framsreader REPO_ROOT
cp -r REPO_ROOT/framsreader YOUR_PROJECT
```

## Sample usage:

```python
import framsreader as fr

# Parsing directly from a file
objects = fr.load("example_file.expdef")

# Parsing a string:
objects = fr.loads("<VALID_FRAMS_CONTENT_HERE>")
```

