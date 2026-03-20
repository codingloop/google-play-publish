class ConfigValidationError(Exception):
    """Raised when the configuration file is missing required fields or has invalid values."""
    pass


class CredentialsError(Exception):
    """Raised when Google Play credentials cannot be decrypted or loaded."""
    pass


class PublishError(Exception):
    """Raised when the publish workflow fails at any stage."""
    pass
