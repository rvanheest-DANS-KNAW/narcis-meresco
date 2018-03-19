__author__ = 'wilkos'

from arxiv import ArXiv
from doi import Doi
from handle import Handle
from purl import Purl
from isbn import Isbn
from issn import Issn
from unknown import Unknown
from nbn import Nbn
from pmid import Pmid
from pure import Pure
from wos import Wos
from scopus import Scopus

import re

class PidFactory(object):

    @staticmethod
    def factory(type, baseval):
        if type.strip().lower() == "local" and (baseval.count(':') >= 1 or baseval.count('|') >= 1):
            baseval_list = re.split(':|', baseval, maxsplit=1)
            type = baseval_list[0].strip().lower()
            baseval = baseval_list[1].strip()
        return PidFactory._getpidclass(type, baseval)

    @staticmethod
    def _getpidclass(type, baseval):
        baseval = baseval.strip().replace('\n', '')
        if type.strip().lower() == "doi":
            return Doi(baseval)
        if type.strip().lower() == "urn" or type.strip().lower() == "urn:nbn" or type.strip().lower() == "urn:nbn:nl" or type.strip().lower() == "urnnbn" or type.strip().lower() == "nbn":
            return Nbn(baseval)
        if type.strip().lower() == "arxiv":
            return ArXiv(baseval)
        if type.strip().lower() == "href" or type.strip().lower() == "url" or type.strip().lower() == "purl": # :mods:relatedItem/@xlink:href wordt met type 'url' opgezet...
            if ("doi.org/" in baseval.lower()):
                return Doi(baseval)
            return Purl(baseval)
        if type.strip().lower() == "issn":
            return Issn(baseval)
        if type.strip().lower() == "isbn":
            return Isbn(baseval)
        if type.strip().lower() == "pmid" or type.strip().lower() == "pubmed":
            return Pmid(baseval)
        if type.strip().lower() == "pure" or "pure" in type.lower():
            return Pure(baseval)
        if type.strip().lower() == "wos":
            return Wos(baseval)
        if type.strip().lower() == "scopus":
            return Scopus(baseval)
        if type.strip().lower() == "uri":
            if ("issn" in baseval.lower()):
                return Issn(baseval)
            if ("isbn" in baseval.lower()):
                return Isbn(baseval)
            if ("doi" in baseval.lower()):
                return Doi(baseval)
            if ("/handle/" in baseval.lower() or "hdl/" in baseval.lower() or "handle.net" in baseval.lower()): #handle may resolve locally, prefixed with local url-resolver, so return url type if given so.
                return Handle(baseval)
            if ("urn:nbn:nl" in baseval.lower()):
                return Nbn(baseval)
            if ("http" in baseval.lower() or "ftp" in baseval.lower()):
                return Purl(baseval)
        if type.strip().lower() == "handle" or type.strip().lower() == "handle.net" or type.strip().lower() == "hdl":
            return Handle(baseval)
        return Unknown(type.strip().replace('\n', ''), baseval)