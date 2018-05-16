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


class SQLComplexity():
    '''
        https://www.w3schools.com/sql/default.asp
    '''
    STATEMENTS = ('select ', 'insert ', 'update ', 'delete ', 'group ', 'order ', 'where ', 'having ', 'from ')
    
    FUNCTIONS = ('min', 'max', 'count', 'avg', 'sum')
    
    OPERATORS = ('+', '-', '*', '/', '%', 
                 '&', '|', '^', 
                 '=', '>', '<', '>=', '<=', '<>', 
                 '+=', '-+', '*=', '/=', '%=', '&=', '^-=', '|*=', 
                 'all', 'and', 'any', 'between', 'exists', 'in', 'like', 'not', 'or', 'some', 
                 'join') + FUNCTIONS
    
    IGNORE = ('as', 'on', 'into', 'by', 'distinct', 'limit', 'top', 'rownum', 'inner', 'left', 'right', 'outer') + STATEMENTS
    DETECT = ('and ', 'or ', 'join ') + STATEMENTS
    
    def __init__(self, max_complexity=10):
        self.max_complexity = max_complexity
        
    def is_sql(self, source):
        try:
            for statement in self.DETECT:
                source = source.lstrip('(')
                if source.lower().lstrip().startswith(statement):
                    return True
        except UnicodeDecodeError:
            pass
        return False
    
    def is_complexity(self, source):
        if self.is_sql(source):
            halstead = HalsteadComplexity(self.OPERATORS, self.IGNORE)
            difficulty = halstead.calcule_difficulty(source)
            return difficulty > self.max_complexity
        return False


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
                var = var+source[position]
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
        difficulty = (float(n1)/2)*(float(N2)/n2)
        return difficulty
    
if __name__ == '__main__':
    
    hc = HalsteadComplexity(SQLComplexity.OPERATORS, SQLComplexity.IGNORE)
    hc.calcule_difficulty('select x, y, z from table1 where x = 1 and y = 2')
    
    