## begin license ##
#
# "Meresco Examples" is a project demonstrating some of the
# features of various components of the "Meresco Suite".
# Also see http://meresco.org.
#
# Copyright (C) 2016 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Meresco Examples"
#
# "Meresco Examples" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Examples" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Examples"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from seecr.test import SeecrTestCase, CallTrace
from meresco.servers.index.metaparttofieldslist import MetaToFieldsList
from lxml.etree import XML, ElementTree
from weightless.core import consume


class MeatToFieldsListTest(SeecrTestCase):

    def testOne(self):
        metaToFieldsList = MetaToFieldsList()
        observer = CallTrace(emptyGeneratorMethods=['add'])
        metaToFieldsList.addObserver(observer)
        consume(metaToFieldsList.add(identifier='record:4', lxmlNode=ElementTree(XML(META_RECORD))))
        self.assertEqual(['add'], observer.calledMethodNames())
        self.assertEqual({'fieldslist': [
            ('meta:id', 'knaw'), 
            ('meta:set', 'oa_publications'), 
            ('meta:baseurl', 'http://depot.knaw.nl/cgi/oai2'), 
            ('meta:repositoryGroupId', 'knaw'), 
            ('meta:metadataPrefix', 'nl_didl'), 
            ('meta:collection', 'publication')
            ], 'identifier': 'record:4'}, observer.calledMethods[0].kwargs)


META_RECORD = """<meta xmlns="http://meresco.org/namespace/harvester/meta">
    <upload>
        <id>knaw:record:4</id>
    </upload>
    <record>
        <id>record:4</id>
        <harvestDate>2016-10-05T10:30:45Z</harvestDate>
        <metadataNamespace>http://www.loc.gov/mods/v3</metadataNamespace>
    </record>
    <repository>
        <id>knaw</id>
        <set>oa_publications</set>
        <baseurl>http://depot.knaw.nl/cgi/oai2</baseurl>
        <repositoryGroupId>knaw</repositoryGroupId>
        <metadataPrefix>nl_didl</metadataPrefix>
        <collection>publication</collection>
    </repository>
</meta>"""