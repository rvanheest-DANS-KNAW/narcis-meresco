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
from meresco.servers.index.longtofieldslist import LongToFieldsList
from lxml.etree import XML, ElementTree
from weightless.core import consume


class DcToFieldsListTest(SeecrTestCase):

    def testOne(self):
        longToFieldsList = LongToFieldsList()
        observer = CallTrace(emptyGeneratorMethods=['add'])
        longToFieldsList.addObserver(observer)
        consume(longToFieldsList.add(identifier='id:1', lxmlNode=ElementTree(XML(LONG_RECORD))))
        self.assertEqual(['add'], observer.calledMethodNames())
        self.assertEqual({
                'fieldslist': [
                    ('dc:identifier', 'http://meresco.com?record=1'),
                    ('dc:genre', 'boek'),
                    ('dc:description', 'This is an example program about Search with Meresco'),
                    ('dc:title', 'Example Program 1'),
                    ('dc:creator', 'Seecr'),
                    ('dc:publisher', 'Seecr'),
                    ('dc:date', '2016'),
                    ('dc:type', 'Example'),
                    ('dc:subject', 'Search'),
                    ('dc:language', 'en'),
                    ('dc:rights', 'Open Source')
                ],
                'identifier': 'id:1'
            }, observer.calledMethods[0].kwargs)


LONG_RECORD = """<long xmlns="http://www.knaw.nl/narcis/1.0/long/" version="1.0">
  <modificationDate>2007-03-18T11:02:39Z</modificationDate>
  <humanStartPage>http://repository.tue.nl/711504</humanStartPage>
  <persistentIdentifier ref="http://repository.tue.nl/711504">URN:NBN:NL:UI:25-711504</persistentIdentifier>
  <objectFiles>
    <objectFile>
      <resource mimeType="application/pdf" ref=" http://alexandria.tue.nl/openaccess/Metis249902.pdf"/>
      <persistentIdentifier>URN:NBN:NL:UI:25-711504-of</persistentIdentifier>
      <accessRights>closedAccess</accessRights>
    </objectFile>
  </objectFiles>
  <accessRights>closedAccess</accessRights>
  <metadata>
    <titleInfo>
      <title>Preface to special issue (Fast reaction - slow diffusion scenarios: PDE approximations and free boundaries)</title>
    </titleInfo>
    <titleInfo xml:lang="en">
      <title>Preface to special issue (Fast reaction - slow diffusion scenarios: PDE approximations and free boundaries)</title>
    </titleInfo>
    <name>
      <type>personal</type>
      <family>Aiki</family>
      <given>T (Toyohiko)</given>
      <mcRoleTerm>aut</mcRoleTerm>
    </name>
    <name>
      <type>personal</type>
      <family>Hilhorst</family>
      <given>D</given>
      <mcRoleTerm>aut</mcRoleTerm>
    </name>
    <name>
      <type>personal</type>
      <family>Mimura</family>
      <given>M</given>
      <mcRoleTerm>aut</mcRoleTerm>
    </name>
    <name>
      <type>personal</type>
      <family>Funder</family>
      <given>$ (Adrian)</given>
      <mcRoleTerm>fnd</mcRoleTerm>
    </name>
    <rightsDescription>Copyright (c) Aiki, T (Toyohiko); Copyright (c) Hilhorst, D; Copyright (c) Mimura, M; Copyright (c) Muntean, A (Adrian)</rightsDescription>
    <genre>article</genre>
    <dateIssued>
      <parsed>2014</parsed>
      <unParsed>2014</unParsed>
    </dateIssued>
    <publication_identifier type="uri">info:doi/10.3934/dcdss.2012.5.1i</publication_identifier>
    <relatedItem type="host">
      <part>
        <volume>5</volume>
        <issue>1</issue>
        <start_page>i</start_page>
      </part>
      <titleInfo>
        <title>Discrete and Continuous Dynamical Systems - Series S</title>
      </titleInfo>
      <titleInfo xml:lang="en">
        <title>Discrete and Continuous Dynamical Systems - Series S</title>
      </titleInfo>
      <publication_identifier type="issn">1937-1632-REL</publication_identifier>
      <placeTerm>Veenendaal</placeTerm>
      <publisher>Springer</publisher>
    </relatedItem>
    <typeOfResource>text</typeOfResource>
    <grantAgreements>
      <grantAgreement>
        <code>info:eu-repo/grantAgreement/EC/FP5/654321</code>
        <title>EERA Design Tools for Offshore Wind Farm Cluster
                    (EERA-DTOC)</title>
        <description>The European Energy Research Alliance (EERA)
                    together with some high-impact industry partners addresses
                    the call proposing an integrated and validated design tool
                    combining the state-of-the-art wake, yield and electrical
                    models available in the consortium, as a plug-in
                    architecture with possibility for third party
                    models.</description>
        <funder>Funder, $ (Adrian)</funder>
      </grantAgreement>
      <grantAgreement>
        <code>info:eu-repo/grantAgreement/EC/FP7/282797</code>
      </grantAgreement>
    </grantAgreements>
  </metadata>
</long>"""
