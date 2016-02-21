web: gunicorn -b "0.0.0.0:$PORT" -w 1 app:app
worker: python bg_worker.py