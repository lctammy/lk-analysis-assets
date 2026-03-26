"""Take individual chart screenshots from eid_9929_explorer.html for Notion."""
from playwright.sync_api import sync_playwright
import os

HTML_PATH = os.path.join(os.path.dirname(__file__), "eid_9929_explorer.html")
OUT_DIR = os.path.join(os.path.dirname(__file__), "_charts_notion")
os.makedirs(OUT_DIR, exist_ok=True)

# Each screenshot: (filename, CSS selector or element ID, optional description)
SHOTS = [
    # Section 3: Cancel breakdown (3 tabs)
    ("eid9929_cancel_by_plan.png", "#cancel-view-plan", "Cancel by Plan tab"),
    ("eid9929_cancel_by_payment.png", "#cancel-view-payment", "Cancel by Trial/Direct tab"),
    ("eid9929_cancel_by_cross.png", "#cancel-view-cross", "Cancel by Plan×Payment tab"),
    # Section 3: W0 retention chart
    ("eid9929_w0_ret_plan.png", "#w0-ret-plan-chart", "W0 Retention by plan chart"),
    # Section 3: Plan delta chart
    ("eid9929_plan_delta.png", "#plan-delta-chart", "Key deltas by plan chart"),
    # Section 4: Segment delta table
    ("eid9929_seg_delta.png", "#seg-delta-table", "Segment delta pivot table"),
    # Section 6: PTR by position
    ("eid9929_ptr_pos.png", "#ptr-pos-chart", "PTR by position chart"),
    # Section 6: Bathroom PTR
    ("eid9929_bathroom_ptr.png", "#bathroom-ptr-chart", "Bathroom PTR by segment"),
    # Section 7: Last play monthly + yearly
    ("eid9929_lastplay_monthly.png", "#last-play-monthly-chart", "Last play monthly"),
    ("eid9929_lastplay_yearly.png", "#last-play-yearly-chart", "Last play yearly"),
    # Section 8: Anna position
    ("eid9929_anna_ctrl.png", "#anna-ctrl", "Anna Control position"),
    ("eid9929_anna_varb.png", "#anna-treat", "Anna VarB position"),
    # Section 8: Source chart
    ("eid9929_source_share.png", "#source-chart", "MF % of total plays"),
    # Section 9: Session start
    ("eid9929_session_source.png", "#session-source-chart", "First play source"),
    ("eid9929_first_mf_game.png", "#first-mf-game-chart", "First MF game"),
    # Section 10: Sticker vs bathroom
    ("eid9929_sticker_dur.png", "#sticker-dur-chart", "Duration distribution"),
    ("eid9929_sticker_loading.png", "#sticker-metrics-chart", "Loading time"),
    # Section 11: Cancel vs retained charts
    ("eid9929_cancel_monthly.png", "#cancel-monthly-chart", "Cancel games monthly"),
    ("eid9929_cancel_yearly.png", "#cancel-yearly-chart", "Cancel games yearly"),
    ("eid9929_cancel_source.png", "#cancel-source-chart", "Cancel source dist"),
    # Section 12: Trial/Direct charts
    ("eid9929_trial_monthly.png", "#trial-monthly-chart", "Trial monthly chart"),
    ("eid9929_trial_yearly.png", "#trial-yearly-chart", "Trial yearly chart"),
    ("eid9929_replay_rate.png", "#replay-rate-chart", "Replay rate chart"),
    # Section 13: Replay charts
    ("eid9929_replay_ctrl.png", "#replay-ctrl-chart", "Replay ctrl chart"),
    ("eid9929_replay_varb.png", "#replay-varb-chart", "Replay varb chart"),
    # Section 6: Jaccard chart
    ("eid9929_jaccard.png", "#jaccard-chart", "Content diversity"),
    # Section 1: Progressive drill-down (3 levels)
    ("eid9929_drilldown.png", "#drilldown-card", "Progressive drill-down"),
    ("eid9929_drill_L1.png", "#drill-L1", "Drill-down Level 1"),
    ("eid9929_drill_L2.png", "#drill-L2", "Drill-down Level 2"),
    ("eid9929_drill_L3.png", "#drill-L3", "Drill-down Level 3"),
]

# Also take screenshots of full tables that are small enough
TABLE_SHOTS = [
    ("eid9929_cancel_top_games.png", ".grid-2:has(#cancel-top-ctrl)", "Cancel top games 2x2"),
    ("eid9929_trial_direct_table.png", "#trial-direct-table", "Trial/Direct detail table"),
    ("eid9929_replay_compare.png", "#replay-compare-table", "Replay comparison table"),
    ("eid9929_sticker_table.png", "#sticker-table", "Sticker behavior table"),
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1400, "height": 900}, device_scale_factor=2)
    page.goto(f"file://{HTML_PATH}")
    page.wait_for_timeout(2000)  # Wait for JS rendering

    # Hide fixed header and sidebar so they don't overlay screenshots
    page.evaluate("""() => {
        document.querySelector('.top-bar').style.display = 'none';
        document.querySelector('.sidebar').style.display = 'none';
        document.querySelector('.main').style.marginLeft = '0';
        document.querySelector('.main').style.marginTop = '0';
    }""")

    # Show all hidden cancel tabs so we can screenshot them
    page.evaluate("""() => {
        document.getElementById('cancel-view-payment').style.display = '';
        document.getElementById('cancel-view-cross').style.display = '';
    }""")

    # Force redraw canvases after layout reflow from hiding header/sidebar
    page.evaluate("if (typeof drawDrillDown === 'function') drawDrillDown();")
    page.wait_for_timeout(500)

    taken = 0
    failed = []

    for fname, selector, desc in SHOTS + TABLE_SHOTS:
        try:
            el = page.query_selector(selector)
            if el:
                el.screenshot(path=os.path.join(OUT_DIR, fname))
                taken += 1
                print(f"  OK: {fname} ({desc})")
            else:
                failed.append((fname, f"Selector not found: {selector}"))
                print(f"  MISS: {fname} - selector not found")
        except Exception as e:
            failed.append((fname, str(e)))
            print(f"  ERR: {fname} - {e}")

    browser.close()

print(f"\nDone: {taken} screenshots taken, {len(failed)} failed")
if failed:
    for f, reason in failed:
        print(f"  FAILED: {f} - {reason}")
