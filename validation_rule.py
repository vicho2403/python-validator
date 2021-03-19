class ValidationRule:
    __rules__ = [
        'required',
        'required_if',
        'str',
        'equals_to',
        'starts_with',
        'ends_with',
        'int',
        'bool',
        'max',
        'min',
        'in',
    ]

    def __init__(self, name, attribute, *args, **kwargs):
        """
        :param name: Name of the function to call
        :type name: string
        :param attribute: Attribute to test
        :type attribute: int|bool|str
        :param args: Arguments containing additional data required for test
        :type args: int|bool|str
        """

        if name not in self.__rules__:
            raise ValueError('Rule `%s` does not exist' % name)

        self.name = name
        self.attribute = attribute
        self.value = args
        self.failed = False
        self.has_error = False
        self.object = kwargs.get('_object')

    def execute(self):
        return self.__getattribute__('_' + self.name)()

    def _required(self):
        self.failed = not self.value[0] not in ['', None]
        if self.failed:
            self.__set_failure('"%s" no puede ser vacío')

    def _required_if(self):
        self.value = self.value[0]
        if len(self.value) < 2:
            self.error = {
                'function': 'required_if',
                'details': 'rule `%s` expect 2 positional argument but %d were given.' % ('required_if', len(self.value))
            }
            self.has_error = True
            return None

        if self.object is None:
            self.error = {
                'function': 'required_if',
                'details': 'object attribute is `None`, `dict` type expected' % ('required_if', len(self.value))
            }
            self.has_error = True
            return None

        field, value = self.value

        # print({'field': field, 'value': value})

        if self.object.get(field) not in ['', None]:
            self.value = value
        else:
            self.failed = True
            if self.failed:
                self.__set_failure('"%s" no puede ser vacío')

    def _int(self):
        self.failed = not type(self.value[0]) is int
        if self.failed:
            self.__set_failure('"%s" debe ser de tipo numérico')

    def _str(self):
        self.failed = not type(self.value[0]) is str
        if self.failed:
            self.__set_failure('"%s" debe ser de tipo texto')

    def _bool(self):
        self.failed = not type(self.value[0]) is bool
        if self.failed:
            self.__set_failure('"%s" debe ser de tipo booleano')

    def _max(self):
        validation = self.__validate_number('max')
        if validation is None:
            return None

        value_set, value = validation
        if type(value) is str:
            value = len(value)

        self.failed = not (value_set > value or value_set == value)

        if self.failed:
            self.__set_failure('"%s" debe ser menor o igual a ' + str(value_set))

    def _min(self):
        validation = self.__validate_number('min')
        if validation is None:
            return None

        value_set, value = validation
        if type(value) is str:
            value = len(value)

        self.failed = not (value_set < value or value_set == value)

        if self.failed:
            self.__set_failure('"%s" debe ser mayor o igual a ' + str(value_set))

    def _equals_to(self):
        value_set, value = self.value[0]
        self.failed = not str(value) == value_set
        if self.failed:
            self.__set_failure('"%s" debe ser igual a ' + str(value_set))
            
    def _starts_with(self):
        value_set, value = self.value[0]
        self.failed = not str(value).startswith(value_set)
        if self.failed:
            self.__set_failure('"%s" debe empezar con ' + str(value_set))
    
    def _ends_with(self):
        value_set, value = self.value[0]
        self.failed = not str(value).endswith(value_set)
        if self.failed:
            self.__set_failure('"%s" debe terminar con ' + str(value_set))

    def _in(self):
        value_set, value = self.value[0]
        value_set_list = list(map(lambda x: x.strip().lower(), value_set.split(',')))
        if isinstance(value, list):
            for i in value:
                self.failed = not str(i).lower() in value_set_list
        else:
            self.failed = not str(value).lower() in list(map(lambda x: x.strip().lower(), value_set.split(',')))

        if self.failed:
            self.__set_failure('"%s" debe estar entre las siguientes opciones: ' + str(value_set))

    def __validate_number(self, caller):
        self.value = self.value[0]
        if len(self.value) < 2:
            self.error = {
                'function': 'max',
                'details': 'rule `%s` expect 2 positional argument but %d were given.' % (caller, len(self.value))
            }
            self.has_error = True
            return None
        try:
            value_set = int(self.value[0])
        except ValueError:
            self.error = {
                'function': 'max',
                'details': 'rule `%s` expect first argument to be integer' % caller
            }
            self.has_error = True
            return None

        return value_set, self.value[1]

    def __set_failure(self, reason):
        self.result = {
            'function': self.name,
            'value': self.value,
            'details': reason % self.attribute
        }
