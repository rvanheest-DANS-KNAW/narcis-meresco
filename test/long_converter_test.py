# encoding=utf-8
## begin license ##
# 
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core". 
# 
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
# This file is part of "Meresco Components"
# 
# "Meresco Components" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# "Meresco Components" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with "Meresco Components"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
## end license ##

import copy
import unittest
from meresco.dans.longconverter import NormaliseOaiRecord
from meresco.dans.uiaconverter import UiaConverter
from lxml import etree
from meresco.xml import namespaces
from enum import Enum

class Format(Enum):
    OAI_DC = 'oai_dc'
    DIDLM23 = 'didl_mods231'
    DIDLM30 = 'didl_mods30'
    DIDLM36 = 'didl_mods36'
    DIDLDC = 'didl_dc'
    DATACITE = 'datacite'


class Item(Enum):
    GENRE = 'genre'
    ACCESS_RIGHTS = 'accessRights'

xmlOaiDc =      '<root xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"><oai_dc:dc/></root>'
xmlDidlMods23 = '<root xmlns:didl="urn:mpeg:mpeg21:2002:02-DIDL-NS" xmlns:mods="http://www.loc.gov/mods/v3"><didl:DIDL><mods:mods/></didl:DIDL></root>'
xmlDidlMods30 = '<root xmlns:didl="urn:mpeg:mpeg21:2002:02-DIDL-NS" xmlns:mods="http://www.loc.gov/mods/v3" xmlns:rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"><didl:DIDL><mods:mods/><rdf:something/></didl:DIDL></root>'
xmlDidlMods36 = '<root xmlns:mods="http://www.loc.gov/mods/v3"><mods:mods/></root>'
xmlDidlDc =     '<root xmlns:didl="urn:mpeg:mpeg21:2002:02-DIDL-NS" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"><didl:DIDL><oai_dc:dc/></didl:DIDL></root>'
xmlDatacite =   '<root xmlns="http://datacite.org/schema/kernel-4"><resource/></root>'

baseXmls = {Format.OAI_DC: xmlOaiDc, Format.DIDLM23: xmlDidlMods23, Format.DIDLM30: xmlDidlMods30, Format.DIDLM36: xmlDidlMods36, Format.DIDLDC: xmlDidlDc, Format.DATACITE: xmlDatacite}
methods = {Item.GENRE: '_getGenre', Item.ACCESS_RIGHTS: '_getAccessRights'}

testEmpty = etree.fromstring('<test/>')
long = NormaliseOaiRecord(UiaConverter)

namespacesmap = namespaces.copyUpdate(
    {  # See: https://github.com/seecr/meresco-xml/blob/master/meresco/xml/namespaces.py
        'dip': 'urn:mpeg:mpeg21:2005:01-DIP-NS',
        'dii': 'urn:mpeg:mpeg21:2002:01-DII-NS',
        'xlink': 'http://www.w3.org/1999/xlink',
        'dai': 'info:eu-repo/dai',
        'gal': 'info:eu-repo/grantAgreement',
        'wmp': 'http://www.surfgroepen.nl/werkgroepmetadataplus',
        'prs': 'http://www.onderzoekinformatie.nl/nod/prs',
        'proj': 'http://www.onderzoekinformatie.nl/nod/act',
        'org': 'http://www.onderzoekinformatie.nl/nod/org',
        'long': 'http://www.knaw.nl/narcis/1.0/long/',
        'short': 'http://www.knaw.nl/narcis/1.0/short/',
        'mods': 'http://www.loc.gov/mods/v3',
        'didl': 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
        'norm': 'http://dans.knaw.nl/narcis/normalized',
        'datacite': 'http://datacite.org/schema/kernel-4'
    })

class LongConverterTest(unittest.TestCase):

    def _reset(self, xmlBase):
        self.xml = copy.deepcopy(xmlBase)
        self.test = copy.deepcopy(testEmpty)

    def _addElement(self, xml, element, elementValue=None, attribute=None, attributeValue=None):
        e = etree.SubElement(xml, element)
        if elementValue:
            e.text = elementValue
        if attribute:
            e.attrib[attribute] = attributeValue
        return e

    def _assert(self, item, expected):
        self.xml = etree.fromstring(etree.tostring(self.xml))
        getattr(long, methods[item])(self.xml, self.test)
        if self.test.find(item.value) >= 0:
            value = self.test.find(item.value).text
        else:
            value = None
        self.assertEqual(expected, value)
        print "+",
