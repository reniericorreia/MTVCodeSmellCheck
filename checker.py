# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast
from complexity import McCabeComplexity, HalsteadComplexity

def checker(models, views, managers, config):
    
    max_mccabe_complexity = float(config['max_mccabe_complexity'])
    min_mccabe_complexity = float(config['min_mccabe_complexity'])
    max_sql_complexity = float(config['max_sql_complexity'])
    min_sql_complexity = float(config['min_sql_complexity'])
    relationships = mapping_relationships(models, managers)
    
    violations = []
    
    for key in views.keys():
        md = MeddlingViewVisitor(key)
        md.visit(views[key])
        violations.extend(md.violations)
        
        bpm = BrainPersistenceMethodVisitor(key, max_mccabe_complexity, min_mccabe_complexity, max_sql_complexity, min_sql_complexity)
        bpm.visit(views[key])
        violations.extend(bpm.violations)
        
        lpm = LaboriousPersistenceMethodVisitor(key, relationships)
        lpm.visit(views[key])
        violations.extend(lpm.violations)
    
    for key in models.keys():
        mm = MeddlingModelVisitor(key)
        mm.visit(models[key])
        violations.extend(mm.violations)
        
        emu = ImproperUseOfManagerVisitor(key, relationships)
        emu.visit(models[key])
        violations.extend(emu.violations)
        
        bpm = BrainPersistenceMethodVisitor(key, max_mccabe_complexity, min_mccabe_complexity, max_sql_complexity, min_sql_complexity)
        bpm.visit(models[key])
        violations.extend(bpm.violations)
        
        lpm = LaboriousPersistenceMethodVisitor(key, relationships)
        lpm.visit(models[key])
        violations.extend(lpm.violations)
    
    result = []    
    if config.has_key('apps'):
        for violation in violations:
            if violation.app in config['apps'].split(';'):
                result.append(violation)
    else:
        result = violations
    return result
               
def mapping_relationships(models_node, managers_node):
    # identifica todos os managers do modelo
    managers = mapping_managers(managers_node)
    relationship = {}
    # identifica os atributos da classe que são relacionamentos com outras classes do modelo ou managers
    for key in models_node.keys():
        scan = ScanModelRelationships(key, managers, models_node)
        scan.visit(models_node[key])
        relationship.update(scan.models)
    return relationship

def mapping_managers(nodes):
    managers = []
    # mapeia todos os managers existentes no modelo
    for key in nodes.keys():
        scan = ScanModelManagers(key)
        scan.visit(nodes[key])
        managers.extend(scan.managers)
    return managers


class Checker(ast.NodeVisitor):
    '''
        Classe base para navegação no AST
    '''
    
    def __init__(self, module, models=None):
        self.imports = {}
        self.violations = []
        self.module = module
        self.models = models
        self.cls = None
        self.method = None 
        
    def visit_Module(self, node):
        self.generic_visit(node)
        #for violation in self.violations:
        #    print violation
            
    def visit_ImportFrom(self, node):
        for item in node.names:
            if node.level == 0:
                i = '{}.{}'.format(node.module, item.name)
            else:
                i = '{}.{}.{}'.format(".".join(self.module.split('.')[:-1]), node.module, item.name)
            
            temp = i.split('.')
            if '.models.' in i and len(temp) == 4:
                i = '.'.join([temp[0], temp[1], temp[3]]) 
            self.imports[item.asname or item.name] = i
            
    def visit_Import(self, node):
        for item in node.names:
            self.imports[item.asname or item.name] = item.name
    
    def visit_ClassDef(self, node):
        if "Meta" == node.name and self.cls:
            pass
        else:
            self.cls = node.name
            self.imports[self.cls] = "{}.{}".format(self.module, self.cls)
            self.pre_visit_ClassDef(node)
            self.generic_visit(node)
            self.cls = None
            
    def visit_FunctionDef(self, node):
        if self.method is None:
            self.method = node.name
        else:
            self.method = '{}>{}'.format(self.method, node.name)
        self.pre_visit_FuncitonDef(node)
        self.generic_visit(node)
        self.pos_visit_FuncitonDef(node)
        if '>' in self.method:
            index = self.method.rindex('>')
            self.method = self.method[:index]
        else:
            self.method = None
            
    def pre_visit_ClassDef(self, node):
        pass
    
    def pre_visit_FuncitonDef(self, node):
        pass
    
    def pos_visit_FuncitonDef(self, node):
        pass
    
    def add_violation(self, node):
        return self.violations.append(Violation(self.module, self.cls, self.method, node.lineno, self.smell))
    

