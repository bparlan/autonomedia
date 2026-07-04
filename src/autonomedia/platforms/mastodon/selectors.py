from playwright.async_api import Locator, Page


def compose_textbox(page: Page) -> Locator:
    return page.get_by_role("textbox")
