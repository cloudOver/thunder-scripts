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

from base_parser import BaseParser
import os
import pycore

class DriverDummy(BaseParser):
    log = ''

    def _call(self, function, params):
        return ''

    def cmd_req_var(self, params):
        if ':' in params[0]:
            k, v = params[0].split(':')
        else:
            k = params[0]
            v = None

        if k not in self.variables or self.variables[k] is None:
            self.variables[k] = v

    def cmd_resource(self, params):
        res_type, res_field, res_value = params[0].split(':')
        as_var, as_field = params[params.index('AS') + 1].split(':')
        self.variables[as_var] = 'SET FROM RESOURCE'

        self._debug('SAVE RESOURCE ' + res_type + ':' + res_field + ' AS ' + as_var)

    def cmd_call(self, params):
        if 'AS' in params:
            self._debug('SAVE IN CALL')
            as_var, as_field = params[params.index('AS') + 1].split(':')
            self.variables[as_var] = 'SAVED IN CALL'

    def _debug(self, msg, exception=None, color=None):
        self.log = self.log + '\n' + msg