class MeddlingViewVisitor(Checker):
    
    def __init__(self, module):
        self.smell = "Meddling View"
        Checker.__init__(self, module)
        
    def visit_ImportFrom(self, node):
        '''
            Adiciona na lista de imports as importações do django.db 
        '''
        for item in node.names:
            if node.level == 0:
                i = '{}.{}'.format(node.module, item.name)
            else:
                i = '{}.{}.{}'.format(".".join(self.module.split('.')[:-1]), node.module, item.name)
            if i.startswith("django.db"):
                self.imports[item.asname or item.name] = i
            
    def visit_Import(self, node):
        '''
            Adiciona na lista de imports as importações do django.db 
        '''
        for item in node.names:
            if item.name.startswith("django.db"):
                self.imports[item.asname or item.name] = item.name
            
    def visit_ClassDef(self, node):
        if self.cls is None:
            self.cls = node.name
        self.generic_visit(node)
        if not "Meta" == node.name:
            self.cls = None
    
    def visit_Str(self, node):
        '''
        Verifica se a string é um SQL
        '''
        if SQLComplexity().is_sql(node.s):
            self.add_violation(node)
            
    def visit_Name(self, node):
        '''
        Verifica se o atributo é um import do django.db 
        '''
        if self.imports.has_key(node.id):
            self.add_violation(node)


class MeddlingModelVisitor(Checker):
    '''
        https://www.w3schools.com/tags/ref_byfunc.asp
    '''        
    
    def __init__(self, module):
        self.smell = "Meddling Model"
        Checker.__init__(self, module)
        
            
    def visit_Str(self, node):
        '''
            Verifica se a string contém alguma tag HTML.
        '''
        tags_html = ["<html", "<head", "<body", "<p", "<span", "<form", "<input", "<link", "<div", "<h", "<d", "<a", '<br']
        for tag in tags_html:
            try:
                if tag in node.s.lower().lstrip():
                    self.add_violation(node)
                    break
            except UnicodeDecodeError:
                pass
            

class ImproperUseOfManagerVisitor(Checker):
    
    def __init__(self, module, models):
        self.smell = "Improper Use of Manager"
        self.is_assign = False
        self.relationships = {}
        Checker.__init__(self, module, models)
        
    def pre_visit_ClassDef(self, node):
        '''
            Adiciona self e o nome da classe na lista de relacionamentos.
        '''
        self.relationships = {}
        self.relationships['self'] = self.imports[node.name]
        self.relationships[node.name] = self.imports[node.name]
        
    def visit_ClassDef(self, node):
        classe = '.'.join(self.module.split('.')[0:2] + [node.name])
        if self.models.has_key(classe):
            Checker.visit_ClassDef(self, node)
        
    def visit_Assign(self, node):
        '''
            Guarda informação que o node faz parte de uma atribuição.
        '''
        self.is_assign = True
        self.generic_visit(node)
        self.is_assign = False
        
    def visit_Call(self, node):
        '''
            Adiciona os relacionamentos com outras classes de modelo na lista de relacionamentos da classe.
            Verifica se a chamada executada é um manager e se esse manager é um dos relacionamentos da classe.
        '''
        if self.is_attribute_class():
            name = self.calcule_Attribute(node.func)
            for value in ['models.ForeignKey', 'models.OneToOneField', 'models.ManyToManyField', 'GenericRelation']:
                if value in name:
                    arg = node.args[0]
                    if isinstance(arg, ast.Name):
                        if self.imports.has_key(arg.id):
                            self.relationships[arg.id] = self.imports[arg.id]
                            break
                        else:
                            self.relationships[arg.id] = arg.id
                            break
                    elif isinstance(arg, ast.Attribute):
                        pass
                    else:
                        if 'self' == arg.s:
                            self.relationships[self.cls] = self.imports[self.cls]
                            break
                        elif len(arg.s.split('.')) == 1:
                            self.relationships[arg.s] = "{}.{}".format(self.module, arg.s)
                            break
                        else:
                            self.relationships[arg.s.split('.')[1]] = arg.s
                            break
        elif self.cls and self.method:
            name = self.calcule_Attribute(node.func)
            split = name.split('.')
            if len(split) > 1:
                cls = split[0]
                method = split[1]
                if cls and not self.is_relationship(cls) and self.is_model(cls) \
                    and self.is_use_manager(cls, method):
                    self.add_violation(node)
        else:
            self.generic_visit(node)
        
    def calcule_Attribute(self, node):
        '''
            Identifica o nome do atributo que está execuntando uma chamada.
        '''
        name = []
        if isinstance(node, ast.Name):
            name.append(node.id)
        elif isinstance(node, ast.Call):
            name.append(self.calcule_Attribute(node.func))
        elif isinstance(node.value, ast.Call):
            name.append(self.calcule_Attribute(node.value.func))
            name.append(node.attr)
        elif isinstance(node.value, ast.Name):
            name.append(node.value.id)
            name.append(node.attr)
        elif isinstance(node.value, ast.Attribute):
            name.append(self.calcule_Attribute(node.value))
            name.append(node.attr)
        return ".".join(name) or ''
    
    def is_attribute_class(self):
        '''
            Verifica se é um atributo de classe.
        '''
        return self.is_assign and self.cls and not self.method
    
    def is_use_manager(self, cls, method):
        '''
            Verifica se método executado pelo objeto/atributo é um manager.
        '''
        if self.imports.has_key(cls):
            split = self.imports[cls].split('.')
            key = '{}.{}.{}'.format(split[0], split[1], cls) 
            if self.models.has_key(key):
                managers = self.models[key][0]['managers']
                for manager in managers:
                    if manager == method:
                        return True
        return False
    
    def is_relationship(self, cls):
        '''
            Verifica se o objeto/atributo faz parte dos relacionamentos da classe verificada.
        '''
        is_relationship = False
        if self.relationships.has_key(cls):
            # relacionamento direto
            is_relationship =  True
        elif self.imports.has_key(cls):
            pk = self.imports[cls]
            if self.models.has_key(pk) and '{}.{}'.format(self.module.split('.')[0], self.cls) in self.models[pk]:
                # relacionamento reverso
                is_relationship = True
        return is_relationship
    
    def is_model(self, cls):
        '''
            Verifica se o objeto/atributo que executa uma chamada é instância de uma classe de modelo. 
        '''
        if self.imports.has_key(cls):
            packages = self.imports[cls].split(".")
            return "models" in packages and not "django" in packages
        return False    
   
   
