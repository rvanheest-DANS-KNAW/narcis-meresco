import re

from persistentidentifier import PersistentIdentifier


class Issn(PersistentIdentifier):
    ID_PATTERN = re.compile("^\d{4}-?\d{3}[\dxX]$", re.IGNORECASE)

    def __init__(self, basestring):
        PersistentIdentifier.__init__(self, "issn", basestring, [], "https://www.worldcat.org/ISSN")

    def _validate_and_initialize(self):

        issn = re.split(':| ', self.init_value).pop()
        m = self.get_idpattern().match(issn)
        if m:
            self.unformatted = issn
            self.id = 'issn:%s-%s' % (self.unformatted[:4], self.unformatted[-4:])
            self.formatted.append(self.unformatted)
            self.resolvableurl = '%s/%s' % (self.resolver, self.unformatted)
            self.typedVariants.add(self.id)
            self.typedVariants.add(self.unformatted)
            self.typedVariants.add('%s%s' % (self.unformatted[:4], self.unformatted[-4:]))
            self.typedVariants.add('%s-%s' % (self.unformatted[:4], self.unformatted[-4:]))
            self.valid = True

    def __str__(self):
        return self.get_init_value()
