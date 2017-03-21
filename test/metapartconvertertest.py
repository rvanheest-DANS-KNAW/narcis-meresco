# -*- coding: utf-8 -*-
#WST
import sys
#
sys.path.insert(0, "..")

from seecr.test import SeecrTestCase, CallTrace
from lxml.etree import parse, tostring, XML, fromstring, dump, XMLSchema, parse as lxmlParse
from StringIO import StringIO
from meresco.dans.metapartconverter import AddMetadataNamespace
from os.path import abspath, dirname, join
from difflib import unified_diff
from meresco.core import Observable
import time
from weightless.core import be, compose
from unittest import main

metaNS = {'meta' : 'http://meresco.org/namespace/harvester/meta',
          'doc' : 'http://meresco.org/namespace/harvester/document'}

class MetaPartConverterTest(SeecrTestCase):

    def setUp(self):        
        SeecrTestCase.setUp(self)
        self.harvestdate = AddMetadataNamespace(dateformat="%Y-%m-%dT%H:%M:%SZ", fromKwarg='lxmlNode')
        self.observer = CallTrace('observer')
        self.harvestdate.addObserver(self.observer)

    def tearDown(self):
        SeecrTestCase.tearDown(self)
            
    def testAddMetadataNamespace(self):
    
        self.observer.methods['add'] = lambda *args, **kwargs: (x for x in [])
        
        list( compose(self.harvestdate.all_unknown('add', 'id', 'metadata', 'anotherone', lxmlNode=parse(open("data/harvesterdoc.xml")), identifier='oai:very:secret:09987' )))
        
        self.assertEquals(1, len(self.observer.calledMethods))
        
        # for m in self.observer.calledMethods:
        #     print 'method name:',m.name, m.args, m.kwargs
            
        result = self.observer.calledMethods[0].kwargs.get('lxmlNode')
        self.assertEquals(3, len(self.observer.calledMethods[0].args))
        arguments = self.observer.calledMethods[0].args
        self.assertEquals("id", arguments[0])
        self.assertEquals("metadata", arguments[1])
        metapart = result.xpath("//doc:part[@name='meta']/text()", namespaces=metaNS)
        mdNamespace = fromstring(metapart[0]).xpath("//meta:metadataNamespace/text()", namespaces=metaNS)

        self.assertTrue( len(mdNamespace)==1 and mdNamespace[0]=="http://www.openarchives.org/OAI/2.0/oai_dc/" ) 
    
        
if __name__ == '__main__':
    main()