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
# from os.path import dirname, abspath, join, isdir

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

from meresco.oai import OaiPmh, OaiDownloadProcessor, UpdateAdapterFromOaiDownloadProcessor, OaiJazz, OaiAddDeleteRecordWithPrefixesAndSetSpecs, OaiBranding, OaiProvenance

from meresco.lucene import SORTED_PREFIX, UNTOKENIZED_PREFIX
from meresco.lucene.remote import LuceneRemote
from meresco.lucene.converttocomposedquery import ConvertToComposedQuery

####### start lucene integration #############
from meresco.lucene import Lucene, MultiLucene, UNTOKENIZED_PREFIX, SORTED_PREFIX
from meresco.lucene.adaptertolucenequery import AdapterToLuceneQuery
from meresco.lucene.fieldregistry import FieldRegistry
from meresco.lucene import LuceneSettings, DrilldownField
from weightless.http import HttpRequest1_1, SocketPool
from meresco.lucene.queryexpressiontolucenequerydict import QueryExpressionToLuceneQueryDict
####### end lucene integration #############

from seecr.utils import DebugPrompt
from meresco.components.drilldownqueries import DrilldownQueries
from storage import StorageComponent

from meresco.dans.merescocomponents import Rss, RssItem, OaiOpenAIREDescription
from meresco.dans.storagesplit import Md5HashDistributeStrategy
from meresco.dans.writedeleted import ResurrectTombstone, WriteTombstone
from meresco.dans.shortconverter import ShortConverter
from meresco.dans.oai_dcconverter import DcConverter
from meresco.dans.filterwcpcollection import FilterWcpCollection

from meresco.dans.merescocomponents import OaiPmh as OaiPmhDans

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
OPENAIRE_PARTNAME = 'oai_cerif_openaire'

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



