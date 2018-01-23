from persistentidentifier import PersistentIdentifier


class Unknown(PersistentIdentifier):
    ID_PATTERN = None

    def __init__(self, type, baseDigits):
        PersistentIdentifier.__init__(self, type, baseDigits)

    def _validate_and_initialize(self):

        if self.init_value.lower().startswith(self.name.lower() + ":"):
            self.unformatted = self.init_value[len(self.name) + 1:]
            self.id = '%s:%s' % (self.name.lower(), self.unformatted)
        else:
            self.unformatted = self.init_value
            self.id = self.name.lower() + ":" + self.init_value

        self.typedVariants.add(self.unformatted)
        self.typedVariants.add(self.id)

        self.valid = True  # Set to true, for we have no knowledge of validating this identifier, but we want to use it anyway.

    def __str__(self):
        return self.get_init_value()
