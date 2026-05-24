import pytest
import time
from playwright.sync_api import Page, expect

def test_crud_operations(page: Page):
    # Use unique ID to avoid collision with existing rows
    test_id = str(int(time.time()))
    topic = f"UI Test Topic {test_id}"
    updated_topic = f"Updated Topic {test_id}"

    # Navigate to dashboard
    page.goto("http://127.0.0.1:8000")

    # 1. Test Add Content
    page.fill("input[name='topic']", topic)
    page.fill("input[name='link_url']", "https://test.com")
    page.fill("input[name='source_idea']", "Test source idea content")
    page.click("button:has-text('Add Content')")
    
    # Verify row created
    expect(page.get_by_text(topic)).to_be_visible()

    # 2. Test Edit Content
    # Click the edit button for the specific row
    row = page.locator(f"tr:has-text('{topic}')")
    row.locator("button[title='Edit']").click()
    
    # Update fields (scoped to the edit form)
    edit_form = page.locator("form[hx-post*='/save-row/']")
    edit_form.locator("input[name='topic']").fill(updated_topic)
    
    # Save (scoped to the edit form)
    edit_form.locator("button:has-text('Save')").click()
    
    # Wait for network activity to settle
    page.wait_for_load_state("networkidle")
    
    # Verify updated row is visible
    expect(page.locator(f"tr:has-text('{updated_topic}')")).to_be_visible()

    # 3. Test Delete Content (with confirmation)
    page.on("dialog", lambda dialog: dialog.accept()) # Automatically click "OK" on confirm
    page.click(f"tr:has-text('{updated_topic}') button[title='Delete']")
    
    # Verify deleted
    expect(page.get_by_text(updated_topic)).not_to_be_visible()
