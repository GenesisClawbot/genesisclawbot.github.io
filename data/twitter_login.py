import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    print("Navigating to x.com...")
    page.goto('https://x.com', timeout=60000)
    
    print("Waiting for page to load...")
    page.wait_for_timeout(5000)
    
    print("Page title:", page.title())
    
    # Check if already logged in
    if "Home / X" in page.title() or page.query_selector('[data-testid="primaryColumn"]'):
        print("Already logged in!")
    else:
        print("Need to log in...")
        # Click Sign In button
        signin_btn = page.query_selector('a[href="/login"]')
        if signin_btn:
            signin_btn.click()
            page.wait_for_timeout(3000)
        
        # Enter email
        email_input = page.query_selector('input[autocomplete="username"]')
        if email_input:
            email_input.fill('clawgenesis@gmail.com')
            page.wait_for_timeout(1000)
            
            # Click Next
            next_btn = page.query_selector('button:has-text("Next")')
            if next_btn:
                next_btn.click()
                page.wait_for_timeout(2000)
        
        # Enter password
        password_input = page.query_selector('input[name="password"]')
        if password_input:
            password_input.fill('ClawbotPassword1!')
            page.wait_for_timeout(1000)
            
            # Click Login
            login_btn = page.query_selector('button:has-text("Log in")')
            if login_btn:
                login_btn.click()
                page.wait_for_timeout(5000)
    
    print("Final page title:", page.title())
    
    # Take screenshot
    page.screenshot(path='/workspace/data/twitter_logged_in.png', full_page=True)
    print("Screenshot saved to /workspace/data/twitter_logged_in.png")
    
    # Save cookies
    cookies = context.cookies()
    with open('/workspace/data/twitter_browser_cookies.json', 'w') as f:
        json.dump(cookies, f, indent=2)
    print(f'Saved {len(cookies)} cookies to /workspace/data/twitter_browser_cookies.json')
    
    browser.close()
