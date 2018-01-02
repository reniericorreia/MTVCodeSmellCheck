# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast


class SmellBase(ast.NodeVisitor):
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
        
    def add_violation(self, node):
        return self.violations.append(Violation(self.module, self.cls, self.method, node.lineno, self.smell))
    
    def visit_Module(self, node):
        self.generic_visit(node)
        for violation in self.violations:
            print violation
            
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
        if "Meta" == node.name:
            pass
        else:
            self.cls = node.name
            self.imports[self.cls] = "{}.{}".format(self.module, self.cls)
            self.pre_visit_ClassDef(node)
            self.generic_visit(node)
            self.cls = None
            
    def pre_visit_ClassDef(self, node):
        pass
    
    def visit_FunctionDef(self, node):
        self.method = node.name
        self.pre_visit_FuncitonDef(node)
        self.generic_visit(node)
        self.pos_visit_FuncitonDef(node)
        self.method = None
    
    def pre_visit_FuncitonDef(self, node):
        pass
    
    def pos_visit_FuncitonDef(self, node):
        pass
    

class MeddlingServiceVisitor(SmellBase):
    '''
        Uma visão conter uma dependência para api de persistência 'django.db' ou construir strings SQLs
        
        [x] Mapear imports do módulo 'django.db'
        [x] Procurar uso de alguma classe ou função do módulo 'django.db'
        [x] Procurar uso de alguma string contendo ["SELECT", "UPDATE", "DELETE", "FROM", "WHERE", "JOIN", "TABLE", "CREATE"]
        [ ] Implementar busca em strings com expressão regular
    '''        
    
    def __init__(self, module):
        self.smell = "Meddling Service"
        SmellBase.__init__(self, module)
        
    def visit_ImportFrom(self, node):
        for item in node.names:
            if node.level == 0:
                i = '{}.{}'.format(node.module, item.name)
            else:
                i = '{}.{}.{}'.format(".".join(self.module.split('.')[:-1]), node.module, item.name)
            if i.startswith("django.db"):
                self.add_violation(node)
                self.imports[item.asname or item.name] = i
            
    def visit_Import(self, node):
        for item in node.names:
            if item.name.startswith("django.db"):
                self.add_violation(node)
                self.imports[item.asname or item.name] = item.name
            
    def visit_Str(self, node):
        EXPR_SQL = ["SELECT", "UPDATE", "DELETE", "FROM", "WHERE", "JOIN", "TABLE", "CREATE"]
        for sql in EXPR_SQL:
            try:
                if sql in node.s:
                    self.add_violation(node)
                    break
            except UnicodeDecodeError:
                pass
            
    def visit_Name(self, node):
        if self.imports.has_key(node.id):
            self.add_violation(node)

   
class BrainRepositoryVisitor(SmellBase):
    '''
        [ ] Medir complexidade de McCabe
        [ ] Medir complexidade do SQL
            [ ] Quantidade de comandos SQLs (WHERE, AND, OR, JOIN, EXISTS, NOT, FROM, XOR, IF, ELSE, CASE, IN) 
    '''
    pass


class LaboriousRepositoryMethodVisitor(SmellBase):
    '''
        Um método de repositório executar mais de uma query string
        
        [x] Identificar chamada ao método django.db.connection.cursor().execute(query)
        [x] Identificar chamada a 'manager.raw()'
        [x] Identificar chamada aos métodos 'get_dict, get_dict_dict, get_list, get_list_extra' (implementação do SUAP).
        [x] Adicionar violação se houver dois ou mais acessos ao bd no mesmo método.
    '''
    
    def __init__(self, module, models):
        self.smell = "Laborious Repository Method"
        self.count = 0
        self.is_assign = False
        self.querys = []
        self.cursor = None
        SmellBase.__init__(self, module, models)
    
    def pre_visit_FuncitonDef(self, node):
        self.count = 0
        self.querys = []
        self.cursor = None
        
    def pos_visit_FuncitonDef(self, node):
        if self.count > 1:
            self.add_violation(node)
        self.querys = []
        self.count = 0
        
    def visit_Assign(self, node):
        self.is_assign = True
        self.generic_visit(node)
        if self.cursor == True:
            self.cursor = node.targets[0].id
        self.is_assign = False
    
    def visit_Call(self, node):
        if self.cls and self.method:
            name = self.visit_Attribute(node.func)
            split = name.split('.')
            if len(split) > 1:
                cls = split[0]
                method = split[1]
                method_2 = len(split) > 2 and split[2] or None
                if cls and method and (self.is_api_persistence(cls, method) or self.is_manager_raw(cls, method, method_2)):
                    self.count+=1
        else:
            self.generic_visit(node)
        
    def visit_Attribute(self, node):
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
    
    def is_manager_raw(self, cls, method, method_2):
        if 'raw' == method_2 and self.imports.has_key(cls):
            split = self.imports[cls].split('.')
            key = '{}.{}.{}'.format(split[0], split[1], cls) 
            if self.models.has_key(key):
                managers = self.models[key][0]['managers']
                for manager in managers:
                    if manager == method:
                        return True
        return False
    
    def is_api_persistence(self, cls, method):
        if self.is_assign:
            if self.imports.has_key(cls):
                package = self.imports[cls]
                if 'django.db.connection' == package and 'cursor' == method:
                    self.cursor = True
                    return False
                # Checkagem específica para o SUAP.
                elif 'djtools.db' == package and method in ['get_dict', 'get_dict_dict', 'get_list', 'get_list_extra']:
                    return True
                
        elif self.cursor and self.cursor == cls and 'execute' == method:
            return True


