class BaseAppException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NotFoundException(BaseAppException):
    pass


class ConflictException(BaseAppException):
    pass


class ForbiddenException(BaseAppException):
    pass


class UnauthorizedException(BaseAppException):
    pass
