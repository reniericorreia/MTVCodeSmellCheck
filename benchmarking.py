# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import ast
from converter import SourceToAST
from complexity import McCabeComplexity
from checker import SQLComplexity

'''
Ao inves de calcular os thresholds de maneira uniforme em todo o código, é identificado as responsabilidades arquiteturais de cada classe/função e 
verificado se existe uma diferença grande entre a métrica geral e a métrica da regra arquitetural.



Arquitetura de aplicações baseadas em Django (MTV)
M. Model: contém as regras de negócio e acesso à base de dados
V. Template: apresentação dos dados
V. View: consulta o modelo e seleciona quais dados exibir
V. Admin: implementa layout padrão de CRUD
V. Form: implementa layout de formulário para cadastro/edição do modelo

Método:
1. Dataset creation > Selecionar sistema para análise da arquitetura. 
2. Architectural roles extraction > Identificar as responsabilidades das classes/funções.
3. Metrics calculation > Calcular as métricas de todas as classes/funções.
4. Statistical measurement > Medir a diferença entre as métricas das classes/funções responsabilidades arquiteturais com as demais.
5. Analysis of the statistical tests > Verifica se a diferença é significativa para prosseguir.
6. Weight ratio calculation > Analisa somemnte classes/funções com papel arquitetural.
7. Weight ratio aggregation > Ordena as classes de acordo com os valores métricos.
8. Thresholds derivation > Extrai o valor da métrica de código da classe que tem sua agregação de peso mais próxima de 70% (moderada), 80% (alta) e 90% (muito alta).

'''


def get_LOC(filename):
    '''
        ignora linhas em branco e comentários
    '''
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
    '''
    tipos desconsiderados (código gerado automaticamente): migrations
    '''
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
    '''
- definir trehsholds
- validar catálogo
 - medir criticidade
 - estudo de caso
  - objetivo: analisar o estado do suap
- validar ferramenta
 - falsos positivos
- mudar smell para violações de design


quantidade de metodos por classe
complexidade do método

quantidade de funções de visão por módulo
complexidade da função
complexidade do sql


    '''

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