class FatRepositoryVisitor(SmellBase):
    '''
        Um model acessar managers de entidades que não são atributos/relacionamentos diretos ou reversos dele.
        
        [x] Mapear atributos de relacionamento da classe (models.ForeignKey, models.OneToOneField e models.ManyToManyField)
        [x] Identificar entidades usadas na classe que não tem relacionamento direto
        [x] Identificar entidades usadas na classe que não tem relacionamento reverso
        [x] Identificar managers das entidades não relacionadas (models.Manager) - https://docs.djangoproject.com/en/2.0/topics/db/managers/
        [ ] Realizar procedimentos nas heranças se houver.
    '''
    
    def __init__(self, module, models):
        self.smell = "Fat Repository"
        self.is_assign = False
        self.relationships = {}
        SmellBase.__init__(self, module, models)
        
    def pre_visit_ClassDef(self, node):
        self.relationships['self'] = self.imports[node.name]
        self.relationships[node.name] = self.imports[node.name]
        
    def visit_Assign(self, node):
        self.is_assign = True
        self.generic_visit(node)
        self.is_assign = False
    
    def visit_Call(self, node):
        if self.is_attribute_class():
            name = self.visit_Attribute(node.func)
            for value in ['models.ForeignKey', 'models.OneToOneField', 'models.ManyToManyField']:
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
            name = self.visit_Attribute(node.func)
            split = name.split('.')
            if len(split) > 1:
                cls = split[0]
                method = split[1]
                if cls and not self.is_relationship(cls) and self.is_model(cls) and self.is_use_manager(cls, method):
                    self.add_violation(node)
        else:
            self.generic_visit(node)
        
    def visit_Attribute(self, node):
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
        return self.is_assign and self.cls and not self.method
    
    def is_use_manager(self, cls, method):
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
        is_relationship = False
        if self.relationships.has_key(cls):
            is_relationship =  True
        elif self.imports.has_key(cls):
            pk = self.imports[cls]
            if self.models.has_key(pk) and '{}.{}'.format(self.module.split('.')[0], self.cls) in self.models[pk]:
                is_relationship = True
        return is_relationship
    
    def is_model(self, cls):
        if self.imports.has_key(cls):
            packages = self.imports[cls].split(".")
            return "models" in packages and not "django" in packages
        return False 
        

class ScanModelRelationships(SmellBase):
        
    def __init__(self, module, managers):
        self.managers = managers
        self.is_assign = False
        self.obj_manager = None
        SmellBase.__init__(self, module, {})
    
    def pre_visit_ClassDef(self, node):
        module = self.module
        temp = module.split('.')
        if '.models.' in module and len(temp) == 3:
            module = '.'.join([temp[0], temp[1]]) 
        self.key = '{}.{}'.format(module, node.name)
        self.models[self.key] = [{'managers':['objects']}]
        
    def visit_Assign(self, node):
        self.is_assign = True
        self.generic_visit(node)
        if self.obj_manager:
            name_manager = node.targets[0].id
            self.models[self.key][0]['managers'].append(name_manager)
        self.obj_manager = None
        self.is_assign = False
        
    def visit_Call(self, node):
        if self.is_attribute_class():
            name = self.visit_Attribute(node.func)
            if self.imports.has_key(name) and self.imports[name] in self.managers:
                self.obj_manager = self.imports[name]
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
        return self.is_assign and self.cls and not self.method


class ScanModelManagers(ast.NodeVisitor):
    
    def __init__(self, module):
        self.managers = []
        self.module = module
    
    def visit_ClassDef(self, node):
        split = self.module.split('.')
        if 'managers' == split[1]:
            self.managers.append('{}.{}'.format(self.module, node.name))
        

class Violation():
    def __init__(self, module, cls, method, line, smell):
        self.module = module
        self.cls = cls
        self.method = method
        self.line = line
        self.smell = smell
        
    def __str__(self):
        cls = ''
        if self.cls:
            cls = '.{}'.format(self.cls)
        method = ''
        if self.method:
            method = '.{}'.format(self.method)
        return "{}: {}{}{} ({})".format(self.smell, self.module, cls, method, self.line)
    
    def __unicode__(self):
        return self.__str__()

