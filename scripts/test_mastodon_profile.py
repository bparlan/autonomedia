from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROFILE_PATH = (
    PROJECT_ROOT / "runtime" / "browser_profiles" / "mastodon"
)


def main() -> None:
    PROFILE_PATH.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_PATH),
            headless=False,
        )

        page = browser.new_page()

        page.goto("https://mastodon.social")

        input("Login manually, then press ENTER here...")

        browser.close()


if __name__ == "__main__":
    main()
