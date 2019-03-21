# MTV Checker
[![DOI](https://zenodo.org/badge/116037508.svg)](https://zenodo.org/badge/latestdoi/116037508)

## Getting started with MTV Checker

> IMPORTANT: This project was developed using python 2

>You can obtain the version from: [download](https://www.python.org/downloads/)

Also to run properly this project you need to have installed in your machine the following libraries from python: 

* Pandas
* Mccabe

Using `pip` command ( suggested ) you can install both by:

    pip install pandas
    pip install mccabe

For more details visit their documentation at [Pandas](https://pypi.org/project/pandas/) and [Mccabe](https://pypi.org/project/mccabe/)

##

### Inside the MTVchecker directory, follow the steps below:

### 1. Edit the config.conf file

* project: set the location of the source code
* managers: set the location where the Manager classes are defined
* mccabe_complexity: set mccabe's complexity number
* sql_complexity: set sql's complexity number

For example:

    project:/Users/reniericorreia/workspace/my_app
    managers:models
    mccabe_complexity:10
    sql_complexity:15

\* more than one value separated by semicolons

### 2. Run the manage.py file

    python manage.py

Architectural code smells will be printed on the console
