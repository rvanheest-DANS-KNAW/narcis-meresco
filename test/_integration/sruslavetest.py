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
# TODO: SRU-throttle mogelijkheden uitzoeken.

testNamespaces = namespaces.copyUpdate({'oaibrand':'http://www.openarchives.org/OAI/2.0/branding/',
    'prs'    : 'http://www.onderzoekinformatie.nl/nod/prs',
    'proj'   : 'http://www.onderzoekinformatie.nl/nod/act',
    'org'    : 'http://www.onderzoekinformatie.nl/nod/org',
    'long'   : 'http://www.knaw.nl/narcis/1.0/long/',
    'short'  : 'http://www.knaw.nl/narcis/1.0/short/',
    'mods'   : 'http://www.loc.gov/mods/v3',
    'didl'   : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
    'norm'   : 'http://dans.knaw.nl/narcis/normalized',
    })

class SruSlaveTest(IntegrationTestCase):

    def testSruQuery(self):
        response = self.doSruQuery(query='*', recordSchema='knaw_short')
        # print "doSruQuery(query='*'):", etree.tostring(response)
        self.assertEqual('12', xpathFirst(response, '//srw:numberOfRecords/text()'))
        self.assertEqual(set([
            'Example Program 1',
            'Example Program 2',
            'RAIN: Pan-European gridded data sets of extreme weather probability of occurrence under present and future climate',
            'Appositie en de interne struktuur van de NP',
            'Paden en stromingen---a historical survey',
            'Late-type Giants in the Inner Galaxy',
            'Preface to special issue (Fast reaction - slow diffusion scenarios: PDE approximations and free boundaries)',
            'Conditiebepaling PVC',
            'Wetenschapswinkel',
            'H.J. Bennis']
            ), set(testNamespaces.xpath(response, '//short:metadata/short:titleInfo[1]/short:title/text()')))

    def testSruQueryWithUntokenized(self):
        response = self.doSruQuery(**{"query": 'untokenized.humanstartpage exact "http://meresco.com?record=1"', "recordSchema": "knaw_long"})        
        # print "humanStartPage:", etree.tostring(response)
        self.assertEqual('meresco:record:1', xpathFirst(response, '//srw:recordIdentifier/text()'))
        response = self.doSruQuery(**{"query": 'untokenized.dd_year exact "1993"'})
        #print "dd_year:", etree.tostring(response)
        self.assertEqual('1', xpathFirst(response, '//srw:numberOfRecords/text()'))


    def testSruIndex(self):
        self.assertSruQuery(2, '__all__ = "Seecr"')
        self.assertSruQuery(2, 'title = program')
        self.assertSruQuery(3, 'untokenized.oai_id exact "record:1"')
        self.assertSruQuery(3, 'untokenized.dd_year exact "2016"')
        self.assertSruQuery(1, 'untokenized.nids exact "info:eu-repo/dai/nl/29806278"')
        self.assertSruQuery(1, 'coverage = Europe')
        self.assertSruQuery(2, 'format = "application/pdf"')
        self.assertSruQuery(2, 'untokenized.nids exact "PRS1242583"')
        self.assertSruQuery(2, 'untokenized.nids exact "http://orcid.org/0000-0002-4703-3788"')
        self.assertSruQuery(2, 'untokenized.nids exact "http://orcid.org/0000-0002-1825-0097"')
        self.assertSruQuery(3, 'untokenized.nids exact "http://isni.org/isni/0000000081508690"')
        self.assertSruQuery(1, 'untokenized.nids_non_aut exact "info:eu-repo/dai/nl/071792279"')
        self.assertSruQuery(1, 'untokenized.nids_aut exact "info:eu-repo/dai/nl/071792279"')
        self.assertSruQuery(4, '"info:eu-repo/dai/nl/071792279"')
        self.assertSruQuery(1, '"OND1272024"')
        self.assertSruQuery(1, '"ORG1236141"')
        self.assertSruQuery(1, 'untokenized.oai_id exact "ORG1236141"')
        self.assertSruQuery(1, '"1937-1632-REL"')
        self.assertSruQuery(3, 'untokenized.fundingid exact "info:eu-repo/grantAgreement/EC/FP7/282797"')
        self.assertSruQuery(1, '"Veenendaal"')
        self.assertSruQuery(1, '"OpenAIRE"')
        self.assertSruQuery(1, '"Nederzetting"')



    def testPublIdentifier(self):
        response = self.doSruQuery(**{'query':'1937-1632-REL', 'maximumRecords': '1', 'recordSchema':'knaw_long'})
        # print "DD body:", etree.tostring(response)
        #print body.searchRetrieveResponse.records.record.recordData.knaw_long.metadata.relatedItem.publication_identifier
        self.assertEqual('Springer', testNamespaces.xpathFirst(response, '//long:metadata/long:relatedItem[@type="host"]/long:publisher/text()'))
        self.assertEqual(1, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))
    
        
    def testNODPRSnameIdentifiers(self):
        self.assertSruQuery(2, '"PRS1242583"')
        self.assertSruQuery(2, '0000000247033788')
        self.assertSruQuery(2, '"0000-0002-4703-3788"')
        self.assertSruQuery(2, '"0000 0002 4703 3788"')
        self.assertSruQuery(2, '"orcid.org/0000-0002-4703-3788"')
        self.assertSruQuery(2, '"http://orcid.org/0000-0002-4703-3788"')


    def testSruQueryWithDrilldown(self):
        # response = self.doSruQuery(**{'maximumRecords': '0', "query": '*', "x-term-drilldown": "dd_penv:6,dd_thesis:6,dd_fin:6,status:5"})
        response = self.doSruQuery(**{"query": '*', 'maximumRecords': '1', "x-term-drilldown": "dd_cat:0"})
        # print "DD body:", etree.tostring(response)
        self.assertEqual('12', xpathFirst(response, '//srw:numberOfRecords/text()'))
        # self.assertEqual(set(['Example Program 1', 'Example Program 2']), set(xpath(response, '//srw:recordData/oai_dc:dc/dc:title/text()')))

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="dd_cat"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        # print 'DD:', drilldown
        self.assertEqual([('A50000', '1'), ('A80000', '1'), ('D40000', '1'), ('D50000', '1'), ('D60000', '1'), ('D37000', '1'), ('D30000', '1')], drilldown)

        # ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="genre"]/drilldown:item')
        # drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        # self.assertEqual([('Search', '1'), ('Programming', '1')], drilldown)

    def testSruQueryWithMultipleDrilldown(self):
        
        response = self.doSruQuery(**{"query": '*', 'maximumRecords': '0', "x-term-drilldown": "dd_cat:0,dd_year:2,meta_collection:0,meta_repositorygroupid:0,access:0,genre:0,dd_abrprd:0,dd_abrcmplx:0,dd_format:0,dd_typeofresource:0,dd_subject:0"})
        # print "DD body:", etree.tostring(response)
        
        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="access"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('openAccess', '5'), ('closedAccess', '3'), ('embargoedAccess', '1')], drilldown)

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="genre"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('article', '2'), ('book', '1'), ('doctoralthesis', '1'), ('dataset', '1')], drilldown)

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="dd_abrcmplx"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('NX', '1'), ('N', '1'), ('NS', '1'), ('RKLO', '1'), ('R', '1')], drilldown)

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="dd_abrprd"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('LMEB', '1'), ('LME', '1'), ('XME', '1'), ('NT', '1')], drilldown)

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="dd_typeofresource"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('text', '3'), ('Dataset/Dataset en zo', '1')], drilldown)

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="dd_subject"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('Search', '1'), ('Programming', '1'), ('Precipitation', '1'), ('Hail', '1'), ('Storms', '1'), ('Floods', '1'), ('Earth system modelling', '1'), ('Winter weather', '1'), ('Climate', '1'), ('Thunderstorms', '1'), ('Climate change', '1'), ('Forest Fires', '1'), ('This is the subject', '1'), ('freight', '1'), ('intermodal', '1'), ('rail', '1'), ('terminals', '1'), ('shunting', '1'), ('hub-and-spoke', '1'), ('In english please.', '1'), ('Geneeskunde', '1'), ('glucocorticoid', '1'), ('dexamethasone', '1'), ('cellular hypertrophy', '1'), ('contractile proteins', '1'), ('OPGRAVING', '1'), (u'\u0433\u043e\u0440\u043e\u0434\u0441\u043a\u0438\u0435 \u0440\u0430\u0439\u043e\u043d\u044b; \u044d\u043a\u043e\u043b\u043e\u0433\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0441\u0435\u0442\u0438; \u0437\u0435\u043b\u0435\u043d\u0430\u044f \u0438\u043d\u0444\u0440\u0430\u0441\u0442', '1')], drilldown)

        # TODO: Uitzoeken waarom ie wel naar storage gaat om records op te halen, hoewel startrecord over de limiet is???
    def testSruLimitStartRecord(self):
        response = self.doSruQuery(**{'maximumRecords': '1', 'startRecord': '4002', 'query':'*'})
        self.assertEqual("Argument 'startRecord' too high, maximum: 4000", xpathFirst(response, '//diag:diagnostic/diag:details/text()'))


    def testRSS(self):
        header, body = getRequest(self.sruslavePort, '/rss', dict(query="*", querylabel='MyWorkerLabel', sortKeys='untokenized.dateissued,,1'))
        # print "RSS body:", etree.tostring(body)
        items = xpath(body, "/rss/channel/item")
        self.assertEquals(12, len(items))
        self.assertTrue(xpathFirst(body, '//item/link/text()').endswith('Language/nl'))
        self.assertEqual(['1993-01-01', '2004-06-30', '2009-11-24', '2013', '2014', '2016', '2016-01-31', '2016-05-05'], xpath(body, "//item/pubDate/text()"))
        self.assertEqual('MyWorkerLabel', xpathFirst(body, '//channel/title/text()'))


    def assertSruQuery(self, numberOfRecords, query, printout=False):
        response = self.doSruQuery(**{'query':query, "recordSchema": "knaw_short", "x-recordSchema": "header"}) # , 'maximumRecords': '1'
        if printout: print "SruQuery response:", etree.tostring(response, pretty_print = True, encoding='utf-8')
        self.assertEquals(numberOfRecords, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))

    def doSruQuery(self, **arguments):
        queryArguments = {'version': '1.2', 'operation': 'searchRetrieve'}
        queryArguments.update(arguments)
        header, body = getRequest(self.sruslavePort, '/sru', queryArguments)
        return body
