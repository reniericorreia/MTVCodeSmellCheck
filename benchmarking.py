# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import ast
from converter import SourceToAST
from complexity import McCabeComplexity
from checker import SQLComplexity

def get_LOC(filename):
    loc = 0
    codelines = open(filename.__str__())
    check_next_line = True
    for line in codelines:
        try:
            if check_next_line:
                if line.isspace() or line.strip().startswith('#'):
                    pass
                elif line.strip().startswith('\'\'\' ') or line.strip().startswith('\"\"\" '):
                    check_next_line = False
                else:
                    loc += 1
            elif line.strip().endswith('\'\'\'') or line.strip().endswith('\"\"\"'):
                check_next_line = True
        except UnicodeDecodeError:
            pass
    return loc


def get_metrics(config, files):
    files_to_converter = []
    for filename in files:
        if 'admin' in filename or 'views' in filename or 'forms' in filename or 'models' in filename:
            files_to_converter.append(filename)
    converter = SourceToAST(config)
    nodes = converter.parse(files_to_converter)
    methods = {}
    functions = {}
    for key in nodes.keys():
        metrics = Metrics(key)
        metrics.visit(nodes[key])
        if len(metrics.methods) > 0:
            methods.update(metrics.methods)
        if len(metrics.functions) > 0:
            functions.update(metrics.functions)
    return methods, functions
        

class Metrics(ast.NodeVisitor):

    def __init__(self, module):
        self.reset()
        self.module = module
        self.methods = {}
        self.functions = {}
    
    def reset(self):
        self.class_name = None
                
    def visit_ClassDef(self, node):
        if node.name == 'Meta':
            return
        self.class_name = node.name
        self.generic_visit(node)
        self.reset()
            
    def visit_FunctionDef(self, node):
        codigo = McCabeComplexity().calcule(node)
        sql = SQLComplexity().calcule(node)
        if self.class_name:
            key = '{}.{}.{}'.format(self.module, self.class_name, node.name)
            self.methods[key] = '{};{}'.format(codigo, sql)
        else:
            key = '{}.{}'.format(self.module, node.name)
            self.functions[key] = '{};{}'.format(codigo, sql)

