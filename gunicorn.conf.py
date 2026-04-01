"""
Gunicorn configuration for Paris Subventions API
Optimized for 100 concurrent users on 512MB RAM
"""
import os
import multiprocessing

# Get port from environment or use default
bind = f"0.0.0.0:{os.environ.get('PORT', '8010')}"

# Worker configuration
# Using sync workers for CPU-bound JSON processing
# Formula: (2 x $num_cores) + 1, but constrained by memory
workers = int(os.environ.get('WEB_CONCURRENCY', 4))

# Threads per worker for handling I/O wait
threads = int(os.environ.get('GUNICORN_THREADS', 2))

# Worker class - sync is fine for our use case (no long-polling)
worker_class = "sync"

# Worker timeout (30 seconds)
timeout = 30

# Keep-alive connections
keepalive = 2

# Maximum requests per worker (to prevent memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Preload app for memory efficiency (workers share memory)
preload_app = True

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.environ.get('LOG_LEVEL', 'info')

# Process naming
proc_name = "paris-subventions"

# Server mechanics
daemon = False
pidfile = None

# SSL (handled by platform, not Gunicorn)
forwarded_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

def on_starting(server):
    """Log startup configuration"""
    print(f"Starting Gunicorn with {workers} workers, {threads} threads each")
    print(f"Total concurrent capacity: ~{workers * threads * 10} requests")

def worker_int(worker):
    """Handle worker interruption"""
    print(f"Worker {worker.pid} received SIGINT or SIGQUIT")

def on_exit(server):
    """Log shutdown"""
    print("Gunicorn server shutting down")