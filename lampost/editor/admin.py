import inspect

from lampost.di.app import on_app_start
from lampost.server.link import LinkListener
from lampost.di.resource import Injected, module_inject

perm = Injected('perm')
module_inject(__name__)

admin_ops = {}


def admin_op(func):
    a_spec = inspect.getargspec(func)

    if a_spec.defaults:
        params = [''] * (len(a_spec.args) - len(a_spec.defaults)) + list(a_spec.defaults)
    else:
        params = [''] * len(a_spec.args)

    admin_ops[func.__name__] = {'func': func, 'dto': {'name': func.__name__, 'args': a_spec.args, 'params': params}}
    return func


@on_app_start
def _start():
    LinkListener('admin_op', _admin_exec, 'supreme')


def _admin_exec(name, params, **_):
    if name == 'list':
        return [op['dto'] for op in admin_ops.values()]
    op = admin_ops['name']
    return op['func'](*params)
