"""
Copyright (c) 2016 Maciej Nabozny

This file is part of CloudOver project.

CloudOver is free software: you can redistribute it and/or modify
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

from corecluster.models.common_models import CoreModel, UserMixin, StateMixin
from django.db import models


class Call(UserMixin, StateMixin, CoreModel):
    states = [
        'init',
        'in progress',
        'done',
        'failed',
        'variable missing',
    ]

    default_state = 'init'

    script_name = models.CharField(max_length=250)
    script_params = models.TextField()
    log = models.TextField()
    variables = models.TextField()
    call_date = models.DateTimeField(auto_now_add=True, null=True)
    finish_date = models.DateTimeField(null=True)

    editable = []
    serializable = ['id',
                    'state',
                    'script_name',
                    'script_params',
                    'log',
                    'variables',
                    'call_date',
                    'finish_date',
                    ]

