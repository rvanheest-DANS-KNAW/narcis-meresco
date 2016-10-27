#-*- coding: utf-8 -*-
## begin license ##
#
# Drents Archief beoogt het Drents erfgoed centraal beschikbaar te stellen.
#
# Copyright (C) 2012-2016 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012-2014 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
# Copyright (C) 2015-2016 Drents Archief http://www.drentsarchief.nl
# Copyright (C) 2015 Koninklijke Bibliotheek (KB) http://www.kb.nl
#
# This file is part of "Drents Archief"
#
# "Drents Archief" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Drents Archief" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Drents Archief"; if not, write to the Free Software
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

from meresco.components import RenameFieldForExact, PeriodicDownload, XmlPrintLxml, XmlXPath, FilterMessages, RewritePartname, XmlParseLxml, CqlMultiSearchClauseConversion, PeriodicCall, Schedule, Rss, RssItem, XsltCrosswalk
from meresco.components.cql import SearchTermFilterAndModifier
from meresco.components.http import ObservableHttpServer, BasicHttpHandler, PathFilter, Deproxy
from meresco.components.log import LogCollector, ApacheLogWriter, HandleRequestLog, LogCollectorScope, QueryLogWriter, DirectoryLog, LogFileServer, LogComponent
from meresco.components.sru import SruHandler, SruParser, SruLimitStartRecord

from meresco.oai import OaiDownloadProcessor, UpdateAdapterFromOaiDownloadProcessor, OaiJazz, OaiPmh, OaiAddDeleteRecordWithPrefixesAndSetSpecs, OaiBranding, OaiProvenance

from meresco.lucene import SORTED_PREFIX, UNTOKENIZED_PREFIX
from meresco.lucene.remote import LuceneRemote
from meresco.lucene.converttocomposedquery import ConvertToComposedQuery

from seecr.utils import DebugPrompt

from meresco.components.drilldownqueries import DrilldownQueries
from storage import StorageComponent
from meresco.dans.storagesplit import Md5HashDistributeStrategy
from meresco.dans.writedeleted import ResurrectTombstone, WriteTombstone
from meresco.dans.shortconverter import ShortConverter
from meresco.dans.oai_dcconverter import DcConverter
# from meresco.dans.oaiprovenance import OaiProvenance
from meresco.xml import namespaces

from storage.storageadapter import StorageAdapter

from meresco.servers.index.indexserver import untokenizedFieldname, untokenizedFieldnames, DEFAULT_CORE
from meresco.servers.gateway.gatewayserver import NORMALISED_DOC_NAME

DEFAULT_PARTNAME = 'oai_dc'

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


