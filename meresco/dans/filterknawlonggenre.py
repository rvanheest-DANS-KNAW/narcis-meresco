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


class FilterKnawLongGenre(Observable):
    """ Tries to find knaw_long <genre>, if it fails, it will not pass the message """

    def __init__(self, allowed=None, disallowed=None, **kwargs):
        Observable.__init__(self, **kwargs)
        # self._getLongAsLxml = False
        if allowed and not disallowed:
            self._allowedGenre = lambda message: message in allowed
        elif disallowed and not allowed:
            self._allowedGenre = lambda message: message not in disallowed
        else:
            raise ValueError('Use disallowed or allowed')


    def _getKnawLongGenre(self, **kwargs):
        genre = None
        try:
            lxmlNode = kwargs['lxmlNode']
        except KeyError:
            pass
        else:
            # Check if knaw_long is available as lxml:
            long_genre = lxmlNode.xpath('//long:knaw_long/long:metadata/long:genre/text()', namespaces=namespacesmap)
            if len(long_genre):
                genre = long_genre[0]
        return genre


    def all_unknown(self, message, *args, **kwargs):
        if self._allowedGenre(self._getKnawLongGenre(**kwargs)):
            yield self.all.unknown(message, *args, **kwargs)


    def any_unknown(self, message, *args, **kwargs):
        if self._allowedGenre(self._getKnawLongGenre(kwargs)):
            try:
                response = yield self.any.unknown(message, *args, **kwargs)
                raise StopIteration(response)
            except NoneOfTheObserversRespond:
                pass
        raise DeclineMessage


    def call_unknown(self, message, *args, **kwargs):
        if self._allowedGenre(self._getKnawLongGenre(**kwargs)):
            try:
                return self.call.unknown(message, *args, **kwargs)
            except NoneOfTheObserversRespond:
                pass
        raise DeclineMessage

    def do_unknown(self, message, *args, **kwargs):
        if self._allowedGenre(self._getKnawLongGenre(**kwargs)):
            self.do.unknown(message, *args, **kwargs)
