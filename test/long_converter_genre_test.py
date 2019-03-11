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

from meresco.dans.metadataformats import MetadataFormat
from lxml import etree
from test.long_converter_test import LongConverterTest, baseXmls, long, namespacesmap, Format, Item

ELEMENT_VALUE = 'element_value'
ATTRIBUTE_VALUE = 'attribute_value'
EXPECTED = 'expected'

test_items = {Format.OAI_DC:   [{ELEMENT_VALUE: 'newspaper', EXPECTED: 'contributiontoperiodical'},
                                {ELEMENT_VALUE: 'bookpart', EXPECTED: 'bookpart'}],
              Format.DATACITE: [{ELEMENT_VALUE: 'Dataset about software', ATTRIBUTE_VALUE: 'Software', EXPECTED: 'software'},
                                {ELEMENT_VALUE: 'Dataset...', ATTRIBUTE_VALUE: '', EXPECTED: 'dataset'},
                                {ELEMENT_VALUE: 'something', ATTRIBUTE_VALUE: 'just something', EXPECTED: 'dataset'}]
              }

class LongConverterGenreTest(LongConverterTest):

    def test_genre(self):
        for format in Format:
            xml = etree.fromstring(baseXmls[format])
            self._test(format, xml)

    def _test(self, format, xmlBase):

        long._metadataformat = MetadataFormat(xmlBase, long._uploadid)
        long._wcpcollection = 'dataset'
        getattr(self, '_test_' + format.value)(format, xmlBase)

    # OAI_DC
    def _test_oai_dc(self, format, xmlBase):

        dc = "http://purl.org/dc/elements/1.1/"
        type = '{' + dc + '}' + 'type'

        for t in test_items[format]:
            self._reset(xmlBase)
            self._addElement(self.xml, type, t[ELEMENT_VALUE])
            self._assert(Item.GENRE, t[EXPECTED])

    # DATACITE
    def _test_datacite(self, format, xmlBase):

        for t in test_items[format]:
            self._reset(xmlBase)
            resource = self.xml.find("datacite:resource", namespaces=namespacesmap)
            self._addElement(resource, 'resourceType', t[ELEMENT_VALUE], 'resourceTypeGeneral', t[ATTRIBUTE_VALUE])
            self._assert(Item.GENRE, t[EXPECTED])
