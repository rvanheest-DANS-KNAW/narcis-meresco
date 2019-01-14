from re import compile, IGNORECASE
from persistentidentifier import PersistentIdentifier


class Purl(PersistentIdentifier):
    ID_PATTERN = compile(r'^(https?|ftp)://.+$', IGNORECASE)

    def __init__(self, basestring):
        PersistentIdentifier.__init__(self, "purl", basestring)

    def _validate_and_initialize(self):
        m = self.get_idpattern().match(self.init_value)

        if m:
            self.unformatted = m.group(0)
            self.id = self.unformatted
            self.formatted.append(self.unformatted)
            self.typedVariants.update(self.formatted)
            self.resolvableurl = self.unformatted
            self.valid = True

    def __str__(self):
        return self.get_init_value()
