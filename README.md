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
objects = fr.loads("classname:\nprop1:1\nprop2:123\n")
```
### Using autocast
By default all integers and floats are be parsed to coresponding types if possible. To disable this behavior use 'autoparse' argument:
```python
import framsreader as fr

input_string = "class:\n" \
               "int_prop: 1e5\n" \
                "float_porp: 123.3\n"\
               "str_prop: whatever"

print(fr.loads(input_string))
print(fr.loads(input_string, autocast=False))
```
Effect (note that int_prop and float prop are kept as strings for autocast=False:
```
[{'_classname': 'class', 'str_prop': 'whatever', 'int_prop': 100000.0, 'float_porp': 123.3}]
[{'_classname': 'class', 'str_prop': 'whatever', 'int_prop': '1e5', 'float_porp': '123.3'}]


```

### Using contexts:
By default, the context will be determined based on the file extension and read from [framscript.xml](https://github.com/ebonyclock/framsreader/blob/master/framsreader/framscript.xml). Additionally you can change context arbitrarily using 'context' argument:

```python
import framsreader as fr

input_string = "expdef:\n" \
               "name: 100\n"

print(fr.loads(input_string))
print(fr.loads(input_string, context="expdef file"))
```
Not that "name" field is parsed as a string because of the context.
```bash
[{'name': 100, '_classname': 'expdef'}]
[{'name': '100', '_classname': 'expdef'}]
```


