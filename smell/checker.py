# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast
from smell.complexity import McCabeComplexity, SQLComplexity, HalsteadComplexity

def checker(models, views, managers, config):
    for key in views.keys():
        MeddlingViewVisitor(key).visit(views[key])
    
    relationships = mapping_relationships(models, managers)
    for key in models.keys():
        MeddlingModelVisitor(key).visit(models[key])
        FatRepositoryVisitor(key, relationships).visit(models[key])
        LaboriousRepositoryMethodVisitor(key, relationships).visit(models[key])
        complexitys = McCabeComplexity(int(config['mccabe_complexity'])).calcule(models[key])
        BrainRepositoryVisitor(key, complexitys, int(config['sql_complexity'])).visit(models[key])
        
def counts(models, views):
    for key in models.keys():
        CountSQLVisitor(key).visit(models[key])
    for key in views.keys():
        CountSQLVisitor(key).visit(views[key])
    
    
def mapping_relationships(models, managers):
    # identifica todos os managers do modelo
    managers = mapping_managers(managers)
    relationship = {}
    # identifica os atributos da classe que são relacionamentos com outras classes do modelo ou managers
    for key in models.keys():
        scan = ScanModelRelationships(key, managers)
        scan.visit(models[key])
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
            #print violation
            print '{}.{}.{}.{}.{}'.format(violation.smell, violation.module, violation.cls or '-', violation.method or '-', violation.line)
            
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
    

class MeddlingViewVisitor(SmellBase):
    '''
        Uma visão conter uma dependência para api de persistência 'django.db' ou construir strings SQLs
        
        [x] Mapear imports do módulo 'django.db'
        [x] Procurar uso de alguma classe ou função do módulo 'django.db'
        [x] Procurar uso de alguma string contendo ["SELECT", "UPDATE", "DELETE", "INSERT", "CREATE"]
        [ ] Implementar busca em strings com expressão regular
    '''        
    
    def __init__(self, module):
        self.smell = "Meddling View"
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
        if SQLComplexity().is_sql(node.s):
            self.add_violation(node)
            
    def visit_Name(self, node):
        if self.imports.has_key(node.id):
            self.add_violation(node)


class MeddlingModelVisitor(SmellBase):
    '''
        Um modelo construir strings HTML
        
        https://www.w3schools.com/tags/ref_byfunc.asp
        
        [ ] Implementar busca em strings com expressão regular
    '''        
    
    def __init__(self, module):
        self.smell = "Meddling Model"
        SmellBase.__init__(self, module)
        
            
    def visit_Str(self, node):
        tags_html = ["<html", "<head", "<body", "<p", "<span", "<form", "<input", "<link", "<div"]
        for tag in tags_html:
            try:
                if tag in node.s.lower():
                    self.add_violation(node)
                    break
            except UnicodeDecodeError:
                pass
            
   
class BrainRepositoryVisitor(SmellBase):
    '''
        Lógica complexa no repositório
    '''
    def __init__(self, module, complexity, max_sql):
        self.smell = "Brain Repository"
        self.complexity = complexity
        self.sql_statement = ''
        self.sql_complexity = SQLComplexity(max_sql)
        self.is_assign = False
        SmellBase.__init__(self, module)
    
    def visit_ClassDef(self, node):
        # verifica a classe se ela contiver algum método complexo (mccabe)
        if self.complexity.has_key(node.name):
            SmellBase.visit_ClassDef(self, node)
        
    def visit_FunctionDef(self, node):
        # verifica o método se ele for complexo (mccabe)
        if self.cls and node.name in self.complexity[self.cls]:
            SmellBase.visit_FunctionDef(self, node)
    
    def pre_visit_FuncitonDef(self, _):
        self.sql_statement = ''
    
    def pos_visit_FuncitonDef(self, node):
        if self.sql_complexity.is_complexity(self.sql_statement):
            self.add_violation(node)
    
    def visit_Assign(self, node):
        self.is_assign = True
        self.generic_visit(node)
        self.is_assign = False
    
    def visit_Str(self, node):
        sql = node.s
        if self.is_assign and self.sql_complexity.is_sql(sql):
            self.sql_statement = ' '.join([self.sql_statement, sql]) 
            
        
class CountSQLVisitor(SmellBase):
    def __init__(self, module):
        self.sql_statement = ''
        self.is_assign = False   
        SmellBase.__init__(self, module)
        
    def pre_visit_FuncitonDef(self, _):
        self.sql_statement = ''
    
    def pos_visit_FuncitonDef(self, node):
        if self.sql_statement:
            hc = HalsteadComplexity(SQLComplexity.OPERATORS, SQLComplexity.IGNORE)
            n1, n2, N1, N2 = hc.count_n(self.sql_statement)
            print '{}.{}.{}.{}.{}.{}.{}'.format(self.module, self.cls or '-', node.name, n1, n2, N1, N2)
            
    def visit_Assign(self, node):
        self.is_assign = True
        self.generic_visit(node)
        self.is_assign = False   
               
    def visit_Str(self, node):
        sql = node.s
        if self.is_assign and SQLComplexity().is_sql(sql):
            self.sql_statement = ' '.join([self.sql_statement, sql]) 
                

class LaboriousRepositoryMethodVisitor(SmellBase):
    '''
        Um método de repositório com várias ações no banco de dados
        
        [x] Identificar chamada ao método django.db.connection.cursor().execute(query)
        [x] Identificar chamada a 'manager.raw()'
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
                #elif 'djtools.db' == package and method in ['get_dict', 'get_dict_dict', 'get_list', 'get_list_extra']:
                #    return True
                
        elif self.cursor and self.cursor == cls and 'execute' == method:
            return True
        else:
            return False


class FatRepositoryVisitor(SmellBase):
    '''
        um modelo deve acessar apenas os seus próprios      ou os managers das entidades que se relacionam diretamente ou inversamente a ele.
        
        [x] Identificar os relacionamentos do modelo (models.ForeignKey, models.OneToOneField e models.ManyToManyField)
        [x] Identificar modelos usados que não são relacionamento direto ou reverso
        [x] Identificar managers dos modelos não relacionadas (models.Manager)
        [ ] Verificar superclass nos casos em que houver herança.
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
        # verifica se classe é do tipo Model
        is_model = False
        for heranca in node.bases:
            if (isinstance(heranca, ast.Name) and 'Model' in heranca.id) or (isinstance(heranca, ast.Attribute) and 'Model' in heranca.attr):
                is_model = True
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
        self.is_assign = True
        self.generic_visit(node)
        # adiciona atributo na lista de managers se ele for do tipo Manager
        if self.obj_manager:
            name_manager = node.targets[0].id
            self.models[self.key][0]['managers'].append(name_manager)
        self.obj_manager = None
        self.is_assign = False
        
    def visit_Call(self, node):
        if self.is_attribute_class():
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

