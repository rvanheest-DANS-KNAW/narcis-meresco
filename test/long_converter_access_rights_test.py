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
MODS_3 = 'mods_3'
ACCESS_LEVELS = ['openAccess', 'restrictedAccess', 'closedAccess', 'embargoedAccess']

test_items = {Format.OAI_DC:   [{ELEMENT_VALUE: 'openAccess', EXPECTED: 'openAccess'},
                                {ELEMENT_VALUE: 'restrictedAccess', EXPECTED: 'restrictedAccess'},
                                {ELEMENT_VALUE: 'closedAccess', EXPECTED: 'closedAccess'},
                                {ELEMENT_VALUE: 'embargoedAccess', EXPECTED: 'embargoedAccess'},
                                {ELEMENT_VALUE: 'something', EXPECTED: 'openAccess'}],
              Format.DATACITE: [{ELEMENT_VALUE: 'info:eu-repo/semantics/openAccess', EXPECTED: 'openAccess'},
                                {ELEMENT_VALUE: 'info:eu-repo/semantics/restrictedAccess', EXPECTED: 'restrictedAccess'},
                                {ELEMENT_VALUE: 'closedAccess', EXPECTED: 'closedAccess'},
                                {ELEMENT_VALUE: 'embargoedAccess', EXPECTED: 'embargoedAccess'},
                                {ELEMENT_VALUE: 'something else', EXPECTED: 'openAccess'}],
              MODS_3:          [{ELEMENT_VALUE: 'text...', ATTRIBUTE_VALUE: 'info:eu-repo/semantics/openAccess', EXPECTED: 'openAccess'},
                                {ELEMENT_VALUE: 'text...', ATTRIBUTE_VALUE: 'info:eu-repo/semantics/restrictedAccess', EXPECTED: 'restrictedAccess'},
                                {ELEMENT_VALUE: 'text...', ATTRIBUTE_VALUE: 'info:eu-repo/semantics/closedAccess', EXPECTED: 'closedAccess'},
                                {ELEMENT_VALUE: 'text...', ATTRIBUTE_VALUE: 'embargoedAccess', EXPECTED: 'embargoedAccess'},
                                {ELEMENT_VALUE: 'text...', ATTRIBUTE_VALUE: 'something', EXPECTED: 'openAccess'}]
              }


class LongConverterAccessRightsTest(LongConverterTest):

    def test_access_rights(self):
        print "\nRunning LongConverter Access Rights test",
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
        elif long._metadataformat.isMods3():
            self._test_mods(MODS_3, xml)

    # OAI_DC
    def _test_oai_dc(self, format, xml):

        dc = "http://purl.org/dc/elements/1.1/"
        rights = '{' + dc + '}' + 'rights'

        for t in test_items[format]:
            self._reset(xml)
            self._addElement(self.xml, rights, t[ELEMENT_VALUE])
            self._assert(Item.ACCESS_RIGHTS, t[EXPECTED])

    # MODS 3
    def _test_mods(self, format, xml):

        mods = "http://www.loc.gov/mods/v3"
        access_condition = '{' + mods + '}' + 'accessCondition'

        for t in test_items[format]:
            self._reset(xml)
            mods = self.xml.find(".//mods:mods", namespaces=namespacesmap)
            self._addElement(mods, access_condition, t[ELEMENT_VALUE], 'type', t[ATTRIBUTE_VALUE])
            self._assert(Item.ACCESS_RIGHTS, t[EXPECTED])

    # DATACITE
    def _test_datacite(self, format, xml):

        for t in test_items[format]:
            self._reset(xml)
            resource = self.xml.find(".//datacite:resource", namespaces=namespacesmap)
            rights_list_element = self._addElement(resource, 'rightsList')
            self._addElement(rights_list_element, 'rights', t[ELEMENT_VALUE])
            self._assert(Item.ACCESS_RIGHTS, t[EXPECTED])
