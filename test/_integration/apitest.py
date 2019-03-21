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
from meresco.dans.persistentidentifier import PidFactory

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

class ApiTest(IntegrationTestCase):

    def testSruQuery(self):
        response = self.doSruQuery(query='*', recordSchema='knaw_short')
        # print "doSruQuery(query='*'):", etree.tostring(response)
        self.assertEqual('14', xpathFirst(response, '//srw:numberOfRecords/text()'))
        self.assertEqual({
            'Example Program 1',
            'Example Program 2',
            'RAIN: Pan-European gridded data sets of extreme weather probability of occurrence under present and future climate',
            'Appositie en de interne struktuur van de NP',
            'Paden en stromingen---a historical survey',
            'Late-type Giants in the Inner Galaxy',
            'Preface to special issue (Fast reaction - slow diffusion scenarios: PDE approximations and free boundaries)',
            'Conditiebepaling PVC',
            'Wetenschapswinkel',
            "The Language Designer's Workbench: Automating Verification of Language Definitions"}, set(testNamespaces.xpath(response, '//short:metadata/short:titleInfo[1]/short:title/text()')))

    def testSruQueryWithUntokenized(self):
        response = self.doSruQuery(**{"query": 'untokenized.humanstartpage exact "http://meresco.com?record=1"', "recordSchema": "knaw_long"})        
        # print "humanStartPage:", etree.tostring(response)
        self.assertEqual('meresco:record:1', xpathFirst(response, '//srw:recordIdentifier/text()'))
        response = self.doSruQuery(**{"query": 'untokenized.dd_year exact "2016"'})
        # print "dd_year:", etree.tostring(response)
        self.assertEqual('3', xpathFirst(response, '//srw:numberOfRecords/text()'))


    def testSruIndex(self):
        self.assertSruQuery(2, '__all__ = "Seecr"')
        self.assertSruQuery(2, 'title = program')
        self.assertSruQuery(3, 'untokenized.oai_id exact "record:1"')
        self.assertSruQuery(3, 'untokenized.dd_year exact "2016"')
        self.assertSruQuery(1, 'untokenized.nids exact "info:eu-repo/dai/nl/29806278"')
        self.assertSruQuery(1, 'coverage = Europe')
        self.assertSruQuery(3, 'format = "application/pdf"')
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
        self.assertSruQuery(1, '"1937-1632"')
        self.assertSruQuery(3, 'untokenized.fundingid exact "info:eu-repo/grantAgreement/EC/FP7/282797"')
        self.assertSruQuery(1, '"Veenendaal"')
        self.assertSruQuery(1, '"Groningen Institute of Archaeology, University of Groningen"')
        self.assertSruQuery(1, 'untokenized.nids exact "ror:008pnp284"')


    def testPublIdentifier(self):
        response = self.doSruQuery(**{'query': 'untokenized.relatedid exact "issn:1937-1632"', 'maximumRecords': '1', 'recordSchema':'knaw_long'})
#         print "DD body:", etree.tostring(response)
        self.assertEqual('knaw:record:4', xpathFirst(response, '//srw:recordIdentifier/text()'))
        self.assertEqual(1, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))
        self.assertEqual('Springer', testNamespaces.xpathFirst(response, '//long:metadata/long:relatedItem[@type="host"]/long:publisher/text()'))


    def testAlternativeIdentifier(self):
        doi = PidFactory.factory("doi", 'doi:10.17026/dans-x38-rkke')
        response = self.doSruQuery(**{'query':'untokenized.pubid exact "'+doi.get_idx_id()+'"', 'maximumRecords': '1', 'recordSchema':'knaw_long'})
        self.assertEqual('rce:rapporten:550000001', xpathFirst(response, '//srw:recordIdentifier/text()'))
