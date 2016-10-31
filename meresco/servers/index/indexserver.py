# -*- coding: utf-8 -*-
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

from os.path import dirname, abspath, join
from sys import stdout

from weightless.core import be, consume
from weightless.http import HttpRequest1_1, SocketPool
from weightless.io import Reactor

from meresco.core import Observable
from meresco.core.alltodo import AllToDo
from meresco.core.processtools import setSignalHandlers, registerShutdownHandler

from meresco.components.http import BasicHttpHandler, ObservableHttpServer, PathFilter
from meresco.components import PeriodicDownload, FilterMessages, XmlXPath, XmlParseLxml, PeriodicCall, Schedule
from meresco.components.log import LogCollector, ApacheLogWriter, HandleRequestLog, LogComponent

from meresco.lucene.lucenecommit import LuceneCommit
from meresco.lucene.queryexpressiontolucenequerydict import QueryExpressionToLuceneQueryDict

from meresco.oai import OaiDownloadProcessor, UpdateAdapterFromOaiDownloadProcessor

from seecr.utils import DebugPrompt
from threading import Thread
from meresco.lucene import LuceneSettings, DrilldownField#, FieldsListToLuceneDocument

from meresco.dans.fieldslisttolucenedocument import FieldsListToLuceneDocument

from meresco.pylucene import getJVM

from meresco.xml import namespaces

from meresco.lucene import Lucene, MultiLucene, UNTOKENIZED_PREFIX, SORTED_PREFIX
from meresco.lucene.adaptertolucenequery import AdapterToLuceneQuery
from meresco.lucene.remote import LuceneRemoteService
from meresco.lucene.fieldregistry import FieldRegistry

from .dctofieldslist import DcToFieldsList
from .dcfields import DcFields
from .metaparttofieldslist import MetaToFieldsList
from .normdoctofieldslist import NormdocToFieldsList

from meresco.servers.gateway.gatewayserver import NORMALISED_DOC_NAME

DEFAULT_PARTNAME = 'oai_dc'


NAMESPACEMAP = namespaces.copyUpdate({ #  See: https://github.com/seecr/meresco-xml/blob/master/meresco/xml/namespaces.py
    
    'dip'    : 'urn:mpeg:mpeg21:2005:01-DIP-NS',
    'dii'    : 'urn:mpeg:mpeg21:2002:01-DII-NS',
    'dai'    : 'info:eu-repo/dai',
    'gal'    : 'info:eu-repo/grantAgreement',
    'wmp'    : 'http://www.surfgroepen.nl/werkgroepmetadataplus',
    'prs'    : 'http://www.onderzoekinformatie.nl/nod/prs',
    'proj'   : 'http://www.onderzoekinformatie.nl/nod/act',
    'org'    : 'http://www.onderzoekinformatie.nl/nod/org',
    'long'   : 'http://www.knaw.nl/narcis/1.0/long/',
    'short'  : 'http://www.knaw.nl/narcis/1.0/short/',
    'mods'   : 'http://www.loc.gov/mods/v3',
    'didl'   : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
    'norm'   : 'http://dans.knaw.nl/narcis/normalized',
})



LUCENE_VM = getJVM()

def untokenizedFieldname(fieldname):
    return UNTOKENIZED_PREFIX + fieldname

UNQUALIFIED_TERM_FIELDS = [('__all__', 1.0)]

drilldownFields = [
    # def __init__(self, name, hierarchical=False, multiValued=True, indexFieldName=None):
    DrilldownField(untokenizedFieldname('meta:repositorygroupid')), # Was:
    DrilldownField(untokenizedFieldname('meta:collection')), # was:
    DrilldownField(untokenizedFieldname('pubtype')), # Dit WAS 'genre': Echter lijkt dit een 'reserved' keyword: Zowel veldnaam als waarden verdijnen automagic: Nergens meer te vinden...
    DrilldownField(untokenizedFieldname('access')),
    DrilldownField(untokenizedFieldname('dd_year')),
    DrilldownField(untokenizedFieldname('status')),
    DrilldownField(untokenizedFieldname('dd_prices')),
    DrilldownField(untokenizedFieldname('dd_werkzaamheid')),
    DrilldownField(untokenizedFieldname('dd_position')),
    DrilldownField(untokenizedFieldname('dd_institute')),
    DrilldownField(untokenizedFieldname('dd_cat')),
    DrilldownField(untokenizedFieldname('dd_thesis')),
    DrilldownField(untokenizedFieldname('dd_penv')),
    DrilldownField(untokenizedFieldname('dd_os')),
    DrilldownField(untokenizedFieldname('dd_cre')),
    DrilldownField(untokenizedFieldname('dd_fin')),
    # DrilldownField(untokenizedFieldname('blaat'), hierarchical=False),   
]

