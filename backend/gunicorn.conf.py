# Gunicorn configuration for Render
import os

# Bind to the port Render provides
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Number of workers
workers = 4

# Worker class (uvicorn for async)
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout
timeout = 120

# Log level
loglevel = "info"

# Access log
accesslog = "-"

# Error log
errorlog = "-"