# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast

class SourceToAST():
     
    def __init__(self, config):
        self.project = config['project']

    def parse(self, files):
        nodes = {}
        # converte cada arquivo python em um node do AST
        for fname in files:
            module = fname.replace(self.project, '').strip('.').replace('/', '.')[1:-3]
            node = ast.parse(open(fname.__str__()).read())
            nodes[module] = node
        return nodes