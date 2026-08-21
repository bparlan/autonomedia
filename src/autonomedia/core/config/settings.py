import os


class Settings:
    BASE_BROWSER_DATA_DIR = os.getenv("BROWSER_DATA_DIR", "./runtime/browser_profiles")
    MASTODON_URL = os.getenv("MASTODON_URL", "https://mastodon.social")
    LINKEDIN_URL = os.getenv("LINKEDIN_URL", "https://www.linkedin.com")
    LINKEDIN_AUTH_TOKEN = os.getenv("LINKEDIN_AUTH_TOKEN")
    X_URL = os.getenv("X_URL", "https://x.com")
    X_AUTH_TOKEN = os.getenv("X_AUTH_TOKEN")
    MASTODON_AUTH_TOKEN = os.getenv("MASTODON_AUTH_TOKEN")


settings = Settings()
