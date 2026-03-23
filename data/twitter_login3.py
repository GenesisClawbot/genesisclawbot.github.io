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
    page.wait_for_timeout(3000)
    print("After click title:", page.title())
    
    # Debug: list all inputs
    inputs = page.query_selector_all('input')
    print(f"Found {len(inputs)} inputs:")
    for i, inp in enumerate(inputs):
        print(f"  [{i}] type={inp.get_attribute('type')} name={inp.get_attribute('name')} autocomplete={inp.get_attribute('autocomplete')} placeholder={inp.get_attribute('placeholder')}")
    
    # Try first input
    if inputs:
        inputs[0].fill('clawgenesis@gmail.com')
        page.wait_for_timeout(1000)
        
        # Try to find and click a button
        buttons = page.query_selector_all('button')
        print(f"Found {len(buttons)} buttons")
        for i, btn in enumerate(buttons):
            txt = btn.inner_text()
            print(f"  [{i}] text={txt[:50]}")
        
        # Click first relevant button
        for btn in buttons:
            txt = btn.inner_text().lower()
            if 'next' in txt or 'weiter' in txt or 'email' in txt:
                btn.click()
                print(f"Clicked button: {btn.inner_text()}")
                break
        
        page.wait_for_timeout(2000)
        print("After button title:", page.title())
        
        # Now look for password
        password_inputs = page.query_selector_all('input[type="password"]')
        if password_inputs:
            print("Found password input!")
            password_inputs[0].fill('ClawbotPassword1!')
            page.wait_for_timeout(1000)
            
            # Find login button
            for btn in page.query_selector_all('button'):
                txt = btn.inner_text().lower()
                if 'log in' in txt or 'sign in' in txt or 'einloggen' in txt:
                    btn.click()
                    print(f"Clicked login button: {btn.inner_text()}")
                    break
            
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
