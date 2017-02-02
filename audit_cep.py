#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict


class Coordinate2D:
    '''Um objeto que guarda uma coordenada 2D(latitude e longitude) implementado para ser usado como chave em um dicionário
para validação de consistência
Fonte: http://stackoverflow.com/questions/4901815/object-of-custom-type-as-dictionary-key '''
    def __init__(self,latitude,longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __hash__(self):
        return hash((self.latitude, self.longitude))

    def __eq__(self, other):
        return (self.latitude, self.longitude) == (other.latitude, other.longitude)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)
    
    def __repr__(self):
        return "({},{})".format(self.latitude,self.longitude)


OSM_FILE = "sample.osm"

postal_code_re = re.compile(r'\d{8}')

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")


def is_default_format(postal_code):
    '''Verifica se o CEP está no formato de 8 dígitos númericos sem quaisquer outros caracteres não-númericos'''
    return postal_code_re.match(postal_code)

def in_range(value,lower_range=70002900, upper_range=73403539):
    '''Verifica se o CEP está num Range de CEPs válidos'''
    int_value = int(value)
    return (int_value >= lower_range) and (int_value <= upper_range)

def is_valid(postal_code):
    '''Verifica se o CEP está no padrão e no range de CEPs da cidade'''
    return is_default_format(postal_code) and in_range(postal_code)


        


def audit_osm_postalcode(osmfile):
    """Retorna uma Lista de CEPs que não estão válidos"""
    
    problem_list = set()
    '''Dicionário para Verificar consistência dos CEPs por meio da latitude e longitude, se um par latitude/longitude 
    ter mais de um CEP, pode haver algum problema o registro'''
    coordinate_dict = defaultdict(list)
    coordinate = None
    with open(osmfile) as f:
        for event, element in ET.iterparse(f, events=("start",)):
            if element.tag == "node" or element.tag == "way":
                #Como Latitude e longitude estão no Node ou Way é necessário adquiri-lo de antemão aqui
                
                #apenas Nodes tem latitude e longitude
                if element.tag == "node":
                    coordinate = Coordinate2D(element.attrib['lat'],element.attrib['lon'])
                for tag in element.iter("tag"):
                    if is_postal_code(tag):
                        postal_value = tag.attrib['v']
                        if element.tag == "node":
                            coordinate_dict[coordinate].append(postal_value)
                        #Não é valido ou tem mais de um CEP para este mesmo par latitude/longitude?
                        if not is_valid(postal_value) or len(coordinate_dict[coordinate]) > 1:
                            problem_list.add(postal_value)
                  
    #DEBUG: Latitude/Longitude Com Problemas
    #adquirindo um Dicionário filtrando apenas com latitudes e longitudes com mais de um registro
    filtered_coordinates = {k: v for k, v in coordinate_dict.iteritems() if len(v) > 1}
    print "Temos {} Latitudes/Latitudes com Mais de um CEP".format(len(filtered_coordinates.keys()))
    pprint.pprint(dict(filtered_coordinates))
    return problem_list

if __name__ == '__main__':                
    problem_list = audit_osm_postalcode(OSM_FILE)
    print 'Encontrados {} CEPs Com Problemas'.format(len(problem_list))
    pprint.pprint(problem_list)



                    
                    
            