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

from corecluster.utils.decorators import register
from corenetwork.utils.logger import log
from thunderscript.drivers.driver_corecluster import DriverCoreCluster
from thunderscript.drivers.driver_dummy import DriverDummy
from thunderscript.exceptions import *


@register(log=True, auth='token')
def call(context, script, variables):
    d = DriverCoreCluster()
    d.variables = variables
    d.context = context
    d.debug = True
    d.recursion = 0
    try:
        d.cmd_require([script])
    except ScriptDone as e:
        return {'finished': 'script_done', 'log': d.log, 'variables': d.variables}
    except ScriptFailed as e:
        return {'finished': str(e), 'log': d.log, 'variables': d.variables}
    except VariableException as e:
        return {'finished': str(e), 'log': d.log, 'variables': d.variables}
    except Exception as e:
        log(msg='Script failed', exception=e, tags=('thunder', 'error'))
        return {'finished': 'failed', 'log': d.log, 'variables': d.variables}


@register(log=True, auth='token')
def variables(context, script):
    d = DriverDummy()
    d.context = context
    d.debug = True
    d.recursion = 0
    d.variables = {}
    try:
        d.cmd_require([script])
    except:
        pass

    return {'log': d.log, 'variables': d.variables}
