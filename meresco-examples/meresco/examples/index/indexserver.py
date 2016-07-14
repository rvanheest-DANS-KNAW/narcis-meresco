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
from meresco.lucene import LuceneSettings, DrilldownField, FieldsListToLuceneDocument
from meresco.pylucene import getJVM

from meresco.lucene import Lucene, MultiLucene, UNTOKENIZED_PREFIX, SORTED_PREFIX
from meresco.lucene.adaptertolucenequery import AdapterToLuceneQuery
from meresco.lucene.remote import LuceneRemoteService
from meresco.lucene.fieldregistry import FieldRegistry

from .dctofieldslist import DcToFieldsList
from .dcfields import DcFields

from meresco.examples.gateway.gatewayserver import DEFAULT_PARTNAME

LUCENE_VM = getJVM()


def untokenizedFieldname(fieldname):
    return UNTOKENIZED_PREFIX + fieldname

UNQUALIFIED_TERM_FIELDS = [('__all__', 1.0)]

drilldownFields = [
    DrilldownField(untokenizedFieldname('dc:date')),
    DrilldownField(untokenizedFieldname('dc:subject')),
]

# Add any non-drilldown untokenized fields:
untokenizedFieldnames = [f.name for f in drilldownFields] + [untokenizedFieldname('dc:identifier')]


DEFAULT_CORE = 'oai_dc'

def luceneAndReaderConfig(defaultLuceneSettings, httpRequestAdapter, luceneserverPort):
    
    # reactor, statePath werden NIET gebruikt? (reactor, statePath, ...)

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
        path='/oai',
        metadataPrefix='oai_dc',
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
                    (LogComponent("PERIOD"), # [PERIOD] httprequest1_1(*(), **{'body': None, 'host': 'localhost', 'request': '/commit/', 'port': 47896, 'method': 'POST'})
                        (http11Request,),
                    ),
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
                        (LogComponent("SRU harvest van GATEWAY"),), #[SRU harvest van GATEWAY] add(*(), **{'partname': 'record', 'identifier': 'meresco:record:1', 'lxmlNode': '_ElementTree(<record xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><header><identifier>meresco:record:1</identifier><datestamp>2016-07-13T15:31:10Z</datestamp></header><metadata><document xmlns="http://meres
                        (FilterMessages(allowed=['add']),
                            # (LogComponent("ADD from GATEWAY"),),
                            (XmlXPath(['/oai:record/oai:metadata/document:document/document:part[@name="record"]/text()'], fromKwarg='lxmlNode', toKwarg='data'),
                                (XmlParseLxml(fromKwarg='data', toKwarg='lxmlNode'),
                                    (XmlXPath(['/oai:record/oai:metadata/oai_dc:dc'], fromKwarg='lxmlNode'),
                                        (DcToFieldsList(),
                                            (LogComponent("DcToFieldsList"),),
                                            (FieldsListToLuceneDocument(
                                                    fieldRegistry=luceneWriter.settings.fieldRegistry,
                                                    untokenizedFieldnames=untokenizedFieldnames,
                                                    indexFieldFactory=DcFields),
                                                (luceneWriter,),
                                            )
                                        )
                                    )
                                )
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
