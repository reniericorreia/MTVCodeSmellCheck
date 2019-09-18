# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from benchmarking import get_LOC, get_metrics
import sys
from report import print_metrics, exportar_csv, export_csv
from identifier import Identifier, get_files
from converter import SourceToAST
from checker import checker


def get_config():
    arquivo = open('config.conf').read().decode("utf8").split('\n')
    config = {}
    for linha in arquivo:
        linha = linha.strip()
        if not linha.startswith('#') and ':' in linha:
            key, value = linha.split(':')
            config[key] = value
    return config


def start_analysis(config):
    print(' - Identificando camadas')
    layers = Identifier(config).all()
    print(' - Convertendo arquivos para AST')
    converter = SourceToAST(config)
    models = converter.parse(layers['model'])
    views = converter.parse(layers['view'])
    managers = converter.parse(layers['manager'])
    
    print(' - Analisando código fonte')
    violations = checker(models, views, managers, config)
    print(' - Gerando relatórios')
    export_csv(['design problem', 'app', 'module', 'class', 'function', 'line'], violations, 'design_problems_details.csv')
    d = {}
    for v in violations:
        key = '{};{};{};{}'.format(v.app, v.module, v.cls or '_', v.method or '_')
        if not d.has_key(key):
            d[key] = {'Meddling View':'', 'Meddling Model':'', 'Improper Use of Manager':'', 'Brain Persistence Method':'', 'Laborious Persistence Method':''}
        d[key][v.smell] = 'yes' 
    result = []
    for k, value in d.items():
        s = '{};{};{};{};{};{}'.format(k, value['Meddling View'],value['Meddling Model'],value['Improper Use of Manager'],value['Brain Persistence Method'],value['Laborious Persistence Method'])
        result.append(s)
    export_csv(['app', 'module', 'class', 'function', 'Meddling View', 'Meddling Model', 'Improper Use of Manager', 'Brain Persistence Method', 'Laborious Persistence Method'], result, 'design_problems.csv')


if __name__ == '__main__':
    print '### execução iniciada ###'
    config = get_config()
    if not config.has_key('project'):
        print '### Adicione no arquivo de configuração o diretório do projeto.'
    else:
        if len(sys.argv) > 1:
            if 'metrics' in sys.argv:
                files = get_files(config['project'])
                methods, functions = get_metrics(config, files)
                print_metrics(methods, functions)
                exportar_csv(methods, functions)
            if 'loc' in sys.argv:
                files = get_files(config['project'])
                total = 0
                models = 0
                views = 0
                for filename in files:
                    if ('views' in filename or 'models' in filename or 'admin' in filename or 'forms' in filename):
                        loc = get_LOC(filename)
                        total += loc
                        if 'models' in filename:
                            models += loc
                        else:
                            views += loc
                        print '{};{}'.format(filename, loc)
                print 'Model: {}'.format(models)
                print 'View: {}'.format(views)
                print 'Total: {}'.format(total)
            if 'checker' in sys.argv:
                start_analysis(config)
        else:
            start_analysis(config)
    print '### execução finalizada ###'

