# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from smell.checker import checker
from smell.identify import LayerFiles
from smell.converter import SourceToAST

config = {}

def start():
    load_config()
    
    identify = LayerFiles(config)
    model_files = identify.get_models()
    view_files = identify.get_views()
    manager_files = identify.load_files('managers')
    
    converter = SourceToAST(config)
    models = converter.parse(model_files)
    views = converter.parse(view_files)
    managers = converter.parse(manager_files)
    
    checker(models, views, managers, config)
    #counts(models, views)


def load_config():
    arquivo = open('config.conf').read().decode("utf8").split('\n')
    for linha in arquivo:
        linha = linha.strip()
        if ':' in linha:
            key, value = linha.split(':')
            config[key] = value
        