def createDownloadHelix(reactor, periodicDownload, oaiDownload, storageComponent, oaiJazz, oai_oa_cerifJazz):
    return \
    (periodicDownload, # Scheduled connection to a remote (response / request)...
        (XmlParseLxml(fromKwarg="data", toKwarg="lxmlNode", parseOptions=dict(huge_tree=True, remove_blank_text=True)), # Convert from plain text to lxml-object.
            (oaiDownload, # Implementation/Protocol of a PeriodicDownload...
                (UpdateAdapterFromOaiDownloadProcessor(), # Maakt van een SRU update/delete bericht (lxmlNode) een relevante message: 'delete' of 'add' message.
                    (FilterMessages(['delete']), # Filtert delete messages
                        # (LogComponent("Delete Update"),),
                        (storageComponent,), # Delete from storage
                        (oaiJazz,), # Delete from OAI-pmh repo
                        (oai_oa_cerifJazz,),
                        # Write a 'deleted' part to the storage, that holds the (Record)uploadId.
                        (WriteTombstone(),
                            (storageComponent,),
                        )
                    ),
                    (FilterMessages(allowed=['add']),
                        (XmlXPath(['/oai:record/oai:metadata/document:document/document:part[@name="record"]/text()'], fromKwarg='lxmlNode', toKwarg='data', namespaces=NAMESPACEMAP),
                            (XmlParseLxml(fromKwarg='data', toKwarg='lxmlNode'),

                                (FilterWcpCollection(allowed=['research']),
                                    (XmlXPath(['/oai:record/oai:metadata/norm:md_original/child::*'], fromKwarg='lxmlNode', namespaces=NAMESPACEMAP), # Origineel 'metadata' formaat
                                        (XsltCrosswalk([join(dirname(abspath(__file__)), '..', '..', 'xslt', 'cerif-project.xsl')], fromKwarg="lxmlNode"),
                                            (RewritePartname(OPENAIRE_PARTNAME),
                                                (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=False),
                                                    (storageComponent,)
                                                )
                                            )
                                        )
                                    )
                                ),

                                (FilterWcpCollection(allowed=['person']),
                                    (XmlXPath(['/oai:record/oai:metadata/norm:md_original/child::*'], fromKwarg='lxmlNode', namespaces=NAMESPACEMAP), # Origineel 'metadata' formaat
                                        (XsltCrosswalk([join(dirname(abspath(__file__)), '..', '..', 'xslt', 'cerif-person.xsl')], fromKwarg="lxmlNode"),
                                            (RewritePartname(OPENAIRE_PARTNAME),
                                                (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=False),
                                                    (storageComponent,)
                                                )
                                            )
                                        )
                                    )
                                ),

                                (FilterWcpCollection(allowed=['organisation']),
                                    (XmlXPath(['/oai:record/oai:metadata/norm:md_original/child::*'], fromKwarg='lxmlNode', namespaces=NAMESPACEMAP), # Origineel 'metadata' formaat
                                        (XsltCrosswalk([join(dirname(abspath(__file__)), '..', '..', 'xslt', 'cerif-orgunit.xsl')], fromKwarg="lxmlNode"),
                                            (RewritePartname(OPENAIRE_PARTNAME),
                                                (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=False),
                                                    (storageComponent,)
                                                )
                                            )
                                        )
                                    )
                                ),


                                (XmlXPath(['/oai:record/oai:metadata/norm:md_original/child::*'], fromKwarg='lxmlNode', namespaces=NAMESPACEMAP), # Origineel 'metadata' formaat
                                    (RewritePartname("metadata"), # Hernoemt partname van 'record' naar "metadata".
                                        (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=False),
                                            (storageComponent,) # Schrijft oai:metadata (=origineel) naar storage.
                                        )
                                    )
                                ),
                                (XmlXPath(['/oai:record/oai:metadata/norm:normalized/long:knaw_long'], fromKwarg='lxmlNode', namespaces=NAMESPACEMAP), # Genormaliseerd 'long' formaat.
                                    (RewritePartname("knaw_long"), # Hernoemt partname van 'record' naar "knaw_long".
                                        (FilterWcpCollection(disallowed=['person', 'research', 'organisation']),
                                            (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=True),
                                                (storageComponent,), # Schrijft 'long' (=norm:normdoc) naar storage.
                                            )
                                        ),
                                        (ShortConverter(fromKwarg='lxmlNode'), # creeer 'knaw_short' subset formaat.
                                            (RewritePartname("knaw_short"),
                                                (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=True),
                                                    (storageComponent,) # Schrijft 'short' naar storage.
                                                )
                                            )
                                        ),
                                        (FilterWcpCollection(disallowed=['person', 'research', 'organisation']),
                                            (DcConverter(fromKwarg='lxmlNode'), # Hernoem partname van 'record' naar "oai_dc".
                                                (RewritePartname("oai_dc"),
                                                    (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=True),
                                                        (storageComponent,) # Schrijft 'oai_dc' naar storage.
                                                    )
                                                )
                                            )
                                        )
                                    )
                                ),
                                # TODO: Check indien conversies misgaan, dat ook de meta en header part niet naar storage gaan: geen 1 part als het even kan...
                                # Schrijf 'header' partname naar storage:
                                (XmlXPath(['/oai:record/oai:header'], fromKwarg='lxmlNode', namespaces=NAMESPACEMAP),
                                    (RewritePartname("header"),
                                        (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=False),
                                            (storageComponent,) # Schrijft OAI-header naar storage.
                                        )
                                    )
                                ),
                                (FilterWcpCollection(allowed=['publication']),
                                    # (LogComponent("PUBLICATION"),),
                                    (OaiAddDeleteRecordWithPrefixesAndSetSpecs(metadataPrefixes=["oai_dc"], setSpecs=['publication'], name='NARCISPORTAL'), #TODO: Skip name='NARCISPORTAL'
                                        (oaiJazz,),
                                    ),
                                    (XmlXPath(["//long:knaw_long[long:accessRights ='openAccess']"], fromKwarg='lxmlNode', namespaceMap=NAMESPACEMAP),
                                        (OaiAddDeleteRecordWithPrefixesAndSetSpecs(metadataPrefixes=["oai_dc"], setSpecs=['oa_publication', 'openaire'], name='NARCISPORTAL'),
                                            (oaiJazz,),
                                        )
                                    ),
                                    (XmlXPath(["//long:knaw_long/long:metadata[long:genre ='doctoralthesis']"], fromKwarg='lxmlNode', namespaceMap=NAMESPACEMAP),
                                        (OaiAddDeleteRecordWithPrefixesAndSetSpecs(metadataPrefixes=["oai_dc"], setSpecs=['thesis'], name='NARCISPORTAL'),
                                            (oaiJazz,),
                                        )
                                    ),
                                    (XmlXPath(['//long:knaw_long/long:metadata/long:grantAgreements/long:grantAgreement[long:code[contains(.,"greement/EC/") or contains(.,"greement/ec/")]][1]'], fromKwarg='lxmlNode', namespaceMap=NAMESPACEMAP),
                                        (OaiAddDeleteRecordWithPrefixesAndSetSpecs(metadataPrefixes=["oai_dc"], setSpecs=['ec_fundedresources', 'openaire'], name='NARCISPORTAL'),
                                            (oaiJazz,),
                                        )
                                    )
                                ),
                                (FilterWcpCollection(allowed=['dataset']),
                                    (OaiAddDeleteRecordWithPrefixesAndSetSpecs(metadataPrefixes=["oai_dc"], setSpecs=['dataset'], name='NARCISPORTAL'),
                                        (oaiJazz,),
                                    )
                                ),

                                # Add NOD OpenAIRE Cerif to OpenAIRE-PMH repo.
                                (FilterWcpCollection(allowed=['research']),
                                    # (LogComponent("RESEARCH ADD:"),),
                                    (OaiAddDeleteRecordWithPrefixesAndSetSpecs(metadataPrefixes=[OPENAIRE_PARTNAME], setSpecs=['openaire_cris_projects'], name=['OpenAIRE_CRIS_projects']),
                                        # (LogComponent("RESEARCH ADD:"),),
                                        (oai_oa_cerifJazz,),
                                    )
                                ),
                                (FilterWcpCollection(allowed=['person']),
                                    (OaiAddDeleteRecordWithPrefixesAndSetSpecs(metadataPrefixes=[OPENAIRE_PARTNAME], setSpecs=['openaire_cris_persons'], name=['OpenAIRE_CRIS_persons']),
                                        (oai_oa_cerifJazz,),
                                    )
                                ),
                                (FilterWcpCollection(allowed=['organisation']),
                                    (OaiAddDeleteRecordWithPrefixesAndSetSpecs(metadataPrefixes=[OPENAIRE_PARTNAME], setSpecs=['openaire_cris_orgunits'], name=['OpenAIRE_CRIS_orgunits']),
                                        (oai_oa_cerifJazz,),
                                    )
                                )

                            )
                        ), # Schrijf 'meta' partname naar storage:
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


