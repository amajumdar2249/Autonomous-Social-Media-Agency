# -*- coding: utf-8 -*-
"""
Social Media Automation Pipeline v6.1 — CLI Runner
===================================================
A clean, modular runner script that orchestrates the
autonomous content pipeline using the agency package.
"""

import sys
import time
from agency.logger import get_logger
from agency.scraper import fetch_all_news
from agency.generator import filter_and_score, generate_posts
from agency.telegram import send_post, send_approval_buttons, wait_for_approval
from agency.dedup import mark_processed, log_pipeline_run

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

log = get_logger("main")

def run_pipeline():
    log.info("=" * 55)
    log.info("  AI AGENCY PIPELINE v6.1 — Voice Engine CLI")
    log.info("=" * 55)
    
    # 1. Fetch News
    log.info("Fetching news...")
    news = fetch_all_news(max_per_feed=3)
    if not news:
        log.warning("No news found.")
        return
    log.info(f"Found {len(news)} fresh topics.")
    
    # 2. Filter & Score
    scored = filter_and_score(news)
    if not scored:
        log.info("No topics passed the virality threshold. Retry next cycle.")
        log_pipeline_run(len(news), 0, 0, "no_topics")
        return
    
    # 3. Pick Best Topic
    best = scored[0]
    log.info(f"BEST TOPIC: {best['title'][:50]}... (Score: {best['score']}/10)")
    
    # 4. Generate 4 Posts
    log.info("Generating 4 viral angle posts...")
    posts = generate_posts(best['title'], best['summary'])
    if not posts:
        log.error("Failed to generate posts.")
        return
    
    # 5. Send to Telegram
    log.info(f"Sending {len(posts)} posts to Telegram...")
    for p in posts:
        send_post(p["post_number"], p["angle"], best["title"], p["text"])
        time.sleep(0.5)
    
    # 6. Send Approval Buttons
    log.info("Sending approval buttons...")
    if not send_approval_buttons(best["title"], len(posts)):
        log.error("Failed to send approval buttons.")
        return
    
    # 7. Wait for Approval
    selected = wait_for_approval(timeout_minutes=60)
    
    if selected and selected > 0:
        chosen = next((p for p in posts if p["post_number"] == selected), None)
        if chosen:
            log.info(f"POST {selected} — {chosen['angle']} APPROVED!")
            print("\n" + "="*50)
            print(f"APPROVED POST ({chosen['angle']}):")
            print("="*50)
            print(chosen["text"])
            print("="*50 + "\n")
        mark_processed(best["title"], approved=True)
        log_pipeline_run(len(news), len(scored), len(posts), f"approved_post_{selected}")
    elif selected == -1:
        log.info("All posts rejected by user.")
        mark_processed(best["title"], approved=False)
        log_pipeline_run(len(news), len(scored), len(posts), "rejected")
    else:
        log.warning("No response received within timeout.")
        log_pipeline_run(len(news), len(scored), len(posts), "timeout")

if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        log.info("Pipeline execution interrupted by user.")
    except Exception as e:
        log.critical(f"Pipeline crashed with unhandled exception: {e}", exc_info=True)
