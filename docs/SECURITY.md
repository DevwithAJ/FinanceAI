# Security Notes

Implemented:
- PBKDF2 password hashing through Werkzeug
- Session-based authentication
- HTTP-only session cookie
- SameSite=Lax session cookie
- Form CSRF token
- Basic login attempt throttling
- Server-side input validation
- User-owned history checks before viewing/deleting
- 2 MB request-size limit
- Secrets/config separated into `.env`
- No passwords are stored in plaintext

Before public deployment:
- Change `SECRET_KEY`
- Set `FLASK_DEBUG=0`
- Serve behind HTTPS
- Set `SESSION_COOKIE_SECURE=1`
- Use a production WSGI server
- Configure secure MySQL credentials if using MySQL
- Add reverse-proxy security headers and production rate limiting
- Review privacy/data-retention requirements before storing real financial data