# Add any non-drilldown untokenized fields:
untokenizedFieldnames = [f.name for f in drilldownFields] + [
    untokenizedFieldname('oai:id'), # Was: 
    untokenizedFieldname('meta:repositoryid'), # Was:
    untokenizedFieldname('fundingid'), # Was funding_id
    untokenizedFieldname('dare:id'), #Was: dare_identifier
    untokenizedFieldname('publicationid'), # Was: publication_identifier
    untokenizedFieldname('mutatiedatum'),
    untokenizedFieldname('dateissued'),
    untokenizedFieldname('nids'),
    untokenizedFieldname('nids_aut'),
    untokenizedFieldname('nids_non_aut'),
    untokenizedFieldname('persistentid'),
    untokenizedFieldname('sort_title_en'),
    untokenizedFieldname('sort_title'),
    untokenizedFieldname('pidref'),
    untokenizedFieldname('humanstartpage'),
]

DEFAULT_CORE = 'narcis'

def luceneAndReaderConfig(defaultLuceneSettings, httpRequestAdapter, luceneserverPort):

    fieldRegistry = FieldRegistry(drilldownFields=drilldownFields)
    luceneIndex = be((Lucene(
            host='127.0.0.1',
            port=luceneserverPort,
            name=DEFAULT_CORE,
            settings=defaultLuceneSettings.clone(fieldRegistry=fieldRegistry)
        ),
        (httpRequestAdapter,)
    ))
    return luceneIndex

