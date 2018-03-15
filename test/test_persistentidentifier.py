import unittest

from meresco.dans.persistentidentifier import PidFactory, Doi, Purl, Handle, ArXiv, Issn, Isbn, Pmid, Pure, Wos, Scopus, Unknown, Nbn


class TestPidFactory(unittest.TestCase):

    def setUp(self):
        self.identifiers = [
            ('local', 'PURE UUID: 09cc3502-8cee-4fb9-a69b-f25daaa6bf1e', Pure, True),
            ('local', 'researchoutputwizard: METIS_UVA_123256', Unknown, False),
            ('local', 'PURE: 47739399', Pure, False),
            ('local', "arXiv:0706.0001v1 [q-bio.CB] 1 Jun 2007", ArXiv, True),
            ('local', 'handle.net: 11245/1.123256', Handle, True),
            ('lOcal', 'WOS: 000387058900004', Wos, True),
            ('local', 'handle.net: http://hdl.handle.net/1871.1/6faea2a1-a4d5-4806-9b3c-08d7cc1ea84e', Handle, True),
            ('local', 'PubMed:28545724', Pmid, True),
            ('local', 'Scopus: 85041205007', Scopus, True),
            ('local', '85041205007', Unknown, False),
            ('pure', 'PURE UUID: 09cc3502-8cee-4fb9-a69b-f25daaa6bf1e', Pure, True),
            ('pure', '09cc3502-8cee-4fb9-a69b-f25daaa6bf1e', Pure, True),
            ('wos', 'WOS 000387058900004', Wos, True),
            ('WoS', '000387058900004', Wos, True),
            ('scopus', 'Scopus: 85041205007', Scopus, True),
            ('scoPus', 'Scopus:85041205007', Scopus, True),
            ('scopus', '85041205007', Scopus, True),
            ('uri', 'info:hdl/1887/58684', Handle, True),
            ('uri', 'http://hdl.handle.net/1765/104628', Handle, True),
            ('uri', 'uuid:e08f93c3-b288-4847-9a6c-7be133f15108', Unknown, False),
            ('uri', 'uuid:e08f93c3-b288-4847-9a6c-7be133f15108', Unknown, False),
            ('uuid', 'uuid:666f93c3-b288-4847-9a6c-7be133f15108', Unknown, False),
            ('uri', 'e08f93c3-b288-4847-9a6c-7be133f15108', Unknown, False),
            ('uri', 'https://surfsharekit.nl/publicatierecord/78ea8643-6e62-40cf-a812-a4c60e80e110&lt;/dii:Identifier',
             Purl, True),
            ('URI', 'urn:isbn:978-94-6290-466-8', Isbn, True),
            ('URI', 'urn:doi:10.1000/182', Doi, True),
            ('URI', 'URN:ISSN:1876-4142', Issn, True),
            ('DMO_ID', 'easy-dataset:74815', Unknown, False),
            ('vsoi', 'vsoi:vsoi-dataset:666', Unknown, False),
            ('VSOI', 'Vsoi:vsoi-dataset:666', Unknown, False),
            ('href', 'https://www.narcis.nl', Purl, True),
            ('uri', 'https://www.narcis.nl', Purl, True),
            ('local', 'https://www.narcis.nl', Unknown, False),
            ('arxiv', "arXiv:0706.0001v1 [q-bio.CB] 1 Jun 2007", ArXiv, True),
        ]

    def test_return_type(self):
        for type, value, clazz, isValid in self.identifiers:
            pid = PidFactory.factory(type, value)
            self.assertEqual(pid.get_classname(), clazz.__name__)
            self.assertEqual(pid.is_valid(), isValid)

    def test_issn(self):
        issn = [
            (Issn('1876414X'), 'issn:1876-414X'),
            (Issn('URN:ISSN:18764142'), 'issn:1876-4142'),
            (Issn('ISSN:9999-666x'), 'issn:9999-666x'),
            (Issn("ISBN-13: 978-0-596-52068-7"), None),
            (Issn("978 1 78536 720 2"), None),
            (Issn('1876414X'), 'issn:1876-414X'),
            (Issn('URN:ISSN:18764142'), 'issn:1876-4142'),
            (Issn('ISSN:9999-666x'), 'issn:9999-666x'),

            (Isbn("ISBN-13: 978-0-596-52068-7"), 'isbn:9780596520687'),
            (Isbn("978 1 78536 720 2"), 'isbn:9781785367202'),
            (Isbn("ISBN-13 978 0 596 52068 7"), 'isbn:9780596520687'),
            (Isbn("ISBN-10 85-359-0277-5"), 'isbn:8535902775'),
            (Isbn("urn:isbn:978-94-6290-466-8"), 'isbn:9789462904668'),
            (Isbn("isbn:978-94-6290-466-8"), 'isbn:9789462904668'),
            (Isbn("90-902734-1-6"), 'isbn:9090273416'),
            (Isbn("978906446101x"), 'isbn:978906446101X'),
            (Isbn("0-8044-2957-X"), 'isbn:080442957X'),

            (Pmid('pmid:1876414'), 'pmid:1876414'),
            (Pmid('PubMed: 27646112'), 'pmid:27646112'),

            (Doi('http://'), None),
            (Doi('http://dx.doi.org/10.1000/182'), 'doi:10.1000/182'),
            (Doi("doi:10.1000/182666"), 'doi:10.1000/182666'),
            (Doi("https://doi.org/urn:10.1000/182"), 'doi:10.1000/182'),
            (Doi("http://dx.doi.org/10.1000/182"), 'doi:10.1000/182'),
            (Doi("urn:doi:10.1000/182"), 'doi:10.1000/182'),
            (Doi("10.1016/j.epsl.2011.11.037"), 'doi:10.1016/j.epsl.2011.11.037'),
            (Doi("http://doi:10.1037/rmh0000008"), None),
            (Doi("https://doi.org/10.1109/5.771073"), 'doi:10.1109/5.771073'),

            (Nbn('urn:nbn:Nl:ui:22-123456789/173004'), 'urn:nbn:nl:ui:22-123456789/173004'),
            (Nbn('URN:urn:nbn:nl:ui:22-123456789/183070'), 'urn:nbn:nl:ui:22-123456789/183070'),
            (Nbn('urn:urn:nbn:nl:ui:22-123456789/183070'), 'urn:nbn:nl:ui:22-123456789/183070'),

            (Purl('000000025228197x'), None),
            (Purl('https://www.narcis.nl'), 'https://www.narcis.nl'),
            (Purl('ftp://ftp.narcis.nl/docs'), 'ftp://ftp.narcis.nl/docs'),

            (Handle('143585'), None),
            (Handle('http://repository-acc.ubn.ru.nl/handle/123456789/143585'), 'hdl:123456789/143585'),
            (Handle('11245/1.132038'), 'hdl:11245/1.132038'),
            (Handle('info:hdl/20.1000/100'), 'hdl:20.1000/100'),
            (Handle("20.1000/100"), 'hdl:20.1000/100'),
            (Handle("2381/12345"), 'hdl:2381/12345'),
            (Handle("hdl:4263537/4000"), 'hdl:4263537/4000'),
            (Handle("http://handle.net/10.1000/182"), 'hdl:10.1000/182'),
            (Handle("https://doi.org/20.1000/100"), 'hdl:20.1000/100'),

            (ArXiv("1501.00001"), 'arxiv:1501.00001'),
            (ArXiv("arXiv:"), None),
            (ArXiv(" arXiv:astro-ph/0703632"), 'arxiv:astro-ph/0703632'),
            (ArXiv("arXiv:1501.00001v1"), 'arxiv:1501.00001v1'),
            (ArXiv("arXiv:0706.0001v1 [q-bio.CB] 1 Jun 2007"), "arxiv:0706.0001v1"),
            (ArXiv("https://arxiv.org/abs/0706.0001v1"), "arxiv:0706.0001v1"),

            (Pure('PURE UUID: 09cc3502-8cee-4fb9-a69b-f25daaa6bf1e'), 'pure:09cc3502-8cee-4fb9-a69b-f25daaa6bf1e'),
            (Pure('09cc3502-8cee-4fb9-a69b-f25daaa6bf1e'), 'pure:09cc3502-8cee-4fb9-a69b-f25daaa6bf1e'),
            (Pure('PURE: 47739399'), None),

            (Scopus("Scopus: 85041205007"), 'scopus:85041205007'),
            (Wos("WOs: 85041205007"), 'wos:85041205007'),
        ]

        for item, idx in issn:
            self.assertEqual(item.get_idx_id(), idx)


if __name__ == '__main__':
    unittest.main()
