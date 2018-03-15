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
from meresco.servers.index.normdoctofieldslist import NormdocToFieldsList
from weightless.core import consume
from lxml.etree import parse, tostring, XML, ElementTree, fromstring, dump, XMLSchema, parse as lxmlParse
from StringIO import StringIO


class NormdocToFieldsListTest(SeecrTestCase):

    def testOne(self):
        normdocToFieldsList = NormdocToFieldsList()
        observer = CallTrace(emptyGeneratorMethods=['add'])
        normdocToFieldsList.addObserver(observer)
        consume(normdocToFieldsList.add(identifier='record:4', lxmlNode=parse(open("data/normdoc.xml")) ))
        self.assertEqual(['add'], observer.calledMethodNames())
        # print "FIELDLIST:", observer.calledMethods[0].kwargs
        self.assertEqual({'fieldslist': [('meta_repositoryid', 'knaw'), ('oai_id', 'record:4'), ('meta_repositorygroupid', 'knaw'), ('dare_id', 'record:4'), ('meta_collection', 'publication'), ('humanstartpage', 'http://repository.tue.nl/711504'), ('persistentid', 'URN:NBN:NL:UI:25-711504'), ('access', 'closedAccess'), ('', 'Copyright (c) Aiki, T (Toyohiko); Copyright (c) Hilhorst, D; Copyright (c) Mimura, M; Copyright (c) Muntean, A (Adrian)'), ('genre', 'article'), ('', 'Discrete and Continuous Dynamical Systems - Series S'), ('', 'Discrete and Continuous Dynamical Systems - Series S'), ('', 'Veenendaal'), ('', 'Springer'), ('', 'text'), ('fundingid', 'info:eu-repo/grantAgreement/EC/FP5/654321'), ('', 'EERA Design Tools for Offshore Wind Farm Cluster                    (EERA-DTOC)'), ('', 'The European Energy Research Alliance (EERA)                    together with some high-impact industry partners addresses                    the call proposing an integrated and validated design tool                    combining the state-of-the-art wake, yield and electrical                    models available in the consortium, as a plug-in                    architecture with possibility for third party                    models.'), ('', 'Funder, $ (Adrian)'), ('fundingid', 'info:eu-repo/grantAgreement/EC/FP7/282797'), ('authors', 'Aiki, T (Toyohiko)'), ('authors', 'Hilhorst, D'), ('authors', 'Mimura, M'), ('names', 'Aiki, T (Toyohiko)'), ('names', 'Hilhorst, D'), ('names', 'Mimura, M'), ('names', 'Funder, $ (Adrian)'), ('publicationid', 'info:doi/10.3934/dcdss.2012.5.1i'), ('publicationid', '1937-1632-REL'), ('pidref', 'http://repository.tue.nl/711504'), ('title_en', 'Preface to special issue (Fast reaction - slow diffusion scenarios: PDE approximations and free boundaries)'), ('title', 'Preface to special issue (Fast reaction - slow diffusion scenarios: PDE approximations and free boundaries)'), ('dd_year', '2014'), ('dateissued', '2014')], 'identifier': 'record:4'}, observer.calledMethods[0].kwargs)
