class PersistentIdentifier(object):
    ID_PATTERN = None

    def __init__(self, name, init_value, prefixes=[], resolver=None):
        self.name = name  # Name of the Identifier (lowercase). doi, urnnbn, hdl, arxiv, etc. 1::1
        self.prefixes = prefixes  # List of 'known' base string prefixes. 0::n
        self.resolver = resolver  # default resolver, if available
        # instance vars:
        self.resolvableurl = None  # resolvable URL.
        self.init_value = init_value  # Initial value used to construct the PersistentIdentifier. 1::1
        self.unformatted = None  # Unformatted 'id' string, without resolver part: 07193555x, 0000000123456789, 000000021694233x, etc. 1::1 (no case correction)
        self.id = None  # 'Fully qualified name' or 'preferred' variant to be stored into the index/database.
        self.formatted = []  # List of 'known' string variations (formatted): 0000 0001 3333 4444, 0000-0001-3333-4444, 0000#0001#3333#4444 etc. 0::n
        self.typedVariants = set()  # List of all possible 'valid' persistentidentifier string configurations. 1::n
        self.valid = False  # Is the given Pid-value valid according to the type and our format check?
        self._validate_and_initialize()  # Match the constructor to the PID validity checks and generate the typedVariants.

    def get_name(self):
        return self.name

    def get_classname(self):
        return self.__class__.__name__

    def get_init_value(self):
        return self.init_value

    def get_unformatted_id(self):  # Unformatted 'id' string, without resolver part
        return self.unformatted

    def get_idx_id(self):
        return self.id

    def get_resolver(self):
        return self.resolvableurl

    def is_valid(self):
        return self.valid

    def _validate_and_initialize(self):
        raise NotImplementedError("Subclasses should implement this.")

    def get_typedvariants(self):
        return self.typedVariants

    def __str__(self):
        return '%s (%s)' % (self.name, self.init_value)

    @classmethod
    def get_idpattern(cls):
        return cls.ID_PATTERN
