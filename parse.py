import os
import pycore
import re
import shlex
import sys

debug_calls = False

class ScriptDone(Exception):
    pass


class ScriptFailed(Exception):
    pass


class VariableException(Exception):
    pass


def cmd_require(params, variables):
    repo = './'
    f = open(os.path.join(repo, params[0] + '.txt'))
    try:
        parse(f.readlines(), variables)
        f.close()
    except ScriptDone as e:
        pass
    except Exception as e:
        print('FAILED: %s' % str(e))
        sys.exit(1)


def cmd_req_var(params, variables):
    if ':' in params[0]:
        k, v = params[0].split(':')
    else:
        k = params[0]
        v = None

    if not params[0] in variables:
        if v is not None:
            variables[k] = v
        else:
            raise VariableException('variable_' + params[0] + ' not found')


def cmd_set(params, variables):
    try:
        variables[params[0]] = int(params[1])
    except:
        variables[params[0]] = parse_var(params[1], variables)


def cmd_append(params, variables):
    if params[0] in variables:
        try:
            variables[params[0]] += int(params[1])
        except:
            variables[params[0]] = variables[params[0]] + parse_var(params[1], variables)
    else:
        cmd_set(params, variables)


def cmd_appendl(params, variables):
    if params[0] in variables:
        try:
            variables[params[0]] += int(params[1])
        except:
            variables[params[0]] = str(variables[params[0]]) + '\n' + str(parse_var(params[1], variables))
    else:
        cmd_set(params, variables)


def cmd_done(params, variables):
    res_type, res_field, res_value = params[0].split(':')
    res_value = parse_var(res_value, variables)
    res_field = parse_var(res_field, variables)
    resources = pycore.utils.request(os.environ['CORE_URL'], '/api/' + res_type + '/get_list/', {'token': os.environ['CORE_TOKEN']}, debug=debug_calls)

    for resource in resources:
        if resource[res_field] == res_value:
            raise ScriptDone()


def cmd_resource(params, variables):
    res_type, res_field, res_value = params[0].split(':')
    res_value = parse_var(res_value, variables)
    res_field = parse_var(res_field, variables)
    resources = pycore.utils.request(os.environ['CORE_URL'], '/api/' + res_type + '/get_list/', {'token': os.environ['CORE_TOKEN']}, debug=debug_calls)

    for resource in resources:
        if resource[res_field] == res_value:
            as_var, as_field = params[params.index('AS') + 1].split(':')
            variables[as_var] = resource[as_field]

            debug('SAVE: %s AS %s: %s' % (str(as_var), str(resource[as_field]), str(variables[as_var])))
            return


def cmd_call(params, variables):
    if 'AS' in params:
        final = params.index('AS')
    else:
        final = len(params)

    call_url = '/' + '/'.join(params[0].split(':')) + '/'
    call_params_list = [(p.split(':')) for p in params[1:final]]
    call_params = {'token': os.environ['CORE_TOKEN']}
    for p in call_params_list:
        try:
            call_params[p[0]] = int(parse_var(p[1], variables))
        except:
            call_params[p[0]] = parse_var(p[1], variables)

    ret = pycore.utils.request(os.environ['CORE_URL'], call_url, call_params, debug=True)
    if 'AS' in params:
        debug('SAVE')
        as_var, as_field = params[params.index('AS')+1].split(':')
        variables[as_var] = ret[as_field]
        debug('SAVE: %s AS %s' % (str(as_var), str(ret[as_field])))


def cmd_raise(params, variables):
    raise ScriptFailed(params[0])


def parse_var(value, variables):
    try:
        return int(value)
    except:
        pass

    while re.search(r'(\$[a-zA-Z_][a-zA-Z0-9_]+)', value):
        match = re.search(r'(\$[a-zA-Z_][a-zA-Z0-9_]+)', value)
        if match:
            for v in match.groups():
                value = re.sub('\$' + v[1:], str(variables[v[1:]]), value)
    return value


def parse_vars(values, variables):
    return [parse_var(v, variables) for v in values]


def debug(msg):
    print(msg)


def parse(commands, variables):
    for command in commands:
        cmd = []
        for c in shlex.split(command):
            try:
                cmd.append(int(c))
            except:
                cmd.append(c)

        if len(cmd) > 0:
            debug('CALL: %s' % cmd[0])
            debug(' - LINE: ' + ' '.join(['"' + str(c) + '" ' for c in cmd]))
            debug(' - VARS: ' + ' '.join(['"' + str(c) + '" ' for c in variables]))

        if len(cmd) > 1 and cmd[0] == 'REQUIRE':
            cmd_require(cmd[1:], variables)
        if len(cmd) > 1 and cmd[0] == 'REQ_VAR':
            cmd_req_var(cmd[1:], variables)
        if len(cmd) > 1 and cmd[0] == 'SET':
            cmd_set(cmd[1:], variables)
        if len(cmd) > 1 and cmd[0] == 'APPEND':
            cmd_append(cmd[1:], variables)
        if len(cmd) > 1 and cmd[0] == 'APPENDL':
            cmd_appendl(cmd[1:], variables)
        if len(cmd) > 1 and cmd[0] == 'RESOURCE':
            cmd_resource(cmd[1:], variables)
        if len(cmd) > 1 and cmd[0] == 'DONE':
            cmd_done(cmd[1:], variables)
        if len(cmd) > 1 and cmd[0] == 'CALL':
            cmd_call(cmd[1:], variables)
        if len(cmd) > 1 and cmd[0] == 'RAISE':
            cmd_raise(cmd[1:], variables)

if __name__ == "__main__":
    vars = {}
    for k in os.environ.keys():
        if k.startswith('CORE_'):
            vars[k] = os.environ[k]
    for p in sys.argv[2:]:
        k, v = p.split('=')
        vars[k] = v
    cmd_require([sys.argv[1]], vars)
