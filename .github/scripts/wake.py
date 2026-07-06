import playwright.sync_api as pw

url = "https://wasylakgolfpoolapp.streamlit.app/"

with pw.sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle", timeout=120000)

    wake_btn = page.locator("text=get this app back up")
    if wake_btn.is_visible(timeout=5000):
        print("App was asleep -- clicking wake-up button...")
        wake_btn.click()
        page.wait_for_load_state("networkidle", timeout=60000)

    print(f"App is alive: {page.title()}")
    browser.close()
