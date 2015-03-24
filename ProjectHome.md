# Mr. CLI #


Mr. CLI is a network command-line interface that allows you to address your commands to many devices simultaneously.  It's a client of the [Notch system](http://code.google.com/p/notch), using the distributed network of Notch Agents to communicate with the devices.

## New features! ##
  * CSV output mode. Use `output csv` command to change to this mode (requires the `netmunge` module to be installed, see the [Netmunge](http://code.google.com/p/netmunge) page for more info. Only a limited number of commands is supported, so far, but text output from any vendor can be parsed.

## Features ##
  * Send commands to many routers.
  * Use regular expressions to name devices.
  * Authentication handled by Notch (no authentication required of the client).

## Installation ##

Use ```easy_install``` or ``pip`` to install Mr. CLI;

```
$ pip install mrcli
```

## Example usage ##

If you're running a Notch [Agent](http://www.enemesco.net/notch/agent.html) at `localhost:8080`, you start Mr. CLI like this:

```
$ mrcli localhost:8080
Welcome to Mr. CLI.  Type 'help' if you want it.

mr.cli [t: 0] > targets
There are no targets.
mr.cli [t: 0] > targ ^[abc]r.*
Targets changed to: ar1.mel, br1.mel, cr1.bne, cr1.mel, cr1.syd, cr2.bne, cr2.mel, cr2.syd
mr.cli [t: 8] > cmd show version | i IOS
ar1.mel:
IOS (tm) 7200 Software (C7200-K4P-M), Version 12.0(33)S6, RELEASE SOFTWARE (fc1)

cr1.bne:
IOS (tm) 7200 Software (C7200-K4P-M), Version 12.0(33)S6, RELEASE SOFTWARE (fc1)

cr2.syd:
IOS (tm) 7200 Software (C7200-K4P-M), Version 12.0(33)S6, RELEASE SOFTWARE (fc1)

cr2.bne:
IOS (tm) 7200 Software (C7200-K4P-M), Version 12.0(33)S6, RELEASE SOFTWARE (fc1)

cr2.mel:
IOS (tm) 7200 Software (C7200-K4P-M), Version 12.0(33)S6, RELEASE SOFTWARE (fc1)

cr1.syd:
IOS (tm) 7200 Software (C7200-K4P-M), Version 12.0(33)S6, RELEASE SOFTWARE (fc1)

cr1.mel:
IOS (tm) 7200 Software (C7200-K4P-M), Version 12.0(33)S6, RELEASE SOFTWARE (fc1)

br1.mel:
IOS (tm) 7200 Software (C7200-K4P-M), Version 12.0(33)S6, RELEASE SOFTWARE (fc1)

mr.cli [t: 8] > c sh arp | e Addr
cr1.bne:
Internet  192.168.0.14            -   ca26.624e.001c  ARPA        GigabitEthernet1/0
Internet  192.168.0.15           82   ca25.624c.001c  ARPA        GigabitEthernet1/0

ar1.mel:
Internet  10.255.0.253            -   ca22.6247.0008  ARPA        GigabitEthernet0/0
Internet  10.255.0.254            9   c624.c542.a9b2  ARPA        GigabitEthernet0/0
Internet  192.168.0.0            83   ca23.6249.001c  ARPA        GigabitEthernet1/0
Internet  192.168.0.1             -   ca22.6247.001c  ARPA        GigabitEthernet1/0

cr1.mel:
Internet  192.168.0.0             -   ca23.6249.001c  ARPA        GigabitEthernet1/0
Internet  192.168.0.1            83   ca22.6247.001c  ARPA        GigabitEthernet1/0

cr2.syd:


cr2.bne:
Internet  192.168.0.14           82   ca26.624e.001c  ARPA        GigabitEthernet1/0
Internet  192.168.0.15            -   ca25.624c.001c  ARPA        GigabitEthernet1/0

cr2.mel:
Internet  192.168.0.4             -   ca27.624f.001c  ARPA        GigabitEthernet1/0
Internet  192.168.0.5            82   ca20.6243.001c  ARPA        GigabitEthernet1/0

cr1.syd:


br1.mel:
Internet  192.168.0.4            82   ca27.624f.001c  ARPA        GigabitEthernet1/0
Internet  192.168.0.5             -   ca20.6243.001c  ARPA        GigabitEthernet1/0

mr.cli [t: 8] > 
```