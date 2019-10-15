# -*- coding: utf-8 -*-
## begin license ##
# 
# "Meresco Oai" are components to build Oai repositories, based on
# "Meresco Core" and "Meresco Components". 
# 
# Copyright (C) 2010 Maastricht University Library http://www.maastrichtuniversity.nl/web/Library/home.htm
# Copyright (C) 2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
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

from xml.sax.saxutils import escape as escapeXml

class OaiOpenAIREDescription(object):
   
    def __init__(self, serviceid, acronym, name, description, website, baseurl, subjectheading, orgunitid, owneracronym):
        self._serviceid = serviceid
        self._acronym = acronym
        self._name = name
        self._description = description
        self._website = website
        self._baseurl = baseurl
        self._subjectheading = subjectheading
        self._orgunitid = orgunitid
        self._owneracronym = owneracronym

    def description(self):
        yield """<description xmlns="http://www.openarchives.org/OAI/2.0/">"""
        yield """<Service xmlns="https://www.openaire.eu/cerif-profile/1.1/">"""
        yield """<Compatibility xmlns="https://www.openaire.eu/cerif-profile/vocab/OpenAIRE_Service_Compatibility">https://www.openaire.eu/cerif-profile/vocab/OpenAIRE_Service_Compatibility#1.1</Compatibility>"""
        yield "<Acronym>%s</Acronym>" % escapeXml(self._acronym)
        yield """<Name xml:lang="en">%s</Name>"""% escapeXml(self._name)
        yield """<Description xml:lang="en">%s</Description>"""% escapeXml(self._description)
        yield "<WebsiteURL>%s</WebsiteURL>" % escapeXml(self._website)
        yield "<OAIPMHBaseURL>%s</OAIPMHBaseURL>" % escapeXml(self._baseurl)
        yield "<SubjectHeadingsURL>%s</SubjectHeadingsURL>" % escapeXml(self._subjectheading)
        yield "<Owner>"
        yield """    <OrgUnit id="%s">""" % escapeXml(self._orgunitid)
        yield "        <Acronym>%s</Acronym>" % escapeXml(self._owneracronym)
        yield "    </OrgUnit>"
        yield "</Owner>"
        yield "</Service>"
        yield "</description>"