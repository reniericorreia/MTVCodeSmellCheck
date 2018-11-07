# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import fnmatch


def get_config():
    arquivo = open('config.conf').read().decode("utf8").split('\n')
    config = {}
    for linha in arquivo:
        linha = linha.strip()
        if ':' in linha:
            key, value = linha.split(':')
            config[key] = value
    return config

           
def get_files(project, extension='py'):
        files = []
        if os.path.isdir(project):
            for root, _, filenames in os.walk(project):
                for filename in fnmatch.filter(filenames, '*.{}'.format(extension)):
                    files.append(os.path.join(root, filename))
        return files

