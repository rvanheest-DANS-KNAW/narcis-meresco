from re import compile, IGNORECASE

from persistentidentifier import PersistentIdentifier

class Pmid(PersistentIdentifier):
    # https://www.ncbi.nlm.nih.gov/pmc/pmctopmid/
    # PMID: use simple numbers, e.g., 23193287
    # TODO: PMCID: include the 'PMC' prefix, e.g., PMC3531190. You may drop the prefix if you select the checkbox for 'Process as PMCIDs'.

    ID_PATTERN = compile(".*?([0-9]+)$", IGNORECASE)

    def __init__(self, basestring):
        PersistentIdentifier.__init__(self, "pmid", basestring, ['https://www.ncbi.nlm.nih.gov/pubmed/'], 'https://www.ncbi.nlm.nih.gov/pubmed/')

    def _validate_and_initialize(self):

        uri_match = Pmid.ID_PATTERN.match(self.init_value)
        if uri_match:
            self.unformatted = uri_match.group(1)
            self.id = "pmid:" + self.unformatted
            self.resolvableurl = '%s%s' % (self.resolver, self.unformatted)

            for prefix in self.prefixes:
                for suffix in self.formatted:
                    self.typedVariants.add(prefix + suffix)

            self.typedVariants.add(self.id)
            self.typedVariants.add(self.init_value)
            self.valid = True


    def __str__(self):
        return self.get_init_value()