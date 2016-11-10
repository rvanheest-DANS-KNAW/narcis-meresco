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

from seecr.test import IntegrationTestCase
from seecr.test.utils import getRequest, sleepWheel, htmlXPath
from meresco.xml import xpathFirst, xpath, namespaces
from lxml import etree

# TODO: create UnitTestCase for o.a. writeDelete / unDelete

testNamespaces = namespaces.copyUpdate({'oaibrand':'http://www.openarchives.org/OAI/2.0/branding/'})

class ApiTest(IntegrationTestCase):

    def testSruQuery(self):
        response = self.doSruQuery(query='*')
        # print "doSruQuery(query='*'):", etree.tostring(response)
        self.assertEqual('10', xpathFirst(response, '//srw:numberOfRecords/text()'))
        self.assertEqual(set(['Example Program 1',
            'Example Program 2', 
            'Paden en stromingen---a historical survey',
            'Preface to special issue (Fast reaction - slow diffusion scenarios: PDE approximations and free boundaries)',
            'Conditiebepaling PVC',
            'Appositie en de interne struktuur van de NP',
            'Wetenschapswinkel',
            'Late-type Giants in the Inner Galaxy',
            'H.J. Bennis',
            'RAIN: Pan-European gridded data sets of extreme weather probability of occurrence under present and future climate']
            ), set(xpath(response, '//srw:recordData/oai_dc:dc/dc:title[1]/text()')))

    def testSruQueryWithUntokenized(self):
        response = self.doSruQuery(**{"query": 'untokenized.humanstartpage exact "http://meresco.com?record=1"', "recordSchema": "long"})        
        # print "humanStartPage:", etree.tostring(response)
        self.assertEqual('meresco:record:1', xpathFirst(response, '//srw:recordIdentifier/text()'))
        response = self.doSruQuery(**{"query": 'untokenized.dd_year exact "2016"'})
        # print "dd_year:", etree.tostring(response)
        self.assertEqual('3', xpathFirst(response, '//srw:numberOfRecords/text()'))


    def testSruIndex(self):
        self.assertSruQuery(2, '__all__ = "Seecr"')
        self.assertSruQuery(2, 'title = program')
        self.assertSruQuery(3, 'untokenized.oai:id exact "record:1"')
        self.assertSruQuery(3, 'untokenized.dd_year exact "2016"')
        self.assertSruQuery(1, 'untokenized.nids exact "info:eu-repo/dai/nl/29806278"', False)
        # self.assertSruQuery(1, 'coverage = Europe')
        # self.assertSruQuery(1, 'format = "text/xml"')
        # self.assertSruQuery(2, 'untokenized.nids exact "PRS1242583"')
        # self.assertSruQuery(2, 'untokenized.nids exact "http://orcid.org/0000-0002-4703-3788"')
        # self.assertSruQuery(3, 'untokenized.nids exact "http://isni.org/isni/0000000081508690"')
        # self.assertSruQuery(2, 'untokenized.nids exact "info:eu-repo/dai/nl/071792279"')


    def testSruQueryWithDrilldown(self):
        # response = self.doSruQuery(**{'maximumRecords': '0', "query": '*', "x-term-drilldown": "dd_penv:6,dd_thesis:6,dd_fin:6,status:5"})
        response = self.doSruQuery(**{"query": '*', 'maximumRecords': '1', "x-term-drilldown": "dd_cat:0"})
        # print "DD body:", etree.tostring(response)
        self.assertEqual('10', xpathFirst(response, '//srw:numberOfRecords/text()'))
        # self.assertEqual(set(['Example Program 1', 'Example Program 2']), set(xpath(response, '//srw:recordData/oai_dc:dc/dc:title/text()')))

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="dd_cat"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        # print 'DD:', drilldown
        self.assertEqual([('A50000', '1'), ('A80000', '1'), ('D40000', '1'), ('D50000', '1'), ('D60000', '1')], drilldown)

        # ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="genre"]/drilldown:item')
        # drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        # self.assertEqual([('Search', '1'), ('Programming', '1')], drilldown)

    def testSruQueryWithMultipleDrilldown(self):
        # response = self.doSruQuery(**{'maximumRecords': '0', "query": '*', "x-term-drilldown": "dd_penv:6,dd_thesis:6,dd_fin:6,status:5"})
        response = self.doSruQuery(**{"query": '*', 'maximumRecords': '0', "x-term-drilldown": "dd_cat:0,dd_year:2,meta:collection:0,meta:repositorygroupid:0,access:0,pubtype:0"})

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="access"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('openAccess', '4'), ('closedAccess', '3')], drilldown)

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="pubtype"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('article', '2'), ('book', '1'), ('doctoralthesis', '1')], drilldown)

    def testSruLimitStartRecord(self):
        response = self.doSruQuery(**{'maximumRecords': '1', 'startRecord': '4002', 'query':'*'})
        self.assertEqual("Argument 'startRecord' too high, maximum: 4000", xpathFirst(response, '//diag:diagnostic/diag:details/text()'))

    def testOai(self):
        header, body = getRequest(self.apiPort, '/oai', dict(verb="ListRecords", metadataPrefix="oai_dc"))
        # print "OAI body:", etree.tostring(body) #
        records = xpath(body, '//oai:record/oai:metadata')
        self.assertEqual(10, len(records))

    def testOaiPovenance(self):
        header, body = getRequest(self.apiPort, '/oai', dict(verb="ListRecords", metadataPrefix="oai_dc"))
        # print "OAI body:", etree.tostring(body)
        self.assertEqual('http://www.openarchives.org/OAI/2.0/oai_dc/', xpathFirst(body, '//oaiprov:provenance/oaiprov:originDescription/oaiprov:metadataNamespace/text()'))

    def testOaiIdentify(self):
        header, body = getRequest(self.apiPort, '/oai', dict(verb="Identify"))
        # print "OAI body:", etree.tostring(body)
        self.assertEqual('NARCIS OAI-pmh', xpathFirst(body, '//oai:Identify/oai:repositoryName/text()'))
        self.assertEqual('Narcis - The gateway to scholarly information in The Netherlands', testNamespaces.xpathFirst(body, '//oai:Identify/oai:description/oaibrand:branding/oaibrand:collectionIcon/oaibrand:title/text()'))

    def testOaiListSets(self):
        header, body = getRequest(self.apiPort, '/oai', dict(verb="ListSets"))
        # print "ListSets", etree.tostring(body)
        self.assertEqual(set(['publication' ]), set(xpath(body, '//oai:setSpec/text()')))

    def testRSS(self):
        header, body = getRequest(self.apiPort, '/rss', dict(query="title=en"))
        # print "RSS body:", etree.tostring(body)
        items = xpath(body, "/rss/channel/item")
        self.assertEquals(2, len(items))
        self.assertEqual(set(["Paden en stromingen---a historical survey", "Appositie en de interne struktuur van de NP"]), set(xpath(body, "//item/title/text()")))
        self.assertEqual(set(["Samenvatting", "FransHeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeellllllang"]), set(xpath(body, "//item/description/text()")))

    def testLog(self):
        header, body = getRequest(self.apiPort, '/log/', parse=False) # yy-mm-dd-query.log is op moment van testen nog niet aanwezig/gepurged/flushed...
        self.assertEqual('"Example Queries" Logging', list(htmlXPath('//head/title/text()', body))[0])

    def assertSruQuery(self, numberOfRecords, query, printout=False):
        response = self.doSruQuery(**{'query':query, "recordSchema": "short", 'maximumRecords': '1'})
        if printout: print "SruQuery response:", etree.tostring(response)
        self.assertEquals(numberOfRecords, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))

    def doSruQuery(self, **arguments):
        queryArguments = {'version': '1.2', 'operation': 'searchRetrieve'}
        queryArguments.update(arguments)
        header, body = getRequest(self.apiPort, '/sru', queryArguments)
        return body
