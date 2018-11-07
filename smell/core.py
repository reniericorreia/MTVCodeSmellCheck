# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from smell.checker import checker
from smell.identify import LayerFiles
from converter import SourceToAST



def start(config, files):
    identify = LayerFiles(config, files)
    model_files = identify.get_model()
    view_files = identify.get_view()
    manager_files = identify.get_managers()
    
    converter = SourceToAST(config)
    models = converter.parse(model_files)
    views = converter.parse(view_files)
    managers = converter.parse(manager_files)
    
    checker(models, views, managers, config)



        