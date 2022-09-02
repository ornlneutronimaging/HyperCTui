import json
import os
from .get import Get
import logging
import versioneer


class ConfigHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def load(self):
        config_file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        with open(config_file_name) as f:
            config = json.load(f)
        self.parent.config = config

        for _homepath in config['homepath']:
            if os.path.exists(_homepath):
                self.parent.homepath = _homepath

        o_get = Get(parent=self.parent)
        log_file_name = o_get.get_log_file_name()
        logging.basicConfig(filename=log_file_name,
                            filemode='a',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")
        logging.info(f" Version: {versioneer.get_version()}")

