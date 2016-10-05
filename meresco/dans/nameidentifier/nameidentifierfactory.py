__author__ = 'wilkos'
from dai_nl import Dai
from isni import Isni
from orcid import Orcid
from rid import Rid
from nod_prs import NodPrs


class NameIdentifierFactory(object):
    # Create based on class name:
    @staticmethod
    def factory(type, baseval):
        baseval = baseval.strip().replace('\n', '')
        # return eval(type + "("+baseval+")")
        if type.strip().lower() == "dai" or type.lower() == "dai-nl": return Dai(baseval)
        if type.strip().lower() == "orcid": return Orcid(baseval)
        if type.strip().lower() == "isni": return Isni(baseval)
        if type.strip().lower() == "rid": return Rid(baseval)
        if type.strip().lower() == "prs" or type.lower() == "nod-prs": return NodPrs(baseval)
        assert 0, "Bad nid creation: " + type
