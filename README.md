# 1Point3Acres Admission Data Crawler
=======================================================
1Point3Acres Admission Data Crawler is used for collecting admission report data on 1Point3Acres BBS. Requests+BeautifulSoup4+MongoDB make up the initial data crawler. Through parsing HTML content of each page of admission report cards on 1Point3Acres, we can obtain the historical data of Chinese students' applications to graduate programs in U.S. The data can be printed out onto terminal or stored in the MongoDB for record purposes. In the future, the data crawler will provide more detailed data and support more options.

## How to run data crawler
You need a Python environment and packages listed in `requirements.txt` to run the data crawler.

You can use a virtualenv, for example:

    virtualenv --system-site-packages ~/pyvenv
    . ~/pyvenv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

To run data crawler, you can use Python to execute the command line tool.

    python crawler.py

Also, you can utilize supported options to satisfy your specific requirement like following examples.

    python crawler.py --start=1 --end=5 --total=100 --store --output
    python crawler.py --admitted-major=CS --degree=MS --output
    python crawler.py --version
    python crawler.py --help

### Options & arguments
There are some options and arguments available for the data crawler.
  - `-h`, `--help` - show this help message and exit.
  - `-v`, `--version` - show program's version number and exit.
  - `--start START` - The first page number to be achieved.
  - `--end END` - The last page number to be achieved.
  - `--total TOTAL` - The total number of admission cards to be achieved.
  - `--collection-name` - The name of MongoDB collection to be stored.
  - `--admitted-major` - only achieve admission data with the specified admitted major. e.g. CS, EE, EECS.
  - `--degree` - only achieve admission data with the specified degree. e.g. MS, PHD.
  - `-s`, `--store` - store admission data into MongoDB.
  - `-o`, `--output` - print out admission data into stdout.