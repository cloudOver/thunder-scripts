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

class DriverPyCore(BaseParser):
    def _call(self, function, params):
        if params is None:
            params = {}
        params['token'] = os.environ['CORE_TOKEN']
        return pycore.utils.request(os.environ['CORE_URL'], function, params, debug=self.debug)