## begin license ##
#
#
## end license ##

import sys

from lxml import etree
from lxml.etree import parse, _ElementTree, tostring

from StringIO import StringIO
from xml.sax.saxutils import escape as escapeXml
from copy import deepcopy
from weightless.core import NoneOfTheObserversRespond, DeclineMessage
from meresco.core import Observable
from meresco.components import lxmltostring, Converter
from meresco.dans.nameidentifier import Orcid, Dai, Isni, Rid, NameIdentifierFactory
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


class ShortConverter(Converter):


    def __init__(self, fromKwarg, toKwarg=None, name=None, truncate_chars=300):
        Converter.__init__(self, name=name, fromKwarg=fromKwarg, toKwarg=toKwarg)
        self._truncate_chars = truncate_chars

    def _convert(self, lxmlNode):

        e_root = deepcopy(lxmlNode).getroot() # We need a deepcopy; otherwise we'll modify the lxmlnode by reference.
        if namespacesmap['long'] in e_root.nsmap.values(): # Assert knaw_long is available.
            hasDateAvailable = False
            dateAvailable = lxmlNode.xpath("/long:knaw_long/long:metadata/long:dateAvailable", namespaces=namespacesmap)
            if len(dateAvailable) > 0:
                hasDateAvailable = True
            for child in e_root.iterchildren():
                if child.tag != namespacesmap.curieToTag('long:accessRights') \
                    and child.tag != namespacesmap.curieToTag('long:metadata'):
                        e_root.remove(child)
                if child.tag == namespacesmap.curieToTag('long:metadata'):
                    for metadatakind in child.iterchildren():
                        if metadatakind.tag != namespacesmap.curieToTag('long:titleInfo') \
                        and metadatakind.tag != namespacesmap.curieToTag('long:name') \
                        and metadatakind.tag != namespacesmap.curieToTag('long:genre') \
                        and metadatakind.tag != namespacesmap.curieToTag('long:abstract') \
                        and metadatakind.tag != namespacesmap.curieToTag('long:dateIssued') \
                        and metadatakind.tag != namespacesmap.curieToTag('long:dateAvailable') \
                        and metadatakind.tag != namespacesmap.curieToTag('long:hostCitation') \
                        and metadatakind.tag != namespacesmap.curieToTag('long:status') \
                        and metadatakind.tag != namespacesmap.curieToTag('long:penvoerder') \
                        and metadatakind.tag != namespacesmap.curieToTag('long:locatie'):
                            child.remove(metadatakind)
                        if metadatakind.tag == namespacesmap.curieToTag('long:dateIssued') and hasDateAvailable == True:
                            child.remove(metadatakind)
                        if metadatakind.tag == namespacesmap.curieToTag('long:abstract'):
                            if metadatakind.text != None: metadatakind.text = self._smarttruncate(metadatakind.text) # , ' (...)' [:self._truncate_chars]
            try:
                returnxml = etree.tostring(e_root, pretty_print=True, encoding='utf-8').replace(namespacesmap['long'], namespacesmap['short'])
                returnxml = returnxml.replace('<knaw_long ', '<knaw_short ').replace('</knaw_long>', '</knaw_short>').replace('<dateAvailable>', '<dateIssued>').replace('</dateAvailable>', '</dateIssued>')
                parser = etree.XMLParser(remove_blank_text=True)
#               print etree.tostring(parse(StringIO(returnxml), parser), pretty_print=True)
                return parse(StringIO(returnxml), parser)
            except:
                print 'Error while parsing', returnxml
                raise
        else:
            return None


    def _smarttruncate(self, content, suffix=''):
        if len(content) <= self._truncate_chars:
            return content
        else:
            return ' '.join(content[:self._truncate_chars+1].split(' ')[0:-1]) + suffix



