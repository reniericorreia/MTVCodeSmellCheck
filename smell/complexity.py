# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mccabe import PathGraphingAstVisitor


class McCabeComplexity():
    
    def __init__(self, max_complexity=10):
        self.max_complexity = max_complexity
        self.result = {}
   
    def calcule(self, node):
        visitor = PathGraphingAstVisitor()
        visitor.preorder(node, visitor)
        for graph in visitor.graphs.values():
            if graph.complexity() > self.max_complexity:
                split = graph.entity.split('.')
                if len(split) == 2:
                    entity, method = split
                    if self.result.has_key(entity):
                        self.result[entity].extend([method])
                    else:
                        self.result[entity] = [method]
        return self.result
