class ValidationException(Exception):
    __schema__ = 'ValidationException'

    def __init__(self, field: str, reason: str):
        self.field = field
        self.error_source = reason

    def create_response(self):
        return {
            'type': 'exception',
            'title': 'ValidationException',
            'message': 'Validacion del campo %s. %s' % (self.field, self.error_source)
        }
