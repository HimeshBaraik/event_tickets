# app/core/email_templates.py

def forgot_password_template(username: str, reset_link: str) -> tuple[str, str]:
    subject = "Reset Your Password"

    body = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi {username},</p>
            <p>Click below to reset your password:</p>
            <a href="{reset_link}">Reset Password</a>
            <p>This link will expire in 10 minutes.</p>
        </body>
    </html>
    """
    return subject, body


def booking_success_template(username: str, ticket_id: str, event_name: str) -> tuple[str, str]:
    subject = "🎟️ Booking Confirmed!"

    body = f"""
    <html>
        <body>
            <h2>Booking Successful</h2>
            <p>Hi {username},</p>
            <p>Your ticket has been confirmed.</p>

            <ul>
                <li><b>Event:</b> {event_name}</li>
                <li><b>Ticket ID:</b> {ticket_id}</li>
            </ul>

            <p>Enjoy your event! 🎉</p>
        </body>
    </html>
    """
    return subject, body