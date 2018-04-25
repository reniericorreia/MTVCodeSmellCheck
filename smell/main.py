# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import fnmatch
import ast
from smell.visitor import MeddlingViewVisitor, FatRepositoryVisitor, LaboriousRepositoryMethodVisitor,\
    ScanModelManagers, ScanModelRelationships, BrainRepositoryVisitor,\
    MeddlingModelVisitor
from smell.complexity import McCabeComplexity

config = {}

def check_code_smells():
    load_config()
    check_model()
    check_view()
    
def check_model():
    files = load_files('models')
    nodes = load_nodes(files)
    models = mapping_relationships(nodes)
    for key in nodes.keys():
        complexitys = McCabeComplexity(int(config['mccabe_complexity'])).calcule(nodes[key])
        BrainRepositoryVisitor(key, complexitys, int(config['sql_complexity'])).visit(nodes[key])
        FatRepositoryVisitor(key, models).visit(nodes[key])
        LaboriousRepositoryMethodVisitor(key, models).visit(nodes[key])
        MeddlingModelVisitor(key).visit(nodes[key])
    
def check_view():
    nodes = load_nodes(load_files('views'))
    for key in nodes.keys():
        MeddlingViewVisitor(key).visit(nodes[key])
    
def mapping_relationships(nodes):
    # identifica todos os managers do modelo
    managers = mapping_managers(load_nodes(load_files('managers')))
    models = {}
    # identifica os atributos da classe que são relacionamentos com outras classes do modelo ou managers
    for key in nodes.keys():
        scan = ScanModelRelationships(key, managers)
        scan.visit(nodes[key])
        models.update(scan.models)
    return models

def mapping_managers(nodes):
    managers = []
    
    # mapeia todos os managers existentes no modelo
    for key in nodes.keys():
        scan = ScanModelManagers(key)
        scan.visit(nodes[key])
        managers.extend(scan.managers)
    return managers    
        
def load_files(layer):
    project = config['project']
    files = []
    layers = [layer]
    
    # adiciona diretórios que estão fora do padrão das camadas Django
    if config.has_key(layer):
        lista = config[layer]
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

def load_nodes(files):
    nodes = {}
    project = config['project']
    
    # converte cada arquivo python em um node do AST
    for f in files:
        module = f.replace(project, '').strip('.').replace('/', '.')[1:-3]
        node = ast.parse(open(f.__str__()).read())
        nodes[module] = node
    return nodes

def load_config():
    arquivo = open('config.conf').read().decode("utf8").split('\n')
    for linha in arquivo:
        linha = linha.strip()
        if ':' in linha:
            key, value = linha.split(':')
            config[key] = value
        