#         print "DD body:", etree.tostring(response)
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
        self.assertEqual('14', xpathFirst(response, '//srw:numberOfRecords/text()'))
        # self.assertEqual(set(['Example Program 1', 'Example Program 2']), set(xpath(response, '//srw:recordData/oai_dc:dc/dc:title/text()')))

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="dd_cat"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('D30000', '5'), ('D37000', '2'), ('D34200', '1'), ('D34000', '1'), ('D10000', '1'), ('D20000', '1'), ('D40000', '1'), ('D50000', '1'), ('D60000', '1'), ('D30100', '1'), ('D36300', '1'), ('D36000', '1')], drilldown)

        # ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="genre"]/drilldown:item')
        # drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        # self.assertEqual([('Search', '1'), ('Programming', '1')], drilldown)
    def testSruDataCiteDOI(self):
        response = self.doSruQuery(**{"query": '"10.17026/dans-zqm-htb9"', 'maximumRecords': '1'})
        # print "RESPONSE:", etree.tostring(response)
        # doi:10.17026/dans-zqm-htb9

    def testSruQueryWithMultipleDrilldownDataCite(self):
        response = self.doSruQuery(**{"query": 'untokenized.meta_collection exact "dataset"', 'maximumRecords': '0', "x-term-drilldown": "dd_cat:0,dd_year:2,meta_collection:0,meta_repositorygroupid:0,access:0,genre:0"})
        # print "DD body:", etree.tostring(response)
        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="access"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('openAccess', '2'), ('embargoedAccess', '1')], drilldown)

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="meta_repositorygroupid"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('4tu', '1'), ('easy', '1'), ('datacite', '1')], drilldown)


    def testSruQueryWithMultipleDrilldown(self):
        # response = self.doSruQuery(**{'maximumRecords': '0', "query": '*', "x-term-drilldown": "dd_penv:6,dd_thesis:6,dd_fin:6,status:5"})
        response = self.doSruQuery(**{"query": '*', 'maximumRecords': '0', "x-term-drilldown": "dd_cat:0,dd_year:2,meta_collection:0,meta_repositorygroupid:0,access:0,genre:0"})

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="access"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('openAccess', '5'), ('restrictedAccess', '3'), ('embargoedAccess', '2')], drilldown)

        ddItems = xpath(response, '//drilldown:term-drilldown/drilldown:navigator[@name="genre"]/drilldown:item')
        drilldown = [(i.text, i.attrib['count']) for i in ddItems]
        self.assertEqual([('dataset', '3'), ('article', '2'), ('book', '1'), ('doctoralthesis', '1'), ('report', '1')], drilldown)

        # TODO: Uitzoeken waarom ie wel naar storage gaat om records op te halen, hoewel startrecord over de limiet is???
    def testSruLimitStartRecord(self):
        response = self.doSruQuery(**{'maximumRecords': '1', 'startRecord': '4002', 'query':'*'})
        self.assertEqual("Argument 'startRecord' too high, maximum: 4000", xpathFirst(response, '//diag:diagnostic/diag:details/text()'))

    def testOai(self):
        header, body = getRequest(self.apiPort, '/oai', dict(verb="ListRecords", metadataPrefix="oai_dc"))
        # print "OAI body:", etree.tostring(body) #
        records = xpath(body, '//oai:record/oai:metadata')
        self.assertEqual(10, len(records))
        self.assertEqual('http://www.openarchives.org/OAI/2.0/oai_dc/', xpathFirst(body, '//oaiprov:provenance/oaiprov:originDescription/oaiprov:metadataNamespace/text()'))
        
    def testOaiSubject(self):
        header, body = getRequest(self.apiPort, '/oai', dict(verb="GetRecord", identifier = "meresco:record:1",   metadataPrefix="oai_dc"))
        self.assertEqual('Search', xpathFirst(body, '//dc:subject/text()'))
        

    # def testOaiPovenance(self):
    #     header, body = getRequest(self.apiPort, '/oai', dict(verb="ListRecords", metadataPrefix="oai_dc"))
    #     # print "OAI body:", etree.tostring(body)
    #     self.assertEqual('http://www.openarchives.org/OAI/2.0/oai_dc/', xpathFirst(body, '//oaiprov:provenance/oaiprov:originDescription/oaiprov:metadataNamespace/text()'))

    def testOaiIdentify(self):
        header, body = getRequest(self.apiPort, '/oai', dict(verb="Identify"))
        # print "OAI body:", etree.tostring(body)
        self.assertEqual('NARCIS OAI-pmh', xpathFirst(body, '//oai:Identify/oai:repositoryName/text()'))
        self.assertEqual('Narcis - The gateway to scholarly information in The Netherlands', testNamespaces.xpathFirst(body, '//oai:Identify/oai:description/oaibrand:branding/oaibrand:collectionIcon/oaibrand:title/text()'))

    def testOaiListSets(self):
        header, body = getRequest(self.apiPort, '/oai', dict(verb="ListSets"))
        # print "ListSets", etree.tostring(body)
        self.assertEqual({'publication','openaire','oa_publication','ec_fundedresources','thesis','dataset'}, set(xpath(body, '//oai:setSpec/text()')))

    def testOaiListMetadataFormats(self):
        header, body = getRequest(self.apiPort, '/oai', dict(verb="ListMetadataFormats"))
        # print "ListMetadataFormats", etree.tostring(body)
        self.assertEqual('oai_dc', xpathFirst(body, '//oai:metadataFormat/oai:metadataPrefix/text()'))
        

    def testRSS(self):
        header, body = getRequest(self.apiPort, '/rss', dict(query="*", querylabel='MyLabel', sortKeys='untokenized.dateissued,,0', startRecord='4'))
        # print "RSS body:", etree.tostring(body)
        # print set(xpath(body, "//item/description/text()"))
        items = xpath(body, "/rss/channel/item")
        self.assertEquals(11, len(items))
        self.assertTrue(xpathFirst(body, '//item/link/text()').endswith('Language/nl'))
        self.assertEqual({'Paden en stromingen---a historical survey', 'Preface to special issue (Fast reaction - slow diffusion scenarios: PDE approximations and free boundaries)', 'Conditiebepaling PVC', 'Appositie en de interne struktuur van de NP', 'Example Program 2', 'Locatie [Matthijs Tinxgracht 16] te Edam, gemeente Edam-Volendam. Een archeologische opgraving.', u'\u042d\u043a\u043e\u043b\u043e\u0433\u043e-\u0440\u0435\u043a\u0440\u0435\u0430\u0446\u0438\u043e\u043d\u043d\u044b\u0439 \u043a\u043e\u0440\u0438\u0434\u043e\u0440 \u0432 \u0433\u043e\u0440\u043d\u043e\u043c \u0437\u0430\u043f\u043e\u0432\u0435\u0434\u043d\u0438\u043a\u0435 \u0411\u043e\u0433\u043e\u0442\u044b', 'Bennis, Prof.dr. H.J. (Hans)', 'Late-type Giants in the Inner Galaxy', 'Wetenschapswinkel', "The Language Designer's Workbench: Automating Verification of Language Definitions"}, set(xpath(body, "//item/title/text()")))
        self.assertEqual({'Abstract van dit document', 'FransHeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeellllllang', 'Microvariatie; (Generatieve) Syntaxis; Morphosyntaxis; Syntaxis-Semantiek Interface; Dialectologie', 'Abstract', 'Samenvatting', 'Projectomschrijving<br>Ontwikkeling van betrouwbare methoden, procedures\n            en extrapolatiemodellen om de conditie en restlevensduur van in gebruik zijnde\n            PVC-leidingen te bepalen.<br>Beoogde projectopbrengsten<br>- uitwerking van\n            huidige kennis en inzichten m.b.t.', 'De KNAW vervult drie (wettelijke) taken: genootschap van excellente wetenschappers uit\n        alle disciplines; bestuurder van wetenschappelijke onderzoeksinstituten; adviseur van de\n        regering op het gebied van wetenschapsbeoefening. Zijne Majesteit de Koning is beschermheer\n        van de', 'The present thesis describes the issue of\n            "neonatal glucocorticoid treatment and predisposition to\n            cardiovascular disease in rats".', 'This is an example program about Programming with Meresco'}, set(xpath(body, "//item/description/text()")))
        self.assertEqual('MyLabel', xpathFirst(body, '//channel/title/text()'))

    def testDcToLong(self):
        response = self.doSruQuery(**{'query': '2016-05-05', 'recordSchema':'knaw_long'})
        self.assertEqual(1, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))
        self.assertEqual('restrictedAccess', testNamespaces.xpathFirst(response, '//long:knaw_long/long:accessRights/text()'))
        self.assertEqual('Example Program 1', testNamespaces.xpathFirst(response, '//long:metadata/long:titleInfo/long:title/text()'))
        self.assertEqual('personal', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:type/text()'))
        self.assertEqual('Seecr', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:unstructured/text()'))
        self.assertEqual('aut', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:mcRoleTerm/text()'))
        self.assertEqual('Seecr', testNamespaces.xpathFirst(response, '//long:metadata/long:publisher/text()'))
        self.assertEqual('Search', testNamespaces.xpathFirst(response, '//long:metadata/long:subject/long:topic/long:topicValue/text()'))
        self.assertEqual('This is an example program about Search with Meresco', testNamespaces.xpathFirst(response, '//long:metadata/long:abstract/text()'))
        self.assertEqual('2016-5-5', testNamespaces.xpathFirst(response, '//long:metadata/long:dateIssued/long:unParsed/text()'))
        self.assertEqual('2016-05-05', testNamespaces.xpathFirst(response, '//long:metadata/long:dateIssued/long:parsed/text()'))
        self.assertEqual('en', testNamespaces.xpathFirst(response, '//long:metadata/long:language/text()'))
        self.assertEqual(1, len(testNamespaces.xpath(response, '//long:metadata/long:name')))
        self.assertEqual(1, len(testNamespaces.xpath(response, '//long:metadata/long:subject/long:topic')))
        self.assertEqual(2, len(testNamespaces.xpath(response, '//long:metadata/long:publication_identifier')))
        self.assertEqual('10.1002/lno.10611', testNamespaces.xpathFirst(response, '//long:metadata/long:publication_identifier/text()'))
        self.assertEqual(2, len(testNamespaces.xpath(response, '//long:metadata/long:related_identifier')))
        self.assertEqual('10.1234.567/abc', testNamespaces.xpathFirst(response, '//long:metadata/long:related_identifier/text()'))

    def testDidlDcToLong(self):
        response = self.doSruQuery(**{'query': '2016-01-31', 'recordSchema':'knaw_long'})
        self.assertEqual(1, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))
        self.assertEqual('doi:10.4121/collection:ab70dbf9-ac4f-40a7-9859-9552d38fdccd', testNamespaces.xpathFirst(response, '//long:persistentIdentifier/text()'))
        self.assertEqual('openAccess', testNamespaces.xpathFirst(response, '//long:knaw_long/long:accessRights/text()'))
        self.assertEqual('RAIN: Pan-European gridded data sets of extreme weather probability of occurrence under present and future climate', testNamespaces.xpathFirst(response, '//long:metadata/long:titleInfo/long:title/text()'))
        self.assertEqual('personal', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:type/text()'))
        self.assertEqual('European Severe Storms Laboratory', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:unstructured/text()'))
        self.assertEqual('aut', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:mcRoleTerm/text()'))
        self.assertEqual('TU Delft', testNamespaces.xpathFirst(response, '//long:metadata/long:publisher/text()'))
        self.assertEqual('Precipitation', testNamespaces.xpathFirst(response, '//long:metadata/long:subject/long:topic/long:topicValue/text()'))
        self.assertEqual('This collection contains results  of Work Package 2 "Hazard Identification" of project RAIN', testNamespaces.xpathFirst(response, '//long:metadata/long:abstract/text()')[0:91])
        self.assertEqual('2016/1/31', testNamespaces.xpathFirst(response, '//long:metadata/long:dateIssued/long:unParsed/text()'))
        self.assertEqual('2016-01-31', testNamespaces.xpathFirst(response, '//long:metadata/long:dateIssued/long:parsed/text()'))
        self.assertEqual('years 1971-2100', testNamespaces.xpathFirst(response, '//long:metadata/long:coverage/text()'))
        self.assertEqual('application/pdf', testNamespaces.xpathFirst(response, '//long:metadata/long:format/text()'))
        self.assertEqual('en', testNamespaces.xpathFirst(response, '//long:metadata/long:language/text()'))
        self.assertEqual(4, len(testNamespaces.xpath(response, '//long:metadata/long:name')))
        self.assertEqual(1, len(testNamespaces.xpath(response, '//long:metadata/long:publisher')))
        self.assertEqual(10, len(testNamespaces.xpath(response, '//long:metadata/long:subject/long:topic')))
        self.assertEqual(2, len(testNamespaces.xpath(response, '//long:metadata/long:coverage')))
        self.assertEqual(4, len(testNamespaces.xpath(response, '//long:metadata/long:format')))
    
    def testModsToLong(self):
        response = self.doSruQuery(**{'query': 'URN:NBN:NL:UI:17-565', 'recordSchema':'knaw_long'})
        self.assertEqual(1, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))
        self.assertEqual('URN:NBN:NL:UI:17-565', testNamespaces.xpathFirst(response, '//long:persistentIdentifier/text()'))
        self.assertEqual('openAccess', testNamespaces.xpathFirst(response, '//long:knaw_long/long:accessRights/text()'))
        self.assertEqual('Appositie en de interne struktuur van de NP', testNamespaces.xpathFirst(response, '//long:metadata/long:titleInfo/long:title/text()'))
        self.assertEqual('personal', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:type/text()'))
        self.assertEqual('Bennis&Bennis', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:family/text()'))
        self.assertEqual('prof.dr. H.J.', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:given/text()'))
        self.assertEqual('aut', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:mcRoleTerm/text()'))
        self.assertEqual('http://isni.org/isni/0000000081508690', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:nameIdentifier[@type="isni"]/text()'))
        self.assertEqual('http://orcid.org/0000-0002-1825-0097', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:nameIdentifier[@type="orcid"]/text()'))
        self.assertEqual('info:eu-repo/dai/nl/068519397', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:nameIdentifier[@type="dai-nl"]/text()'))
        self.assertEqual('Blackwell Publishers', testNamespaces.xpathFirst(response, '//long:metadata/long:relatedItem[@type="host"]/long:publisher/text()'))
        self.assertEqual('2008 Royal Tropical Institute. This work is licensed under', testNamespaces.xpathFirst(response, '//long:metadata/long:rightsDescription/text()')[2:60])
        self.assertEqual('article', testNamespaces.xpathFirst(response, '//long:metadata/long:genre/text()'))
        self.assertEqual('This is the subject', testNamespaces.xpathFirst(response, '//long:metadata/long:subject/long:topic/long:topicValue/text()'))
        self.assertEqual('FransHeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeellllllang', testNamespaces.xpathFirst(response, '//long:metadata/long:abstract/text()'))
        self.assertEqual('opgraafdatum 3000 jaar voor christus', testNamespaces.xpathFirst(response, '//long:metadata/long:dateIssued/long:unParsed/text()'))
        self.assertEqual('00282162', testNamespaces.xpathFirst(response, '//long:metadata/long:publication_identifier[@type="issn"]/text()'))
        self.assertEqual('http://www.dds.nl/semantics/article', testNamespaces.xpathFirst(response, '//long:metadata/long:location_url/text()'))
        self.assertEqual('Amsterdam', testNamespaces.xpathFirst(response, '//long:metadata/long:placeTerm/text()'))
        self.assertEqual('text', testNamespaces.xpathFirst(response, '//long:metadata/long:typeOfResource/text()'))
        self.assertEqual('nl', testNamespaces.xpathFirst(response, '//long:metadata/long:language/text()'))
        self.assertEqual('info:eu-repo/grantAgreement/EC/FP5/654321', testNamespaces.xpathFirst(response, '//long:metadata/long:grantAgreements/long:grantAgreement/long:code/text()'))
        self.assertEqual('EERA Design Tools for Offshore Wind Farm Cluster (EERA-DTOC)', testNamespaces.xpathFirst(response, '//long:metadata/long:grantAgreements/long:grantAgreement/long:title/text()'))
        self.assertEqual('The European Energy Research Alliance (EERA)', testNamespaces.xpathFirst(response, '//long:metadata/long:grantAgreements/long:grantAgreement/long:description/text()')[0:44])
        self.assertEqual('Uni, Versiteit', testNamespaces.xpathFirst(response, '//long:metadata/long:grantAgreements/long:grantAgreement/long:funder/text()'))
        self.assertEqual('8', testNamespaces.xpathFirst(response, '//long:metadata/long:relatedItem[@type="host"]/long:part/long:volume/text()'))
        self.assertEqual('5', testNamespaces.xpathFirst(response, '//long:metadata/long:relatedItem[@type="host"]/long:part/long:issue/text()'))
        self.assertEqual('209', testNamespaces.xpathFirst(response, '//long:metadata/long:relatedItem[@type="host"]/long:part/long:start_page/text()'))
        self.assertEqual('228', testNamespaces.xpathFirst(response, '//long:metadata/long:relatedItem[@type="host"]/long:part/long:end_page/text()'))
        self.assertEqual('Spektator', testNamespaces.xpathFirst(response, '//long:metadata/long:relatedItem[@type="host"]/long:titleInfo[@xml:lang="en"]/long:title/text()'))
        self.assertEqual('00286666', testNamespaces.xpathFirst(response, '//long:metadata/long:relatedItem[@type="host"]/long:publication_identifier[@type="issn"]/text()'))
        self.assertEqual('Oxford', testNamespaces.xpathFirst(response, '//long:metadata/long:relatedItem[@type="host"]/long:placeTerm/text()'))
        self.assertEqual(0, len(testNamespaces.xpathFirst(response, '//long:objectFiles/long:objectFile/long:resource[@mimeType="application/pdf" and @ref="http://depot.knaw.nl/565/1/14807.pdf"]')))
        self.assertEqual(3, len(testNamespaces.xpath(response, '//long:metadata/long:name')))
        self.assertEqual(1, len(testNamespaces.xpath(response, '//long:metadata/long:rightsDescription')))
        self.assertEqual(1, len(testNamespaces.xpath(response, '//long:metadata/long:subject[@xml:lang="en"]/long:topic')))
        self.assertEqual(2, len(testNamespaces.xpath(response, '//long:metadata/long:grantAgreements/long:grantAgreement')))
 
    
    def testMods3xToLong(self):
        response = self.doSruQuery(**{'query': 'urn:NBN:nl:ui:18-2271', 'recordSchema':'knaw_long'}) # knaw_record2_didlmods
        self.assertEqual(1, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))
        self.assertEqual('urn:NBN:nl:ui:18-2271', testNamespaces.xpathFirst(response, '//long:persistentIdentifier/text()'))
        self.assertEqual('closedAccess', testNamespaces.xpathFirst(response, '//long:objectFiles/long:objectFile/long:accessRights/text()'))
        self.assertEqual('urn:NBN:nl:ui:18-2271-OF', testNamespaces.xpathFirst(response, '//long:objectFiles/long:objectFile/long:persistentIdentifier/text()'))
        self.assertEqual('2012-01-01', testNamespaces.xpathFirst(response, '//long:objectFiles/long:objectFile/long:embargo/text()'))
        self.assertEqual('embargoedAccess', testNamespaces.xpathFirst(response, '//long:knaw_long/long:accessRights/text()'))
        self.assertEqual('Paths and flows---a historical survey', testNamespaces.xpathFirst(response, '//long:metadata/long:titleInfo[@xml:lang="en"]/long:title/text()'))
        self.assertEqual('personal', testNamespaces.xpathFirst(response, '//long:metadata/long:name[2]/long:type/text()'))
        self.assertEqual('prof.dr. Bennis, H. (Hans)', testNamespaces.xpathFirst(response, '//long:metadata/long:name[2]/long:unstructured/text()'))
        self.assertEqual('Bennis', testNamespaces.xpathFirst(response, '//long:metadata/long:name[2]/long:family/text()'))
        self.assertEqual('prof.dr. H.J. (Hans)', testNamespaces.xpathFirst(response, '//long:metadata/long:name[2]/long:given/text()'))
        self.assertEqual('dgg', testNamespaces.xpathFirst(response, '//long:metadata/long:name[2]/long:mcRoleTerm/text()'))
        self.assertEqual('http://orcid.org/0000-0002-1825-0097', testNamespaces.xpathFirst(response, '//long:metadata/long:name[2]/long:nameIdentifier[@type="orcid"]/text()'))
        self.assertEqual('info:eu-repo/dai/nl/071792279', testNamespaces.xpathFirst(response, '//long:metadata/long:name[2]/long:nameIdentifier[@type="dai-nl"]/text()'))
        self.assertEqual('Copyright (c) Aiki, T (Toyohiko); Copyright (c) Hilhorst, D; Copyright (c) Mimura,', testNamespaces.xpathFirst(response, '//long:metadata/long:rightsDescription/text()')[0:82])
        self.assertEqual('book', testNamespaces.xpathFirst(response, '//long:metadata/long:genre/text()'))
        self.assertEqual('freight', testNamespaces.xpathFirst(response, '//long:metadata/long:subject[not(@xml:lang)]/long:topic/long:topicValue/text()'))
        self.assertEqual('In english please.', testNamespaces.xpathFirst(response, '//long:metadata/long:subject[@xml:lang="en"]/long:topic/long:topicValue/text()'))
        self.assertEqual('Samenvatting', testNamespaces.xpathFirst(response, '//long:metadata/long:abstract/text()'))
        self.assertEqual('1993-1-01', testNamespaces.xpathFirst(response, '//long:metadata/long:dateIssued/long:unParsed/text()'))
        self.assertEqual('1993-01-01', testNamespaces.xpathFirst(response, '//long:metadata/long:dateIssued/long:parsed/text()'))
        self.assertEqual('0010-440X', testNamespaces.xpathFirst(response, '//long:metadata/long:publication_identifier[@type="issn"]/text()'))
        self.assertEqual('9002233389', testNamespaces.xpathFirst(response, '//long:metadata/long:publication_identifier[@type="isbn"]/text()'))
        self.assertEqual('http://repository-acc.ubn.ru.nl/handle/123456789/126651', testNamespaces.xpathFirst(response, '//long:metadata/long:related_identifier/text()'))
        self.assertEqual('http://repository.cwi.nl/search/fullrecord.php?publnr=2271', testNamespaces.xpathFirst(response, '//long:metadata/long:location_url/text()'))
        self.assertEqual('text', testNamespaces.xpathFirst(response, '//long:metadata/long:typeOfResource/text()'))
        self.assertEqual('en', testNamespaces.xpathFirst(response, '//long:metadata/long:language/text()'))
        self.assertEqual('info:eu-repo/grantAgreement/EC/FP7/282797', testNamespaces.xpathFirst(response, '//long:metadata/long:grantAgreements/long:grantAgreement/long:code/text()'))
        self.assertEqual('EERA Design Tools for Offshore Wind Farm Cluster (EERA-DTOC)', testNamespaces.xpathFirst(response, '//long:metadata/long:grantAgreements/long:grantAgreement/long:title/text()'))
        self.assertEqual('The European Energy Research Alliance (EERA)', testNamespaces.xpathFirst(response, '//long:metadata/long:grantAgreements/long:grantAgreement/long:description/text()')[0:44])
        self.assertEqual('European Commission CORDIS', testNamespaces.xpathFirst(response, '//long:metadata/long:grantAgreements/long:grantAgreement/long:funder/text()'))
        self.assertEqual(2, len(testNamespaces.xpathFirst(response, '//long:objectFiles/long:objectFile')))
        self.assertEqual(0, len(testNamespaces.xpathFirst(response, '//long:objectFiles/long:objectFile/long:resource[@mimeType="application/pdf" and @ref="http://oai.cwi.nl/oai/asset/2271/2271OA.pdf"]')))
        self.assertEqual(3, len(testNamespaces.xpath(response, '//long:metadata/long:name')))
        self.assertEqual(1, len(testNamespaces.xpath(response, '//long:metadata/long:rightsDescription')))
        self.assertEqual(7, len(testNamespaces.xpath(response, '//long:metadata/long:subject/long:topic')))
        self.assertEqual(3, len(testNamespaces.xpath(response, '//long:metadata/long:grantAgreements/long:grantAgreement')))
        
        response = self.doSruQuery(**{'query': 'URN:NBN:NL:UI:25-711504', 'recordSchema':'knaw_long'}) # TODO find exact op pubid
        #print etree.tostring(response)
        self.assertEqual('restrictedAccess', testNamespaces.xpathFirst(response, '//long:objectFiles/long:objectFile/long:accessRights/text()'))
        self.assertEqual('restrictedAccess', testNamespaces.xpathFirst(response, '//long:knaw_long/long:accessRights/text()'))
 
    def testDataciteToLong(self):
        response = self.doSruQuery(**{'query': 'urn:nbn:nl:ui:13-jsk-7ek', 'recordSchema':'knaw_long'})
        self.assertEqual(1, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))
        self.assertEqual('urn:nbn:nl:ui:13-jsk-7ek', testNamespaces.xpathFirst(response, '//long:persistentIdentifier/text()'))
        self.assertEqual('doi:10.17026/dans-zqm-htb9', testNamespaces.xpathFirst(response, '//long:humanStartPage/text()'))
        self.assertEqual('embargoedAccess', testNamespaces.xpathFirst(response, '//long:accessRights/text()'))
        self.assertEqual('Locatie [Matthijs Tinxgracht 16] te Edam, gemeente Edam-Volendam.', testNamespaces.xpathFirst(response, '//long:metadata/long:titleInfo/long:title/text()')[0:65])
        self.assertEqual('Jacobs, E.', testNamespaces.xpathFirst(response, '//long:metadata/long:name[1]/long:unstructured/text()'))
        self.assertEqual('personal', testNamespaces.xpathFirst(response, '//long:metadata/long:name[1]/long:type/text()'))
        self.assertEqual('Burnier, C.Y.', testNamespaces.xpathFirst(response, '//long:metadata/long:name[2]/long:unstructured/text()'))
        self.assertEqual('corporate', testNamespaces.xpathFirst(response, '//long:metadata/long:name[2]/long:type/text()'))
        self.assertEqual('Miller, Elizabeth', testNamespaces.xpathFirst(response, '//long:metadata/long:name[3]/long:unstructured/text()'))
        self.assertEqual('personal', testNamespaces.xpathFirst(response, '//long:metadata/long:name[3]/long:type/text()'))
        self.assertEqual('Miller', testNamespaces.xpathFirst(response, '//long:metadata/long:name[3]/long:family/text()'))
        self.assertEqual('Elizabeth', testNamespaces.xpathFirst(response, '//long:metadata/long:name[3]/long:given/text()'))
        self.assertEqual('cre', testNamespaces.xpathFirst(response, '//long:metadata/long:name[3]/long:mcRoleTerm/text()'))
        self.assertEqual('ctb', testNamespaces.xpathFirst(response, '//long:metadata/long:name[5]/long:mcRoleTerm/text()'))
        self.assertEqual('http://orcid.org/0000-0001-5000-0007', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:nameIdentifier[@type="orcid"]/text()'))
        self.assertEqual('info:eu-repo/dai/nl/072728442', testNamespaces.xpathFirst(response, '//long:metadata/long:name/long:nameIdentifier[@type="dai-nl"]/text()'))
        self.assertEqual('Groningen Institute of Archaeology, University of Groningen', testNamespaces.xpathFirst(response, '//long:metadata/long:name[1]/long:affiliation/text()'))
        self.assertEqual('Jacobs en Burnier, archeologisch projectbureau', testNamespaces.xpathFirst(response, '//long:metadata/long:publisher/text()'))
        self.assertEqual('Archaeology', testNamespaces.xpathFirst(response, '//long:metadata/long:subject/long:topic[long:subjectScheme/text() = "NARCIS-classification"]/long:topicValue/text()'))
        self.assertEqual('OPGRAVING', testNamespaces.xpathFirst(response, '//long:metadata/long:subject[@xml:lang="en"]/long:topic/long:topicValue/text()'))
        self.assertEqual('ABR-complex', testNamespaces.xpathFirst(response, '//long:metadata/long:subject[not(@xml:lang)]/long:topic/long:subjectScheme/text()'))
        self.assertEqual('Abstract van dit document', testNamespaces.xpathFirst(response, '//long:metadata/long:abstract/text()'))
        self.assertEqual('Abstract of this document', testNamespaces.xpathFirst(response, '//long:metadata/long:abstract[@xml:lang="en"]/text()'))
        self.assertEqual('2009-9-4', testNamespaces.xpathFirst(response, '//long:metadata/long:dateSubmitted/long:unParsed/text()'))
        self.assertEqual('2009-09-04', testNamespaces.xpathFirst(response, '//long:metadata/long:dateSubmitted/long:parsed/text()'))
        self.assertEqual('2009-11-24', testNamespaces.xpathFirst(response, '//long:metadata/long:dateAvailable/long:parsed/text()'))
        self.assertEqual('urn:nbn:nl:ui:13-jsk-7ek', testNamespaces.xpathFirst(response, '//long:metadata/long:publication_identifier[@type="nbn"]/text()'))
        self.assertEqual('dataset', testNamespaces.xpathFirst(response, '//long:metadata/long:typeOfResource/@generaltype'))
        self.assertEqual('Dataset/Dataset en zo', testNamespaces.xpathFirst(response, '//long:metadata/long:typeOfResource/text()'))
        self.assertEqual('dataset', testNamespaces.xpathFirst(response, '//long:metadata/long:genre/text()'))
        self.assertEqual('European Commission', testNamespaces.xpathFirst(response, '//long:metadata/long:grantAgreements//long:grantAgreement/long:funder/text()'))
        self.assertEqual('nl', testNamespaces.xpathFirst(response, '//long:metadata/long:language/text()'))
        self.assertEqual('19 p.', testNamespaces.xpathFirst(response, '//long:metadata/long:format/text()'))
        self.assertEqual('Matthijs Tinxgracht 16', testNamespaces.xpathFirst(response, '//long:metadata/long:geoLocations/long:geoLocation[3]/long:geoLocationPlace/text()'))
        self.assertEqual('52.51483176', testNamespaces.xpathFirst(response, '//long:metadata/long:geoLocations/long:geoLocation[3]/long:geoLocationPoint/long:pointLongitude/text()'))
        self.assertEqual('5.04757305', testNamespaces.xpathFirst(response, '//long:metadata/long:geoLocations/long:geoLocation[3]/long:geoLocationPoint/long:pointLatitude/text()'))
        self.assertEqual('51.69204992', testNamespaces.xpathFirst(response, '//long:metadata/long:geoLocations/long:geoLocation[4]/long:geoLocationBox/long:northBoundLatitude/text()'))
        self.assertEqual(5, len(testNamespaces.xpath(response, '//long:metadata/long:name')))
        self.assertEqual(8, len(testNamespaces.xpath(response, '//long:metadata/long:subject[not(@xml:lang)]/long:topic')))
        self.assertEqual(2, len(testNamespaces.xpath(response, '//long:metadata/long:abstract')))
        self.assertEqual(4, len(testNamespaces.xpath(response, '//long:metadata/long:geoLocations/long:geoLocation')))

    def testProjectToShort(self):
        response = self.doSruQuery(**{'query': 'OND1272024', 'recordSchema':'knaw_short'})
        self.assertEqual(1, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))
        self.assertEqual('Conditiebepaling PVC', testNamespaces.xpathFirst(response, '//short:metadata/short:titleInfo/short:title/text()'))
        self.assertEqual('research', testNamespaces.xpathFirst(response, '//short:metadata/short:genre/text()'))
        self.assertEqual('Projectomschrijving<br>Ontwikkeling van betrouwbare methoden,', testNamespaces.xpathFirst(response, '//short:metadata/short:abstract/text()')[:61])
        self.assertEqual(2, len(testNamespaces.xpath(response, '//short:metadata/short:titleInfo/short:title')))
     
    def testOrganisationToShort(self):
        response = self.doSruQuery(**{'query': 'ORG1236141', 'recordSchema':'knaw_short'})
        self.assertEqual(1, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))
        self.assertEqual('Wetenschapswinkel', testNamespaces.xpathFirst(response, '//short:metadata/short:titleInfo/short:title/text()'))
        self.assertEqual('organisation', testNamespaces.xpathFirst(response, '//short:metadata/short:genre/text()'))
        self.assertEqual(1, len(testNamespaces.xpath(response, '//short:metadata/short:titleInfo/short:title')))
        self.assertEqual('Wetenschapswinkel', testNamespaces.xpathFirst(response, '//short:metadata/short:name/short:name/text()'))
        self.assertEqual('0000000121536865', testNamespaces.xpathFirst(response, '//short:metadata/short:name/short:nameIdentifier[@type="isni"]/text()'))
        self.assertEqual('008pnp284', testNamespaces.xpathFirst(response, '//short:metadata/short:name/short:nameIdentifier[@type="ror"]/text()'))

    def testPersonToShort(self):
        response = self.doSruQuery(**{'query': 'person:PRS1242583', 'recordSchema':'knaw_short'})
        self.assertEqual(1, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))
        self.assertEqual('Bennis, Prof.dr. H.J. (Hans)', testNamespaces.xpathFirst(response, '//short:metadata/short:titleInfo/short:title/text()'))
        self.assertEqual('person', testNamespaces.xpathFirst(response, '//short:metadata/short:genre/text()'))
        self.assertEqual('Microvariation; (Generative) Syntax; Morphosyntax;', testNamespaces.xpathFirst(response, '//short:metadata/short:abstract[@xml:lang="en"]/text()')[:50])
        self.assertEqual('personal', testNamespaces.xpathFirst(response, '//short:metadata/short:name/short:type/text()'))
        self.assertEqual('Bennis, Prof.dr. H.J. (Hans)', testNamespaces.xpathFirst(response, '//short:metadata/short:name/short:name/text()'))
        self.assertEqual('071792279', testNamespaces.xpathFirst(response, '//short:metadata/short:name/short:nameIdentifier[@type="dai-nl"]/text()'))
        self.assertEqual('0000000081508690', testNamespaces.xpathFirst(response, '//short:metadata/short:name/short:nameIdentifier[@type="isni"]/text()'))
        self.assertEqual('0000-0002-4703-3788', testNamespaces.xpathFirst(response, '//short:metadata/short:name/short:nameIdentifier[@type="orcid"]/text()'))
        self.assertEqual('PRS1242583', testNamespaces.xpathFirst(response, '//short:metadata/short:name/short:nameIdentifier[@type="nod-prs"]/text()'))
        self.assertEqual(4, len(testNamespaces.xpath(response, '//short:metadata/short:name/short:nameIdentifier')))
     

    def assertSruQuery(self, numberOfRecords, query, printout=False):
        response = self.doSruQuery(**{'query':query, "recordSchema": "knaw_short", "x-recordSchema": "header"}) # , 'maximumRecords': '1'
        if printout: print "SruQuery response:", etree.tostring(response, pretty_print = True, encoding='utf-8')
        self.assertEquals(numberOfRecords, int(str(xpathFirst(response, '//srw:numberOfRecords/text()'))))

    def doSruQuery(self, **arguments):
        queryArguments = {'version': '1.2', 'operation': 'searchRetrieve'}
        queryArguments.update(arguments)
        header, body = getRequest(self.apiPort, '/sru', queryArguments)
        return body