def main(reactor, port, statePath, lucenePort, gatewayPort, quickCommit=False, **ignored):

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
            (MultiLucene(host='localhost', port=lucenePort, defaultCore=DEFAULT_CORE),
                (luceneIndex,),
                (http11Request,),
            )
        )
    )

######## END Lucene Integration ###############################################################

    fieldnameRewrites = {
#         UNTOKENIZED_PREFIX+'genre': UNTOKENIZED_PREFIX+'dc:genre',
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


    strategie = Md5HashDistributeStrategy()
    storage = StorageComponent(join(statePath, 'store'), strategy=strategie, partsRemovedOnDelete=[HEADER_PARTNAME, META_PARTNAME, METADATA_PARTNAME, OAI_DC_PARTNAME, LONG_PARTNAME, SHORT_PARTNAME, OPENAIRE_PARTNAME])

    oaiJazz = OaiJazz(join(statePath, 'oai'))
    oaiJazz.updateMetadataFormat(OAI_DC_PARTNAME, "http://www.openarchives.org/OAI/2.0/oai_dc.xsd", "http://purl.org/dc/elements/1.1/") # def updateMetadataFormat(self, prefix, schema, namespace):

    oai_oa_cerifJazz = OaiJazz(join(statePath, 'oai_cerif'))
    oai_oa_cerifJazz.updateMetadataFormat(OPENAIRE_PARTNAME, " https://github.com/openaire/guidelines-cris-managers/raw/v1.1/schemas/openaire-cerif-profile.xsd", "https://www.openaire.eu/cerif-profile/1.1/")


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

    periodicGateWayDownload = PeriodicDownload(
        reactor,
        host='localhost',
        port=gatewayPort,
        schedule=Schedule(period=1 if quickCommit else 10), # WST: Interval in seconds before sending a new request to the GATEWAY in case of an error while processing batch records.(default=1). IntegrationTests need 1 second! Otherwise tests will fail!
        name='api',
        autoStart=True)

    oaiDownload = OaiDownloadProcessor(
        path='/oaix',
        metadataPrefix=NORMALISED_DOC_NAME,
        workingDirectory=join(statePath, 'harvesterstate', 'gateway'),
        userAgentAddition='ApiServer',
        xWait=True,
        name='api',
        autoCommit=False)

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
        createDownloadHelix(reactor, periodicGateWayDownload, oaiDownload, storage, oaiJazz, oai_oa_cerifJazz),
        (ObservableHttpServer(reactor, port, compressResponse=True),
            (BasicHttpHandler(),
                (PathFilter(["/oai"]),
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
                            harvestDate=('meta', '//meta:record/meta:harvestdate/text()'),
                            metadataNamespace=('meta', '//meta:record/meta:metadataNamespace/text()'),
                            identifier=('header','//oai:identifier/text()'),
                            datestamp=('header', '//oai:datestamp/text()')
                            ),
                            (storage,)
                        )
                    )
                ),
                (PathFilter(["/cerif_oa"]),
                    (OaiPmhDans(repositoryName="OpenAIRE CERIF", adminEmail="narcis@dans.knaw.nl", repositoryIdentifier="narcis.nl"),
                        (oai_oa_cerifJazz,),
                        (StorageAdapter(),
                            (storage,)
                        ),
                        (OaiOpenAIREDescription(
                            serviceid='',
                            acronym='OpenAIRE',
                            name='',
                            description='Beschrijving...',
                            website='',
                            baseurl='',
                            subjectheading='',
                            orgunitid='',
                            owneracronym='NARCIS'),
                        ),
                        # (OaiBranding(
                        #     url="http://www.narcis.nl/images/logos/logo-knaw-house.gif",
                        #     link="http://oai.narcis.nl",
                        #     title="Narcis - The gateway to scholarly information in The Netherlands"),
                        # ),
                        (OaiProvenance(
                            nsMap=NAMESPACEMAP,
                            baseURL=('meta', '//meta:repository/meta:baseurl/text()'),
                            harvestDate=('meta', '//meta:record/meta:harvestdate/text()'),
                            metadataNamespace=('meta', '//meta:record/meta:metadataNamespace/text()'),
                            identifier=('header','//oai:identifier/text()'),
                            datestamp=('header', '//oai:datestamp/text()')
                            ),
                            (storage,)
                        )
                    )
                ),
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
                                    enableCollectLog=False),
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

def startServer(port, stateDir, lucenePort, gatewayPort, quickCommit=False, **kwargs):
    setSignalHandlers()
    print 'Firing up API Server.'
    reactor = Reactor()
    statePath = abspath(stateDir)

    dna = main(
        reactor=reactor,
        port=port,
        statePath=statePath,
        lucenePort=lucenePort,
        gatewayPort=gatewayPort,
        quickCommit=quickCommit,
        **kwargs
    )

    server = be(dna)
    consume(server.once.observer_init())

    registerShutdownHandler(statePath=statePath, server=server, reactor=reactor, shutdownMustSucceed=False)

    print "Ready to rumble at %s" % port
    sys.stdout.flush()
    reactor.loop()
