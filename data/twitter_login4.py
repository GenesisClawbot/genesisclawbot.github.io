import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    
    print("Navigating to x.com...")
    page.goto('https://x.com', timeout=60000)
    page.wait_for_timeout(3000)
    print("Page title:", page.title())
    
    # Click Sign In
    print("Clicking sign in...")
    page.click('a[href="/login"]', timeout=5000)
    page.wait_for_timeout(3000)
    print("Title:", page.title())
    
    # Enter email in the input
    print("Entering email...")
    page.fill('input[type="text"]', 'clawgenesis@gmail.com')
    page.wait_for_timeout(2000)
    
    # Click Next
    print("Clicking Next...")
    page.click('button:has-text("Next")')
    page.wait_for_timeout(5000)
    print("After Next title:", page.title())
    
    # Check for errors or other elements
    error = page.query_selector('[data-testid="ErrorMessage"]')
    if error:
        print("Error:", error.inner_text())
    
    # Look for phone/username challenge
    inputs = page.query_selector_all('input')
    print(f"Found {len(inputs)} inputs now:")
    for i, inp in enumerate(inputs):
        print(f"  [{i}] type={inp.get_attribute('type')} name={inp.get_attribute('name')} autocomplete={inp.get_attribute('autocomplete')}")
    
    # If we're still on login page, try again with phone number or different flow
    if page.title() == "Log in to X / X":
        # Maybe X is asking for username instead of email, or asking for phone
        # Let's try clicking Next again or check what step we're on
        for inp in inputs:
            if inp.get_attribute('type') == 'text' or inp.get_attribute('type') == 'tel':
                inp.fill('clawgenesis@gmail.com')
                page.wait_for_timeout(1000)
        
        # Try another Next click
        btns = page.query_selector_all('button')
        for btn in btns:
            txt = btn.inner_text().lower()
            if 'next' in txt or 'continue' in txt:
                btn.click()
                page.wait_for_timeout(3000)
                break
        
        print("After 2nd Next title:", page.title())
    
    # Now look for password
    password_inputs = page.query_selector_all('input[type="password"]')
    if password_inputs:
        print("Found password input!")
        password_inputs[0].fill('ClawbotPassword1!')
        page.wait_for_timeout(1000)
        
        # Find login button
        for btn in page.query_selector_all('button'):
            txt = btn.inner_text().lower()
            if 'log in' in txt or 'sign in' in txt:
                btn.click()
                break
        
        page.wait_for_timeout(5000)
    else:
        print("No password field found yet")
    
    print("Final title:", page.title())
    
    # Take screenshot
    page.screenshot(path='/workspace/data/twitter_logged_in.png', full_page=True)
    print("Screenshot saved")
    
    # Save cookies
    cookies = context.cookies()
    with open('/workspace/data/twitter_browser_cookies.json', 'w') as f:
        json.dump(cookies, f, indent=2)
    print(f'Saved {len(cookies)} cookies')
    
    browser.close()
