import unittest
from meresco.dans.persistentidentifier import PidFactory

valid_dois = ["http://doi.org/10.1234/abc",
              "https://doi.org/10.1234/abc",
              "http://dx.doi.org/10.1234/abc",
              "https://dx.doi.org/10.1234/abc",
              "doi.org/10.1234/abc",
              "doi.org/urn:10.1234/abc",
              "doi.org/doi:10.1234/abc",
              "doi.org/urn:doi:10.1234/abc",
              "urn:10.1234/abc",
              "doi:10.1234/abc",
              "urn:doi:10.1234/abc",
              "10.1234/abc",
              "10.123.456/789",
              "10.1/2",
              ]
invalid_dois = ["http://doi.org/10.1234",
              "https://doi.org/10.1234/",
              "ftp://doi.org/10.1234/abc",
              "doi.org/urn:10.1234",
              "doi:urn:10.1234/abc",
              "11.1234/abc",
              "10.1234",
              "10.1234/",
              "10.abc/def",
              "10/abc",
              "",
              ]

valid_handles = ["20.1000/100", "2381/12345","http://hdl.handle.net/10.1000/182", "http://handle.net/10.1000/182", "https://doi.org/20.1000/100",
                 "info:hdl/20.1000/100", "hdl:4263537/4000", "youcanwriteherewhatever.herealso/andheretoo"]

invalid_handles = ["", "1", "1/", "10.1234"]

valid_pmids = ["PMID|123", "PMID 12345", "whateverbeforenumbers(s) 123"]

invalid_pmids = ["", "PMID"]

valid_pures = ["0123aBcD-5e6F-aB78-8cD9-123456abcdef", "somethingpreceding... 0123aBcD-5e6F-aB78-8cD9-123456abcdef", "1234567890 0123aBcD-5e6F-aB78-8cD9-123456abcdef"]

invalid_pures = ["", "0123GBcD-5e6F-aB78-8cD9-123456abcdef", "0123aBcD-12345-aB78-8cD9-123456abcdef","0123aBcD:5e6F:aB78:8cD9:123456abcdef",
                 "0123aBcD-5e6F-aB78-ccD9-123456abcdef", "0123aBcD-5e6F-aB78-8cD9-123456abcdefghijklmn", "12345678900123aBcD-5e6F-aB78-8cD9-123456abcdef"]

valid_purls = ["https://dans.knaw.nl", "http://dans.knaw.nl", "ftp://dans.knaw.nl", "http://whatever"]

invalid_purls = ["", "http://", "httpx://dans.knaw.nl", "https:/dans.knaw.nl", "ftp//dans.knaw.nl", "something-http://whatever"]


class PersistentIdentifierTest(unittest.TestCase):

    def test_doi(self):
        print "\nRunning DOI validator test..."
        for doi in valid_dois:
            pId = PidFactory.factory("doi", doi)
            self.assertTrue(pId.is_valid())

        for doi in invalid_dois:
            pId = PidFactory.factory("doi", doi)
            self.assertFalse(pId.is_valid())

    def test_handle(self):
        print "Running HANDLE validator test..."
        for handle in valid_handles:
            pId = PidFactory.factory("handle", handle)
            self.assertTrue(pId.is_valid())

        for handle in invalid_handles:
            pId = PidFactory.factory("handle", handle)
            self.assertFalse(pId.is_valid())


    def test_pmid(self):
        print "Running PMID validator test..."
        for pmid in valid_pmids:
            pId = PidFactory.factory("pmid", pmid)
            self.assertTrue(pId.is_valid())

        for pmid in invalid_pmids:
            pId = PidFactory.factory("pmid", pmid)
            self.assertFalse(pId.is_valid())

    def test_pure(self):
        print "Running PURE validator test..."
        for pure in valid_pures:
            pId = PidFactory.factory("pure", pure)
            self.assertTrue(pId.is_valid())

        for pure in invalid_pures:
            pId = PidFactory.factory("pure", pure)
            self.assertFalse(pId.is_valid())

    def test_purl(self):
        print "Running PURL validator test..."
        for purl in valid_purls:
            print "valid purl? ", purl
            pId = PidFactory.factory("purl", purl)
            self.assertTrue(pId.is_valid())

        for purl in invalid_purls:
            print "invalid purl? ", purl
            pId = PidFactory.factory("purl", purl)
            self.assertFalse(pId.is_valid())



if __name__ == '__main__':
    unittest.main()