class BrainPersistenceMethodVisitor(Checker):
  
    def __init__(self, module, max_code, min_code, max_sql, min_sql):
        self.smell = "Brain Persistence Method"
        self.max_code = max_code
        self.min_code = min_code
        self.min_sql = min_sql
        self.max_sql = max_sql
        Checker.__init__(self, module)
    
    def visit_FunctionDef(self, node):
        '''
            Avalia a complexidade código e do SQL no método. 
        '''
        self.method = node.name
        code = McCabeComplexity().calcule(node)
        if code >= self.min_code:
            sql = SQLComplexity().calcule(node)
            if (sql >= self.max_sql and code >= self.min_code) or (sql >= self.min_sql and 
                                                                   code >= self.max_code):
                self.add_violation(node)
        self.method = None


class LaboriousPersistenceMethodVisitor(Checker):
    
    def __init__(self, module, models):
        self.smell = "Laborious Persistence Method"
        self.count = 0
        self.is_assign = False
        self.querys = []
        self.cursor = None
        Checker.__init__(self, module, models)
    
    def pre_visit_FuncitonDef(self, _):
        '''
            reinicia variáveis antes de analisar nova função.
        '''
        self.count = 0
        self.querys = []
        self.cursor = None
        
    def pos_visit_FuncitonDef(self, node):
        '''
            Adiciona mensagem de violação se houver mais de uma chamada a métodos de persistência.
        '''
        if self.count > 1:
            self.add_violation(node)
        self.count = 0
        self.querys = []
        
    def visit_Assign(self, node):
        self.is_assign = True
        self.generic_visit(node)
        if self.cursor == True:
            self.cursor = node.targets[0].id
        self.is_assign = False
    
    def visit_Call(self, node):
        '''
            Verifica chamadas executadas dentro de métodos.
            Verifica se chamada é executada pelo método raw (manager) ou  execute (django.db)
        '''
        if self.method:
            name = self.visit_Attribute(node.func)
            split = name.split('.')
            if len(split) > 1:
                cls = split[0]
                method = split[1]
                method_2 = len(split) > 2 and split[2] or None
                if cls and method and (self.is_api_persistence(cls, method) or 
                                       self.is_manager_raw(cls, method, method_2)):
                    self.count+=1
        else:
            self.generic_visit(node)
    
    def is_manager_raw(self, cls, method, method_2):
        '''
            Verifica se chamada executada é manager.raw()
        '''
        if 'raw' == method_2 and self.imports.has_key(cls):
            split = self.imports[cls].split('.')
            key = '{}.{}.{}'.format(split[0], split[1], cls) 
            if self.models.has_key(key):
                managers = self.models[key][0]['managers']
                for manager in managers:
                    return manager == method
        return False
    
    def is_api_persistence(self, cls, method):
        '''
            Verifica se chamada executada é django.db.connection.cursor.execute()
        '''
        if self.is_assign:
            if self.imports.has_key(cls):
                package = self.imports[cls]
                if 'django.db.connection' == package and 'cursor' == method:
                    self.cursor = True
                    return False
        elif self.cursor and self.cursor == cls and 'execute' == method: return True
        else: return False    
    
    def visit_Attribute(self, node):
        '''
            Identifica nome do objeto que executa chamada.
        '''
        name = []
        if isinstance(node, ast.Name):
            name.append(node.id)
        elif isinstance(node, ast.Call):
            name.append(self.visit_Attribute(node.func))
        elif isinstance(node.value, ast.Name):
            name.append(node.value.id)
            name.append(node.attr)
        elif isinstance(node.value, ast.Attribute):
            name.append(self.visit_Attribute(node.value))
            name.append(node.attr)
        return ".".join(name) or ''    


