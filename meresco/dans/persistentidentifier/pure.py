from re import compile, IGNORECASE

from persistentidentifier import PersistentIdentifier

class Pure(PersistentIdentifier):

    ID_PATTERN = compile("(?:.*?[^[0-9a-fA-F])?([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[89ab][0-9a-fA-F]{3}-[0-9a-fA-F]{12})$", IGNORECASE)

    def __init__(self, basestring):
        PersistentIdentifier.__init__(self, "pure", basestring, [])

    def _validate_and_initialize(self):

        uuid_match = Pure.ID_PATTERN.match(self.init_value)
        if uuid_match:
            # print uuid_match.group(1)
            self.unformatted = uuid_match.group(1)
            self.id = "pure:" + self.unformatted
            for prefix in self.prefixes:
                for suffix in self.formatted:
                    self.typedVariants.add(prefix + suffix)
            self.typedVariants.add(self.id)
            self.typedVariants.add(self.unformatted)
            self.valid = True

    def __str__(self):
        return self.get_init_value()