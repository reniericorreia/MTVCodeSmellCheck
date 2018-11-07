# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import fnmatch


def get_files(project, extension='py'):
        files = []
        if os.path.isdir(project):
            for root, _, filenames in os.walk(project):
                for filename in fnmatch.filter(filenames, '*.{}'.format(extension)):
                    files.append(os.path.join(root, filename))
        return files


class Identifier():
    
    def __init__(self, config):
        self.config = config
        self.files = get_files(self.config['project'])
        
    def all(self):
        return {'view':self.get_view(), 'model':self.get_model(), 'manager':self.get_managers()} 
        
    def get_model(self):
        return self.get_files_by_layer('models')
    
    def get_view(self):
        result = []
        result.extend(self.get_files_by_layer('views'))
        result.extend(self.get_files_by_layer('admin'))
        result.extend(self.get_files_by_layer('forms'))
        return result
    
    def get_managers(self):
        return self.get_files_by_layer('managers')
        
    def get_files_by_layer(self, layer):
        layer_files = []
        layers = [layer]
        # adiciona outros diretórios da camada fora do padrão
        if self.config.has_key(layer):
            lista = self.config[layer]
            if ';' in lista: 
                for l in list.split(';'):
                    layers.append(l)
            else:
                layers.append(lista)
            
        # identifica os arquivos python da camada
        for filedir in self.files:
            f = filedir.split('/')
            for layer in layers:
                if f[-2] == layer or f[-1] == '{}.py'.format(layer):
                    layer_files.append(filedir)
        return layer_files
