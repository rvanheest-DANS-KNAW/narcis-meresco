import re

from persistentidentifier import PersistentIdentifier

class Scopus(PersistentIdentifier):

    ID_PATTERN = None

    def __init__(self, basestring):
        PersistentIdentifier.__init__(self, "scopus", basestring, [])

    def _validate_and_initialize(self):
        idee = re.split(':| ', self.init_value).pop()
        self.unformatted = idee
        self.id = "scopus:" + self.unformatted
        for prefix in self.prefixes:
            for suffix in self.formatted:
                self.typedVariants.add(prefix + suffix)
        self.typedVariants.add(self.id)
        self.typedVariants.add(self.unformatted)
        self.valid = True

    def __str__(self):
        return self.get_init_value()