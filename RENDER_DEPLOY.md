# FinanceAI — Render Deployment

1. Push this project folder to a GitHub repository. Do not commit `.env`.
2. In Render choose **New > Web Service** and connect the repository.
3. Render can detect `render.yaml`. If entering settings manually use:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. Environment values are defined in `render.yaml`, including a generated `SECRET_KEY`.
5. Deploy and open the generated `onrender.com` URL.

## Database note
The current default is SQLite at `instance/financeai.db`. This is suitable for a demo, but Render's normal web-service filesystem is ephemeral, so records can be lost on redeploy/restart. For persistent production data, configure a persistent database (for example, a supported MySQL host using the existing MYSQL_* settings) or adapt the app for Render Postgres.

## Model note
Keep the `models/` directory in Git. The loan-risk `.pkl` model is required by the application.
