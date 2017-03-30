# -*- coding: utf-8 -*-
## begin license ##
#
#
## end license ##


class Namespaces():
    
    NAMESPACEMAP = {
        'oai_dc'    : 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'mods'      : 'http://www.loc.gov/mods/v3',
        'datacite'  : 'http://datacite.org/schema/kernel-4',
        'org'       : 'http://www.onderzoekinformatie.nl/nod/org',
        'proj'      : 'http://www.onderzoekinformatie.nl/nod/act',
        'prs'       : 'http://www.onderzoekinformatie.nl/nod/prs',
        'didl'      : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
        'dc'        : 'http://purl.org/dc/elements/1.1/',
        'rdf'       : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'ore'       : 'http://www.openarchives.org/ore/terms/',
    }
    
    NAMESPACEMAPPER = {
        'oai_dc'       : NAMESPACEMAP.get('oai_dc'),
        'didl_dc'      : NAMESPACEMAP.get('oai_dc'),
        'didl_mods231' : NAMESPACEMAP.get('mods'),
        'didl_mods30'  : NAMESPACEMAP.get('mods'),
        'didl_mods36'  : NAMESPACEMAP.get('mods'),
        'datacite'     : NAMESPACEMAP.get('datacite'),
        'org'          : NAMESPACEMAP.get('org'),
        'proj'         : NAMESPACEMAP.get('proj'),
        'prs'          : NAMESPACEMAP.get('prs'),
    }

    @staticmethod
    def getNamespace(format):
        return Namespaces.NAMESPACEMAPPER.get(format, None)