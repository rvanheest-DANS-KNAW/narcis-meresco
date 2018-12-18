import re

from persistentidentifier import PersistentIdentifier


class Handle(PersistentIdentifier):
    ID_PATTERN = re.compile(r"^[^/]+(\.[^/]+)*/.+$")

    # Valid handles: "info:hdl/20.1000/100", "20.1000/100", "2381/12345", "http://hdl.handle.net/10.1000/182", "hdl:4263537/4000", "http://handle.net/10.1000/182", "https://doi.org/20.1000/100"
    # Handles may consist of any printable characters from the Universal Character Set of ISO/IEC 10646, which is the exact character set defined by Unicode

    def __init__(self, basestring):
        PersistentIdentifier.__init__(self, "handle", basestring,
                                      ["http://hdl.handle.net/", "https://hdl.handle.net/", "hdl:"],
                                      "https://hdl.handle.net/")

    def _validate_and_initialize(self):

        m = self.get_idpattern().match(self.init_value)
        if m:
            handle = re.split('/|hdl:|handle:', self.init_value)
            if len(handle) > 1:
                self.unformatted = '/'.join(handle[-2:])
                self.id = "hdl:" + self.unformatted
                self.formatted.append(self.unformatted)
                self.resolvableurl = self.resolver + self.unformatted
                for prefix in self.prefixes:
                    for suffix in self.formatted:
                        self.typedVariants.add(prefix + suffix)
                self.typedVariants.add(self.unformatted)
                self.typedVariants.add(self.init_value)
                self.valid = True

    def __str__(self):
        return self.get_init_value()
