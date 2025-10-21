class LoginError(Exception):
    def __init__(self, message="Failed to login"):
        super().__init__(message)


class NumberNotFound(Exception):
    def __init__(self, message="No number provided. Plz provide number in whatsapp_login(number=)"):
        super().__init__(message)


class CountryNotFound(Exception):
    def __init__(self, message="No number provided. Plz provide country in the whatsapp_login(country=)"):
        super().__init__(message)


class QRNotScanned(Exception):
    def __init__(self, message="QR scan failed."):
        super().__init__(message)


class PageNotFound(Exception):
    def __init__(self, message="Page not found. Check Browser Integration and page init and try again"):
        super().__init__(message)


class ChatsNotFound(Exception):
    def __init__(self, message="Chats not found."):
        super().__init__(message)


class MessageTypeError(Exception):
    def __init__(self, message="Message type not found."):
        super().__init__(message)


class MessageNotFound(Exception):
    def __init__(self, message="Message not found."):
        super().__init__(message)
