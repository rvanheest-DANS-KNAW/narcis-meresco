from persistentidentifier import PersistentIdentifier


class ArXiv(PersistentIdentifier):
    # ["1501.00001", "arXiv:", " arXiv:astro-ph/0703632", "arXiv:1501.00001v1", "arXiv:0706.0001v1 [q-bio.CB] 1 Jun 2007", "https://arxiv.org/abs/0706.0001v1"]

    ID_PATTERN = None

    def __init__(self, basestring):
        PersistentIdentifier.__init__(self, "arxiv", basestring, ['https://arxiv.org/abs/', 'http://arxiv.org/abs/'],
                                      "https://arxiv.org/abs")

    def _validate_and_initialize(self):

        minprefix = self.init_value.lower().replace("arxiv:", '').replace("https://arxiv.org/abs/", '').replace(
            "http://arxiv.org/abs/", '').strip()
        arxivelist = minprefix.split(" ")
        if arxivelist[0]:
            self.unformatted = arxivelist[0]
            self.id = "arxiv:" + self.unformatted
            self.formatted.append(self.unformatted)
            self.resolvableurl = '%s/%s' % (self.resolver, self.unformatted)
            for prefix in self.prefixes:
                for suffix in self.formatted:
                    self.typedVariants.add(prefix + suffix)
            self.typedVariants.add(self.id)
            self.valid = True

    def __str__(self):
        return self.get_init_value()

# https://arxiv.org/help/arxiv_identifier
# The canonical form of identifiers from January 2015 (1501) is arXiv:YYMM.NNNNN, with 5-digits for the sequence number within the month.
