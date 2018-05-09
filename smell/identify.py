# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import fnmatch


class LayerFiles():
    
    def __init__(self, config):
        self.config = config
        
    def get_models(self):
        return self.load_files('models')
    
    def get_views(self):
        return self.load_files('views')
        
    def load_files(self, layer):
        project = self.config['project']
        files = []
        layers = [layer]
        
        # adiciona diretórios que estão fora do padrão das camadas Django
        if self.config.has_key(layer):
            lista = self.config[layer]
            if ';' in lista: 
                for l in list.split(';'):
                    layers.append(l)
            else:
                layers.append(lista)
            
        # adiciona os arquivos python da camada
        if os.path.isdir(project):
            for root, _, filenames in os.walk(project):
                for l in layers:
                    if root.endswith(l):
                        for filename in fnmatch.filter(filenames, '*.py'):
                            files.append(os.path.join(root, filename))
                    else:
                        for filename in fnmatch.filter(filenames, '{}.py'.format(l)):
                            files.append(os.path.join(root, filename))
        else:
            print("Este diretório não existe: {}".format(project))
        return files
