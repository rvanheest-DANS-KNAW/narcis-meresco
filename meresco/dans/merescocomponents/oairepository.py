## begin license ##
#
# "Meresco Oai" are components to build Oai repositories, based on
# "Meresco Core" and "Meresco Components".
#
# Copyright (C) 2014 Netherlands Institute for Sound and Vision http://instituut.beeldengeluid.nl/
# Copyright (C) 2014, 2016 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2014 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
# Copyright (C) 2016 SURFmarket https://surf.nl
#
# This file is part of "Meresco Oai"
#
# "Meresco Oai" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Oai" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Oai"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

#######################
# wilkos-dans, 20190718
# Changed #prefixIdentifier() and  #unprefixIdentifier() methods to accomodate the requiement by OpenAIRE Advance to put the CERIF type in the identifier (=added semantics, IMHO=Bad)
# Files affected:
# - oaipmh.py
# - oairecord.py
# - oairepository.py
#######################

import re

from meresco.oai.oaiutils import OaiException
from socket import gethostname

HOSTNAME = gethostname()

class OaiRepository(object):
    def __init__(self, identifier=None, name=None, adminEmail=None, externalUrl=None):
        self._validateRepositoryIdentifier(identifier)
        self.identifier = identifier
        self.name = name or ''
        self.adminEmail = adminEmail or ''
        self._identifierPrefix = '' if identifier is None else 'oai:{0}:'.format(identifier)
        self._externalUrl = externalUrl
        self._unPrefixRegEx=r"^"+self._identifierPrefix+".*?s/" # The 's/' is the end of plurals: OrgUnit + s/ = OrgUnits/

    def prefixIdentifier(self, identifier, cerif_type=''):
        ######     
        return self._identifierPrefix + cerif_type + identifier
        ######

    def unprefixIdentifier(self, identifier):
        if not self._identifierPrefix:
            return identifier
        if not identifier.startswith(self._identifierPrefix):
            raise OaiException('idDoesNotExist')
        #####
        unprefixedId = re.sub(self._unPrefixRegEx, '', identifier)
        return unprefixedId
        #####

    def requestUrl(self, Headers, path, port, **kwargs):
        if self._externalUrl:
            return self._externalUrl + path
        hostname = Headers.get('Host', HOSTNAME).split(':')[0]
        return 'http://%s:%s%s' % (hostname, port, path)

    @staticmethod
    def _validateRepositoryIdentifier(identifier):
        if not identifier:
            return
        if not re.match(r"[a-zA-Z][a-zA-Z0-9\-]*(\.[a-zA-Z][a-zA-Z0-9\-]+)+", identifier):
            raise ValueError("Invalid repository identifier: %s" % identifier)

    def updateName(self, name):
        self.name = name

    def updateAdminEmail(self, adminEmail):
        self.adminEmail = adminEmail
