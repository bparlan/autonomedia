import os

class Settings:
    BASE_BROWSER_DATA_DIR = os.getenv("BROWSER_DATA_DIR", "./runtime/browser_profiles")
    MASTODON_URL = os.getenv("MASTODON_URL", "https://mastodon.social")

settings = Settings()
