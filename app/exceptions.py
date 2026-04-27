class SMSClientError(Exception):
    pass


class ConfigError(SMSClientError):
    """Ошибки конфигурации"""

    pass


class NetworkError(SMSClientError):
    """Ошибки сетевого взаимодействия"""

    pass


class ValidationError(SMSClientError):
    """Ошибки валидации данных"""

    pass


class AuthenticationError(SMSClientError):
    """Ошибки аутентификации"""

    pass


class HTTPMessageError(SMSClientError):
    """Базовое исключение для ошибок HTTP сообщений"""

    pass


class HTTPRequestError(HTTPMessageError):
    """Ошибки при работе с HTTP запросами"""

    pass


class HTTPResponseError(HTTPMessageError):
    """Ошибки при работе с HTTP ответами"""

    pass


class PhoneNumberError(ValidationError):
    """Ошибки, связанные с номером телефона"""

    pass


class MessageError(ValidationError):
    """Ошибки, связанные с текстом сообщения"""

    pass


class SerializationError(SMSClientError):
    """Ошибки сериализации/десериализации данных"""

    pass
