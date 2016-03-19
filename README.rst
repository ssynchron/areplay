*****************************************************************
Apache Replay: Replay Apache log in real time.
*****************************************************************

Apache Replay is a command line tool that reads Apache log files and replays it on a remote server in real time. It's goal it's to load test HTTP/HTTPS servers with the same traffic that is received on another server.

This tool is written in Python and it uses `apache-log-parser <https://github.com/rory/apache-log-parser>`_, `requests <http://python-requests.org>`_ and `gevent <http://www.gevent.org/>`_  libraries.


=============
Main Features
=============

* Real time replay load testing
* Accept any Apache log format
* Support Basic Authentication
* URL match and ignore filters

============
Installation
============

On **Linux**, first install python development and libevent packages using system package manager:

.. code-block:: bash

    # Debian-based distributions (eg Ubuntu, ...):
    $ sudo apt-get install python-dev libevent-dev

    # RPM-based distributions:
    $ yum install python-devel libevent-* 


Then it can be installed from PyPi using `pip <http://www.pip-installer.org/en/latest/index.html>`_
:

.. code-block:: bash

    $ pip install areplay


===========
Basic usage
===========

.. code-block:: bash

    $ areplay http://test.example.com /var/log/apache2/access.log


Synopsis:

.. code-block:: bash

    $ areplay --help


    usage: areplay [-h] [-v] [-a AUTH] [-w WORKERS] [-m MATCH] [-i IGNORE]
                   [-d] [-f FORMAT] [-sv] [-iu IGNORE_URL]
                   server log_file

     positional arguments:

      server                      Remote Server
      log_file                    Apache log file path

     optional arguments:

       -h, --help                           Show this help message and exit
       -v, --version                        Show program's version number and exit
       -a AUTH, --auth AUTH                 Basic authentication user:password
       -w NUM, --workers NUM                Workers pool size
       -d, --dry-run                        Only prints URLs
       -f FORMAT, --format FORMAT           Apache log format
       -i IGNORE, --ignore IGNORE           Ignore matching requests
       -iu URL, --ignore-url URL            URL to hit when URL from log is ignored
       -m MATCH, --match MATCH              Only process matching requests
       -sv, --skip-verify                   Skip SSL certificate verify
       

========
Examples
========

**Basic auth:**

.. code-block:: bash

    $ areplay -a username:password http://test.example.com access.log


**URL filtering - ignore js and css** - use | (pipe) to separate keywords:

.. code-block:: bash

    $ areplay -i '.css|.js' http://test.example.com access.log


**URL filtering - process only js and css** - use | (pipe) to separate keywords:

.. code-block:: bash

    $ areplay -m '.css|.js' http://test.example.com access.log


**Custom Apache Log format** - get LogFormat for Apache configuration file:

.. code-block:: bash

    $ cat /etc/apache2/apache2.conf | grep LogFormat | grep combined
    LogFormat "%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"" combined

    $ areplay -f "%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"" http://test.example.com access.log


==========
Change Log
==========

Please see `CHANGELOG <https://github.com/ssynchron/areplay/blob/master/CHANGES.rst>`_.


=======
Licence
=======

Please see `LICENSE <https://github.com/ssynchron/areplay/blob/master/LICENSE>`_.

===============
Acknowledgments
===============

Thank you to the people from `Boom! <https://github.com/tarekziade/boom>`_ for inspiration and Dinko Korunic for snippet (`GeventTail <https://www.snip2code.com/Snippet/506288/Gevent-based-Tail-F-generator>`_).




