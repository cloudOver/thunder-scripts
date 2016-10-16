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
from corenetwork.utils.logger import log
from corecluster.urls import decorated_functions
from corecluster.utils.exception import CoreException
from base_parser import BaseParser
import re

class DriverCoreCluster(BaseParser):
    context = None
    log = ''

    def _call(self, function, params):
        if not function.startswith('/api/'):
            raise CoreException('not_api_function')

        if not self.context:
            raise CoreException('context_failed')

        for f in decorated_functions:
            if re.match(r'^/%s' % (f.function_name.replace('.', '/')), function):
                return f.function(self.context, **params)

    def _debug(self, msg, exception=None, color=None):
        self.log = self.log + '\n' + msg
        if exception is None:
            log(msg=msg, tags=('thunder'))
        else:
            log(msg=msg, exception=exception, tags=('thunder', 'error'))
