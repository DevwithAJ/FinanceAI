# Deployment Notes

## Local demo
Use SQLite and Flask development server.

## Production-style deployment
Do not use Flask's development server. A common Windows option is Waitress:

```powershell
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

For Linux, Gunicorn can be used instead.

Set:
- `FLASK_DEBUG=0`
- a strong random `SECRET_KEY`
- `SESSION_COOKIE_SECURE=1` behind HTTPS

For a hosted environment, keep the model `.pkl` files together with the exact `scikit-learn==1.8.0` dependency.
