# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import subprocess
import os
import fnmatch
import ast
from smell.visitor import MeddlingServiceVisitor, FatRepositoryVisitor, LaboriousRepositoryMethodVisitor,\
    ScanModelManagers, ScanModelRelationships


def check_code_smells():
    files = load_files('models')
    nodes = load_nodes(files)
    models = mapping_relationships(nodes)
    
    brain_repository(nodes, files)
    fat_repository(nodes, models)
    laborious_repository_method(nodes, models)
    meddling_service()
    
def mapping_relationships(nodes):
    managers = mapping_managers(load_nodes(load_files('managers')))
    models = {}
    for key in nodes.keys():
        scan = ScanModelRelationships(key, managers)
        scan.visit(nodes[key])
        models.update(scan.models)
    return models

def mapping_managers(nodes):
    '''
        TODO: verificar classes do Model que herdam de 'models.Manager'
    '''
    managers = []
    for key in nodes.keys():
        scan = ScanModelManagers(key)
        scan.visit(nodes[key])
        managers.extend(scan.managers)
    return managers    

def brain_repository(nodes, files):
    process_python = subprocess.Popen(['whereis', 'python'], stdout=subprocess.PIPE)
    python, _ = process_python.communicate()
    python = python.replace('\n', '')
    
    for f in files:
        print f
        process_mccabe = subprocess.Popen([python,"-m", "mccabe", "--min", "10", f], stdout=subprocess.PIPE)
        mccabe, _ = process_mccabe.communicate()
        print mccabe
        
def laborious_repository_method(nodes, models):
    for key in nodes.keys():
        LaboriousRepositoryMethodVisitor(key, models).visit(nodes[key])

def fat_repository(nodes, models):
    for key in nodes.keys():
        FatRepositoryVisitor(key, models).visit(nodes[key])

def meddling_service():
    nodes = load_nodes(load_files('views'))
    for key in nodes.keys():
        MeddlingServiceVisitor(key).visit(nodes[key])

def load_files(layer):
    '''
        TODO: parametrizar em arquivo de configuração nome dos arquivos fora do padrão Django que fazem parte da camada.
    '''
    project = load_config()
    files = []
    diretorios = [project]
        
    for diretorio in diretorios:
        if os.path.isdir(diretorio):
            for root, _, filenames in os.walk(diretorio):
                if root.endswith(layer):
                    for filename in fnmatch.filter(filenames, '*.py'):
                        files.append(os.path.join(root, filename))
                else:
                    for filename in fnmatch.filter(filenames, '{}.py'.format(layer)):
                        files.append(os.path.join(root, filename))
        else:
            print("Diretório não localizado: {}".format(diretorio))
    return files

def load_nodes(files):
    nodes = {}
    project = load_config()
    for f in files:
        module = f.replace(project, '').strip('.').replace('/', '.')[1:-3]
        node = ast.parse(open(f.__str__()).read())
        nodes[module] = node
    return nodes

def load_config():
    project = None  
    arquivo = open('config.conf').read().decode("utf8").split('\n')
    for linha in arquivo:
        linha = linha.strip()
        if linha.startswith('project'):
            project = linha.split(':')[1]
    return project
        