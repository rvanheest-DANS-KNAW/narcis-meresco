#-*- coding: utf-8 -*-
## begin license ##
#
# Copyright (C) 2012-2016 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) Data Archiving and Networked Services (DANS) http://dans.knaw.nl
#
# This file is part of "NARCIS Index"
#
# "NARCIS Index" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "NARCIS Index" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "NARCIS Index"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import sys
from os.path import join, dirname, abspath

from weightless.core import be, consume
from weightless.io import Reactor

from meresco.components.drilldown import SruTermDrilldown
from meresco.core import Observable
from meresco.core.alltodo import AllToDo
from meresco.core.processtools import setSignalHandlers, registerShutdownHandler

from meresco.components import RenameFieldForExact, PeriodicDownload, XmlPrintLxml, XmlXPath, FilterMessages, RewritePartname, XmlParseLxml, CqlMultiSearchClauseConversion, PeriodicCall, Schedule, XsltCrosswalk #, Rss, RssItem
from meresco.components.cql import SearchTermFilterAndModifier
from meresco.components.http import ObservableHttpServer, BasicHttpHandler, PathFilter, Deproxy
from meresco.components.log import LogCollector, ApacheLogWriter, HandleRequestLog, LogCollectorScope, QueryLogWriter, DirectoryLog, LogFileServer, LogComponent
from meresco.components.sru import SruHandler, SruParser, SruLimitStartRecord

from meresco.oai import OaiDownloadProcessor, UpdateAdapterFromOaiDownloadProcessor, OaiJazz, OaiPmh, OaiAddDeleteRecordWithPrefixesAndSetSpecs, OaiBranding, OaiProvenance

from meresco.lucene import SORTED_PREFIX, UNTOKENIZED_PREFIX
from meresco.lucene.remote import LuceneRemote
from meresco.lucene.converttocomposedquery import ConvertToComposedQuery

####### start lucene integration #############
from meresco.lucene import Lucene, MultiLucene, UNTOKENIZED_PREFIX, SORTED_PREFIX
from meresco.lucene.adaptertolucenequery import AdapterToLuceneQuery
from meresco.lucene.fieldregistry import FieldRegistry
from meresco.lucene import LuceneSettings, DrilldownField#, FieldsListToLuceneDocument
from weightless.http import HttpRequest1_1, SocketPool
from meresco.lucene.queryexpressiontolucenequerydict import QueryExpressionToLuceneQueryDict
####### end lucene integration #############

from seecr.utils import DebugPrompt

from meresco.dans.merescocomponents import Rss, RssItem

from meresco.components.drilldownqueries import DrilldownQueries
from storage import StorageComponent
from meresco.dans.storagesplit import Md5HashDistributeStrategy
from meresco.dans.writedeleted import ResurrectTombstone, WriteTombstone
from meresco.dans.shortconverter import ShortConverter
from meresco.dans.oai_dcconverter import DcConverter
from meresco.dans.filterwcpcollection import FilterWcpCollection

from meresco.xml import namespaces

from storage.storageadapter import StorageAdapter

from meresco.servers.index.indexserver import untokenizedFieldname, untokenizedFieldnames, drilldownFields, DEFAULT_CORE, UNQUALIFIED_TERM_FIELDS
from meresco.servers.gateway.gatewayserver import NORMALISED_DOC_NAME


OAI_DC_PARTNAME = 'oai_dc'
HEADER_PARTNAME = 'header'
META_PARTNAME = 'meta'
METADATA_PARTNAME = 'metadata'
LONG_PARTNAME = 'knaw_long'
SHORT_PARTNAME = 'knaw_short'

NAMESPACEMAP = namespaces.copyUpdate({
    'prs'   : 'http://www.onderzoekinformatie.nl/nod/prs',
    'prj'   : 'http://www.onderzoekinformatie.nl/nod/act',
    'org'   : 'http://www.onderzoekinformatie.nl/nod/org',
    'long'  : 'http://www.knaw.nl/narcis/1.0/long/',
    'short' : 'http://www.knaw.nl/narcis/1.0/short/',
    'mods'  :'http://www.loc.gov/mods/v3',
    'didl'  : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
    'norm'  : 'http://dans.knaw.nl/narcis/normalized',
})


######## START Lucene Integration ###############################################################

def luceneAndReaderConfig(defaultLuceneSettings, httpRequestAdapter, lucenePort):

    fieldRegistry = FieldRegistry(drilldownFields=drilldownFields)
    luceneIndex = be((Lucene(
            host='127.0.0.1',
            port=lucenePort,
            name=DEFAULT_CORE,
            settings=defaultLuceneSettings.clone(fieldRegistry=fieldRegistry)
        ),
        (httpRequestAdapter,)
    ))
    return luceneIndex
######## END Lucene Integration ###############################################################


def main(reactor, port, statePath, lucenePort, **ignored):


######## START Lucene Integration ###############################################################
    defaultLuceneSettings = LuceneSettings(
        commitTimeout=30,
        readonly=True,)
    
    
    http11Request = be(
        (HttpRequest1_1(),
            (SocketPool(reactor=reactor, unusedTimeout=5, limits=dict(totalSize=100, destinationSize=10)),),
        )
    )
    
    luceneIndex = luceneAndReaderConfig(defaultLuceneSettings.clone(readonly=True), http11Request, lucenePort)
    
    
    luceneRoHelix = be(
        (AdapterToLuceneQuery(
                defaultCore=DEFAULT_CORE,
                coreConverters={
                    DEFAULT_CORE: QueryExpressionToLuceneQueryDict(UNQUALIFIED_TERM_FIELDS, luceneSettings=luceneIndex.settings),
                }
            ),
            (MultiLucene(host='127.0.0.1', port=lucenePort, defaultCore=DEFAULT_CORE),
                (luceneIndex,),
                (http11Request,),
            )
        )
    )

