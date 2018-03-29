# MTV Checker
[![DOI](https://zenodo.org/badge/116037508.svg)](https://zenodo.org/badge/latestdoi/116037508)

## Getting started with MTV Checker

Inside the MTVchecker folder, follow the steps below.

### 1. Edit the config.conf file

* project: put the location of the source code
* managers: put the location where the Manager classes are defined
* mccabe_complexity:put mccabe's complexity number
* sql_complexity:put sql's complexity number

For example:
```
project:/Users/reniericorreia/workspace/my_app
managers:models
mccabe_complexity:10
sql_complexity:15
```
\* more than one place separated by semicolons

### 2. Run the main.py file
```
python main.py
```
Architectural code smells will be printed on the console
