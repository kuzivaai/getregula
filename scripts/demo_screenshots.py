#!/usr/bin/env python3
"""
Capture dashboard demo screenshots using Playwright.

Usage:
    # Start the API server first:
    python3 scripts/api_server.py --port 18497 &
    sleep 2

    # Then run this script:
    python3 scripts/demo_screenshots.py
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = Path(__file__).parent.parent / "docs" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

DASHBOARD_URL = "http://localhost:18497/v1/dashboard"
VIEWPORT = {"width": 1280, "height": 800}


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=2,  # Retina-quality screenshots
        )
        page = context.new_page()

        # ---- 1. Overview (empty state) ----
        print("[1/5] Capturing overview (empty state)...")
        page.goto(DASHBOARD_URL)
        page.wait_for_load_state("networkidle")
        # Wait for API health check to resolve (green dot)
        page.wait_for_function(
            "document.getElementById('apiDot').className.includes('dot-green')",
            timeout=10000,
        )
        time.sleep(0.5)  # Let CSS transitions settle
        page.screenshot(
            path=str(SCREENSHOTS_DIR / "dashboard-overview.png"),
            full_page=False,
        )
        print(f"  -> {SCREENSHOTS_DIR / 'dashboard-overview.png'}")

        # ---- 2. Self-Assessment questionnaire ----
        print("[2/5] Capturing self-assessment questionnaire...")
        # Click the "Self-Assessment" nav item
        page.click('[data-view="questionnaire"]')
        time.sleep(0.3)
        page.screenshot(
            path=str(SCREENSHOTS_DIR / "dashboard-questionnaire.png"),
            full_page=False,
        )
        print(f"  -> {SCREENSHOTS_DIR / 'dashboard-questionnaire.png'}")

        # ---- 3. Self-Assessment with answers and score ----
        print("[3/5] Capturing assessment result...")
        # Click Yes on all 4 Article 9 questions
        # The question blocks are inside the first card (Article 9)
        # Each question has Yes/No/Unsure buttons
        # We'll use JS to set answers and click buttons

        # Get all q-btn elements and click Yes on Article 9 (first 4 questions)
        question_blocks = page.query_selector_all(".question-block")

        # Article 9 questions (indices 0-3): click "Yes"
        for i in range(4):
            yes_btn = question_blocks[i].query_selector(".q-btn")  # First button is "Yes"
            yes_btn.click()
            time.sleep(0.1)

        # Article 10 first question (index 4): click "No"
        no_btn = question_blocks[4].query_selector_all(".q-btn")[1]  # Second button is "No"
        no_btn.click()
        time.sleep(0.1)

        # Click "Evaluate Governance Readiness"
        page.click("text=Evaluate Governance Readiness")
        time.sleep(0.5)

        # Scroll to show the result
        page.evaluate("document.getElementById('assessmentResult').scrollIntoView({block: 'center'})")
        time.sleep(0.3)

        page.screenshot(
            path=str(SCREENSHOTS_DIR / "dashboard-assessment-result.png"),
            full_page=False,
        )
        print(f"  -> {SCREENSHOTS_DIR / 'dashboard-assessment-result.png'}")

        # ---- 4. Enforcement Timeline ----
        print("[4/5] Capturing enforcement timeline...")
        page.click('[data-view="timeline"]')
        time.sleep(0.3)
        page.screenshot(
            path=str(SCREENSHOTS_DIR / "dashboard-timeline.png"),
            full_page=False,
        )
        print(f"  -> {SCREENSHOTS_DIR / 'dashboard-timeline.png'}")

        # ---- 5. Export Reports ----
        print("[5/5] Capturing export reports...")
        page.click('[data-view="export"]')
        time.sleep(0.3)
        page.screenshot(
            path=str(SCREENSHOTS_DIR / "dashboard-export.png"),
            full_page=False,
        )
        print(f"  -> {SCREENSHOTS_DIR / 'dashboard-export.png'}")

        browser.close()

    print(f"\nDone. {len(list(SCREENSHOTS_DIR.glob('*.png')))} screenshots saved to {SCREENSHOTS_DIR}/")


if __name__ == "__main__":
    main()
