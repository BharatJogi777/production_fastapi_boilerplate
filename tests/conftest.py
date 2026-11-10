import os
os.environ.setdefault("SECRET_KEY","test-only-secret-key-that-is-long-enough-123456")
os.environ.setdefault("DATABASE_URL","sqlite+aiosqlite:///./test-bootstrap.db")
os.environ.setdefault("ALLOWED_HOSTS",'["testserver","localhost"]')
os.environ.setdefault("CORS_ORIGINS","[]")
os.environ.setdefault("APP_ENV","test")
