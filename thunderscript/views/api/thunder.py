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
from corecluster.utils.exception import CoreException
from corenetwork.utils.logger import log
from thunderscript.drivers.driver_corecluster import DriverCoreCluster
from thunderscript.drivers.driver_dummy import DriverDummy
from thunderscript.exceptions import *
from thunderscript.models.thunder import Call

import datetime

@register(log=True, auth='token')
def call(context, script, variables):
    '''
    Execute thunder script
    :param script: Script name or public ID
    :param variables: Dictionary with initial variables for script
    '''
    c = Call()
    c.script_name = script
    c.script_params = '\n'.join([str(k) + '=' + str(variables[k]) for k in variables.keys()])
    c.user = context.user
    c.state = 'init'
    c.call_time = datetime.datetime.now()
    c.save()

    d = DriverCoreCluster()
    d.variables = variables
    d.context = context
    d.debug = True
    d.recursion = 0
    d.call_object = c

    c.state = 'in progress'
    c.save()
    try:
        d.cmd_require([script])
        c.state = 'done'
        c.variables = '\n'.join([str(k) + '=' + str(d.variables[k]) for k in d.variables.keys()])
        c.finish_date = datetime.datetime.now()
        c.save()
        return {'finished': 'script_done', 'log': d.log, 'variables': d.variables}
    except ScriptDone as e:
        d.cmd_require([script])
        c.state = 'done'
        c.variables = '\n'.join([str(k) + '=' + str(d.variables[k]) for k in d.variables.keys()])
        c.finish_date = datetime.datetime.now()
        c.save()
        return {'finished': 'script_done', 'log': d.log, 'variables': d.variables}
    except ScriptFailed as e:
        d.cmd_require([script])
        c.state = 'failed'
        c.variables = '\n'.join([str(k) + '=' + str(d.variables[k]) for k in d.variables.keys()])
        c.finish_date = datetime.datetime.now()
        c.save()
        return {'finished': str(e), 'log': d.log, 'variables': d.variables}
    except VariableException as e:
        d.cmd_require([script])
        c.state = 'variable missing'
        c.variables = '\n'.join([str(k) + '=' + str(d.variables[k]) for k in d.variables.keys()])
        c.finish_date = datetime.datetime.now()
        c.save()
        return {'finished': str(e), 'log': d.log, 'variables': d.variables}
    except Exception as e:
        d.cmd_require([script])
        c.state = 'failed'
        c.variables = '\n'.join([str(k) + '=' + str(d.variables[k]) for k in d.variables.keys()])
        c.finish_date = datetime.datetime.now()
        c.save()
        log(msg='Script failed', exception=e, tags=('thunder', 'error'))
        return {'finished': 'failed', 'log': d.log, 'variables': d.variables}


@register(log=True, auth='token')
def get_list(context):
    '''
    Get list of Thunder scripts
    '''
    scripts = Call.get_list(context.user_id)
    return [script.to_dict for script in scripts]


@register(log=True, auth='token')
def delete(context, call_id):
    script = Call.get(context.user_id, call_id)
    if script.in_states(['done']):
        script.delete()
    else:
        raise CoreException('script_not_done')


@register(log=True, auth='token')
def variables(context, script):
    '''
    Get variables required by script
    :param script: Script name or public ID
    '''
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