class ScanModelRelationships(Checker):
        
    def __init__(self, module, managers, models_node):
        self.managers = managers
        self.is_assign = False
        self.obj_manager = None
        self.models_node = models_node
        Checker.__init__(self, module, {})
        
    def pre_visit_ClassDef(self, node):
        # verifica se classe é do tipo Model
        is_model = False
        for heranca in node.bases:
            classe_heranca = None
            if isinstance(heranca, ast.Name):
                classe_heranca = heranca.id
            elif isinstance(heranca, ast.Attribute):
                classe_heranca = heranca.attr
            if classe_heranca and 'Model' in classe_heranca:
                is_model = True
                break
            else:
                if self.imports.has_key(classe_heranca):
                    key_module = '.'.join(self.imports[classe_heranca].split('.')[:-1])
                    if self.models_node.has_key(key_module):
                        scan = ScanModelBases(classe_heranca, self.models_node[key_module])
                        scan.visit(self.models_node[key_module])
                        is_model = scan.is_model
                        if is_model:
                            break
                                     
        if is_model:
            module = self.module
            temp = module.split('.')
            # padroniza o identificador chave de cada modelo
            if '.models.' in module and len(temp) == 3:
                module = '.'.join([temp[0], temp[1]]) 
            self.key = '{}.{}'.format(module, node.name)
            # adiciona na lista de managers o manager padrão
            self.models[self.key] = [{'managers':['objects']}]
        
    def visit_Assign(self, node):
        if hasattr(self, "key"):
            self.is_assign = True
            self.generic_visit(node)
            # adiciona atributo na lista de managers se ele for do tipo Manager
            if self.obj_manager:
                name_manager = node.targets[0].id
                self.models[self.key][0]['managers'].append(name_manager)
            self.obj_manager = None
            self.is_assign = False
        
    def visit_Call(self, node):
        if hasattr(self, "key") and self.is_attribute_class():
            name = self.visit_Attribute(node.func)
            # identifica se atributo é do tipo Manager
            if self.imports.has_key(name) and self.imports[name] in self.managers:
                self.obj_manager = self.imports[name]
            else:
                # adiciona o tipo do modelo se o atributo for relacionamento com outro modelo
                for value in ['models.ForeignKey', 'models.OneToOneField', 'models.ManyToManyField']:
                    if value in name:
                        arg = node.args[0]
                        if isinstance(arg, ast.Name):
                            if self.imports.has_key(arg.id):
                                cls = '{}.{}'.format(self.imports[arg.id].split('.')[0], arg.id)
                                self.models[self.key].append(cls)
                                break
                            else:
                                cls = '{}.{}'.format(self.module.split('.')[0], arg.id)
                                self.models[self.key].append(cls)
                                break
                        elif isinstance(arg, ast.Attribute):
                            pass
                        else:
                            if 'self' == arg.s:
                                break
                            elif len(arg.s.split('.')) == 1:
                                cls = "{}.{}".format(self.module.split('.')[0], arg.s)
                                self.models[self.key].append(cls)
                                break
                            else:
                                self.models[self.key].append(arg.s)
                                break
        else:
            self.generic_visit(node)
    
    def visit_Attribute(self, node):
        # identifica o tipo do atributo
        name = []
        if isinstance(node, ast.Name):
            name.append(node.id)
        elif isinstance(node, ast.Call):
            name.append(self.visit_Attribute(node.func))
        elif isinstance(node.value, ast.Name):
            name.append(node.value.id)
            name.append(node.attr)
        elif isinstance(node.value, ast.Attribute):
            name.append(self.visit_Attribute(node.value))
            name.append(node.attr)
        return ".".join(name) or ''
    
    def is_attribute_class(self):
        # identifica se é um atributo de classe
        return self.is_assign and self.cls and not self.method