def createDownloadHelix(reactor, periodicDownload, oaiDownload, storageComponent, oaiJazz):
    return \
    (periodicDownload, # Scheduled connection to a remote (response / request)...
        (XmlParseLxml(fromKwarg="data", toKwarg="lxmlNode", parseOptions=dict(huge_tree=True, remove_blank_text=True)), # Convert from plain text to lxml-object.
            (oaiDownload, # Implementation/Protocol of a PeriodicDownload...
                (UpdateAdapterFromOaiDownloadProcessor(), # Maakt van een SRU update/delete bericht (lxmlNode) een relevante message: 'delete' of 'add' message.
                    (FilterMessages(['delete']), # Filtert delete messages
                        # (LogComponent("Delete Update"),),
                        (storageComponent,), # Delete from storage
                        (oaiJazz,), # Delete from OAI-pmh repo
                        # Write a 'deleted' part to the storage, that holds the (Record)uploadId.
                        (WriteTombstone(),
                            (storageComponent,),
                        )
                    ),
                    (FilterMessages(['add']),
                        # TODO: onderstaande toKwarg='data' kan eruit. Dan de volgende regel ook:-)
                        (XmlXPath(['/oai:record/oai:metadata/document:document/document:part[@name="record"]/text()'], fromKwarg='lxmlNode', toKwarg='data', namespaces=NAMESPACEMAP),
                            (XmlParseLxml(fromKwarg='data', toKwarg='lxmlNode'),
                                (XmlXPath(['/oai:record/oai:metadata/norm:md_original/child::*'], fromKwarg='lxmlNode', namespaces=NAMESPACEMAP),
                                    (RewritePartname("metadata"), # Hernoemt partname van 'record' naar "metadata".
                                        (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=False),
                                            (storageComponent,) # Schrijft oai:metadata (=origineel) naar storage.
                                        )
                                    )
                                    # (OaiAddDeleteRecordWithPrefixesAndSetSpecs(metadataPrefixes=["oai_dc"], setSpecs=['publications'], name='NARCISPORTAL'),
                                    #     (oaiJazz,),
                                    # )
                                ),
                                (XmlXPath(['/oai:record/oai:metadata/norm:normalized/long:long'], fromKwarg='lxmlNode', namespaces=NAMESPACEMAP),
                                    (RewritePartname("long"), # Hernoemt partname van 'record' naar "long".
                                        (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=True),
                                            (storageComponent,), # Schrijft 'long' (=norm:normdoc) naar storage.
                                        ),
                                        (ShortConverter(fromKwarg='lxmlNode'),
                                            (RewritePartname("short"),
                                                (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=True),
                                                    (storageComponent,) # Schrijft 'short' naar storage.
                                                )
                                            )
                                        ),
                                        # Hernoem partname van 'record' naar "oai_dc".
                                        (DcConverter(fromKwarg='lxmlNode'),
                                            (RewritePartname("oai_dc"),
                                                (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=True),
                                                    (storageComponent,) # Schrijft 'oai_dc' naar storage.
                                                ),
                                                (OaiAddDeleteRecordWithPrefixesAndSetSpecs(metadataPrefixes=["oai_dc", "long"], setSpecs=['publication'], name='NARCISPORTAL'),
                                                    (oaiJazz,), # Stop alles wat geconverteerd is naar DC ook in OAI-PMH repo.
                                                )
                                            )
                                        )
                                    )
                                ),
                                # TODO: Check indien conversies misgaan, dat ook de meta en header part niet naar storage gaan: geen 1 part als het even kan...
                                # Schrijf headerPart naar storage:
                                (XmlXPath(['/oai:record/oai:header'], fromKwarg='lxmlNode', namespaces=NAMESPACEMAP),
                                    (RewritePartname("header"),
                                        (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=False),
                                            (storageComponent,) # Schrijft OAI-header naar storage.
                                        )
                                    )
                                )
                            )
                        ), # Schrijf metaPart naar storage:
                        (XmlXPath(['/oai:record/oai:metadata/document:document/document:part[@name="meta"]/text()'], fromKwarg='lxmlNode', toKwarg='data', namespaces=NAMESPACEMAP),
                            (RewritePartname("meta"),
                                (storageComponent,) # Schrijft harvester 'meta' data naar storage.
                            )
                        )
                    ),
                    (FilterMessages(allowed=['add']),
                        # (LogComponent("UnDelete"),),
                        (ResurrectTombstone(),
                            (storageComponent,),
                        )
                    )
                )
            )
        )
    )

