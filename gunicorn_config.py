# gunicorn_config.py

bind = '127.0.0.1:8000'  # Bind to localhost on port 8000
workers = 3  # Adjust based on your server's CPU cores
timeout = 60
