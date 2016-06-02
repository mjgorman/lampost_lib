from importlib import import_module

from lampost.event.dispatcher import PulseDispatcher
from lampost.util import json
from lampost.di import resource, config, app
from lampost.db import redisstore, permissions, dbconfig
from lampost.server.user import UserManager

log = resource.get_resource('log').factory(__name__)


def new_setup(args):
    json.select_json()

    datastore = resource.register('datastore', redisstore.RedisStore(args.db_host, args.db_port, args.db_num, args.db_pw), True)
    if args.flush:
        db_num = datastore.pool.connection_kwargs['db']
        if db_num == args.db_num:
            log.info("Flushing database {}", db_num)
            datastore.redis.flushdb()
        else:
            print("Error:  DB Numbers do not match")
            return

    db_config = datastore.load_object(args.config_id, 'config')
    if db_config:
        print("Error:  This instance is already set up")
        return

    # Load config yaml files and create the database configuration
    config_yaml = config.load_yaml(args.config_dir)
    db_config = dbconfig.create(args.config_id, config_yaml, True)
    config_values = config.activate(db_config.section_values)

    # Initialize core services needed by the reset of the setup process
    resource.register('dispatcher', PulseDispatcher())
    perm = resource.register('perm', permissions)
    user_manager = resource.register('user_manager', UserManager())
    app.start_app()

    app_setup = import_module('{}.setup'.format(args.app_id))

    first_player = app_setup.first_time_setup(args, datastore, config_values)
    user = user_manager.create_user(args.imm_account, args.imm_password)
    player = user_manager.attach_player(user, first_player)
    perm.update_immortal_list(player)


class SetupEditUpdate:
    @classmethod
    def publish_edit(cls, edit_type, edit_obj, *_):
        log.info("Edit:  type: {}  obj: {}".format(edit_type, edit_obj))
