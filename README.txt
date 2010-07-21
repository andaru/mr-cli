Mr. CLI
=======

A Multi Router Command-Line Interface
--------------------------------------
Mr. CLI presents a command-line interface similar to network equipment
operators are familiar with, giving them access to all of the
equipment known by Notch Agents (see http://www.enemesco.net/notch/index.html)

When a command is executed, the individual commands are submitted to
all targetted devices in parallel, making for a powerful diagnostic
tool for planned events as well as diagnosis during break fix.

It can be used in both command-line mode::

  $ mrcli localhost:8080 -t "^[abc].*" -c "sh int desc | i PO"
  ar1.mel:
  PO5/0                  admin down     down     
  PO6/0                  admin down     down     

  cr1.mel:
  PO3/0                  up             up       
  PO4/0                  admin down     down     
  PO5/0                  admin down     down     
  PO6/0                  admin down     down     

..and interactive mode::

  $ mrcli localhost:8080
  Welcome to Mr. CLI.  Type 'help' if you need it.
  mr.cli [t: 0] > targets ^[ab].*
  Targets changed to: ar1.mel, br1.mel
  mr.cli [t: 2] > cmd show ver | i IOS
  ar1.mel:
  IOS (tm) 7200 Software (C7200-K4P-M), Version 12.0(33)S6, RELEASE SOFTWARE (fc1)

  br1.mel:
  IOS (tm) 7200 Software (C7200-K4P-M), Version 12.0(33)S6, RELEASE SOFTWARE (fc1)

Changelog
---------

Version 0.2: 2010-07-21
^^^^^^^^^^^^^^^^^^^^^^^

  * ``mrcli/mrcli.py``: Add documentation note.  [0ec1a5dded46] [tip]
  * ``mrcli/mrcli.py``: Correct misterminated error message.  [a69a6da59a7f]
  * ``mrcli/mrcli.py``: Can use netmunge router output munging library if available. To use, switch output mode to 'csv'.

