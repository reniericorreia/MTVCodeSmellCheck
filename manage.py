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
    layers = Identifier(config).all()
    
    converter = SourceToAST(config)
    models = converter.parse(layers['model'])
    views = converter.parse(layers['view'])
    managers = converter.parse(layers['manager'])
    
    violations = checker(models, views, managers, config)
    export_csv(['design problem', 'app', 'module', 'class', 'function', 'line'], violations, 'problems_report.csv')
    print '### Relatório salvo em problems_report.csv ###'


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
                for filename in files:
                    if ('views' in filename or 'models' in filename or 'admin' in filename or 'forms' in filename):
                        loc = get_LOC(filename)
                        total += loc
                        print '{};{}'.format(filename, loc)
                print 'Total: {}'.format(total)
            if 'checker' in sys.argv:
                start_analysis(config)
        else:
            start_analysis(config)
    print '### execução finalizada ###'

