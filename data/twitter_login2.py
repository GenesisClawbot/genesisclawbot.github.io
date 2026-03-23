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
    print("Looking for sign in link...")
    page.click('a[href="/login"]', timeout=5000)
    page.wait_for_timeout(2000)
    print("After click title:", page.title())
    
    # Enter email
    print("Looking for email input...")
    page.fill('input[autocomplete="username"]', 'clawgenesis@gmail.com', timeout=5000)
    page.wait_for_timeout(1000)
    
    # Click Next
    print("Clicking Next...")
    page.click('button:has-text("Next")', timeout=5000)
    page.wait_for_timeout(2000)
    print("After Next title:", page.title())
    
    # Enter password
    print("Looking for password input...")
    page.fill('input[name="password"]', 'ClawbotPassword1!', timeout=5000)
    page.wait_for_timeout(1000)
    
    # Click Log in
    print("Clicking Log in...")
    page.click('button:has-text("Log in")', timeout=5000)
    page.wait_for_timeout(5000)
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
