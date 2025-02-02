class BotError(Exception):
    """Base exception for bot errors"""
    pass

class DownloadError(BotError):
    """Raised when download fails"""
    pass

class RateLimitError(BotError):
    """Raised when rate limit exceeded"""
    pass

class AuthError(BotError):
    """Raised for authentication errors"""
    pass

class SecurityError(BotError):
    """Raised for security violations"""
    pass

class ValidationError(BotError):
    """Raised for invalid input"""
    pass

def handle_error(error: Exception) -> str:
    """Convert exceptions to user-friendly messages"""
    if isinstance(error, DownloadError):
        return "❌ Download failed. Please try again later."
    elif isinstance(error, RateLimitError):
        return "⚠️ Too many requests. Please wait a moment."
    elif isinstance(error, AuthError):
        return "🔒 Authentication failed. Please login again."
    elif isinstance(error, SecurityError):
        return "⚠️ Security check failed. Operation denied."
    elif isinstance(error, ValidationError):
        return f"❌ Invalid input: {str(error)}"
    else:
        return "❌ An unexpected error occurred."
