import os

# Default local windows mysql assumed to have no password or 123456 or empty.
# If password is required, set DB_PASSWORD environment variable.
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "ycr270514")
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "sitp_hedging")

DB_URL = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

TORTOISE_ORM = {
    "connections": {
        "default": DB_URL
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai"
}
