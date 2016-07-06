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

import os
import sys

from implementations.driver_pycore import DriverPyCore

if __name__ == "__main__":
    vars = {}
    for k in os.environ.keys():
        if k.startswith('CORE_'):
            vars[k] = os.environ[k]
    for p in sys.argv[2:]:
        k, v = p.split('=')
        vars[k] = v
    d = DriverPyCore()
    d.variables = vars
    d.cmd_require([sys.argv[1]])