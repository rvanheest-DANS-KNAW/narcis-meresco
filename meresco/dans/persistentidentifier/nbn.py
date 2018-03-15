from re import compile, IGNORECASE

from persistentidentifier import PersistentIdentifier


class Nbn(PersistentIdentifier):

    ID_PATTERN = compile(r'^(?:.*?)([uU][rR][nN]:[nN][bB][nN]:[nN][lL](:([a-zA-Z]{2}))?:\d{2}-.+)', IGNORECASE)

    def __init__(self, basestring):
        PersistentIdentifier.__init__(self, "nbn", basestring, None, "http://www.persistent-identifier.nl")

    def _validate_and_initialize(self):

        m = self.get_idpattern().match(self.init_value)

        if m:
            self.unformatted = m.group(1)
            self.formatted.append(self.unformatted.lower())

            str_id = None
            if len(self.formatted) > 0:
                str_id = '%s' % (self.formatted[0])  # urn:nbn:nl:ui:13-jsk-7ek
                self.resolvableurl = '%s/%s' % (self.resolver, self.formatted[0])
                self.valid = True
            self.id = str_id

            self.typedVariants.update(self.formatted)
            self.typedVariants.add(self.init_value)

    def __str__(self):
        return self.get_init_value()
