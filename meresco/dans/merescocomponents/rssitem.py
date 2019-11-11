## begin license ##
# 
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core". 
# 
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
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

from meresco.components import XmlCompose
from xml.sax.saxutils import escape as xmlEscape
from urllib import quote as urlQuote

RSS_TEMPLATE = """<item>
    <title>%(title)s</title>
    <description>%(description)s</description>
    <link>%(link)s</link>
    <guid>%(link)s</guid>
    <pubDate>%(pubdate)s</pubDate>
</item>"""


# # WCP (Target) Collection : NARCIS Portal URL
# narcisLinkTemplates = {
#     'publication'  : 'http://www.narcis.nl/publication/RecordID/%(oai_identifier)s/Language/%(language)s',
#     'dataset'      : 'http://www.narcis.nl/dataset/RecordID/%(oai_identifier)s/Language/%(language)s',
#     'organisation' : 'http://www.narcis.nl/organisation/RecordID/%(oai_identifier)s/Language/%(language)s',
#     'person'       : 'http://www.narcis.nl/person/RecordID/%(oai_identifier)s/Language/%(language)s',
#     'research'     : 'http://www.narcis.nl/research/RecordID/%(oai_identifier)s/Language/%(language)s',
#     'unknown'      : 'http://www.narcis.nl/?RecordID=%(oai_identifier)s&Language=%(language)s'
#     }

class RssItem(XmlCompose):
    def __init__(self, nsMap, title, description, pubdate, linkTemplate, **linkFields):
        XmlCompose.__init__(self,
            template="ignored",
            nsMap=nsMap,
            title=title,
            description=description,
            pubdate=pubdate,
            **linkFields)

        self._linkTemplate = linkTemplate
        assertLinkTemplate(linkTemplate, linkFields)

    def createRecord(self, dataDictionary):
        try:
            link = self._linkTemplate % dict(((k, urlQuote(v, safe='')) for k,v in dataDictionary.items()))
        except KeyError:
            link = ''
        rssData = {
            'link': xmlEscape(link),
            'description': xmlEscape(dataDictionary.get('description', '')),
            'title': xmlEscape(dataDictionary.get('title', '')),
            'pubdate': xmlEscape(dataDictionary.get('pubdate', ''))
        }
        return str(RSS_TEMPLATE % rssData)

    # Add method from xmlCompose:
    def getRecord(self, identifier, preflang, defaultlang):
        data = {}
        data['language'] = preflang # By default, put language to the data map. This might be overridden by xpath
        cachedRecord = {}
        for tagName, values in self._fieldMapping.items():

            if isinstance(values, str): # Skip if string only... (No key, value pairs available)
                continue
            partname, xPathDict = values

            if not partname in cachedRecord:
                cachedRecord[partname] = self._getPart(identifier, partname)
            xml = cachedRecord[partname]

            if isinstance(xPathDict, str):
                results = xml.xpath(xPathDict, namespaces=self._nsMap)
            elif isinstance(xPathDict, dict):
                xmllang = preflang if preflang in xPathDict else defaultlang
                results = xml.xpath(xPathDict.get(xmllang), namespaces=self._nsMap)
                if len(results) == 0 and xmllang != defaultlang: # No results, try again for default language if not already done.
                    results = xml.xpath(xPathDict.get(defaultlang), namespaces=self._nsMap)
            else:
                pass

            if results:
                data[tagName] = str(results[0])
        return self.createRecord(data)


def assertLinkTemplate(linkTemplate, linkFields):
    try:
        linkTemplate % dict(((k,'value') for k in linkFields.keys()))
    except KeyError, e:
        givenArguments = len(linkFields) + len(['self', 'nsMap', 'supportedLanguages', 'title', 'description', 'linkTemplate'])
        raise TypeError("__init__() takes at least %s arguments (%s given, missing %s)" % (givenArguments + 1, givenArguments, str(e)))

# def assertLinkTemplate(linkTemplate, linkFields):
#     try:
#         for k in linkFields.keys():
#             linkTemplate % dict(((k,'value') for k in linkFields.keys()))
#     except KeyError, e:
#         givenArguments = len(linkFields) + len(['self', 'nsMap', 'supportedLanguages'])
#         raise TypeError("__init__() takes at least %s arguments (%s given, missing %s)" % (givenArguments + 1, givenArguments, str(e)))
