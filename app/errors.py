class BadRequestError(Exception):
    """Client sent invalid data"""
    pass

class UnauthorizedError(Exception):
    """Authentication failed or missing"""
    pass