class ScanModelBases(ast.NodeVisitor):
    
    def __init__(self, classe_base, node_original):
        self.classe_base = classe_base
        self.node_original = node_original
        self.is_model = False
    
    def visit_ClassDef(self, node):
        if self.classe_base == node.name:
            for base in node.bases:
                classe = None
                if isinstance(base, ast.Name):
                    classe = base.id
                elif isinstance(base, ast.Attribute):
                    classe = base.attr
                if 'Model' in classe:
                    self.is_model = True
                    break
                else:
                    scan = ScanModelBases(classe, self.node_original)
                    scan.visit(self.node_original)
                    self.is_model = scan.is_model
    

class ScanModelManagers(ast.NodeVisitor):
    
    def __init__(self, module):
        self.managers = []
        self.module = module
    
    def visit_ClassDef(self, node):
        # se classe herdar de Manager então adiciona na lista de managers
        for heranca in node.bases:
            if isinstance(heranca, ast.Name) and 'Manager' in heranca.id:
                self.managers.append('{}.{}'.format(self.module, node.name))
            elif isinstance(heranca, ast.Attribute) and 'Manager' in heranca.attr:
                self.managers.append('{}.{}'.format(self.module, node.name))


class SQLComplexity(ast.NodeVisitor):
    '''
        https://www.w3schools.com/sql/default.asp
    '''
    STATEMENTS = ('select', 'insert', 'update', 'delete', 'group', 'order', 'where', 'having', 'from', 'create', 'drop','with')
    
    FUNCTIONS = ('min', 'max', 'count', 'avg', 'sum', 'coalesce')
    
    OPERATORS = ('+', '-', '*', '/', '%',
                 '&', '|', '^',
                 '=', '>', '<', '>=', '<=', '<>',
                 '+=', '-+', '*=', '/=', '%=', '&=', '^-=', '|*=',
                 'all', 'and', 'any', 'between', 'union', 'exists', 'in', 'like', 'not', 'or', 'some',
                 'join', 'limit', 'is') + FUNCTIONS + STATEMENTS
    
    IGNORE = ('as', 'on', 'into', 'by', 'distinct', 'top', 'rownum', 'inner', 'left', 'right', 'outer', 'desc', 'asc')
    DETECT = ('and ', 'or ', 'join ', 'select ', 'insert', 'update ', 'delete ', 'group ',
               'order ', 'where ', 'having ', 'from ', 'create ', 'drop ', 'with ')
    
    '''
        ignorar coisas depois do filter
        notas_4 = matriculas_diarios.filter(nota_4__isnull=False).aggregate(media=Avg('nota_4'), minima=Min('nota_4'),maxima=Max('nota_4')
        atendimentos_do_mes = demandas_atendidas.filter(demanda__nome=demanda.nome)
        atendimentos_do_mes.aggregate(Sum('quantidade'))['quantidade__sum'] or 0]
    '''
    
    def visit_Assign(self, node):
        self.is_assign = True
        self.generic_visit(node)
        self.is_assign = False
    
    def visit_Str(self, node):
        source = node.s
        if self.is_assign and self.is_sql(source):
            self.source = ' '.join([self.source, source])
            
    def calcule(self, node):
        self.is_assign = False
        self.source = ''
        self.visit(node)
        if self.source != '':
            return self.complexity(self.source)
        return -1
    
    def complexity(self, source):
        return HalsteadComplexity(self.OPERATORS, self.IGNORE).calcule_difficulty(source)        
                
    def is_sql(self, source):
        try:
            for statement in self.DETECT:
                source = source.lstrip('(')
                if source.lower().lstrip().startswith(statement):
                    return True
        except UnicodeDecodeError:
            pass
        return False


class Violation():
    def __init__(self, module, cls, method, line, smell):
        self.app = module.split('.')[0]
        self.module = module.split('.')[1]
        self.cls = cls
        self.method = method
        self.line = line
        self.smell = smell
        
    def __str__(self):
        return '{};{};{};{};{};{};'.format(self.smell, self.app, self.module, self.cls or '-', self.method or '-', self.line)
    
    def __unicode__(self):
        return self.__str__()