def readerMain(readerReactor, statePath, port, defaultLuceneSettings, luceneserverPort):
    apacheLogStream = stdout

    http11Request = be(
        (HttpRequest1_1(),
            (SocketPool(reactor=readerReactor, unusedTimeout=5, limits=dict(totalSize=100, destinationSize=10)),),
        )
    )
    luceneIndex = luceneAndReaderConfig(defaultLuceneSettings.clone(readonly=True), http11Request, luceneserverPort)

    return \
    (Observable(),
        # (DebugPrompt(reactor=readerReactor, port=port+1, globals=locals()),),
        (ObservableHttpServer(reactor=readerReactor, port=port),
            (LogCollector(),
                (ApacheLogWriter(apacheLogStream),),
                (HandleRequestLog(),
                    (BasicHttpHandler(),
                        (PathFilter('/lucene'),
                            (LuceneRemoteService(reactor=readerReactor),
                                (AdapterToLuceneQuery(
                                        defaultCore=DEFAULT_CORE,
                                        coreConverters={
                                            DEFAULT_CORE: QueryExpressionToLuceneQueryDict(UNQUALIFIED_TERM_FIELDS, luceneSettings=luceneIndex.settings),
                                        }
                                    ),
                                    (MultiLucene(host='localhost', port=luceneserverPort, defaultCore=DEFAULT_CORE),
                                        (luceneIndex,),
                                        (http11Request,),
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def writerMain(writerReactor, readerReactor, readerPort, statePath, luceneserverPort, gatewayPort):
    #apacheLogStream = stdout

    http11Request = be(
        (HttpRequest1_1(),
            (SocketPool(reactor=writerReactor, unusedTimeout=5, limits=dict(totalSize=100, destinationSize=10)),),
        )
    )
    indexCommitTimeout = 30

    defaultLuceneSettings = LuceneSettings(
            commitTimeout=indexCommitTimeout,
            readonly=False,
        )

    luceneWriter = luceneAndReaderConfig(defaultLuceneSettings, http11Request, luceneserverPort)

    periodicDownload = PeriodicDownload(
        writerReactor,
        host='localhost',
        port=gatewayPort,
        name='gateway',
        autoStart=True)

    oaiDownload = OaiDownloadProcessor(
        path='/oaix',
        metadataPrefix=NORMALISED_DOC_NAME,
        workingDirectory=join(statePath, 'harvesterstate', 'gateway'),
        xWait=True,
        name='gateway',
        autoCommit=False)

    # Post commit naar Lucene(server):
    scheduledCommitPeriodicCall = be(
        (PeriodicCall(writerReactor, message='commit', name='Scheduled commit', schedule=Schedule(period=1), initialSchedule=Schedule(period=1)),
            (AllToDo(),
                (periodicDownload,),
                (LuceneCommit(host='localhost', port=luceneserverPort,),
                    # (LogComponent("PERIODIC"),), # [PERIOD] httprequest1_1(*(), **{'body': None, 'host': 'localhost', 'request': '/commit/', 'port': 47896, 'method': 'POST'})
                    (http11Request,),
                    # ),
                )
            )
        )
    )

    readerServer = readerMain(
            readerReactor=readerReactor,
            statePath=statePath,
            port=readerPort,
            defaultLuceneSettings=defaultLuceneSettings,
            luceneserverPort=luceneserverPort,
        )

    writerServer = \
    (Observable(),
        (scheduledCommitPeriodicCall,), # Commit de spullen naar LuceneServer...
        # (DebugPrompt(reactor=writerReactor, port=readerPort-1, globals=locals()),),
        (periodicDownload, # Connect met de Gateway...
            (XmlParseLxml(fromKwarg="data", toKwarg="lxmlNode", parseOptions=dict(huge_tree=True, remove_blank_text=True)),
                (oaiDownload, # Haal OAI spulletjes van de Gateway...
                    (UpdateAdapterFromOaiDownloadProcessor(), # Maakt van een SRU update/delete bericht (lxmlNode) een relevante message: 'delete' of 'add' message.
                        # (LogComponent("SRU harvest van GATEWAY"),), #[SRU harvest van GATEWAY] add(*(), **{'partname': 'record', 'identifier': 'meresco:record:1', 'lxmlNode': '_ElementTree(<record xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><header><identifier>meresco:record:1</identifier><datestamp>2016-07-13T15:31:10Z</datestamp></header><metadata><document xmlns="http://meres
                        (FilterMessages(allowed=['add']),
                            # (LogComponent("ADD from GATEWAY"),),
                            # (XmlXPath(['/oai:record/oai:metadata/document:document/document:part[@name="record"]/text()'], fromKwarg='lxmlNode', toKwarg='data'),
                            #     (XmlParseLxml(fromKwarg='data', toKwarg='lxmlNode'),
                            #         (XmlXPath(['/oai:record/oai:metadata/norm:md_original/oai_dc:dc'], fromKwarg='lxmlNode', namespaces=NAMESPACEMAP),
                            #             # (LogComponent("DCToFieldsList"),),
                            #             (DcToFieldsList(), # Platte lijst met veldnamen en waardes...
                            #                 # (LogComponent("DcToFieldsList"),), # [DcToFieldsList] add(*(), **{'fieldslist': [('dc:identifier', 'http://meresco.com?record=1'), ('dc:description', 'This is an example program about Search with Meresco'), ('dc:title', 'Example Program 1'), ('dc:creator', 'Seecr'), ('dc:publisher', 'Seecr'), ('dc:date', '2016'), ('dc:type', 'Example'), ('dc:subject', 'Search'), ('dc:language', 'en'), ('dc:rights', 'Open Source')], 'partname': 'record', 'identifier': 'meresco:record:1'})
                            #                 (FieldsListToLuceneDocument( # Maakt addDocument message + creeert de facet/drilldown velden waarvan de value's tot max. 256 chars getruncated worden.
                            #                         fieldRegistry=luceneWriter.settings.fieldRegistry, # o.a. drilldownfields definitie
                            #                         untokenizedFieldnames=untokenizedFieldnames, # untokenized fields
                            #                         indexFieldFactory=DcFields, # Creeert een "__all__", veldnaam en optioneel "untokenized.veldnaam"... 
                            #                         #rewriteIdentifier=(lambda idee: idee.split(':', 1)[-1]) # meresco:record:1' => 'record:1'
                            #                     ), # LET OP: Een reeds bestaand Document voor deze identifier/uploadId zal overschreven worden in Lucene (=delete) !!!
                            #                 # Dus GAAT ERVAN UIT DAT ALLES IN 1 KEER WEGGESCHREVEN WORDT.

                            #                     # (LogComponent("DC_WRITER"),), # [LUCENE_WRITER] addDocument(*(), **{'fields': [{'type': 'TextField', 'name': '__all__', 'value': 'http://meresco.com?record=1'}, {'type': 'TextField', 'name': 'dc:identifier', 'value': 'http://meresco.com?record=1'}, {'type': 'StringField', 'name': 'untokenized.dc:identifier', 'value': 'http://meresco.com?record=1'}, {'type': 'TextField', 'name': '__all__', 'value': 'This is an example program about Search with Meresco'}, {'type': 'TextField', 'name': 'dc:description', 'value': 'This is an example program about Search with Meresco'}, {'type': 'TextField', 'name': '__all__', 'value': 'Example Program 1'}, {'type': 'TextField', 'name': 'dc:title', 'value': 'Example Program 1'}, {'type': 'TextField', 'name': '__all__', 'value': 'Seecr'}, {'type': 'TextField', 'name': 'dc:creator', 'value': 'Seecr'}, {'type': 'TextField', 'name': '__all__', 'value': 'Seecr'}, {'type': 'TextField', 'name': 'dc:publisher', 'value': 'Seecr'}, {'type': 'TextField', 'name': '__all__', 'value': '2016'}, {'type': 'TextField', 'name': 'dc:date', 'value': '2016'}, {'path': ['2016'], 'type': 'FacetField', 'name': 'untokenized.dc:date'}, {'type': 'TextField', 'name': '__all__', 'value': 'Example'}, {'type': 'TextField', 'name': 'dc:type', 'value': 'Example'}, {'type': 'TextField', 'name': '__all__', 'value': 'Search'}, {'type': 'TextField', 'name': 'dc:subject', 'value': 'Search'}, {'path': ['Search'], 'type': 'FacetField', 'name': 'untokenized.dc:subject'}, {'type': 'TextField', 'name': '__all__', 'value': 'en'}, {'type': 'TextField', 'name': 'dc:language', 'value': 'en'}, {'type': 'TextField', 'name': '__all__', 'value': 'Open Source'}, {'type': 'TextField', 'name': 'dc:rights', 'value': 'Open Source'}], 'identifier': 'meresco:record:1'})
                            #                     (luceneWriter,),
                            #                     # ),
                            #                 )
                            #             )
                            #         ),
                            #     )
                            # ),
                            
                            (XmlXPath(['/oai:record/oai:metadata/document:document'], fromKwarg='lxmlNode'),   
                                # (LogComponent("NormdocToFieldsList"),),                             
                                # (XmlParseLxml(fromKwarg='data', toKwarg='lxmlNode'),
                                    # (LogComponent("NormdocToFieldsList"),),
                                    # (NormdocToFieldsList(),),
                                    # (XmlXPath(['/oai:record/oai:metadata/norm:md_original/oai_dc:dc'], fromKwarg='lxmlNode', namespaces=NAMESPACEMAP),
                                        # (MetaToFieldsList(), # Platte lijst met veldnamen en waardes...
                                        (NormdocToFieldsList(), # Platte lijst met veldnamen en waardes...
                                            # (LogComponent("NormdocToFieldsList"),), # [DcToFieldsList] add(*(), **{'fieldslist': [('dc:identifier', 'http://meresco.com?record=1'), ('dc:description', 'This is an example program about Search with Meresco'), ('dc:title', 'Example Program 1'), ('dc:creator', 'Seecr'), ('dc:publisher', 'Seecr'), ('dc:date', '2016'), ('dc:type', 'Example'), ('dc:subject', 'Search'), ('dc:language', 'en'), ('dc:rights', 'Open Source')], 'partname': 'record', 'identifier': 'meresco:record:1'})
                                            (FieldsListToLuceneDocument( # Maakt addDocument messege + creeert de facet/drilldown velden waarvan de value's tot max. 256 chars getruncated worden.
                                                    fieldRegistry=luceneWriter.settings.fieldRegistry, # o.a. drilldownfields definitie
                                                    untokenizedFieldnames=untokenizedFieldnames, # untokenized fields
                                                    indexFieldFactory=DcFields, # Creeert een "__all__", veldnaam en optioneel "untokenized.veldnaam"... 
                                                    #rewriteIdentifier=(lambda idee: idee.split(':', 1)[-1]) # meresco:record:1' => 'record:1'
                                                ),
                                                (LogComponent("FIELDS TO LUCENE_WRITER"),), # [LUCENE_WRITER] addDocument(*(), **{'fields': [{'type': 'TextField', 'name': '__all__', 'value': 'http://meresco.com?record=1'}, {'type': 'TextField', 'name': 'dc:identifier', 'value': 'http://meresco.com?record=1'}, {'type': 'StringField', 'name': 'untokenized.dc:identifier', 'value': 'http://meresco.com?record=1'}, {'type': 'TextField', 'name': '__all__', 'value': 'This is an example program about Search with Meresco'}, {'type': 'TextField', 'name': 'dc:description', 'value': 'This is an example program about Search with Meresco'}, {'type': 'TextField', 'name': '__all__', 'value': 'Example Program 1'}, {'type': 'TextField', 'name': 'dc:title', 'value': 'Example Program 1'}, {'type': 'TextField', 'name': '__all__', 'value': 'Seecr'}, {'type': 'TextField', 'name': 'dc:creator', 'value': 'Seecr'}, {'type': 'TextField', 'name': '__all__', 'value': 'Seecr'}, {'type': 'TextField', 'name': 'dc:publisher', 'value': 'Seecr'}, {'type': 'TextField', 'name': '__all__', 'value': '2016'}, {'type': 'TextField', 'name': 'dc:date', 'value': '2016'}, {'path': ['2016'], 'type': 'FacetField', 'name': 'untokenized.dc:date'}, {'type': 'TextField', 'name': '__all__', 'value': 'Example'}, {'type': 'TextField', 'name': 'dc:type', 'value': 'Example'}, {'type': 'TextField', 'name': '__all__', 'value': 'Search'}, {'type': 'TextField', 'name': 'dc:subject', 'value': 'Search'}, {'path': ['Search'], 'type': 'FacetField', 'name': 'untokenized.dc:subject'}, {'type': 'TextField', 'name': '__all__', 'value': 'en'}, {'type': 'TextField', 'name': 'dc:language', 'value': 'en'}, {'type': 'TextField', 'name': '__all__', 'value': 'Open Source'}, {'type': 'TextField', 'name': 'dc:rights', 'value': 'Open Source'}], 'identifier': 'meresco:record:1'})
                                                    # [####LUCENE_WRITER] addDocument(*(), **{'fields': [{'type': 'TextField', 'name': '__all__', 'value': 'knaw'}, {'type': 'TextField', 'name': 'meta:id', 'value': 'knaw'}, {'type': 'TextField', 'name': '__all__', 'value': 'olddata'}, {'type': 'TextField', 'name': 'meta:set', 'value': 'olddata'}, {'type': 'TextField', 'name': '__all__', 'value': 'http://oai.knaw.nl/oai'}, {'type': 'TextField', 'name': 'meta:baseurl', 'value': 'http://oai.knaw.nl/oai'}, {'type': 'TextField', 'name': '__all__', 'value': 'knaw'}, {'type': 'TextField', 'name': 'meta:repositoryGroupId', 'value': 'knaw'}, {'type': 'TextField', 'name': '__all__', 'value': 'nl_didl'}, {'type': 'TextField', 'name': 'meta:metadataPrefix', 'value': 'nl_didl'}, {'type': 'TextField', 'name': '__all__', 'value': 'publication'}, {'type': 'TextField', 'name': 'meta:collection', 'value': 'publication'}, {'path': ['publication'], 'type': 'FacetField', 'name': 'untokenized.meta:collection'}], 'identifier': 'knaw:record:3'})
                                                (luceneWriter,),
                                                # ),
                                            )
                                        )
                                    # )
                                # )
                            )
                        ),
                        (FilterMessages(allowed=['delete']),                            
                            (luceneWriter,),
                        )
                    )
                )
            )
        )
    )
    return readerServer, writerServer


def startServer(port, stateDir, luceneserverPort, gatewayPort, **ignored):
    
    setSignalHandlers()
    print 'Firing up Index Server.'

    statePath = abspath(stateDir)
    writerReactor = Reactor()
    readerReactor = Reactor()

    reader, writer = writerMain(
            writerReactor=writerReactor,
            readerReactor=readerReactor,
            readerPort=port,
            statePath=statePath,
            luceneserverPort=luceneserverPort,
            gatewayPort=gatewayPort,
        )

    readerServer = be(reader)
    writerServer = be(writer)

    # Attaches reader to Lucene thread:
    def startReader():
        LUCENE_VM.attachCurrentThread()
        consume(readerServer.once.observer_init())
        readerReactor.loop()

    # Start writer in main (this) thread:
    consume(writerServer.once.observer_init())

    registerShutdownHandler(statePath=statePath, server=writerServer, reactor=writerReactor, shutdownMustSucceed=False)

    # Start reader in separate/own thread:
    tReader = Thread(target=startReader)
    tReader.setDaemon(True)
    tReader.start()

    print "Ready to rumble at port %s" % port
    stdout.flush()

    writerReactor.loop()