def main(reactor, port, statePath, indexPort, gatewayPort, **ignored):
    apacheLogStream = sys.stdout


    # xsltPath = join(join(dirname(dirname(dirname(abspath(__file__)))), 'xslt'), 'MODS3-5_DC_XSLT1-0.xsl')
    # print "xsltPath:", xsltPath


    periodicGateWayDownload = PeriodicDownload(
        reactor,
        host='localhost',
        port=gatewayPort,
        name='gateway')

    oaiDownload = OaiDownloadProcessor(
        path='/oaix',
        metadataPrefix=NORMALISED_DOC_NAME,
        workingDirectory=join(statePath, 'harvesterstate', 'gateway'),
        xWait=True,
        name='gateway',
        autoCommit=False)

    # def sortFieldRename(name):
    #     if not name.startswith('__'):
    #         name = SORTED_PREFIX + name
    #     return name

    fieldnameRewrites = {
        UNTOKENIZED_PREFIX+'genre': UNTOKENIZED_PREFIX+'dc:genre',
    }

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

    luceneRemote = LuceneRemote(host='localhost', port=indexPort, path='/lucene')

    strategie = Md5HashDistributeStrategy()
    storage = StorageComponent(join(statePath, 'store'), strategy=strategie, partsRemovedOnDelete=[DEFAULT_PARTNAME, NORMALISED_DOC_NAME])

    oaiJazz = OaiJazz(join(statePath, 'oai'))
    oaiJazz.updateMetadataFormat(DEFAULT_PARTNAME, None, None)
    # def updateMetadataFormat(self, prefix, schema, namespace):
    # self._prefixes[prefix] = (schema, namespace)

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

    # # Post commit naar storage en ??
    # scheduledCommitPeriodicCall = be(
    #     (PeriodicCall(reactor, message='commit', name='Scheduled commit', initialSchedule=Schedule(period=1), schedule=Schedule(period=1)),
    #         (AllToDo(),
    #             (LogComponent("PeriodicCall"),), # commit(*(), **{})
    #             (storage,),
    #             (periodicGateWayDownload,),
    #         )
    #     )
    # )

    directoryLog = DirectoryLog(join(statePath, 'log'), extension='-query.log')

    executeQueryHelix = \
        (FilterMessages(allowed=['executeQuery']),
            (CqlMultiSearchClauseConversion(cqlClauseConverters, fromKwarg='query'),
                (DrilldownQueries(),
                    (convertToComposedQuery,
                        (luceneRemote,),
                    )
                )
            )
        )

    return \
    (Observable(),
        # (scheduledCommitPeriodicCall,),
        # (DebugPrompt(reactor=reactor, port=port+1, globals=locals()),),
        createDownloadHelix(reactor, periodicGateWayDownload, oaiDownload, storage, oaiJazz),
        (ObservableHttpServer(reactor, port, compressResponse=True),
            (LogCollector(),
                (ApacheLogWriter(apacheLogStream),),
                (QueryLogWriter.forHttpArguments(
                        log=directoryLog,
                        scopeNames=('http-scope',)
                    ),
                ),
                (QueryLogWriter(log=directoryLog, scopeNames=('sru-scope',)),),
                (Deproxy(),
                    (HandleRequestLog(),
                        (BasicHttpHandler(),
                            (PathFilter(["/oai"]),
                                (LogCollectorScope("http-scope"),
                                    (OaiPmh(repositoryName="NARCIS OAI-pmh", adminEmail="narcis@dans.knaw.nl"),
                                        (oaiJazz,),
                                        (StorageAdapter(),
                                            (storage,)
                                        ),
                                        (OaiBranding(
                                            url="http://www.narcis.nl/images/logos/logo-knaw-house.gif", 
                                            link="http://oai.narcis.nl", 
                                            title="Narcis - The gateway to scholarly information in The Netherlands"),
                                        ),
                                        (OaiProvenance(
                                            nsMap=NAMESPACEMAP,
                                            baseURL=('meta', '//meta:repository/meta:baseurl/text()'), 
                                            harvestDate=('meta', '//meta:record/meta:harvestDate/text()'),
                                            metadataNamespace=('meta', '//meta:record/meta:metadataNamespace/text()'),
                                            identifier=('header','//oai:identifier/text()'),
                                            datestamp=('header', '//oai:datestamp/text()')
                                            ),
                                            (storage,)
                                        )
                                    )
                                )
                            ),
                            (PathFilter(['/sru']),
                                (LogCollectorScope('sru-scope'),
                                    (SruParser(
                                            host='example.org',
                                            port=80,
                                            defaultRecordSchema='oai_dc',
                                            defaultRecordPacking='xml'),
                                        (SruLimitStartRecord(limitBeyond=4000),
                                            (SruHandler(
                                                    includeQueryTimes=False,
                                                    extraXParameters=[],
                                                    enableCollectLog=True),
                                                (SruTermDrilldown(),),
                                                executeQueryHelix,
                                                (StorageAdapter(),
                                                    (storage,)
                                                )
                                            )
                                        )
                                    )
                                )
                            ),
                            (PathFilter('/rss'),
                                (Rss(   title = 'Meresco',
                                        description = 'RSS feed for Meresco',
                                        link = 'http://meresco.org',
                                        maximumRecords = 20),
                                    executeQueryHelix,
                                    (RssItem(
                                            nsMap={
                                                'dc': "http://purl.org/dc/elements/1.1/",
                                                'oai_dc': "http://www.openarchives.org/OAI/2.0/oai_dc/",
                                                'norm' : "http://dans.knaw.nl/narcis/normalized",
                                                'long'  : 'http://www.knaw.nl/narcis/1.0/long/',
                                            },
                                            title = ("oai_dc", '/oai_dc:dc/dc:title/text()'),
                                            description = ("oai_dc", '/oai_dc:dc/dc:description/text()'),
                                            linkTemplate = 'http://localhost/sru?operation=searchRetrieve&version=1.2&query=dc:identifier%%3D%(identifier)s',
                                            identifier = ("long", '/long:long/long:humanStartPage/text()')),
                                        (StorageAdapter(),
                                            (storage,)
                                        )
                                    )
                                )
                            ),
                            (PathFilter('/log'),
                                (LogFileServer(name="Example Queries", log=directoryLog, basepath='/log'),)
                            )
                        )
                    )
                )
            )
        )
    )

def startServer(port, stateDir, **kwargs):
    setSignalHandlers()
    print 'Firing up API Server.'
    reactor = Reactor()
    statePath = abspath(stateDir)

    #main
    dna = main(
        reactor=reactor,
        port=port,
        statePath=statePath,
        **kwargs
    )
    #/main

    server = be(dna)
    consume(server.once.observer_init())

    registerShutdownHandler(statePath=statePath, server=server, reactor=reactor, shutdownMustSucceed=False)

    print "Ready to rumble at %s" % port
    sys.stdout.flush()
    reactor.loop()
