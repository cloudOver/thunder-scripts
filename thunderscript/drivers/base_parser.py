"""
Copyright (c) 2016 cloudover.io

This file is part of Thunder project.

cloudover.coreCluster is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from thunderscript.exceptions import *
import os
import re
import requests
import shlex
import sys


class BaseParser(object):
    variables = {}
    debug = False
    recursion = 0

    def _call(self, function, params):
        raise Exception('Method not implemented')

    def cmd_require(self, params):
        if self.recursion > 100:
            self._debug('FAILED: RECURSION LIMIT REACHED', color='error')
            raise ScriptFailed('Recursion limit reached')

        r = requests.get('http://cloudover.io/thunder/raw/' + self._parse_var(params[0])).text.splitlines()
        try:
            self.recursion = self.recursion + 1
            self._parse(r)
        except ScriptDone as e:
            pass
        

    def cmd_req_var(self, params):
        if ':' in params[0]:
            k, v = params[0].split(':')
        else:
            k = params[0]
            v = None

        if not k in self.variables:
            if v is not None:
                self.variables[k] = v
            else:
                raise VariableException('variable_' + params[0] + ' not found')

    def cmd_set(self, params):
        try:
            self.variables[params[0]] = int(params[1])
        except:
            self.variables[params[0]] = self._parse_var(params[1])

    def cmd_append(self, params):
        if params[0] in self.variables:
            try:
                self.variables[params[0]] += int(params[1])
            except:
                self.variables[params[0]] = self.variables[params[0]] + self._parse_var(params[1])
        else:
            self.cmd_set(params)

    def cmd_appendl(self, params):
        if params[0] in self.variables:
            try:
                self.variables[params[0]] += int(params[1])
            except:
                self.variables[params[0]] = str(self.variables[params[0]]) + '\n' + str(self._parse_var(params[1]))
        else:
            self.cmd_set(params)

    def cmd_done(self, params):
        if 'AS' in params:
            final_param = params.index('AS')
        else:
            final_param = len(params)

        filters = {}
        res_type = ''
        found = 0
        for param in params[:final_param]:
            res_type, res_field, res_value = param.split(':')
            filters[res_field] = self._parse_var(res_value)
        resources = self._call('/api/' + res_type + '/get_list/', {})

        if resources:
            for resource in resources:
                for filter in filters.keys():
                    if filter in resource and resource[filter] == filters[filter]:
                        found = found+1
                        if 'AS' in params:
                            as_var, as_field = params[final_param + 1].split(':')
                            self.variables[as_var] = resource[as_field]
                            self._debug('SAVE: %s AS %s' % (str(as_var), str(resource[as_field])), color='yellow')
                        raise ScriptDone()

    def cmd_resource(self, params):
        final_param = params.index('AS')

        filters = {}
        res_type = ''
        for param in params[:final_param]:
            res_type, res_field, res_value = param.split(':')
            filters[res_field] = self._parse_var(res_value)
        resources = self._call('/api/' + res_type + '/get_list/', {})

        if resources:
            for resource in resources:
                for filter in filters.keys():
                    if filter in resource and resource[filter] == filters[filter]:
                        as_var, as_field = params[final_param + 1].split(':')
                        self.variables[as_var] = resource[as_field]
                        self._debug('SAVE: %s AS %s' % (str(as_var), str(resource[as_field])), color='yellow')
                        return

        raise ScriptFailed('RESOURCE NOT FOUND')

    def cmd_call(self, params):
        if 'AS' in params:
            final_param = params.index('AS')
        else:
            final_param = len(params)

        call_url = '/' + '/'.join(params[0].split(':')) + '/'
        call_params_list = [(p.split(':')) for p in params[1:final_param]]
        call_params = {}
        for p in call_params_list:
            try:
                call_params[p[0]] = int(self._parse_var(p[1]))
            except:
                call_params[p[0]] = self._parse_var(p[1])

        ret = self._call(call_url, call_params)

        if 'AS' in params:
            as_var, as_field = params[final_param + 1].split(':')
            self.variables[as_var] = ret[as_field]
            self._debug('SAVE: %s AS %s' % (str(as_var), str(ret[as_field])), color='yellow')

    def cmd_raise(self, params):
        raise ScriptFailed(params[0])

    def cmd_bootcmd(self, params):
        parsed_params = self._parse_vars(params)
        if not 'CLOUDINIT_BOOTCMD' in self.variables:
            self.variables['CLOUDINIT_BOOTCMD'] = '#cloud-config\n'\
                                                  '\n'\
                                                  'bootcmd:\n'

        self.variables['CLOUDINIT_BOOTCMD'] = '%s  - %s\n' % (self.variables['CLOUDINIT_BOOTCMD'], ' '.join(parsed_params))

    def _parse_var(self, value):
        try:
            return int(value)
        except:
            pass

        while re.search(r'(\$[a-zA-Z_][a-zA-Z0-9_]+)', value):
            match = re.search(r'(\$[a-zA-Z_][a-zA-Z0-9_]+)', value)
            if match:
                for v in match.groups():
                    value = re.sub('\$' + v[1:], str(self.variables[v[1:]]), value)
        return value

    def _parse_vars(self, values):
        return [self._parse_var(v) for v in values]

    def _debug(self, msg, exception=None, color=None, newline=True):
        C_BLUE = '\033[94m'
        C_GREEN = '\033[92m'
        C_YELLOW = '\033[93m'
        C_WARNING = '\033[91m'
        C_ERROR = '\033[91m'
        C_CLEAR = '\033[0m'
        if self.debug:
            if color == 'warning':
                sys.stderr.write(C_WARNING)
            elif color == 'error':
                sys.stderr.write(C_ERROR)
            elif color == 'yellow':
                sys.stderr.write(C_YELLOW)
            elif color == 'blue':
                sys.stderr.write(C_BLUE)
            elif color == 'green':
                sys.stderr.write(C_GREEN)

            sys.stderr.write(msg)
            if newline == True:
                sys.stderr.write('\n')

            if color is not None:
                sys.stderr.write(C_CLEAR)

    def _parse(self, commands):
        for command in commands:
            cmd = []
            for c in shlex.split(command):
                try:
                    cmd.append(int(c))
                except:
                    cmd.append(c)

            if len(cmd) > 0:
                self._debug('CALL: %s' % cmd[0], color='green')
                self._debug('  - LINE: ' + ' '.join(['"' + str(c) + '" ' for c in cmd]), color='blue')
                self._debug('  - VARS: ' + ' '.join(['"' + str(c) + '" ' for c in self.variables]), color='blue')

            if len(cmd) > 1 and cmd[0] == 'REQUIRE':
                self.cmd_require(cmd[1:])
            if len(cmd) > 1 and cmd[0] == 'REQ_VAR':
                self.cmd_req_var(cmd[1:])
            if len(cmd) > 1 and cmd[0] == 'SET':
                self.cmd_set(cmd[1:])
            if len(cmd) > 1 and cmd[0] == 'APPEND':
                self.cmd_append(cmd[1:])
            if len(cmd) > 1 and cmd[0] == 'APPENDL':
                self.cmd_appendl(cmd[1:])
            if len(cmd) > 1 and cmd[0] == 'RESOURCE':
                self.cmd_resource(cmd[1:])
            if len(cmd) > 1 and cmd[0] == 'DONE':
                self.cmd_done(cmd[1:])
            if len(cmd) > 1 and cmd[0] == 'CALL':
                self.cmd_call(cmd[1:])
            if len(cmd) > 1 and cmd[0] == 'RAISE':
                self.cmd_raise(cmd[1:])
            if len(cmd) > 1 and cmd[0] == 'BOOTCMD':
                self.cmd_bootcmd(cmd[1:])
