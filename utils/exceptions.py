# utils/exceptions.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Custom Exceptions
=============================================================================
"""

class AmoriaError(Exception):
    """Base exception untuk semua error AMORIA"""
    def __init__(self, message: str, code: str = "AMORIA_ERROR", details=None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class ConfigurationError(AmoriaError):
    pass


class MissingAPIKeyError(ConfigurationError):
    pass


class DatabaseError(AmoriaError):
    pass


class ConnectionError(DatabaseError):
    pass


class AINotAvailableError(AmoriaError):
    pass


class AITimeoutError(AINotAvailableError):
    pass


class RegistrationNotFoundError(AmoriaError):
    pass


class CharacterNotFoundError(AmoriaError):
    pass


class SessionNotFoundError(AmoriaError):
    pass


class RoleNotFoundError(AmoriaError):
    pass


class IntimacyLevelError(AmoriaError):
    pass


class StaminaTooLowError(AmoriaError):
    pass


class ValidationError(AmoriaError):
    pass


class InvalidCommandError(ValidationError):
    pass


class BackupError(AmoriaError):
    pass


class BackupNotFoundError(BackupError):
    pass


__all__ = [
    'AmoriaError',
    'ConfigurationError',
    'MissingAPIKeyError',
    'DatabaseError',
    'ConnectionError',
    'AINotAvailableError',
    'AITimeoutError',
    'RegistrationNotFoundError',
    'CharacterNotFoundError',
    'SessionNotFoundError',
    'RoleNotFoundError',
    'IntimacyLevelError',
    'StaminaTooLowError',
    'ValidationError',
    'InvalidCommandError',
    'BackupError',
    'BackupNotFoundError',
]
