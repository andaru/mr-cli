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

"""An advanced Command-Line Interface.

The CommandLineInterface class provides an alternative to the cmd.Cmd class
from the Python standard library, offering much the same interface.
"""

import sys

import pytrie


EOF_SENTINEL = '__EOF__'


class CLI(object):
    """An abstract command-line interface or CLI.

    Attributes:
      menu: A dict, keyed by string, with string value. The key is
        the command, and the value is appended to 'do_command_' to
        find a method defined in your concrete subclass.
    """
    HELP_COMMANDS = ('help', '?' '/help')

    # Some unique symbolic constants.
    A_OPTION = 100
    A_COMMAND = 101
    A_HELP = 102
    
    PROMPT = 'cli > '

    INTRO = None
    HELP_INTRODUCTION = 'Command-line interface help.'
    AVAIL_COMMANDS = 'Available commands:'
    NOHELP = '% No help for %s'

    def __init__(self, menu, completekey='tab', stdin=None, stdout=None,
                 prompt=None):
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.completekey = completekey
        self.prompt = prompt or self.PROMPT
        self.lastcmd = None
        self._menu = menu
        self._reverse_menu = {}
        self._old_completer = None
        self._completer = None
        self._build_command_prefixes()
   
    def _build_command_prefixes(self):
        self._command_trie = pytrie.SortedStringTrie(self._menu)
        self._reverse_menu = {}
        for k, v in self._menu.iteritems():
            if v in self._reverse_menu:
                self._reverse_menu[v].append(k)
            else:
                self._reverse_menu[v] = [k]

    def cmdloop(self, intro=None):
        self.preloop()
        self._setup_readline()
        try:
            stop = None
            if self.INTRO:
                self.stdout.write(self.INTRO+'\n')
            while not stop:
                try:
                    try:
                        line = raw_input(self.prompt)
                    except EOFError:
                        line = EOF_SENTINEL

                    line = self.precmd(line)
                    stop = self.onecmd(line)
                    stop = self.postcmd(stop, line)
                except KeyboardInterrupt:
                    stop = self.interrupted()
                    continue
            self.postloop()
        finally:
            self._teardown_readline()

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        if state <= 0:
            orig_line = readline.get_line_buffer()
            if orig_line[-1:] != '?':
                line = orig_line.lstrip()
                if not line:
                    methods = self.get_docstrings_for_all().keys()
                    self.completion_matches = [m.rstrip(' .')
                                               for m in methods
                                               if not m.startswith('__')]
                else:
                    methods = self.get_docstrings_for_matching_choices(
                        self._command_trie.values(prefix=line.split()[0]))
            else:
                self.stdout.write('\nMatching commands:\n')
                self.stdout.write(self._build_help(orig_line))
                self.stdout.write('\n\nPress enter to continue.\n')

                
                
            self.completion_matches = [m+' ' for m in methods
                                       if (not m.startswith('__')
                                           and m.startswith(line))]
        try:
            return self.completion_matches[state]
        except IndexError:
            return None

    def _setup_readline(self):
        if not self.completekey:
            return
        try:
            import readline
        except ImportError:
            # Readline is not available, so disable completion.
            self.completekey = None
            return
        else:
            self._old_completer = readline.get_completer()
            readline.set_completer(self.complete)
            readline.parse_and_bind('?: "\C-v?\t\d"')
            readline.parse_and_bind(self.completekey+": complete")

    def _teardown_readline(self):
        if not self._old_completer:
            return
        readline.set_completer(self._old_completer)
      
    def precmd(self, line):
        """Hook method executed just before the command line is
        interpreted, but after the input prompt is generated and issued.

        """
        return line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        return stop

    def preloop(self):
        """Hook method executed once when the cmdloop() method is called."""
        pass

    def postloop(self):
        """Hook method executed once when the cmdloop() method is about to
        return.

        """
        pass

    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.

        This may be overridden, but should not normally need to be;
        see the precmd() and postcmd() methods for useful execution hooks.
        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        line = line.lstrip()
        if not line:
            return self.emptyline()
        else:
            # Only check the first-word.
            matches = self._command_trie.keys(prefix=line.split()[0])
            if not matches or not len(matches):
                return self.default(line)
            elif len(matches) == 1:
                choice = self._command_trie.longest_prefix_value(matches[0])
                return getattr(self, choice)(line)
            elif len(matches) > 1:
                # Use the shortest common prefix.
                _, match = sorted([(len(m), m) for m in matches])[0]
                choice = self._command_trie.longest_prefix_value(match)
                return getattr(self, choice)(line)

    def get_docstrings_for_matching_choices(self, choices):
        menu_items = []
        menu_docs = {}
        for c in choices:
            menu_items.extend(self._reverse_menu.get(c))
        for k in menu_items:
            method = self._menu.get(k, None)
            if method:
                docstring = getattr(self, method).__doc__
                if docstring:
                    menu_docs[k.replace('*', '...')] = docstring
        return menu_docs

    def get_docstrings_for_all(self):
        return self.get_docstrings_for_matching_choices(self._menu.values())

    def get_docstring_for_command(self, command, full=True):
        method_name = self._menu.get(command)
        docstring = None
        if method_name:
            if hasattr(self, method_name):
                docstring = getattr(self, method_name).__doc__
        if docstring is not None:
            if full:
                return docstring.rstrip()   
            else:
                return ''.join(docstring.split('\n')[0])
    
    def display_choices(self, choices):
        menu_docs = self.get_docstrings_for_matching_choices(choices)
        self.stdout.write('Matching commands:\n')
        for k in sorted(menu_docs):
            if k.startswith('__'):
                continue
            self.stdout.write('%-30s%s\n' % (k, menu_docs[k]))
        self.stdout.write('\n')
       
    def _build_help(self, line):
        """Builds the help, for a command if supplied."""
        w = line.split()
        result = []
        if len(w) <= 1:
            result.append(self.HELP_INTRODUCTION + '\n')
            result.append(self.AVAIL_COMMANDS)
            # Produce a command list.
            for k, v in sorted(self.get_docstrings_for_all().iteritems()):
                if k.startswith('__'):
                    # Ignore magic commands.
                    continue
                else:
                    # Just the short docstrings here.
                    v = v.split('\n')[0]
                    result.append('%-30s%s' % (k, v))
        else:
            docstring = self.get_docstring_for_command(w[1])
            if docstring is not None:
                result.append('Help for %r:\n\n%s\n' % (w[1], docstring))
            else:
                result.append('No help available for %r' % w[1])
        return '\n'.join(result)
      
    def do_help(self, line):
        """Displays help, for a command if supplied."""
        self.stdout.write(self._build_help(line))
        self.stdout.write('\n')
    
    def emptyline(self):
        """Called when an empty line is entered in response to the prompt.

        If this method is not overridden, it repeats the last nonempty
        command entered.

        """
        if self.lastcmd:
            return self.onecmd(self.lastcmd)

    def default(self, line, action=None):
        """Called on an input line when the command prefix is not recognized.

        If this method is not overridden, it prints an error message and
        returns.

        """
        self.stdout.write('*** Unknown syntax: %s\n'%line)
