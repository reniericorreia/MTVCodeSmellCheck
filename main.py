# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from smell.core import start
from benchmarking import get_LOC, get_metrics
import sys
from report import print_metrics, exportar_csv
from util import get_config, get_files

if __name__ == '__main__':
    config = get_config()
    if config.has_key('project'):
        files = get_files(config['project'])
    else:
        print '### Adicione no arquivo de configuração o diretório do projeto.'
    if len(sys.argv) > 1:
        if 'metrics' in sys.argv:
            methods, functions = get_metrics(config, files)
            print_metrics(methods, functions)
            exportar_csv(methods, functions)
        if 'loc' in sys.argv:
            total = 0
            for filename in files:
                loc = get_LOC(filename)
                total += loc
                print '{};{}'.format(filename, loc)
            print 'Total: {}'.format(total)
        if 'checker' in sys.argv:
            start(config, files)
    else:
        start(config, files)

