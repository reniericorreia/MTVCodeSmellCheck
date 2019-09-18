# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import pandas as pd


def export_csv(head=[], datalist=[], filename='export_csv.csv', delimitator=';'):
    c = csv.writer(open(filename, "wb"))
    c.writerow(head)
    for data in datalist:
        c.writerow(data.__str__().split(delimitator))
    print('   - {}'.format(filename))

def exportar_csv(methods, functions):
    c = csv.writer(open("metrics_report.csv", "wb"))
    c.writerow(["app", "modulo", "classe", "metodo", "mccabe", "sql"])
    for key in methods.keys():
        keys = key.split('.')
        values = methods[key].split(';')
        c.writerow([keys[0], keys[1], keys[-2], keys[-1], values[0], values[1]])
        
    for key in functions.keys():
        keys = key.split('.')
        values = functions[key].split(';')
        c.writerow([keys[0], keys[1], '-', keys[-1], values[0], values[1]])


def print_metrics(methods, functions):
    methods.update(functions)
    list_complexidade_ciclomatica = []
    list_complexidade_sql = []
    list_complexidade_ciclomatica_models = []
    list_complexidade_sql_models = []
    list_complexidade_ciclomatica_views = []
    list_complexidade_sql_views = []
    list_complexidade_ciclomatica_admin = []
    list_complexidade_sql_admin = []
    list_complexidade_ciclomatica_forms = []
    list_complexidade_sql_forms = []
    list_complexidade_ciclomatica_outros = []
    list_complexidade_sql_outros = []
    for key in methods.keys():
        values = methods[key].split(';')
        contains_sql = values[1] != '-1'
        list_complexidade_ciclomatica.append(int(values[0]))
        if contains_sql:
            list_complexidade_sql.append(round(float(values[1]),2))
        if 'models' in key:
            list_complexidade_ciclomatica_models.append(int(values[0]))
            if contains_sql:
                list_complexidade_sql_models.append(round(float(values[1]),2))
        elif 'views' in key:
            list_complexidade_ciclomatica_views.append(int(values[0]))
            if contains_sql:
                list_complexidade_sql_views.append(round(float(values[1]),2))
        elif 'admin' in key:
            list_complexidade_ciclomatica_admin.append(int(values[0]))
            if contains_sql:
                list_complexidade_sql_admin.append(round(float(values[1]),2))
        elif 'forms' in key:
            list_complexidade_ciclomatica_forms.append(int(values[0]))
            if contains_sql:
                list_complexidade_sql_forms.append(round(float(values[1]),2))
        else:
            list_complexidade_ciclomatica_outros.append(int(values[0]))
            if contains_sql:
                list_complexidade_sql_outros.append(float(values[1]))
    
    series_complexidade_ciclomatica = pd.Series(list_complexidade_ciclomatica)
    print '[todos] Total de métodos: ', len(list_complexidade_ciclomatica)
    print 'Complexidade Ciclomática Média: ', series_complexidade_ciclomatica.mean()
    print 'Complexidade Ciclomática Mediana: ', series_complexidade_ciclomatica.median()
    print 'Complexidade Ciclomática Quantil (LOW): ', series_complexidade_ciclomatica.quantile(q=0.25)
    print 'Complexidade Ciclomática Quantil (MEDIUM): ', series_complexidade_ciclomatica.quantile(q=0.5)
    print 'Complexidade Ciclomática Quantil (HIGH): ', series_complexidade_ciclomatica.quantile(q=0.75)
    print 'Complexidade Ciclomática Moda: ', series_complexidade_ciclomatica.mode()
    print 'Complexidade Ciclomática Mínima: ', series_complexidade_ciclomatica.min()
    print 'Complexidade Ciclomática Máxima: ', series_complexidade_ciclomatica.max()
    print 'Complexidade Ciclomática Variância: ', series_complexidade_ciclomatica.var()
    print 'Complexidade Ciclomática Desvio Padrão: ', series_complexidade_ciclomatica.std()
    print 'Complexidade Ciclomática Desvio Absoluto: ', series_complexidade_ciclomatica.mad()
    print '--------------------------------------------\n'
    series_complexidade_sql = pd.Series(list_complexidade_sql)
    print '[todos] Total de métodos com SQL: ', len(list_complexidade_sql)
    print 'Complexidade do SQL Média: ', series_complexidade_sql.mean()
    print 'Complexidade do SQL Mediana: ', series_complexidade_sql.median()
    print 'Complexidade do SQL Quantil (LOW): ', series_complexidade_sql.quantile(q=0.25)
    print 'Complexidade do SQL Quantil (MEDIUM): ', series_complexidade_sql.quantile(q=0.5)
    print 'Complexidade do SQL Quantil (HIGH): ', series_complexidade_sql.quantile(q=0.75)
    print 'Complexidade do SQL Moda: ', series_complexidade_sql.mode()
    print 'Complexidade do SQL Mínima: ', series_complexidade_sql.min()
    print 'Complexidade do SQL Máxima: ', series_complexidade_sql.max()
    print 'Complexidade do SQL Variância: ', series_complexidade_sql.var()
    print 'Complexidade do SQL Desvio Padrão: ', series_complexidade_sql.std()
    print 'Complexidade do SQL Desvio Absoluto: ', series_complexidade_sql.mad()
    print '############################################\n'
    series_complexidade_ciclomatica = pd.Series(list_complexidade_ciclomatica_models)
    print '[models] Total de métodos: ', len(list_complexidade_ciclomatica_models)
    print 'Complexidade Ciclomática Média: ', series_complexidade_ciclomatica.mean()
    print 'Complexidade Ciclomática Mediana: ', series_complexidade_ciclomatica.median()
    print 'Complexidade Ciclomática Quantil (LOW): ', series_complexidade_ciclomatica.quantile(q=0.25)
    print 'Complexidade Ciclomática Quantil (MEDIUM): ', series_complexidade_ciclomatica.quantile(q=0.5)
    print 'Complexidade Ciclomática Quantil (HIGH): ', series_complexidade_ciclomatica.quantile(q=0.75)
    print 'Complexidade Ciclomática Moda: ', series_complexidade_ciclomatica.mode()
    print 'Complexidade Ciclomática Mínima: ', series_complexidade_ciclomatica.min()
    print 'Complexidade Ciclomática Máxima: ', series_complexidade_ciclomatica.max()
    print 'Complexidade Ciclomática Variância: ', series_complexidade_ciclomatica.var()
    print 'Complexidade Ciclomática Desvio Padrão: ', series_complexidade_ciclomatica.std()
    print 'Complexidade Ciclomática Desvio Absoluto: ', series_complexidade_ciclomatica.mad()
    print '--------------------------------------------\n'
    series_complexidade_sql = pd.Series(list_complexidade_sql_models)
    print '[models] Total de métodos com SQL: ', len(list_complexidade_sql_models)
    print 'Complexidade do SQL Média: ', series_complexidade_sql.mean()
    print 'Complexidade do SQL Mediana: ', series_complexidade_sql.median()
    print 'Complexidade do SQL Quantil (LOW): ', series_complexidade_sql.quantile(q=0.25)
    print 'Complexidade do SQL Quantil (MEDIUM): ', series_complexidade_sql.quantile(q=0.5)
    print 'Complexidade do SQL Quantil (HIGH): ', series_complexidade_sql.quantile(q=0.75)
    print 'Complexidade do SQL Moda: ', series_complexidade_sql.mode()
    print 'Complexidade do SQL Mínima: ', series_complexidade_sql.min()
    print 'Complexidade do SQL Máxima: ', series_complexidade_sql.max()
    print 'Complexidade do SQL Variância: ', series_complexidade_sql.var()
    print 'Complexidade do SQL Desvio Padrão: ', series_complexidade_sql.std()
    print 'Complexidade do SQL Desvio Absoluto: ', series_complexidade_sql.mad()
    print '############################################\n'
    series_complexidade_ciclomatica = pd.Series(list_complexidade_ciclomatica_views)
    print '[views] Total de métodos: ', len(list_complexidade_ciclomatica_views)
    print 'Complexidade Ciclomática Média: ', series_complexidade_ciclomatica.mean()
    print 'Complexidade Ciclomática Mediana: ', series_complexidade_ciclomatica.median()
    print 'Complexidade Ciclomática Quantil (LOW): ', series_complexidade_ciclomatica.quantile(q=0.25)
    print 'Complexidade Ciclomática Quantil (MEDIUM): ', series_complexidade_ciclomatica.quantile(q=0.5)
    print 'Complexidade Ciclomática Quantil (HIGH): ', series_complexidade_ciclomatica.quantile(q=0.75)
    print 'Complexidade Ciclomática Moda: ', series_complexidade_ciclomatica.mode()
    print 'Complexidade Ciclomática Mínima: ', series_complexidade_ciclomatica.min()
    print 'Complexidade Ciclomática Máxima: ', series_complexidade_ciclomatica.max()
    print 'Complexidade Ciclomática Variância: ', series_complexidade_ciclomatica.var()
    print 'Complexidade Ciclomática Desvio Padrão: ', series_complexidade_ciclomatica.std()
    print 'Complexidade Ciclomática Desvio Absoluto: ', series_complexidade_ciclomatica.mad()
    print '--------------------------------------------\n'
    series_complexidade_sql = pd.Series(list_complexidade_sql_views)
    print '[views] Total de métodos com SQL: ', len(list_complexidade_sql_views)
    print 'Complexidade do SQL Média: ', series_complexidade_sql.mean()
    print 'Complexidade do SQL Mediana: ', series_complexidade_sql.median()
    print 'Complexidade do SQL Quantil (LOW): ', series_complexidade_sql.quantile(q=0.25)
    print 'Complexidade do SQL Quantil (MEDIUM): ', series_complexidade_sql.quantile(q=0.5)
    print 'Complexidade do SQL Quantil (HIGH): ', series_complexidade_sql.quantile(q=0.75)
    print 'Complexidade do SQL Moda: ', series_complexidade_sql.mode()
    print 'Complexidade do SQL Mínima: ', series_complexidade_sql.min()
    print 'Complexidade do SQL Máxima: ', series_complexidade_sql.max()
    print 'Complexidade do SQL Variância: ', series_complexidade_sql.var()
    print 'Complexidade do SQL Desvio Padrão: ', series_complexidade_sql.std()
    print 'Complexidade do SQL Desvio Absoluto: ', series_complexidade_sql.mad()
    print '############################################\n'
    series_complexidade_ciclomatica = pd.Series(list_complexidade_ciclomatica_admin)
    print '[admin] Total de métodos: ', len(list_complexidade_ciclomatica_admin)
    print 'Complexidade Ciclomática Média: ', series_complexidade_ciclomatica.mean()
    print 'Complexidade Ciclomática Mediana: ', series_complexidade_ciclomatica.median()
    print 'Complexidade Ciclomática Quantil (LOW): ', series_complexidade_ciclomatica.quantile(q=0.25)
    print 'Complexidade Ciclomática Quantil (MEDIUM): ', series_complexidade_ciclomatica.quantile(q=0.5)
    print 'Complexidade Ciclomática Quantil (HIGH): ', series_complexidade_ciclomatica.quantile(q=0.75)
    print 'Complexidade Ciclomática Moda: ', series_complexidade_ciclomatica.mode()
    print 'Complexidade Ciclomática Mínima: ', series_complexidade_ciclomatica.min()
    print 'Complexidade Ciclomática Máxima: ', series_complexidade_ciclomatica.max()
    print 'Complexidade Ciclomática Variância: ', series_complexidade_ciclomatica.var()
    print 'Complexidade Ciclomática Desvio Padrão: ', series_complexidade_ciclomatica.std()
    print 'Complexidade Ciclomática Desvio Absoluto: ', series_complexidade_ciclomatica.mad()
    print '--------------------------------------------\n'
    series_complexidade_sql = pd.Series(list_complexidade_sql_admin)
    print '[admin] Total de métodos com SQL: ', len(list_complexidade_sql_admin)
    print 'Complexidade do SQL Média: ', series_complexidade_sql.mean()
    print 'Complexidade do SQL Mediana: ', series_complexidade_sql.median()
    print 'Complexidade do SQL Quantil (LOW): ', series_complexidade_sql.quantile(q=0.25)
    print 'Complexidade do SQL Quantil (MEDIUM): ', series_complexidade_sql.quantile(q=0.5)
    print 'Complexidade do SQL Quantil (HIGH): ', series_complexidade_sql.quantile(q=0.75)
    print 'Complexidade do SQL Moda: ', series_complexidade_sql.mode()
    print 'Complexidade do SQL Mínima: ', series_complexidade_sql.min()
    print 'Complexidade do SQL Máxima: ', series_complexidade_sql.max()
    print 'Complexidade do SQL Variância: ', series_complexidade_sql.var()
    print 'Complexidade do SQL Desvio Padrão: ', series_complexidade_sql.std()
    print 'Complexidade do SQL Desvio Absoluto: ', series_complexidade_sql.mad()
    print '############################################\n'
    series_complexidade_ciclomatica = pd.Series(list_complexidade_ciclomatica_forms)
    print '[forms] Total de métodos: ', len(list_complexidade_ciclomatica_forms)
    print 'Complexidade Ciclomática Média: ', series_complexidade_ciclomatica.mean()
    print 'Complexidade Ciclomática Mediana: ', series_complexidade_ciclomatica.median()
    print 'Complexidade Ciclomática Quantil (LOW): ', series_complexidade_ciclomatica.quantile(q=0.25)
    print 'Complexidade Ciclomática Quantil (MEDIUM): ', series_complexidade_ciclomatica.quantile(q=0.5)
    print 'Complexidade Ciclomática Quantil (HIGH): ', series_complexidade_ciclomatica.quantile(q=0.75)
    print 'Complexidade Ciclomática Moda: ', series_complexidade_ciclomatica.mode()
    print 'Complexidade Ciclomática Mínima: ', series_complexidade_ciclomatica.min()
    print 'Complexidade Ciclomática Máxima: ', series_complexidade_ciclomatica.max()
    print 'Complexidade Ciclomática Variância: ', series_complexidade_ciclomatica.var()
    print 'Complexidade Ciclomática Desvio Padrão: ', series_complexidade_ciclomatica.std()
    print 'Complexidade Ciclomática Desvio Absoluto: ', series_complexidade_ciclomatica.mad()
    print '--------------------------------------------\n'
    series_complexidade_sql = pd.Series(list_complexidade_sql_forms)
    print '[forms] Total de métodos com SQL: ', len(list_complexidade_sql_forms)
    print 'Complexidade do SQL Média: ', series_complexidade_sql.mean()
    print 'Complexidade do SQL Mediana: ', series_complexidade_sql.median()
    print 'Complexidade do SQL Quantil (LOW): ', series_complexidade_sql.quantile(q=0.25)
    print 'Complexidade do SQL Quantil (MEDIUM): ', series_complexidade_sql.quantile(q=0.5)
    print 'Complexidade do SQL Quantil (HIGH): ', series_complexidade_sql.quantile(q=0.75)
    print 'Complexidade do SQL Moda: ', series_complexidade_sql.mode()
    print 'Complexidade do SQL Mínima: ', series_complexidade_sql.min()
    print 'Complexidade do SQL Máxima: ', series_complexidade_sql.max()
    print 'Complexidade do SQL Variância: ', series_complexidade_sql.var()
    print 'Complexidade do SQL Desvio Padrão: ', series_complexidade_sql.std()
    print 'Complexidade do SQL Desvio Absoluto: ', series_complexidade_sql.mad()
    print '############################################\n'
    series_complexidade_ciclomatica = pd.Series(list_complexidade_ciclomatica_outros)
    print '[outros] Total de métodos: ', len(list_complexidade_ciclomatica_outros)
    print 'Complexidade Ciclomática Média: ', series_complexidade_ciclomatica.mean()
    print 'Complexidade Ciclomática Mediana: ', series_complexidade_ciclomatica.median()
    print 'Complexidade Ciclomática Quantil (LOW): ', series_complexidade_ciclomatica.quantile(q=0.25)
    print 'Complexidade Ciclomática Quantil (MEDIUM): ', series_complexidade_ciclomatica.quantile(q=0.5)
    print 'Complexidade Ciclomática Quantil (HIGH): ', series_complexidade_ciclomatica.quantile(q=0.75)
    print 'Complexidade Ciclomática Moda: ', series_complexidade_ciclomatica.mode()
    print 'Complexidade Ciclomática Mínima: ', series_complexidade_ciclomatica.min()
    print 'Complexidade Ciclomática Máxima: ', series_complexidade_ciclomatica.max()
    print 'Complexidade Ciclomática Variância: ', series_complexidade_ciclomatica.var()
    print 'Complexidade Ciclomática Desvio Padrão: ', series_complexidade_ciclomatica.std()
    print 'Complexidade Ciclomática Desvio Absoluto: ', series_complexidade_ciclomatica.mad()
    print '--------------------------------------------\n'
    series_complexidade_sql = pd.Series(list_complexidade_sql_outros)
    print '[outros] Total de métodos com SQL: ', len(list_complexidade_sql_outros)
    print 'Complexidade do SQL Média: ', series_complexidade_sql.mean()
    print 'Complexidade do SQL Mediana: ', series_complexidade_sql.median()
    print 'Complexidade do SQL Quantil (LOW): ', series_complexidade_sql.quantile(q=0.25)
    print 'Complexidade do SQL Quantil (MEDIUM): ', series_complexidade_sql.quantile(q=0.5)
    print 'Complexidade do SQL Quantil (HIGH): ', series_complexidade_sql.quantile(q=0.75)
    print 'Complexidade do SQL Moda: ', series_complexidade_sql.mode()
    print 'Complexidade do SQL Mínima: ', series_complexidade_sql.min()
    print 'Complexidade do SQL Máxima: ', series_complexidade_sql.max()
    print 'Complexidade do SQL Variância: ', series_complexidade_sql.var()
    print 'Complexidade do SQL Desvio Padrão: ', series_complexidade_sql.std()
    print 'Complexidade do SQL Desvio Absoluto: ', series_complexidade_sql.mad()
    print '############################################\n'

