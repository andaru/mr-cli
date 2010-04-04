#!/usr/bin/env python
#
# Copyright 2010 Andrew Fort. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Mr. CLI: A Multi Router Command-Line Interface.

Mr. CLI presents a command-line interface similar to network equipment
operators are familiar with, giving them access to all of the
equipment known by the Notch Agents.

When a command is executed, the individual commands are submitted to
all targetted devices in parallel, making for a powerful diagnostic
tool for planned events as well as diagnosis during break fix.
"""


import optparse
import os
import re
import sys

import notch.client

import cmdline


class MisterCLI(cmdline.CLI):
    """MR. CLI.  The multi-router interface."""

    CMD = 'cmd'
    HELP_INTRODUCTION = 'Mr. CLI command-line interface help.'
    PREFIX = 'mr.cli'
    PROMPT = '%s [t: 0] > ' % PREFIX

    def __init__(self, notch, completekey='tab', stdin=None, stdout=None,
                 menu=None, targets=None):
        menu = {r'exit': 'do_exit',
                r'quit': 'do_exit',
                r'help': 'do_help',
                cmdline.EOF_SENTINEL: 'do_exit',
                r'counters': 'do_counters',
                self.CMD: 'do_command',
                r'targets': 'do_targets',
                r'timeout': 'do_timeout',
                r'matches': 'do_matches',
                }
        super(MisterCLI, self).__init__(menu, completekey=completekey,
                                        stdin=stdin, stdout=stdout)
        
        self.notch = notch
        self.targets = []
        if targets:
            for t in targets:
                if t.startswith('^'):
                    self.targets.extend(
                        self._complete_targets([t], only_regexp=True))
                else:
                    self.targets.append(t)
        self.timeout = 90.0

    def default(self, line):
        self.stdout.write('Error: Unknown command: %s. Try "help".\n' % line)

    def do_command(self, line):
        """Executes a command on all targets.

          > cmd show version | i IOS

          > cmd show int desc | i up.*up
        """
        line = ' '.join(line.split()[1:])
        self._execute_command(line)

    def do_counters(self, _):
        """Displays the Notch request counters.

        Example output:

        > counters
        Notch Transport Counters
        [Requests]  total: 97        ok: 97        error: 0        
        [Responses] total: 97        ok: 85        error: 12        data: 1.2 MB

        ------------------------------------------------------------------------

        [Requests] counters refer to the number of requests that were
                   sent (ok), did not leave the client (error).

        [Responses] counters refer to the number of requests that
                    returned a response from an Agent, either without
                    (ok) or with an error (error). Data refers to the
                    volume of (result) responses received.
        """
        self.stdout.write(str(self.notch.counters)+'\n')

    def do_exit(self, _):
        """Exits Mr. CLI."""
        return True

    def do_matches(self, line):
        """Displays devices on the agent matching a regexp.

        Supply a regular expression to use to match device names returned
        on the Notch Agent.

        All regexes are automatically anchored to the beginning of the line.

        > matches ^ar1.*
        Matching device names (1): ar1.mel

        > matches ar1.*
        Matching device names (1): ar1.mel
        """
        arg = line.split()
        if not arg or len(arg) == 1:
            return
        else:
            try:
                targets = self._get_targets(line, only_regexp=True)
            except NoDevicesMatching, e:
                self.stdout.write('Targets could not be retrieved.')
            else:
                if targets:
                    self.stdout.write('Matching device names (%d): %s\n'
                                      % (len(targets), str(', '.join(targets))))
                else:
                    self.stdout.write('No targets matched your query.\n')

    def do_notallowed(self, line):
        """This command is disallowed."""
        # To be used to specifically disable commands from being used.
        self.stdout.write('*** The command %r is disallowed.' % line)
        self.stdout.write('\n\n')

    def emptyline(self):
        pass

    def _get_targets(self, line, only_regexp=False):
        arg = line.split()
        if not arg or len(arg) == 1:
            if not self.targets:
                self.stdout.write('There are no targets.\n')
            else:
                self.stdout.write('Current targets [%d]: %s\n'
                                  % (len(self.targets), self._targets_str()))
        else:
            return self._complete_targets(self._parse_targets(line),
                                          only_regexp=only_regexp)

    def do_targets(self, line):
        """Displays or sets the list of target devices commands go to.

        To display the current targets, supply no arguments.

        You can use regular expressions in your target
        list, in which case you must prefix them with ^ to identify
        them as such.

          > targets ^ar1.*
          Targets changed to: ar1.mel

          > targets br1.mel,cr2.syd
          Targets changed to: br1.mel, cr2.syd

          > targets
          Current targets [2]: br1.mel, cr2.syd

        """
        targets = self._get_targets(line)
        if targets is not None:
            self.targets = targets
            self.prompt = '%s [t: %d] > ' % (self.PREFIX, len(self.targets))
            self.stdout.write('Targets changed to: %s\n' % self._targets_str())

    def do_timeout(self, line):
        """Displays or sets the timeout, in seconds.

        Issuing the 'timeout' command will display the current timeout.
        
        To set the timeout, supply an integer or floating point value
        argument.

          > timeout
          Timeout is 90.0 seconds.

          > timeout 5.0
          Timeout is 5.0 seconds.

          > timeout 0.5
          Error: 1 second is the minimum timeout.
          Timeout is 5.0 seconds.
        
          > timeout
          Timeout is 5.0 seconds.
        """
        args = line.split()
        if len(args) < 2:
            self.stdout.write('Timeout is %.1f seconds.\n'
                              % self.timeout)
        else:
            try:
                timeout = float(args[1])
                if timeout < 1.0:
                    self.stdout.write(
                        'Error: 1 second is the minimum timeout.\n')
                else:
                    self.timeout = timeout
                self.stdout.write('Timeout is %.1f seconds.\n'
                                  % self.timeout)
            except ValueError:
                self.stdout.write(
                    'Error: The value %r must be float or integer.' % args[1])

    def _complete_targets(self, targets, only_regexp=False):
        result = []
        for t in targets:
            if t.startswith('^') or only_regexp:
                matches = self._devices_matching(t)
                if matches:
                    result.extend(matches)
            else:
                if not only_regexp:
                    result.append(t)
        return result
                
    def _parse_targets(self, line):
        """Parses the targets argument."""
        args = line.split()
        if len(args) < 2:
            return []
        else:
            targets = []
            target_spec = args[1:]
            target_spec = [t.split(',') for t in target_spec]
            specs = []
            for spec in target_spec:
                specs.extend([e for e in spec if e])
            return specs

    def _targets_str(self):
        return str(', '.join(sorted(self.targets)))

    def _devices_matching(self, arg, timeout=5.0):
        try:
            r = notch.client.Request('devices_matching',
                                     arguments={'regexp': arg},
                                     timeout_s=timeout)
            return self.notch.exec_request(r).result
        except notch.client.Error, e:
            if str(e):
                self.stdout.write('%s: %s\n', e.__class__.__name__, str(e))
            else:
                self.stdout.write(e.__class__.__name__+'\n')
            return None

    def _execute_command(self, command, output_method=None, targets=None):
        targets = targets or self.targets
        for target in targets:
            method_args = {'device_name': target,
                           'command': command}
            kwargs = {'output_mehod': output_method}
            timeout = self.timeout
            r = notch.client.Request(
                'command',
                arguments=method_args, callback=self._notch_callback,
                callback_kwargs=kwargs,
                timeout_s=timeout)
            self.notch.exec_request(r)
        try:
            self.notch.wait_all()
        except notch.client.TimeoutError, e:
            self.stdout.write('%s: request timed out (%.1f s).\n' %
                              (target, timeout))

    def _print_error(self, request):
        device_name = request.arguments.get('device_name', 'from agent')
        # We ignore RequestCancelledError here, since the user has already
        # had their cancellation confirmed.
        if not isinstance(request.error, notch.client.RequestCancelledError):
            self.stdout.write('ERROR: %s [%s] %s\n' %
                              (device_name, request.error.__class__.__name__,
                               str(request.error)))

    def _notch_callback(self, request, *args, **kwargs):
        output_method = kwargs.get('output_method', None)
        if output_method is not None and hasattr(self, output_method):
            method = getattr(self, output_method)
        else:
            method = self._output_text
        method(request)

    def _output_text(self, request):
        device_name = request.arguments.get('device_name')
        if request.result is not None:
            self.stdout.write('%s:\n%s\n' %
                              (device_name, request.result))
        elif request.error is not None:
            self._print_error(request)
        else:
            self.stdout.write('%s: Incomplete response from Notch Agent.\n' %
                              (device_name))

    def interrupted(self):
        if self.notch.num_requests_running or self.notch.num_requests_waiting:
            self.stdout.write('\nCancelling all requests.\n')
            self.notch.kill_all()
            return
        else:
            # No requests underway, so return True to stop the command-loop.
            return True


def get_option_parser():
    prog = os.path.basename(sys.argv[0])
    parser = optparse.OptionParser()
    parser.usage = '\n'.join([
            '%s [options] <comma-separated list of agent host:port pairs>'
            % prog,
            '',
            'Examples:',
            '    $ %s localhost:8080,localhost:8081' % prog,
            '',
            '    $ NOTCH_AGENTS="localhost:8080,server.example.com:8080" %s'
            % prog,
            '',
            '    $ export NOTCH_AGENTS="localhost:8080"',
            '    $ %s -t cr1.mel -c "show arp"' % prog,
            ])

    parser.add_option('-t', '--target', dest='targets', action='append',
                      default=None,
                      help='Adds a single target device')
    parser.add_option('-c', '--cmd', dest='cmd', default=None,
                      help='The command to execute on each target')
    return parser


WELCOME_MSG = 'Welcome to Mr. CLI.  Type \'help\' if you need it.'

def main():
    option_parser = get_option_parser()
    options, args = option_parser.parse_args()

    # Attempt to gather agent addresses from the environment.
    agents = os.getenv('NOTCH_AGENTS')
    if not args and not agents:
        print option_parser.format_help()
        raise SystemExit(1)

    # Figure out the agent addresses from the commandline.
    if not agents:
        agents = ' '.join(args).split(',')
        for i, a in enumerate(agents):
            agents[i] = a.lstrip()

    # Start the Notch client and CLI
    try:
        nc = notch.client.Connection(agents)
        cli = MisterCLI(nc, targets=options.targets)

        if options.cmd:
            cli.do_command('cmd %s' % options.cmd)
        else:
            print WELCOME_MSG
            cli.cmdloop()
            print '\nBye.'
    except notch.client.NoAgentsError, e:
        print 'No valid agents were found.'
        print
        print option_parser.get_usage()
        raise SystemExit(1)


if __name__ == '__main__':
    main()
