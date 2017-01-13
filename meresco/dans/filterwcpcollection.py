## begin license ##
#
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core".
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2012, 2014 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2014 Netherlands Institute for Sound and Vision http://instituut.beeldengeluid.nl/
#
# This file is part of "Meresco Components"
#
# "Meresco Components" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Components" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Components"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from weightless.core import NoneOfTheObserversRespond, DeclineMessage
from meresco.core import Observable

from lxml import etree
from lxml.etree import parse, _ElementTree, tostring
from meresco.xml import namespaces



namespacesmap = namespaces.copyUpdate({ #  See: https://github.com/seecr/meresco-xml/blob/master/meresco/xml/namespaces.py
    
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


class FilterWcpCollection(Observable):
    """ Tries to find wcp collection from (meta) data, if it fails, it will not pass the message """

    def __init__(self, allowed=None, disallowed=None, **kwargs):
        Observable.__init__(self, **kwargs)
        # self._getLongAsLxml = False
        if allowed and not disallowed:
            self._allowedCollection = lambda message: message in allowed
        elif disallowed and not allowed:
            self._allowedCollection = lambda message: message not in disallowed
        else:
            raise ValueError('Use disallowed or allowed')


    def _convert(self, lxmlNode):
        recordpart = lxmlNode.xpath('/oai:record/oai:metadata/document:document/document:part[@name="record"]/text()', namespaces=namespacesmap)
        if len(recordpart) == 1:
            record_lxml = etree.fromstring(recordpart[0])
            longpart = record_lxml.xpath('//norm:normalized/long:knaw_long', namespaces=namespacesmap)
            if len(longpart) == 1:
                print tostring(longpart[0])
                return longpart[0]


    def _getWcpCollection(self, **kwargs):
        collection = None
        try:
            lxmlNode = kwargs['lxmlNode']
        except KeyError:
            pass
        else:
            # Check if long is available as lxml:
            long_wcpcollection = lxmlNode.xpath('//long:knaw_long/long:wcpcollection/text()', namespaces=namespacesmap)
            if len(long_wcpcollection):
                collection = long_wcpcollection[0]
                # print 'collection from <wcpcollection>'
            else: # Hopefully meta is available
                metapart = lxmlNode.xpath('/oai:record/oai:metadata/document:document/document:part[@name="meta"]/text()', namespaces=namespacesmap)
                if len(metapart) == 1:
                    # print metapart[0]
                    meta_lxml = etree.fromstring(metapart[0])
                    collection = meta_lxml.xpath('//meta:repository/meta:collection/text()', namespaces=namespacesmap)
                    if len(collection) == 1:
                        collection = collection[0]
                        # print 'collection from <meta:collection>'
        return collection


    def all_unknown(self, message, *args, **kwargs):
        if self._allowedCollection(self._getWcpCollection(**kwargs)):
            yield self.all.unknown(message, *args, **kwargs)


    def any_unknown(self, message, *args, **kwargs):
        if self._allowedCollection(self._getWcpCollection(kwargs)):
            try:
                response = yield self.any.unknown(message, *args, **kwargs)
                raise StopIteration(response)
            except NoneOfTheObserversRespond:
                pass
        raise DeclineMessage


    def call_unknown(self, message, *args, **kwargs):
        if self._allowedCollection(self._getWcpCollection(**kwargs)):
            try:
                return self.call.unknown(message, *args, **kwargs)
            except NoneOfTheObserversRespond:
                pass
        raise DeclineMessage

    def do_unknown(self, message, *args, **kwargs):
        if self._allowedCollection(self._getWcpCollection(**kwargs)):
            self.do.unknown(message, *args, **kwargs)
