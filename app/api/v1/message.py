from enum import Enum

class UserMessages(str, Enum):
    USER_NOT_FOUND = "User not found"
    INVALID_CREDENTIALS = "Invalid credentials"
    USER_CREATED = "User created successfully"
    USER_UPDATED = "User updated successfully"
    USER_DELETED = "User deleted successfully"
    EMAIL_ALREADY_EXISTS = "Email already exists"

class AuthMessages(str, Enum):
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = "Logout successful"
    TOKEN_EXPIRED = "Token expired"
    INVALID_TOKEN = "Invalid token"
    REFRESH_TOKEN_ISSUED = "Refresh token issued"

class BookTicketMessages(str, Enum):
    EVENT_NOT_FOUND = "Event not found"
    TICKET_NOT_FOUND = "Ticket not found"
    TICKET_UNAVAILABLE = "Ticket not available"
    TICKET_RESERVED = "Ticket reserved temporarily"
    TICKET_CONFIRMED = "Ticket reservation confirmed"
    RESERVATION_EXPIRED = "Reservation expired"