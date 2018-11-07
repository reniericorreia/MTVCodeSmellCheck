# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mccabe import PathGraphingAstVisitor


class McCabeComplexity():
    
    def calcule(self, node):
        '''
            Recebe um nó de uma função como entrada e utiliza PathGraphingAstVisitor para calcular a complexidade de mccabe
        '''
        mccabe_visitor = PathGraphingAstVisitor()
        mccabe_visitor.preorder(node, mccabe_visitor)
        return mccabe_visitor.graphs.values()[0].complexity()
    

class HalsteadComplexity():
    
    def __init__(self, operators=(), ignore=()):
        self.operators = operators
        self.ignore = ignore
    
    def count_n(self, source):
        n1, n2, N1, N2 = self.calcule_n(source)
        return len(n1), len(n2), len(N1), len(N2)
        
    def calcule_n(self, source):
        '''
        n1 = the number of distinct operators
        n2 = the number of distinct operands
        N1 = the total number of operators
        N2 = the total number of operands
        '''
        n1 = []
        n2 = []
        N1 = []
        N2 = []
        position = 0
        source = source.replace('\n', ' ')
        source = source.lower()
        while position < len(source):
            var = ''
            while source[position] not in (' ', ',', '(', ')'):
                var = var + source[position]
                position += 1
                if position + 1 > len(source):
                    break
                
            if var != '':
                if var in self.operators:
                    N1.append(var)
                    if var not in n1:
                        n1.append(var)
                elif var not in self.ignore:
                    N2.append(var)
                    if var not in n2:
                        n2.append(var)
            position += 1
            if position + 1 > len(source):
                break
        return n1, n2, N1, N2
    
    def calcule_difficulty(self, source):
        ''' 
        (n1/2) x (N2/n2) 
        '''
        n1, n2, _, N2 = self.count_n(source)
        difficulty = int((float(n1) / 2) * (float(N2) / n2))
        return difficulty
    
