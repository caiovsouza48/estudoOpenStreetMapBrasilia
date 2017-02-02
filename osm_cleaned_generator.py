#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow
import re

OSM_FILE = "bsb.osm"  # Replace this with your osm file
CLEANED_FILE = "bsb_cleaned.osm"

mapping = { "Q": u"Quadra",
            "Q.": u"Quadra",
            "Qd": u"Quadra",
            "Qd.": u"Quadra",
            "Pc": u"Praça",
            "Pc.": u"Praça",
            "Av": u"Avenida",
            "Av.": u"Avenida",
            "Ed": u"Edifício",
            "Ed.": u"Edifício",
            "ED": u"Edifício",
            "ED.": u"Edifício",
            "Bl": u"Bloco",
            "Bl.": u"Bloco",
            "BL": u"Bloco",
            "BL.": u"Bloco",
            "Lt": u"Lote",
            "Lt.": u"Lote",
            "LT": u"Lote",
            "cj": u"Conjunto",
            "cj.": u"Conjunto",
            "lj": u"Loja",
            "Lj": u"Loja",
            "Lj.": u"Loja",
            "LJ": u"Loja",
            "QI": u"Quadra Interna",
            "Ch.": u"Chácara",
            "CH.": u"Chácara",
            "QL": u"Quadra do Lago",
            "Ql": u"Quadra do Lago",
            "Ql.": u"Quadra do Lado",
            "APT": u"Apartamento",
            "apt": u"Apartamento"}

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

#Atualiza o o Endereço substituindo abreviações pelo nome inteiro
def update_name(name, mapping):
    final_name = name
    for key in mapping.keys():
        key_whitespace = key + " "
        if key_whitespace in name:
            final_name = (final_name.replace(key,mapping[key]) + " ")
    return final_name

# Retorna um Código-postal sem caracteres não-numéricos
def update_postal_code(postal):
    return re.sub('[^0-9]','', postal)
    

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def generate_cleaned_osm():
    '''Gera um OSM com as devidas correções definidas na auditoria'''
    with open(CLEANED_FILE, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ')
        for element in get_element(OSM_FILE):
            if element.tag == "node" or element.tag == "way":
                for tag in element.iter("tag"):
                    # é endereço?
                    if is_street_name(tag):
                        tag.attrib['v'] = update_name(tag.attrib['v'],mapping)
                    #É CEP?
                    elif is_postal_code(tag):
                        tag.attrib['v'] = update_postal_code(tag.attrib['v'])
                output.write(ET.tostring(element, encoding='utf-8'))
        output.write('</osm>')
        print 'OSM Generated'

if __name__ == '__main__':
    print 'Generating...'
    generate_cleaned_osm()