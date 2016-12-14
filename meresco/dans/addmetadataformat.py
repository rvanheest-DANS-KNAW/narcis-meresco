## begin license ##
#
#
## end license ##

import sys
from lxml.etree import _ElementTree as ElementTreeType
from lxml import etree

from weightless.core import NoneOfTheObserversRespond, DeclineMessage
from meresco.core import Observable
from meresco.components import lxmltostring, Converter
from xml.sax.saxutils import unescape
from meresco.dans.metadataformats import MetadataFormat

import time

# HVSTR_NS = '{http://meresco.org/namespace/harvester/meta}'
# DOCUMENT_NS = '{http://meresco.org/namespace/harvester/document}'
# surfshareNamespaceMap = {'document'  :  "http://meresco.org/namespace/harvester/document" }

# Deze aanpak gaat helaas mis. Vraag is waarom? Het formaat wordt correct als kwarg aan de message toegevoegd:
# add(*(), **{'partname': 'oai_dc', 'identifier': 'meresco:record:2', 'md_format': 'simple_mods', 'lxmlNode': '_ElementTree(<
# Blijkbaar gaat de add() methode niet correct met kwargs om? (alleen die args eruit prikken die nodig zijn?):

# 127.0.0.1 - - [21/Jul/2016:07:09:30 +0000] "POST /update HTTP/1.0" 200 1823 "-" "-"
# Traceback (most recent call last):
#   File "/usr/lib/python2.7/site-packages/meresco/components/sru/srurecordupdate.py", line 91, in handleRequest
#     lxmlNode=ElementTree(lxmlElementUntail(lxmlNode)),
#   File "/usr/lib/python2.7/site-packages/meresco/components/rewritepartname.py", line 39, in add
#     yield self.all.add(identifier=identifier, partname=self._partname, **kwargs)
#   File "/usr/lib/python2.7/site-packages/meresco/components/filtermessages.py", line 56, in all_unknown
#     yield self.all.unknown(message, *args, **kwargs)
#   File "/home/wilkos/meresco/narcisindex/meresco-examples/meresco/dans/addmetadataformat.py", line 31, in all_unknown
#     yield self.all.unknown(message, *args, **kwargs)
#   File "/usr/lib/python2.7/site-packages/meresco/components/xmlxpath.py", line 69, in all_unknown
#     yield self.all.unknown(msg, *newArgs, **newKwargs)
#   File "/usr/lib/python2.7/site-packages/meresco/components/converter.py", line 46, in all_unknown
#     yield self.all.unknown(msg, *newArgs, **newKwargs)
#   File "/usr/lib64/python2.7/site-packages/weightless/core/_observable.py", line 119, in all
#     c, v, t = exc_info(); raise c, v, t.tb_next
# TypeError: add() got an unexpected keyword argument 'md_format'


class AddMetadataFormat(Observable):
    def __init__(self, fromKwarg, name, **kwargs):
        Observable.__init__(self, **kwargs)
        self._fromKwarg = fromKwarg
        self._name = name if name else 'md_format'

    def all_unknown(self, message, *args, **kwargs):
        kwargs = self._addMetadataFormatToKwargs(**kwargs)
        yield self.all.unknown(message, *args, **kwargs)

    def any_unknown(self, message, *args, **kwargs):
        kwargs = self._addMetadataFormatToKwargs(**kwargs)
        try:
            response = yield self.any.unknown(message, *args, **kwargs)
        except NoneOfTheObserversRespond:
            raise DeclineMessage
        raise StopIteration(response)

    def do_unknown(self, message, *args, **kwargs):
        kwargs = self._addMetadataFormatToKwargs(**kwargs)
        self.do.unknown(message, *args, **kwargs)

    def call_unknown(self, message, *args, **kwargs):
        kwargs = self._addMetadataFormatToKwargs(**kwargs)
        try:
            return self.call.unknown(message, *args, **kwargs)
        except NoneOfTheObserversRespond:
            raise DeclineMessage


    def _addMetadataFormatToKwargs(self, **kwargs):
        lxmlnode = kwargs[self._fromKwarg]
        # TODO: Get metadata format from this node...
        # print 'FOUND LXML NODE'
        # Add found metadataFormat as new kwarg: TODO: Check if key already exists...
        kwargs[self._name] = 'simple_mods'
        return kwargs

    