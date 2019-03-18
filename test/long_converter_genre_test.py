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
COLLECTION = 'collection'
MODS = 'mods'

test_items = {Format.OAI_DC:   [{ELEMENT_VALUE: 'newspaper', EXPECTED: 'contributiontoperiodical'},
                                {ELEMENT_VALUE: 'bookpart', EXPECTED: 'bookpart'}],
              Format.DATACITE: [{ELEMENT_VALUE: 'Dataset about software', ATTRIBUTE_VALUE: 'Software', COLLECTION: 'dataset', EXPECTED: 'software'},
                                {ELEMENT_VALUE: 'Dataset...', ATTRIBUTE_VALUE: '', COLLECTION: 'dataset', EXPECTED: 'dataset'},
                                {ELEMENT_VALUE: 'something', ATTRIBUTE_VALUE: 'Collection', COLLECTION: 'dataset', EXPECTED: 'dataset'},
                                {ELEMENT_VALUE: 'article', ATTRIBUTE_VALUE: '', COLLECTION: 'other', EXPECTED: 'article'},
                                {ELEMENT_VALUE: 'something else', ATTRIBUTE_VALUE: '', COLLECTION: 'other', EXPECTED: None}],
              MODS:             [{ELEMENT_VALUE: 'info:eu-repo/semantics/article', EXPECTED: 'article'},
                                {ELEMENT_VALUE: 'info:eu-repo/semantics/something', EXPECTED: None}]
              }


class LongConverterGenreTest(LongConverterTest):

    def test_genre(self):
        print "\nRunning LongConverter Genre test",
        for format in Format:
            xml = etree.fromstring(baseXmls[format])
            self._test(format, xml)
        print ""

    def _test(self, format, xml):

        long._metadataformat = MetadataFormat(xml, long._uploadid)
        if format == Format.OAI_DC:
            self._test_oai_dc(format, xml)
        elif format == Format.DATACITE:
            self._test_datacite(format, xml)
        elif long._metadataformat.isMods():
            self._test_mods(MODS, xml)

    # OAI_DC
    def _test_oai_dc(self, format, xml):

        dc = "http://purl.org/dc/elements/1.1/"
        type = '{' + dc + '}' + 'type'

        for t in test_items[format]:
            self._reset(xml)
            self._addElement(self.xml, type, t[ELEMENT_VALUE])
            self._assert(Item.GENRE, t[EXPECTED])

    # MODS
    def _test_mods(self, format, xml):

        mods = "http://www.loc.gov/mods/v3"
        genre = '{' + mods + '}' + 'genre'

        for t in test_items[format]:
            self._reset(xml)
            mods = self.xml.find(".//mods:mods", namespaces=namespacesmap)
            self._addElement(mods, genre, t[ELEMENT_VALUE])
            self._assert(Item.GENRE, t[EXPECTED])

    # DATACITE
    def _test_datacite(self, format, xml):

        for t in test_items[format]:
            long._wcpcollection = t[COLLECTION]
            self._reset(xml)
            resource = self.xml.find(".//datacite:resource", namespaces=namespacesmap)
            self._addElement(resource, 'resourceType', t[ELEMENT_VALUE], 'resourceTypeGeneral', t[ATTRIBUTE_VALUE])
            self._assert(Item.GENRE, t[EXPECTED])
