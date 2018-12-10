import unittest
from meresco.dans.persistentidentifier import PidFactory

VALID = "valid"
INVALID = "invalid"

pid_types = \
{"doi":
    {VALID:  ["http://doi.org/10.1234/abc", "https://doi.org/10.1234/abc", "http://dx.doi.org/10.1234/abc", "https://dx.doi.org/10.1234/abc",
              "doi.org/10.1234/abc", "doi.org/urn:10.1234/abc", "doi.org/doi:10.1234/abc", "doi.org/urn:doi:10.1234/abc",
              "urn:10.1234/abc", "doi:10.1234/abc", "urn:doi:10.1234/abc",
              "10.1234/abc", "10.123.456/789", "10.1/2"],
    INVALID: ["http://doi.org/10.1234", "https://doi.org/10.1234/", "ftp://doi.org/10.1234/abc",
              "doi.org/urn:10.1234", "doi:urn:10.1234/abc",
              "11.1234/abc", "10.1234", "10.1234/", "10.abc/def", "10/abc", ""]
    },

 "handle":
    {VALID:   ["20.1000/100", "2381/12345","http://hdl.handle.net/10.1000/182", "http://handle.net/10.1000/182", "https://doi.org/20.1000/100",
               "info:hdl/20.1000/100", "hdl:4263537/4000", "you_can_write_here_whatever/and_here_too"],
     INVALID: ["", "1", "10.1234", "hdl:4263537"]
    },

 "nbn":
    {VALID:   ["URN:NBN:NL:12-abc", "URN:NBN:NL:UI:12-abc", "urn:nbn:nl:23-u7-c5nw", "Urn:Nbn:Nl:34-----****whatever", "you_can_have_here_whateverURN:NBN:NL:12-abc"] ,
     INVALID: ["", "URN:12-abc", "URN:NBN:12-abc", "URN:NBN:NL:12", "URN:NBN:NL:12-", "NBN:NL:12-abc", "NBN:URN:NL:12-abc", "URX:NBN:NL:12-abc"]
    },

 "arxiv":
    {VALID:   ["0706.0001", "1501.00001", "1501.00001v1", "1501.00001V1", "arXiv:1501.00001v1", "https://arxiv.org/abs/0706.1234v99", "http://arxiv.org/abs/1806.00099V77",
               "arXiv:0706.0001v1 [q-bio.CB] 1 Jun 2007", "math.GT/0309136", "arXiv:astro-ph/0703632"],
     INVALID: ["", "1501", "1501.", "1501.123", "1501.123456", "1501.00001X1", "HarXiv:1501.00001v1", "ftp://arxiv.org/abs/0706.1234v99"]
    },

 "pmid":
    {VALID:   ["PMID|123", "PMID 12345", "whatever_before_number(s) 123"],
     INVALID: ["", "no numbers"]
    },

 "pure":
    {VALID:   ["0123aBcD-5e6F-aB78-8cD9-123456abcdef", "something_preceding... 0123aBcD-5e6F-aB78-8cD9-123456abcdef", "1234567890 0123aBcD-5e6F-aB78-8cD9-123456abcdef"],
     INVALID: ["", "0123GBcD-5e6F-aB78-8cD9-123456abcdef", "0123aBcD-12345-aB78-8cD9-123456abcdef","0123aBcD:5e6F:aB78:8cD9:123456abcdef",
               "0123aBcD-5e6F-aB78-ccD9-123456abcdef", "0123aBcD-5e6F-aB78-8cD9-123456abcdefghijklmn", "12345678900123aBcD-5e6F-aB78-8cD9-123456abcdef"]
    },

 "purl":
    {VALID:   ["https://dans.knaw.nl", "http://dans.knaw.nl", "ftp://dans.knaw.nl", "http://whatever"],
     INVALID: ["", "http://", "httpx://dans.knaw.nl", "https:/dans.knaw.nl", "ftp//dans.knaw.nl", "something-http://whatever"]
    },

 "isbn":
    {VALID:   ["1234567890", "1234567890123", "123456789012X", "978-0-596-52068-7", "978  0 596 52068  7",
               "ISBN-13: 978-0-596-52068-7", "ISBN-13 978 0 596 52068 7","ISBN-10 85-359-0277-5", "urn:isbn:978-94-6290-466-8", "isbn:978-94-6290-466-8",
               "whatever_preceding_colon : 978-0-596-52068-7", "whatever_preceding_ISBN 85-359-0277-5"],
     INVALID: ["", "123456789", "12345678901234", "123456789012Y", "978:0:596:52068:7", "978_0_596_52068_7",
               "whatever_without_colon  978-0-596-52068-7", "space_preceding ISBN 85-359-0277-5"]
      },

 "issn":
    {VALID:   ["12345678", "12345678", "1234567X", "1234-5678",
               "urn:ISSN:1046-8188", "ISSN:1046-8188",
               "whatever_preceding_colon : 12345678", "whatever_preceding_space 12345678"],
     INVALID: ["", "1234567", "123456789", "2434561Y", "1234 5678", "12-345678",
               "whatever_without_preceding_colon_or_space12345678"]
    }
}


class PersistentIdentifierTest(unittest.TestCase):

    def test_pid(self):

        for pid_type in pid_types:

            print "\nRunning {} validator test".format(pid_type.upper()),

            for pid in pid_types[pid_type][VALID]:
                pId = PidFactory.factory(pid_type, pid)
                self.assertTrue(pId.is_valid())
                print "+",
                # print "valid {} {}".format(pid_type, pid)

            for pid in pid_types[pid_type][INVALID]:
                pId = PidFactory.factory(pid_type, pid)
                self.assertFalse(pId.is_valid())
                print "-",
                # print "invalid {} {}".format(pid_type, pid)


if __name__ == '__main__':
    unittest.main()