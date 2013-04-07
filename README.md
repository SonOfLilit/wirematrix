Wirematrix is a matrix screensaver that shows encoded packets captured
from the local network interface. This is extremely cool and with
time, the user learns to "see the matrix" in the encoded stream.

Installation
============

This rough version is a little hard to install. This probably runs
only on linux. You will need:

pyopengl

py2cairo (must be installed manually. To install into virtualenv see
here:
http://stackoverflow.com/questions/11491268/install-pycairo-in-virtualenv)

pyhack (http://www.liquidx.net/pyhack/)

libpcap

pypcap (current version in pypi needs a bit of manual intervention to
get it to build: change `_pcap_config(` to `pcap_config(` in setup.py)


Running
=======

I still didn't figure out how to use `setcap` to allow this to run as
non-root, so for now it must run as root. Soon, soon...

TODO
====

* Make it look more like The Matrix, as seen here:
http://www.endlessvideo.com/watch?v=Or2m7rYHb_Q&start=0m31s&end=0m36s

* Figure out how to run as non-root

* Write instructions on setting this as the screensaver

* Port to Windows for all my friends
