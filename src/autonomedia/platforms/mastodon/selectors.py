def compose_textbox(page: Page) -> Locator:
    return page.get_by_role("textbox")
