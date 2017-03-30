## begin license ##
#
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core".
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2011-2013, 2015 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2011, 2015 Stichting Kennisnet http://www.kennisnet.nl
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

from xml.sax.saxutils import escape as xmlEscape

from urlparse import parse_qs
from urlparse import urlsplit
from urllib import urlencode

from meresco.core import Observable
from meresco.components.sru.sruparser import SruMandatoryParameterNotSuppliedException
from meresco.components.http import utils as httputils

from cqlparser import cqlToExpression
from cqlparser.cqlparser import CQLParseException
from meresco.components.web import WebQuery

class BadRequestException(Exception):
    pass

SRU_IS_ONE_BASED = 1 #And our RSS plugin is closely based on SRU

class Rss(Observable):

    # def __init__(self, supportedLanguages, title, description, link, max_maximumRecords=50, **sruArgs):

    def __init__(self, supportedLanguages, title, description, link, antiUnaryClause='', max_maximumRecords=50, **sruArgs):
        Observable.__init__(self)
        self._title = title
        self._description = description
        self._link = link
        self._antiUnaryClause = antiUnaryClause
        self._sortKeys = sruArgs.get('sortKeys', None)

        # Added DANS properties:
        self._supportedLanguages = supportedLanguages # First index is default language
        self._max_maximumRecords = max_maximumRecords
        self._maximumRecords = self._max_maximumRecords if sruArgs.get('maximumRecords', 20) > self._max_maximumRecords else sruArgs.get('maximumRecords', 20)
        self._startRecord = 1
        self._totalhits = 0
        assertDefaultLanguage([title, description, link], supportedLanguages) #Check if al supportedLanguages are available for rss headerTag.


    def handleRequest(self, RequestURI='', **kwargs):
        yield httputils.okRss
        yield """<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>"""

        try:
            Scheme, Netloc, Path, Query, Fragment = urlsplit(RequestURI)
            arguments = parse_qs(Query)
            sortKeys = arguments.get('sortKeys', [self._sortKeys])[0]
            sortBy, sortDescending = None, None
            if sortKeys:
                sortBy, ignored, sortDescending = sortKeys.split(',')
                sortDescending = sortDescending == '0'

            # Set Language:
            prefLanguage = arguments.get('preflang', [self._supportedLanguages[0]])[0]
            # This might be German:-(  Not anymore :-)
            prefLanguage = prefLanguage if prefLanguage.lower() in self._supportedLanguages else self._supportedLanguages[0]

            # Get max records, from request or get default
            maximumRecords = int(arguments.get('maximumRecords', [self._maximumRecords])[0])
            maximumRecords = maximumRecords if maximumRecords <= self._max_maximumRecords else int(self._max_maximumRecords) # Check if requested max does not exceed our max...

            #set startrecord: we support rss paging...
            startRecord = int(arguments.get('startRecord', [self._startRecord])[0])
            
            #set querylabel:
            querylabel = arguments.get('querylabel', [self._title.get(prefLanguage)])[0]

            #get userquery:
            query = arguments.get('query', [''])[0]
            filters = arguments.get('filter', [])
            # startRecord = 1

            if not query and not self._antiUnaryClause:
                raise SruMandatoryParameterNotSuppliedException("query")

            webquery = WebQuery(query, antiUnaryClause=self._antiUnaryClause)
            for filter in filters:
                if not ':' in filter:
                    raise BadRequestException('Invalid filter: %s' % filter)
                field,term = filter.split(':', 1)
                webquery.addFilter(field, term)

            ast = webquery.ast

        except (SruMandatoryParameterNotSuppliedException, BadRequestException, CQLParseException), e:
            yield '<title>ERROR %s</title>' % xmlEscape(self._title)
            # yield '<link>%s</link>' % xmlEscape(self._link)
            yield '<link>%s</link>' % xmlEscape(self._link.get(prefLanguage))
            yield "<description>An error occurred '%s'</description>" % xmlEscape(str(e))
            yield """</channel></rss>"""
            raise StopIteration()

        yield '<title>%s</title>' % xmlEscape(querylabel)
        yield '<description>%s</description>' % xmlEscape(self._description.get(prefLanguage))
        yield '<link>%s</link>' % xmlEscape(self._link.get(prefLanguage))

        
        yield self._yieldResults(
                query=cqlToExpression(ast),
                start=startRecord - SRU_IS_ONE_BASED,
                stop=startRecord - SRU_IS_ONE_BASED+maximumRecords,
                sortBy=sortBy,
                sortDescending=sortDescending,
                prefLang=prefLanguage)
        yield str(self._createPaging(Query, maximumRecords))
        yield """</channel>"""
        yield """</rss>"""

# def _yieldResults(self, query=None, start=0, stop=19, sortBy=None, sortDescending=False, prefLang='nl', **kwargs):
    def _yieldResults(self, query=None, start=0, stop=19, sortBy=None, sortDescending=False, prefLang='nl'):
        response = yield self.any.executeQuery(
            query=query,
            start=start,
            stop=stop,
            sortKeys=[{'sortBy': sortBy, 'sortDescending': sortDescending}] if sortBy is not None else None
        )
        total, hits = response.total, response.hits
        self._totalhits = int(total)
        # print "totalhits", total, "hits", hits # totalhits 2 hits [Hit(score=1.454383373260498, id='knaw:record:2')]
        for hit in hits:
            yield self.call.getRecord(identifier=hit.id, preflang=prefLang, defaultlang=self._supportedLanguages[0])

    def _createPaging(self, query, maximumRecords):
        # print "In create pagingl; maxrec; query:", maximumRecords, xmlEscape(query)
        # Add atom:self link:
        rss_paging = '\n<atom:link rel="self" type="application/rss+xml" href="http://rss.narcis.nl/rss?%s"/>' % (xmlEscape(query))
        arguments = parse_qs(query)
        arguments.update({'maximumRecords' : maximumRecords}) #Reset 'maximumRecords' in case of overvragen...
        currentStartRecordNumber = int(arguments.get('startRecord', [self._startRecord])[0])

        # Add atom:next link:
        if self._totalhits > int(currentStartRecordNumber)+maximumRecords-SRU_IS_ONE_BASED:
            arguments.update({'startRecord':str(int(currentStartRecordNumber)+maximumRecords)}) #introduce/update startRecord param
            rss_paging += '\n<atom:link rel="next" type="application/rss+xml" href="http://rss.narcis.nl/rss?%s"/>' % xmlEscape(urlencode(arguments, True))

        # Add atom:previous link:
        if currentStartRecordNumber-maximumRecords >= 0:
            arguments.update({'startRecord':str(int(currentStartRecordNumber)-maximumRecords)}) #update startRecord param
            rss_paging += '\n<atom:link rel="previous" type="application/rss+xml" href="http://rss.narcis.nl/rss?%s"/>' % xmlEscape(urlencode(arguments, True))        
        return rss_paging

def assertDefaultLanguage(headerLanguageMapping, supportedLanguages):
    for headerDict in headerLanguageMapping:
        for lang in supportedLanguages:
            if not lang in headerDict:
                raise TypeError("__init__() missing claimed supported language '%s' in %s" % (lang, headerDict))

