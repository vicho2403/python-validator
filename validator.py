from .exceptions import ValidationException
from .validation_rule import ValidationRule


class Validator:
    def __init__(self, object_to_validate=None, rules=None, **kwargs):
        """
        :param object_to_validate: Object to validate
        :type object_to_validate: dict
        :param rules: Rules to apply
        :type rules: dict
        """

        if type(object_to_validate) is not dict:
            raise TypeError('_object must be dict')

        if type(rules) is not dict:
            raise TypeError('_rules must be dict')

        validate = kwargs.get('validate', True)
        raise_exception = kwargs.get('validate', True)

        self.rules = rules
        self.object = object_to_validate
        self._raise_exception = raise_exception

        if validate:
            self.validate()

    def validate(self):
        options = self.rules

        for option in options.items():
            attribute = option[0].split('|')
            nickname = None
            if len(attribute) == 2:
                nickname = attribute[1]

            attribute = attribute[0]

            rules = option[1].split('|')
            for rule in rules:
                if rule in ['', None]:
                    continue
                
                if rule.split(':')[0] not in ValidationRule.__rules__:
                    raise ValueError('Rule `%s` does not exist' % rule)

                if rule != 'required':
                    if attribute not in self.object:
                        continue

                name = rule
                value = self.object.get(attribute)
                if attribute in self.object:
                    if ':' in rule:
                        name = rule.split(':')[0]
                        value = rule.split(':')[1], value

                field = attribute if not nickname else nickname
                validation_rule = ValidationRule(name, field, value, _object=self.object)
                validation_rule.execute()

                if validation_rule.has_error and self._raise_exception:
                    raise Exception('Error in function `%s`: %s' % (
                        validation_rule.error['function'],
                        validation_rule.error['details'],
                    ))

                if validation_rule.failed and self._raise_exception:
                    raise ValidationException(
                        attribute,
                        'Error de validación: %s - %s' % (
                            validation_rule.result['function'],
                            validation_rule.result['details'],
                        )
                    )