######## END Lucene Integration ###############################################################


    fieldnameRewrites = {}

    def fieldnameRewrite(name):
        return fieldnameRewrites.get(name, name)

    def drilldownFieldnamesTranslate(fieldname):
        untokenizedName = untokenizedFieldname(fieldname)
        if untokenizedName in untokenizedFieldnames:
            fieldname = untokenizedName
        return fieldnameRewrite(fieldname)

    convertToComposedQuery = ConvertToComposedQuery(
            resultsFrom=DEFAULT_CORE,
            matches=[],
            drilldownFieldnamesTranslate=drilldownFieldnamesTranslate
        )


    strategie = Md5HashDistributeStrategy()
    storage = StorageComponent(join(statePath, 'store'), strategy=strategie, partsRemovedOnDelete=[HEADER_PARTNAME, META_PARTNAME, METADATA_PARTNAME, OAI_DC_PARTNAME, LONG_PARTNAME, SHORT_PARTNAME])


    # Wat doet dit?
    cqlClauseConverters = [
        RenameFieldForExact(
            untokenizedFields=untokenizedFieldnames,
            untokenizedPrefix=UNTOKENIZED_PREFIX,
        ).filterAndModifier(),
        SearchTermFilterAndModifier(
            shouldModifyFieldValue=lambda *args: True,
            fieldnameModifier=fieldnameRewrite
        ).filterAndModifier(),
    ]



    executeQueryHelix = \
        (FilterMessages(allowed=['executeQuery']),
            (CqlMultiSearchClauseConversion(cqlClauseConverters, fromKwarg='query'),
                (DrilldownQueries(),
                    (convertToComposedQuery,
                        (luceneRoHelix,),
                    )
                )
            )
        )


    return \
    (Observable(),
        
        (ObservableHttpServer(reactor, port, compressResponse=True),
            (BasicHttpHandler(),
                (PathFilter(['/sru']),
                    (SruParser(
                            host='sru.narcis.nl',
                            port=80,
                            defaultRecordSchema='knaw_short',
                            defaultRecordPacking='xml'),
                        (SruLimitStartRecord(limitBeyond=4000),
                            (SruHandler(
                                    includeQueryTimes=False,
                                    extraXParameters=[],
                                    enableCollectLog=False), #2017-03-24T12:00:33Z 127.0.0.1 3.5K 0.019s - /sru OF (TRUE): 2017-03-24T11:58:53Z 127.0.0.1 2.3K 0.004s 1hits /sru maximumRecords=10&operation=searchRetrieve&query=untokenized.dd_year+exact+%221993%22&recordPacking=xml&recordSchema=knaw_short&startRecord=1&version=1.2
                                (SruTermDrilldown(),),
                                executeQueryHelix,
                                (StorageAdapter(),
                                    (storage,)
                                )
                            )
                        )
                    )
                ),
                (PathFilter('/rss'),
                    (Rss(   supportedLanguages = ['nl','en'], # defaults to first, if requested language is not available or supplied.
                            title = {'nl':'NARCIS', 'en':'NARCIS'},
                            description = {'nl':'NARCIS: De toegang tot de Nederlandse wetenschapsinformatie', 'en':'NARCIS: The gateway to Dutch scientific information'},
                            link = {'nl':'http://www.narcis.nl/?Language=nl', 'en':'http://www.narcis.nl/?Language=en'},
                            maximumRecords = 20),
                        executeQueryHelix,
                        (RssItem(
                                nsMap=NAMESPACEMAP,                                            
                                title = ('knaw_short', {'nl':'//short:metadata/short:titleInfo[not (@xml:lang)]/short:title/text()', 'en':'//short:metadata/short:titleInfo[@xml:lang="en"]/short:title/text()'}),
                                description = ('knaw_short', {'nl':'//short:abstract[not (@xml:lang)]/text()', 'en':'//short:abstract[@xml:lang="en"]/text()'}),
                                pubdate = ('knaw_short', '//short:dateIssued/short:parsed/text()'),
                                linkTemplate = 'http://www.narcis.nl/%(wcpcollection)s/RecordID/%(oai_identifier)s/Language/%(language)s',                                
                                wcpcollection = ('meta', '//*[local-name() = "collection"]/text()'),
                                oai_identifier = ('meta', '//meta:record/meta:id/text()'),
                                language = ('Dummy: Language is auto provided by the calling RSS component, but needs to be present to serve the linkTemplate.')
                            ),
                            (StorageAdapter(),
                                (storage,)
                            )
                        )
                    )
                )
            )
        )
    )

def startServer(port, stateDir, lucenePort, **kwargs):
    setSignalHandlers()
    print 'Firing up SRU-slave.'
    reactor = Reactor()
    statePath = abspath(stateDir)

    dna = main(
        reactor=reactor,
        port=port,
        statePath=statePath,
        lucenePort=lucenePort,
        **kwargs
    )

    server = be(dna)
    consume(server.once.observer_init())

    registerShutdownHandler(statePath=statePath, server=server, reactor=reactor, shutdownMustSucceed=False)

    print "Ready to rumble at %s" % port
    sys.stdout.flush()
    reactor.loop()
