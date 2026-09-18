# import time
# import random
# import uuid
# import datetime
# import re
# from playwright.sync_api import expect
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright
# import json
# import logging
# import traceback
# import sys
# import os

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     logging.error("Install GoLogin: pip install gologin")
#     exit(1)

# # Setup logging
# try:
#     # Clear existing handlers to avoid conflicts
#     for handler in logging.root.handlers[:]:
#         logging.root.removeHandler(handler)

#     # Get the directory where the script is running
#     log_dir = os.getcwd()
#     log_file = os.path.join(log_dir, 'bot.log')

#     # Configure logging to write to bot.log in the current directory and console
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         handlers=[
#             logging.FileHandler(log_file, mode='a'),  # Write to bot.log in current directory
#             logging.StreamHandler(sys.stdout)  # Also output to console
#         ]
#     )
#     logging.info(f"Logging to file: {log_file}")
#     logging.info(f"Current working directory: {os.getcwd()}")
# except Exception as e:
#     print(f"Failed to configure logging: {e}")
#     sys.exit(1)

# # Load config
# try:
#     with open('config.json', 'r') as f:
#         config = json.load(f)
#     tokens = config['tokens']
#     if not tokens:
#         logging.error("No tokens found in config.json")
#         sys.exit(1)
# except FileNotFoundError:
#     logging.error("config.json not found")
#     sys.exit(1)
# except json.JSONDecodeError:
#     logging.error("Invalid JSON in config.json")
#     sys.exit(1)

# current_token_idx = 0

# # ---------- CONFIG ----------
# TARGET_URLS = [
#     "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc",
# ]
# TOTAL_PROFILES = 100
# PAGE_LOAD_PATIENCE = (4, 8)
# HUMAN_BEHAVIOR_TIME = (15, 30)

# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# AIRPORT_CODES = {
#     "BLR": "Bengaluru",
#     "BOM": "Mumbai",
#     "DEL": "Delhi",
#     "CCU": "Kolkata",
#     "MAA": "Chennai",
#     "HYD": "Hyderabad",
#     "AMD": "Ahmedabad",
#     "PNQ": "Pune",
#     "GOI": "Goa",
#     "COK": "Kochi",
#     "IXC": "Chandigarh",
#     "IXJ": "Jammu",
#     "SXV": "Srinagar",
#     "GAU": "Guwahati",
#     "PAT": "Patna",
#     "NAG": "Nagpur",
#     "BBI": "Bhubaneswar",
#     "TRV": "Thiruvananthapuram",
#     "VNS": "Varanasi",
#     "ATQ": "Amritsar"
# }

# def is_results_page(url):
#     """Check if current page is results page"""
#     return ("/transport/flights/" in url and "/config/" not in url and "captcha" not in url.lower())

# def is_details_page(url):
#     """Check if current page is details page"""
#     return ("/transport/flights/" in url and "/config/" in url and "captcha" not in url.lower())

# def generate_random_flight_url():
#     """Generate random Skyscanner flight search URL"""
#     airports = list(AIRPORT_CODES.keys())
#     origin = random.choice(airports)
#     destination = random.choice([a for a in airports if a != origin])
    
#     days_ahead = random.randint(1, 90)
#     flight_date = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
#     date_str = flight_date.strftime("%y%m%d")
    
#     adults = random.randint(1, 4)
#     cabin_class = random.choice(["economy", "premium_economy", "business", "first"])
#     one_way = random.choice([True, False])
#     rtn = 0 if one_way else 1
    
#     flight_url = (
#         f"https://www.skyscanner.co.in/transport/flights/"
#         f"{origin.lower()}/{destination.lower()}/{date_str}/"
#         f"?adultsv2={adults}"
#         f"&cabinclass={cabin_class}"
#         f"&childrenv2="
#         f"&ref=home"
#         f"&rtn={rtn}"
#         f"&outboundaltsenabled=false"
#         f"&inboundaltsenabled=false"
#         f"&preferdirects=false"
#     )
    
#     logging.info(f"\nGenerated Flight Search:")
#     logging.info(f"   Route: {AIRPORT_CODES[origin]} -> {AIRPORT_CODES[destination]}")
#     logging.info(f"   Date: {flight_date.strftime('%d %b %Y')}")
#     logging.info(f"   Adults: {adults}, Class: {cabin_class}, {'One-way' if one_way else 'Round-trip'}")
#     logging.info(f"   URL: {flight_url}")
    
#     return flight_url

# def close_popup_safely(page: Page, preserve_url=None):
#     """Close popup while preserving current URL state"""
#     try:
#         logging.info("   Checking for popup...")
        
#         # Save current URL if provided
#         url_before = preserve_url or page.url
        
#         close_selectors = [
#             'button[aria-label="Close"]',
#             'button[title="Close"]', 
#             'button.BpkCloseButton_bpk-close-button__default__ZDA3N',
#             'button.BpkCloseButton_bpk-button__NDQyM',
#             'dialog button[type="button"]',
#         ]
        
#         for selector in close_selectors:
#             try:
#                 close_button = page.locator(selector).first
#                 if close_button.is_visible(timeout=2000):
#                     logging.info(f"   Popup detected! Closing with selector: {selector}")
                    
#                     # Click with force to avoid navigation
#                     close_button.click(timeout=3000, force=True, no_wait_after=True)
#                     time.sleep(0.5)
                    
#                     # Check if URL changed unexpectedly
#                     url_after = page.url
#                     if preserve_url and url_after != url_before:
#                         logging.info(f"   WARNING: URL changed during popup close!")
#                         logging.info(f"   Before: {url_before[:80]}")
#                         logging.info(f"   After: {url_after[:80]}")
                        
#                         # Try to go back to preserved URL
#                         if preserve_url in url_before:
#                             logging.info("   Attempting to restore URL...")
#                             try:
#                                 page.goto(url_before, timeout=30000, wait_until="domcontentloaded")
#                                 time.sleep(2)
#                             except:
#                                 pass
#                     else:
#                         logging.info("   Popup closed successfully")
                    
#                     return True
#             except:
#                 continue
        
#         logging.info("   No popup detected")
#         return False
        
#     except Exception as e:
#         logging.warning(f"   Popup check warning: {e}")
#         return False

# def find_select_button_on_results_page(page: Page):
#     """Find Select button on RESULTS page - FLIGHT CARD only"""
#     try:
#         logging.info(f"\n[RESULTS PAGE] Finding Select button...")
        
#         current_url = page.url
#         if not is_results_page(current_url):
#             logging.error(f"   ERROR: Not on results page! Current URL: {current_url[:80]}")
#             return None, None
        
#         logging.info(f"   ✓ Confirmed on results page")
        
#         button_found = False
#         button_element = None
        
#         # Strategy 1: Find buttons in flight card containers ONLY
#         logging.info("   Strategy 1: Looking for buttons in flight cards...")
#         try:
#             # Flight cards have specific parent containers
#             flight_cards = page.locator('div[data-testid*="flight"], div[class*="FlightCard"], div[class*="Ticket"]').all()
#             logging.info(f"   Found {len(flight_cards)} potential flight cards")
            
#             for idx, card in enumerate(flight_cards):
#                 try:
#                     # Find Select button within this card
#                     select_buttons = card.locator('button:has-text("Select"), a:has-text("Select")').all()
                    
#                     for btn in select_buttons:
#                         if btn.is_visible(timeout=3000):
#                             text = btn.inner_text(timeout=2000).strip().lower()
                            
#                             # CRITICAL: Exclude filter/checkbox buttons
#                             if text == 'select' and 'all' not in text:
#                                 # Verify it's clickable and has proper dimensions
#                                 try:
#                                     dimensions = btn.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
#                                     if dimensions['width'] > 50 and dimensions['height'] > 20:
#                                         logging.info(f"   ✓ Valid Select button found in card {idx}")
#                                         button_element = btn
#                                         button_found = True
#                                         break
#                                 except:
#                                     continue
                    
#                     if button_found:
#                         break
#                 except:
#                     continue
#         except Exception as e:
#             logging.warning(f"   Strategy 1 failed: {e}")
        
#         # Strategy 2: Look for primary action buttons with specific class patterns
#         if not button_found:
#             logging.info("   Strategy 2: Looking for primary action buttons...")
#             try:
#                 # These classes are specifically for flight selection, not filters
#                 primary_selectors = [
#                     'div[class*="TicketStub"] button.bpk-button--primary',
#                     'button.BpkButton_bpk-button__NDRjO.bpk-button--primary:not([class*="compact"])',
#                     'div[class*="ctaButton"] button',
#                 ]
                
#                 for selector in primary_selectors:
#                     buttons = page.locator(selector).all()
#                     logging.info(f"   Checking selector: {selector} ({len(buttons)} found)")
                    
#                     for btn in buttons:
#                         try:
#                             if btn.is_visible(timeout=3000):
#                                 text = btn.inner_text(timeout=2000).strip().lower()
                                
#                                 # Must be exactly "select" - not "select all"
#                                 if text == 'select':
#                                     # Check it's not in a filter/modal context
#                                     parent_html = btn.evaluate("el => el.parentElement.parentElement.className")
#                                     if 'filter' not in parent_html.lower() and 'checkbox' not in parent_html.lower():
#                                         dimensions = btn.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
#                                         if dimensions['width'] > 50:
#                                             logging.info(f"   ✓ Valid Select button found with selector: {selector}")
#                                             button_element = btn
#                                             button_found = True
#                                             break
#                         except:
#                             continue
                    
#                     if button_found:
#                         break
#             except Exception as e:
#                 logging.warning(f"   Strategy 2 failed: {e}")
        
#         if not button_found:
#             logging.info("   ✗ Select button NOT found on results page")
#             return None, None
        
#         return page, button_element
        
#     except Exception as e:
#         logging.error(f"   Error finding button on results page: {e}")
#         return None, None

# def find_select_button_on_details_page(page: Page):
#     """Find BEST Select button on DETAILS page - prioritize external links"""
#     try:
#         logging.info(f"\n[DETAILS PAGE] Finding Select button...")
        
#         current_url = page.url
#         if not is_details_page(current_url):
#             logging.error(f"   ERROR: Not on details page! Current URL: {current_url[:80]}")
#             return None, None
        
#         logging.info(f"   ✓ Confirmed on details page (has /config/)")
        
#         # Wait for AJAX content
#         logging.info("   Waiting for AJAX content...")
#         try:
#             page.wait_for_function(
#                 "() => document.querySelectorAll('.loading, .spinner').length === 0",
#                 timeout=20000
#             )
#             time.sleep(3)
#         except:
#             logging.info("   AJAX wait completed")
        
#         button_candidates = []
        
#         selectors = [
#             'div.PricedCta_ctaButton__OTZiN a.BpkButton_bpk-button__NDRjO.bpk-button--primary',
#             'div.PricedCta_ctaButton__OTZiN a[data-testid="pricing-item-redirect-button"]',
#             'a[data-testid="pricing-item-redirect-button"]',
#             'div.PricedCta_ctaButton__OTZiN a',
#             'a.BpkButton_bpk-button__NDRjO.bpk-button--primary',
#             'a.bpk-button--primary',
#         ]
        
#         # Collect ALL valid Select buttons
#         for selector in selectors:
#             try:
#                 logging.info(f"   Checking selector: {selector}")
#                 buttons = page.locator(selector).all()
                
#                 for button in buttons:
#                     try:
#                         if button.is_visible(timeout=5000):
#                             text = button.inner_text(timeout=2000).strip().lower()
#                             if 'select' in text:
#                                 # Get href if it's a link
#                                 try:
#                                     href = button.evaluate("el => el.href || ''")
#                                     tag = button.evaluate("el => el.tagName")
                                    
#                                     # Prioritize external links (not skyscanner domain)
#                                     has_external_href = href and 'http' in href and 'skyscanner' not in href
                                    
#                                     dimensions = button.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
#                                     if dimensions['width'] > 0 and dimensions['height'] > 0:
#                                         priority = 10 if has_external_href else 5
#                                         button_candidates.append({
#                                             'button': button,
#                                             'selector': selector,
#                                             'href': href,
#                                             'tag': tag,
#                                             'external': has_external_href,
#                                             'priority': priority
#                                         })
#                                         logging.info(f"   Found candidate: href={href[:60] if href else 'N/A'}, external={has_external_href}")
#                                 except:
#                                     continue
#                     except:
#                         continue
#             except:
#                 continue
        
#         if not button_candidates:
#             logging.info("   ✗ No Select buttons found on details page")
#             return None, None
        
#         # Sort by priority (external links first)
#         button_candidates.sort(key=lambda x: x['priority'], reverse=True)
        
#         logging.info(f"   Found {len(button_candidates)} Select button(s)")
#         best_candidate = button_candidates[0]
#         logging.info(f"   ✓ Using button with href: {best_candidate['href'][:80] if best_candidate['href'] else 'N/A'}")
#         logging.info(f"   External link: {best_candidate['external']}")
        
#         return page, best_candidate['button']
        
#     except Exception as e:
#         logging.error(f"   Error finding button on details page: {e}")
#         return None, None

# def remove_overlays_safely(page: Page):
#     """Aggressively remove ALL blocking overlays and scrims"""
#     try:
#         logging.info("   Removing overlays aggressively...")
#         removed_count = page.evaluate("""
#             () => {
#                 let count = 0;
                
#                 // Remove ALL scrim/overlay elements that block clicks
#                 const overlaySelectors = [
#                     'div.bpk-scrim',
#                     'div.bpk-scrim_bpk-scrim__NzY2M',
#                     'div[role="presentation"]',
#                     'div[class*="scrim"]',
#                     '.loading',
#                     '.spinner',
#                     'div[class*="overlay"]',
#                     'div[class*="backdrop"]',
#                 ];
                
#                 overlaySelectors.forEach(selector => {
#                     document.querySelectorAll(selector).forEach(el => {
#                         // Check if it's actually blocking something
#                         const rect = el.getBoundingClientRect();
#                         const zIndex = window.getComputedStyle(el).zIndex;
                        
#                         // If it's large and has high z-index, it's likely a blocker
#                         if ((rect.width > 100 || rect.height > 100) && (zIndex === 'auto' || parseInt(zIndex) > 100)) {
#                             el.remove();
#                             count++;
#                         }
#                     });
#                 });
                
#                 // Also remove modal-container contents if present
#                 const modalContainer = document.getElementById('modal-container');
#                 if (modalContainer) {
#                     // Don't remove the container itself, just problematic children
#                     modalContainer.querySelectorAll('div[role="presentation"]').forEach(el => {
#                         el.remove();
#                         count++;
#                     });
#                 }
                
#                 // Make ALL Select buttons accessible (not just visible ones)
#                 document.querySelectorAll('button, a').forEach(el => {
#                     const text = (el.textContent || '').toLowerCase().trim();
#                     if (text === 'select') {
#                         el.style.visibility = 'visible';
#                         el.style.opacity = '1';
#                         el.style.pointerEvents = 'auto';
#                         el.style.display = 'block';
#                     }
#                 });
                
#                 return count;
#             }
#         """)
#         logging.info(f"   Removed {removed_count} blocking elements")
#         time.sleep(1.5)
        
#         # Double-check and remove again if needed
#         try:
#             still_blocking = page.evaluate("""
#                 () => {
#                     const scrim = document.querySelector('div.bpk-scrim, div[role="presentation"][class*="scrim"]');
#                     if (scrim) {
#                         scrim.remove();
#                         return true;
#                     }
#                     return false;
#                 }
#             """)
#             if still_blocking:
#                 logging.info("   Removed additional scrim blocker")
#         except:
#             pass
            
#     except Exception as e:
#         logging.warning(f"   Overlay removal warning: {e}")

# def click_select_button(page: Page, page_type="results"):
#     """Click Select button with URL protection and new tab handling"""
#     try:
#         logging.info(f"\n{'='*60}")
#         logging.info(f"CLICKING SELECT BUTTON ON {page_type.upper()} PAGE")
#         logging.info(f"{'='*60}")
        
#         current_url = page.url
#         logging.info(f"Current URL: {current_url[:100]}...")
        
#         # Verify page type
#         if page_type == "results":
#             if not is_results_page(current_url):
#                 logging.error(f"   ERROR: Not on results page!")
#                 return False
#         elif page_type == "details":
#             if not is_details_page(current_url):
#                 logging.error(f"   ERROR: Not on details page!")
#                 return False
        
#         # Save URL before any operations
#         preserved_url = current_url
#         logging.info(f"   Preserved URL for protection")
        
#         # Get context for tab monitoring
#         context = page.context
#         initial_page_count = len(context.pages)
        
#         # Wait for page load
#         page.wait_for_load_state("domcontentloaded", timeout=60000)
#         time.sleep(random.uniform(3, 5))
        
#         # Close popup with URL protection
#         close_popup_safely(page, preserved_url)
#         time.sleep(1)
        
#         # Verify URL hasn't changed
#         if page.url != preserved_url:
#             logging.info(f"   WARNING: URL changed after popup close!")
#             logging.info(f"   Restoring to: {preserved_url[:80]}")
#             try:
#                 page.goto(preserved_url, timeout=30000, wait_until="domcontentloaded")
#                 time.sleep(3)
#             except:
#                 logging.warning("   Failed to restore URL")
#                 return False
        
#         # Remove overlays safely
#         remove_overlays_safely(page)
        
#         # Find button
#         if page_type == "results":
#             target_frame, button = find_select_button_on_results_page(page)
#         else:
#             target_frame, button = find_select_button_on_details_page(page)
        
#         if not button:
#             logging.info(f"   ✗ No Select button found!")
#             return False
        
#         # Scroll into view
#         logging.info("   Scrolling button into view...")
#         try:
#             button.scroll_into_view_if_needed(timeout=15000)
#             time.sleep(random.uniform(1.5, 2.5))
#         except Exception as e:
#             logging.warning(f"   Scroll warning: {e}")
        
#         # Verify URL again after scroll
#         if page.url != preserved_url:
#             logging.warning(f"   WARNING: URL changed after scroll!")
#             return False
        
#         # Get button details for debugging
#         try:
#             button_tag = button.evaluate("el => el.tagName")
#             button_href = button.evaluate("el => el.href || 'N/A'") if button_tag.lower() == 'a' else 'N/A'
#             button_onclick = button.evaluate("el => el.onclick ? 'has onclick' : 'no onclick'")
#             logging.info(f"   Button details: Tag={button_tag}, Href={button_href[:60] if button_href != 'N/A' else 'N/A'}, OnClick={button_onclick}")
#         except:
#             pass
        
#         logging.info("   Clicking Select button...")
#         click_success = False
        
#         # Set up popup/new tab listener
#         new_page_promise = None
#         if page_type == "details":
#             logging.info("   Setting up new tab listener...")
#             try:
#                 new_page_promise = context.expect_page(timeout=30000)
#             except:
#                 logging.warning("   New tab listener setup failed")
        
#         # Multiple click strategies with deeplink handling
#         for attempt in range(3):
#             logging.info(f"   Click attempt {attempt + 1}/3")
#             try:
#                 # Re-verify button is still present
#                 expect(button).to_be_visible(timeout=10000)
#                 expect(button).to_be_enabled(timeout=10000)
                
#                 # For deeplink URLs, use special handling
#                 if page_type == "details" and button_href and 'transport_deeplink' in button_href:
#                     logging.info(f"   Strategy: Deeplink click with extended wait")
#                     try:
#                         # Click and wait for redirect
#                         button.click(timeout=15000, force=True)
#                         click_success = True
#                         logging.info("   ✓ Deeplink click initiated")
                        
#                         # Wait longer for deeplink to redirect
#                         logging.info("   Waiting for deeplink redirect (up to 45s)...")
#                         start_wait = time.time()
#                         redirected = False
                        
#                         while time.time() - start_wait < 45:
#                             try:
#                                 current = page.url
#                                 # Check if redirected away from Skyscanner or to new page
#                                 if 'transport_deeplink' not in current and 'skyscanner.co.in/transport/flights/' not in current:
#                                     logging.info(f"   ✓ Redirected to: {current[:80]}")
#                                     redirected = True
#                                     break
#                             except:
#                                 pass
#                             time.sleep(1)
                        
#                         if not redirected:
#                             logging.info("   Deeplink redirect timeout, but click happened")
                        
#                         break
#                     except Exception as e:
#                         logging.warning(f"   Deeplink click failed: {str(e)[:80]}")
                
#                 # For details page with external href, try direct navigation
#                 elif page_type == "details" and button_tag and button_tag.lower() == 'a' and button_href and button_href != 'N/A' and 'http' in button_href and 'skyscanner' not in button_href:
#                     logging.info(f"   Strategy: Direct navigation to external href")
#                     try:
#                         target_url = button_href
#                         logging.info(f"   Target URL: {target_url[:80]}")
#                         page.goto(target_url, timeout=45000, wait_until="load")
#                         click_success = True
#                         logging.info("   ✓ Direct navigation successful")
#                         break
#                     except Exception as e:
#                         logging.warning(f"   Direct navigation failed: {str(e)[:80]}")
                
#                 # Try force click
#                 try:
#                     button.click(timeout=15000, force=True)
#                     click_success = True
#                     logging.info("   ✓ Force click successful")
#                     break
#                 except Exception as e:
#                     logging.warning(f"   Force click failed: {str(e)[:80]}")
                
#                 # Try normal click with mouse movement
#                 try:
#                     box = button.bounding_box(timeout=10000)
#                     if box:
#                         center_x = box['x'] + box['width'] / 2
#                         center_y = box['y'] + box['height'] / 2
#                         page.mouse.move(center_x, center_y, steps=random.randint(10, 20))
#                         time.sleep(random.uniform(0.3, 0.7))
#                         button.click(timeout=15000)
#                         click_success = True
#                         logging.info("   ✓ Mouse click successful")
#                         break
#                 except Exception as e:
#                     logging.warning(f"   Mouse click failed: {str(e)[:80]}")
                
#             except Exception as e:
#                 logging.warning(f"   Attempt {attempt + 1} failed: {str(e)[:100]}")
                
#                 # Don't retry if button disappeared (likely page changed)
#                 if 'not found' in str(e).lower():
#                     logging.info("   Button disappeared - likely page is changing")
#                     click_success = True  # Consider this a success
#                     time.sleep(5)
#                     break
                
#                 # Remove overlays again before next attempt
#                 if attempt < 2:
#                     logging.info("   Removing overlays again before retry...")
#                     remove_overlays_safely(page)
#                     time.sleep(2)
        
#         # JS Fallback with deeplink awareness
#         if not click_success:
#             logging.info("   Trying JavaScript approaches...")
            
#             # For deeplinks, try JS click with extended wait
#             if page_type == "details" and button_href and 'transport_deeplink' in button_href:
#                 try:
#                     logging.info("   JS: Clicking deeplink button...")
#                     button.evaluate("el => el.click()")
#                     click_success = True
#                     logging.info("   ✓ JS deeplink click successful")
                    
#                     # Wait for redirect
#                     logging.info("   Waiting for deeplink redirect...")
#                     time.sleep(10)
#                 except Exception as e:
#                     logging.warning(f"   JS deeplink click failed: {str(e)[:80]}")
            
#             # Try getting href and navigating
#             elif page_type == "details":
#                 try:
#                     href = button.evaluate("el => el.href")
#                     if href and 'http' in href:
#                         logging.info(f"   JS: Navigating to href: {href[:80]}")
#                         page.goto(href, timeout=45000, wait_until="load")
#                         click_success = True
#                         logging.info("   ✓ JS navigation successful")
#                     else:
#                         logging.info("   JS: No valid href found")
#                 except Exception as e:
#                     logging.warning(f"   JS href navigation failed: {str(e)[:80]}")
            
#             # Last resort: JS click
#             if not click_success:
#                 try:
#                     button.evaluate("el => el.click()")
#                     click_success = True
#                     logging.info("   ✓ JS click successful")
#                     time.sleep(5)
#                 except Exception as e:
#                     logging.warning(f"   JS click failed: {str(e)[:80]}")
        
#         if not click_success:
#             logging.info("   ✗ All click attempts failed!")
#             return False
        
#         # Wait for navigation - CRITICAL FIX with deeplink handling
#         logging.info("   Waiting for navigation to complete...")
        
#         # Check for new tab/popup (especially for details page)
#         active_page = page
#         new_tab_opened = False
        
#         if page_type == "details":
#             try:
#                 logging.info("   Checking for new tab (extended wait for deeplinks)...")
#                 # Wait longer for deeplink to potentially open tab
#                 max_tab_wait = 15  # Extended wait
#                 tab_check_start = time.time()
                
#                 while time.time() - tab_check_start < max_tab_wait:
#                     current_page_count = len(context.pages)
#                     if current_page_count > initial_page_count:
#                         new_tab_opened = True
#                         latest_page = context.pages[-1]
#                         logging.info(f"   ✓ New tab detected after {time.time() - tab_check_start:.1f}s!")
#                         logging.info(f"   New tab URL: {latest_page.url[:80]}")
                        
#                         # Switch to new tab
#                         active_page = latest_page
                        
#                         # Wait for new tab to load
#                         try:
#                             active_page.wait_for_load_state("load", timeout=30000)
#                             logging.info("   New tab loaded successfully")
#                         except:
#                             logging.info("   New tab still loading...")
#                             time.sleep(3)
#                         break
#                     time.sleep(1)
                
#                 if not new_tab_opened:
#                     logging.info("   No new tab detected after extended wait")
#             except Exception as e:
#                 logging.warning(f"   New tab check error: {e}")
        
#         # Wait for proper page load with multiple strategies
#         navigation_successful = False
        
#         # Strategy 1: Wait for load state
#         try:
#             active_page.wait_for_load_state("load", timeout=20000)
#             logging.info("   Page load state reached")
#             navigation_successful = True
#         except Exception as e:
#             logging.warning(f"   Load state timeout: {str(e)[:80]}")
        
#         # Strategy 2: Wait for network idle (skip for slow deeplinks)
#         if not ('transport_deeplink' in active_page.url):
#             try:
#                 active_page.wait_for_load_state("networkidle", timeout=20000)
#                 logging.info("   Network idle reached")
#                 navigation_successful = True
#             except Exception as e:
#                 logging.warning(f"   Network idle timeout: {str(e)[:80]}")
        
#         # Strategy 3: Wait for URL change (with deeplink awareness)
#         if not navigation_successful and not new_tab_opened:
#             logging.info("   Waiting for URL change...")
#             max_wait = 30  # Longer wait for deeplinks
#             start_wait = time.time()
#             url_changed = False
#             last_url = preserved_url
            
#             while time.time() - start_wait < max_wait:
#                 try:
#                     current = active_page.url
#                     if current != last_url:
#                         logging.info(f"   URL changed: {current[:80]}")
#                         last_url = current
#                         url_changed = True
                        
#                         # If moved away from deeplink, that's success
#                         if 'transport_deeplink' not in current and current != preserved_url:
#                             logging.info("   ✓ Moved away from deeplink")
#                             break
#                 except:
#                     pass
#                 time.sleep(1)
            
#             if url_changed:
#                 # Wait for page to stabilize
#                 time.sleep(3)
#                 try:
#                     active_page.wait_for_load_state("domcontentloaded", timeout=10000)
#                 except:
#                     pass
#                 navigation_successful = True
        
#         # Final wait
#         time.sleep(3)
        
#         new_url = active_page.url
#         logging.info(f"   Final URL: {new_url[:100]}...")
        
#         # If new tab opened, that's automatically a success for details page
#         if new_tab_opened and page_type == "details":
#             logging.info("   ✓ New tab opened - booking site loaded")
#             return True, active_page
        
#         # Verify navigation for same-page transitions
#         if page_type == "results":
#             if is_details_page(new_url):
#                 logging.info("   ✓ Successfully navigated to DETAILS page")
#                 return True, active_page
#             else:
#                 logging.info("   ⚠ Warning: Expected details page")
#                 if new_url != preserved_url:
#                     logging.info("   URL did change, checking validity...")
#                     time.sleep(5)
#                     final_url = active_page.url
#                     if is_details_page(final_url):
#                         logging.info("   ✓ Details page loaded after delay")
#                         return True, active_page
#                 return False, None
#         else:  # details page
#             # If new tab opened, that's success regardless of URL
#             if new_tab_opened:
#                 logging.info("   ✓ New tab opened (confirmed success)")
#                 return True, active_page
            
#             # Check if we're on external booking site
#             if 'skyscanner.co.in' not in new_url:
#                 logging.info("   ✓ Successfully navigated to external booking site")
#                 return True, active_page
            
#             # Check if moved away from details page
#             if not is_details_page(new_url):
#                 logging.info("   ✓ Successfully navigated away from details page")
#                 return True, active_page
            
#             # Still on details page - but maybe tab opened slowly
#             # Do one final comprehensive tab check
#             logging.info("   Final comprehensive tab check...")
#             time.sleep(3)
#             final_page_count = len(context.pages)
#             if final_page_count > initial_page_count:
#                 logging.info(f"   ✓ New tab detected in final check!")
#                 latest_page = context.pages[-1]
#                 latest_url = latest_page.url
#                 logging.info(f"   New tab URL: {latest_url[:80]}")
                
#                 # This is success!
#                 return True, latest_page
            
#             # Still on details page - check if URL changed at all
#             if new_url != preserved_url:
#                 logging.info("   URL changed within Skyscanner")
                
#                 # Check if it's a deeplink URL
#                 if 'transport_deeplink' in new_url:
#                     logging.info("   On deeplink page - waiting for external redirect...")
#                     time.sleep(10)
                    
#                     final_url = active_page.url
#                     logging.info(f"   Final check URL: {final_url[:100]}")
                    
#                     if 'skyscanner.co.in' not in final_url:
#                         logging.info("   ✓ Redirected to external site")
#                         return True, active_page
#                     else:
#                         logging.info("   ⚠ Still on Skyscanner after deeplink wait")
#                         # But check tabs one more time
#                         if len(context.pages) > initial_page_count:
#                             logging.info("   ✓ But new tab exists - SUCCESS!")
#                             return True, context.pages[-1]
#                         return True, active_page  # Consider success anyway
#                 else:
#                     logging.info("   Waiting for external redirect...")
#                     time.sleep(5)
                    
#                     final_check_url = active_page.url
#                     if not is_details_page(final_check_url):
#                         logging.info("   ✓ Redirect completed")
#                         return True, active_page
#                     else:
#                         logging.info("   ⚠ Still on details page")
#                         return True, active_page
#             else:
#                 logging.info("   URL did not change on main page")
#                 # Final desperate tab check
#                 if len(context.pages) > initial_page_count:
#                     logging.info("   ✓ But new tab was opened - SUCCESS!")
#                     return True, context.pages[-1]
                
#                 logging.info("   ✗ No navigation detected")
#                 return False, None
        
#     except Exception as e:
#         logging.error(f"   Error clicking button: {e}")
#         return False

# def parse_proxy_string(s: str):
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     global current_token_idx
#     while current_token_idx < len(tokens):
#         TOKEN = tokens[current_token_idx]
#         try:
#             gl = GoLogin({"token": TOKEN})
#             logging.info(f"Creating stealth profile: {profile_name}")
            
#             profile = gl.createProfileRandomFingerprint({
#                 "os": random.choice(["win", "mac"]),
#                 "name": profile_name,
#                 "webgl": {
#                     "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"]),
#                     "renderer": random.choice(["Intel Iris OpenGL Engine", "GeForce GTX 1650/PCIe/SSE2"])
#                 },
#                 "audioContext": {
#                     "enable": True,
#                     "noise": random.uniform(0.0001, 0.0005)
#                 }
#             })
            
#             if not profile or 'id' not in profile:
#                 raise Exception("Profile creation failed")
                
#             profile_id = profile['id']
#             logging.info(f"Profile created: {profile_id}")
            
#             if proxy_config:
#                 try:
#                     proxy_data = {
#                         "mode": proxy_config['type'],
#                         "host": proxy_config['host'],
#                         "port": int(proxy_config['port']),
#                         "username": proxy_config.get('username', ''),
#                         "password": proxy_config.get('password', '')
#                     }
#                     gl.changeProfileProxy(profile_id, proxy_data)
#                     logging.info(f"Proxy configured: {proxy_config['host']}")
#                 except Exception as e:
#                     logging.warning(f"Proxy setup warning: {e}")
            
#             return profile_id
            
#         except Exception as e:
#             logging.error(f"Error with token {current_token_idx}: {e}")
#             current_token_idx += 1
#             if current_token_idx >= len(tokens):
#                 logging.error("All tokens exhausted")
#                 return None
#             logging.info(f"Switching to next token {current_token_idx}")

# def start_maximum_stealth_browser(profile_id):
#     try:
#         gl = GoLogin({
#             "token": tokens[current_token_idx],
#             "profile_id": profile_id
#         })
#         logging.info(f"Starting browser for: {profile_id}")
#         debugger_address = gl.start()
        
#         time.sleep(random.uniform(3, 5))
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         context.set_extra_http_headers({
#             "DNT": "1",
#             "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
#         })
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         logging.error(f"Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     try:
#         logging.info("Injecting stealth...")
        
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
#         """)
        
#         logging.info("Stealth active")
        
#     except Exception as e:
#         logging.warning(f"Stealth injection warning: {e}")

# def handle_captcha_challenge(page: Page, max_retries=3):
#     """Handle CAPTCHA"""
#     for attempt in range(max_retries):
#         try:
#             logging.info(f"\nCAPTCHA Handler - Attempt {attempt + 1}/{max_retries}")
            
#             current_url = page.url
#             if "captcha" not in current_url.lower():
#                 return False
            
#             page.wait_for_load_state("load", timeout=30000)
#             time.sleep(3)
            
#             button_found = False
#             target_frame = page
#             button_element = None
            
#             # Search main page first
#             try:
#                 button_element = page.locator("text=/PRESS.*HOLD/i").first
#                 if button_element.is_visible(timeout=5000):
#                     button_found = True
#                     logging.info("Button found in main page")
#             except:
#                 pass
            
#             # Search in iframes
#             if not button_found:
#                 frames = page.frames
#                 for idx, frame in enumerate(frames):
#                     try:
#                         button_element = frame.locator("text=/PRESS.*HOLD/i").first
#                         if button_element.is_visible(timeout=5000):
#                             target_frame = frame
#                             button_found = True
#                             logging.info(f"Button found in frame {idx}")
#                             break
#                     except:
#                         continue
            
#             if not button_found:
#                 if attempt < max_retries - 1:
#                     time.sleep(5)
#                 continue
            
#             bounding_box = button_element.bounding_box()
#             if not bounding_box:
#                 continue
            
#             center_x = bounding_box['x'] + bounding_box['width'] / 2
#             center_y = bounding_box['y'] + bounding_box['height'] / 2
            
#             page.mouse.move(center_x, center_y, steps=25)
#             time.sleep(random.uniform(0.3, 0.6))
#             page.mouse.down()
            
#             hold_duration = 90
#             start_time = time.time()
            
#             while time.time() - start_time < hold_duration:
#                 elapsed = time.time() - start_time
                
#                 try:
#                     if "captcha" not in page.url.lower():
#                         logging.info(f"\nCAPTCHA solved after {elapsed:.1f}s")
#                         page.mouse.up()
#                         return True
#                 except:
#                     pass
                
#                 time.sleep(0.5)
            
#             page.mouse.up()
#             time.sleep(3)
            
#             if "captcha" not in page.url.lower():
#                 return True
                
#         except Exception as e:
#             logging.error(f"Attempt {attempt + 1} error: {e}")
#             if attempt < max_retries - 1:
#                 time.sleep(5)
    
#     return False

# def ultimate_human_browsing(page: Page):
#     try:
#         logging.info("Starting human behavior simulation...")
        
#         # Go to Google first
#         google_url = "https://www.google.co.in/"
#         logging.info(f"\nNavigating to Google: {google_url}")
        
#         for attempt in range(3):
#             try:
#                 page.goto(google_url, timeout=60000, wait_until="networkidle")
#                 break
#             except:
#                 if attempt == 2:
#                     return False
        
#         time.sleep(3)
        
#         for url in TARGET_URLS:
#             logging.info(f"\n{'='*60}")
#             logging.info(f"STEP 1: Affiliate URL")
#             logging.info(f"{'='*60}")
            
#             for attempt in range(3):
#                 try:
#                     page.goto(url, timeout=60000, wait_until="networkidle")
#                     break
#                 except:
#                     if attempt == 2:
#                         continue
            
#             time.sleep(random.uniform(5, 8))
            
#             if "captcha" in page.url.lower():
#                 if not handle_captcha_challenge(page):
#                     continue
            
#             # STEP 2: Flight search (RESULTS page)
#             logging.info(f"\n{'='*60}")
#             logging.info(f"STEP 2: Flight Search (RESULTS PAGE)")
#             logging.info(f"{'='*60}")
            
#             flight_loaded = False
            
#             for flight_attempt in range(3):
#                 logging.info(f"\nAttempt {flight_attempt + 1}/3")
                
#                 flight_url = generate_random_flight_url()
                
#                 for nav_attempt in range(3):
#                     try:
#                         page.goto(flight_url, timeout=60000, wait_until="networkidle")
#                         break
#                     except:
#                         if nav_attempt == 2:
#                             break
                
#                 time.sleep(random.uniform(5, 8))
                
#                 current_url = page.url
                
#                 if "captcha" in current_url.lower():
#                     if not handle_captcha_challenge(page):
#                         if flight_attempt < 2:
#                             continue
#                         else:
#                             break
                
#                 if not is_results_page(current_url):
#                     if flight_attempt < 2:
#                         continue
#                     else:
#                         break
                
#                 logging.info("✓ On RESULTS page")
                
#                 time.sleep(random.uniform(*PAGE_LOAD_PATIENCE))
                
#                 # STEP 3: First Select button (RESULTS -> DETAILS)
#                 logging.info(f"\n{'='*60}")
#                 logging.info(f"STEP 3: First Select Button")
#                 logging.info(f"{'='*60}")
                
#                 if click_select_button(page, "results"):
#                     time.sleep(3)
#                     new_url = page.url
#                     if is_details_page(new_url):
#                         logging.info("✓ Moved to DETAILS page")
#                         flight_loaded = True
#                         break
#                     elif is_results_page(new_url):
#                         logging.error("ERROR: Still on results page")
#                         if flight_attempt < 2:
#                             continue
#                 else:
#                     if flight_attempt < 2:
#                         continue
            
#             if not flight_loaded:
#                 logging.info("\n✗ Failed to reach details page")
#                 continue
            
#             # Now on DETAILS page
#             current_url = page.url
            
#             if not is_details_page(current_url):
#                 logging.error(f"ERROR: Not on details page!")
#                 continue
            
#             logging.info("✓ Confirmed on DETAILS page")
            
#             time.sleep(random.uniform(3, 6))
            
#             if "captcha" in page.url.lower():
#                 if not handle_captcha_challenge(page):
#                     continue
            
#             # Verify still on details page before second click
#             if not is_details_page(page.url):
#                 logging.error("ERROR: Lost details page before second click")
#                 continue
            
#             # STEP 4: Second Select button (DETAILS -> Booking)
#             logging.info(f"\n{'='*60}")
#             logging.info(f"STEP 4: Second Select Button")
#             logging.info(f"{'='*60}")
            
#             # Extra verification
#             logging.info(f"Pre-click URL check: {page.url[:80]}")
#             if not is_details_page(page.url):
#                 logging.error("ERROR: Not on details page before click!")
#                 continue
            
#             click_result = click_select_button(page, "details")
#             if isinstance(click_result, tuple):
#                 success, booking_page = click_result
#             else:
#                 success = click_result
#                 booking_page = page
            
#             if success:
#                 logging.info("✓ Second Select button clicked successfully")
                
#                 # Use the returned page (might be new tab)
#                 if booking_page and booking_page != page:
#                     logging.info(f"   Using new booking page for human behavior")
#                     final_page = booking_page
#                 else:
#                     final_page = page
                
#                 time.sleep(3)
                
#                 # Human behavior on final booking page
#                 human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#                 logging.info(f"\nFinal page human behavior for {human_time:.1f}s")
#                 logging.info(f"Final page URL: {final_page.url[:80]}")
                
#                 start_time = time.time()
#                 while time.time() - start_time < human_time:
#                     try:
#                         action = random.choice(['scroll', 'mouse_move', 'pause'])
                        
#                         if action == 'scroll':
#                             final_page.evaluate(f"window.scrollBy({{top: {random.randint(50, 150)}, behavior: 'smooth'}});")
#                         elif action == 'mouse_move':
#                             final_page.mouse.move(random.randint(100, 800), random.randint(100, 600))
#                         else:
#                             time.sleep(random.uniform(1, 3))
                        
#                         time.sleep(random.uniform(1, 2))
#                     except Exception as e:
#                         # Page might be closed or navigated
#                         logging.warning(f"   Human behavior warning: {str(e)[:50]}")
#                         break
                
#                 logging.info("✓ Human behavior completed on booking page")
#             else:
#                 logging.info("✗ Failed second click")
#                 continue
        
#         logging.info("\nHuman behavior complete")
#         return True
        
#     except Exception as e:
#         logging.error(f"Human browsing error: {e}")
#         logging.error(traceback.format_exc())
#         return False

# def run_ultimate_stealth_test():
#     logging.info("FIXED SKYSCANNER BOT WITH URL PROTECTION")
#     logging.info("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         logging.info(f"\n=== PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_flight_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             time.sleep(random.uniform(4, 8))
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         logging.info(f"\nPROFILE {profile_num} - SUCCESS!")
#                     else:
#                         logging.info(f"\nPROFILE {profile_num} - FAILED")
                    
#                     time.sleep(random.uniform(10, 20))
                  
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 logging.info(f"PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             logging.info(f"PROFILE {profile_num} - PROFILE CREATION FAILED")

#     logging.info(f"\n{'='*60}")
#     logging.info(f"TEST COMPLETE!")
#     logging.info(f"Success Rate: {successful_runs}/{TOTAL_PROFILES}")
#     logging.info(f"{'='*60}")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         logging.info("Browser session terminated")
#     except Exception as e:
#         logging.warning(f"Cleanup warning: {e}")

# if __name__ == "__main__":
#     logging.info("FIXED ANTI-BOT BYPASS WITH URL PROTECTION")
#     logging.info("=" * 60)

#     if not GOLOGIN_AVAILABLE:
#         logging.error("GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         logging.info("\nTest interrupted by user")
#     except Exception as e:
#         logging.error(f"Fatal error: {e}")
#         logging.error(traceback.format_exc())



import time
import random
import uuid
import datetime
import re
from playwright.sync_api import expect
from playwright.sync_api import sync_playwright, TimeoutError
from playwright.sync_api import Page, Browser, Playwright
import json
import logging
import traceback
import sys
import os

try:
    from gologin import GoLogin
    GOLOGIN_AVAILABLE = True
except ImportError:
    logging.error("Install GoLogin: pip install gologin")
    exit(1)

# Setup logging
try:
    # Clear existing handlers to avoid conflicts
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Get the directory where the script is running
    log_dir = os.getcwd()
    log_file = os.path.join(log_dir, 'bot.log')

    # Configure logging to write to bot.log in the current directory and console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a', encoding='utf-8'),  # UTF-8 added!
            logging.StreamHandler(sys.stdout)  # Also output to console
        ]
    )
    logging.info(f"Logging to file: {log_file}")
    logging.info(f"Current working directory: {os.getcwd()}")
except Exception as e:
    print(f"Failed to configure logging: {e}")
    sys.exit(1)

# Load config
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    tokens = config['tokens']
    if not tokens:
        logging.error("No tokens found in config.json")
        sys.exit(1)
except FileNotFoundError:
    logging.error("config.json not found")
    sys.exit(1)
except json.JSONDecodeError:
    logging.error("Invalid JSON in config.json")
    sys.exit(1)

current_token_idx = 0

# ---------- CONFIG ----------
TARGET_URLS = [
    "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc",
]
TOTAL_PROFILES = 200
PAGE_LOAD_PATIENCE = (4, 8)
HUMAN_BEHAVIOR_TIME = (15, 30)

PROXY_LIST = [
    "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
]

AIRPORT_CODES = {
    "BLR": "Bengaluru",
    "BOM": "Mumbai",
    "DEL": "Delhi",
    "CCU": "Kolkata",
    "MAA": "Chennai",
    "HYD": "Hyderabad",
    "AMD": "Ahmedabad",
    "PNQ": "Pune",
    "GOI": "Goa",
    "COK": "Kochi",
    "IXC": "Chandigarh",
    "IXJ": "Jammu",
    "SXV": "Srinagar",
    "GAU": "Guwahati",
    "PAT": "Patna",
    "NAG": "Nagpur",
    "BBI": "Bhubaneswar",
    "TRV": "Thiruvananthapuram",
    "VNS": "Varanasi",
    "ATQ": "Amritsar"
}

def is_results_page(url):
    """Check if current page is results page"""
    return ("/transport/flights/" in url and "/config/" not in url and "captcha" not in url.lower())

def is_details_page(url):
    """Check if current page is details page"""
    return ("/transport/flights/" in url and "/config/" in url and "captcha" not in url.lower())

def generate_random_flight_url():
    """Generate random Skyscanner flight search URL"""
    airports = list(AIRPORT_CODES.keys())
    origin = random.choice(airports)
    destination = random.choice([a for a in airports if a != origin])
    
    days_ahead = random.randint(1, 90)
    flight_date = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
    date_str = flight_date.strftime("%y%m%d")
    
    adults = random.randint(1, 4)
    cabin_class = random.choice(["economy", "premium_economy", "business", "first"])
    one_way = random.choice([True, False])
    rtn = 0 if one_way else 1
    
    flight_url = (
        f"https://www.skyscanner.co.in/transport/flights/"
        f"{origin.lower()}/{destination.lower()}/{date_str}/"
        f"?adultsv2={adults}"
        f"&cabinclass={cabin_class}"
        f"&childrenv2="
        f"&ref=home"
        f"&rtn={rtn}"
        f"&outboundaltsenabled=false"
        f"&inboundaltsenabled=false"
        f"&preferdirects=false"
    )
    
    logging.info(f"\nGenerated Flight Search:")
    logging.info(f"   Route: {AIRPORT_CODES[origin]} -> {AIRPORT_CODES[destination]}")
    logging.info(f"   Date: {flight_date.strftime('%d %b %Y')}")
    logging.info(f"   Adults: {adults}, Class: {cabin_class}, {'One-way' if one_way else 'Round-trip'}")
    logging.info(f"   URL: {flight_url}")
    
    return flight_url

def close_popup_safely(page: Page, preserve_url=None):
    """Close popup while preserving current URL state"""
    try:
        logging.info("   Checking for popup...")
        
        # Save current URL if provided
        url_before = preserve_url or page.url
        
        close_selectors = [
            'button[aria-label="Close"]',
            'button[title="Close"]', 
            'button.BpkCloseButton_bpk-close-button__default__ZDA3N',
            'button.BpkCloseButton_bpk-button__NDQyM',
            'dialog button[type="button"]',
        ]
        
        for selector in close_selectors:
            try:
                close_button = page.locator(selector).first
                if close_button.is_visible(timeout=2000):
                    logging.info(f"   Popup detected! Closing with selector: {selector}")
                    
                    # Click with force to avoid navigation
                    close_button.click(timeout=3000, force=True, no_wait_after=True)
                    time.sleep(0.5)
                    
                    # Check if URL changed unexpectedly
                    url_after = page.url
                    if preserve_url and url_after != url_before:
                        logging.info(f"   WARNING: URL changed during popup close!")
                        logging.info(f"   Before: {url_before[:80]}")
                        logging.info(f"   After: {url_after[:80]}")
                        
                        # Try to go back to preserved URL
                        if preserve_url in url_before:
                            logging.info("   Attempting to restore URL...")
                            try:
                                page.goto(url_before, timeout=30000, wait_until="domcontentloaded")
                                time.sleep(2)
                            except:
                                pass
                    else:
                        logging.info("   Popup closed successfully")
                    
                    return True
            except:
                continue
        
        logging.info("   No popup detected")
        return False
        
    except Exception as e:
        logging.warning(f"   Popup check warning: {e}")
        return False

def find_select_button_on_results_page(page: Page):
    """Find Select button on RESULTS page - FLIGHT CARD only"""
    try:
        logging.info(f"\n[RESULTS PAGE] Finding Select button...")
        
        current_url = page.url
        if not is_results_page(current_url):
            logging.error(f"   ERROR: Not on results page! Current URL: {current_url[:80]}")
            return None, None
        
        logging.info(f"   V Confirmed on results page")
        
        button_found = False
        button_element = None
        
        # Strategy 1: Find buttons in flight card containers ONLY
        logging.info("   Strategy 1: Looking for buttons in flight cards...")
        try:
            # Flight cards have specific parent containers
            flight_cards = page.locator('div[data-testid*="flight"], div[class*="FlightCard"], div[class*="Ticket"]').all()
            logging.info(f"   Found {len(flight_cards)} potential flight cards")
            
            for idx, card in enumerate(flight_cards):
                try:
                    # Find Select button within this card
                    select_buttons = card.locator('button:has-text("Select"), a:has-text("Select")').all()
                    
                    for btn in select_buttons:
                        if btn.is_visible(timeout=3000):
                            text = btn.inner_text(timeout=2000).strip().lower()
                            
                            # CRITICAL: Exclude filter/checkbox buttons
                            if text == 'select' and 'all' not in text:
                                # Verify it's clickable and has proper dimensions
                                try:
                                    dimensions = btn.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
                                    if dimensions['width'] > 50 and dimensions['height'] > 20:
                                        logging.info(f"   V Valid Select button found in card {idx}")
                                        button_element = btn
                                        button_found = True
                                        break
                                except:
                                    continue
                    
                    if button_found:
                        break
                except:
                    continue
        except Exception as e:
            logging.warning(f"   Strategy 1 failed: {e}")
        
        # Strategy 2: Look for primary action buttons with specific class patterns
        if not button_found:
            logging.info("   Strategy 2: Looking for primary action buttons...")
            try:
                # These classes are specifically for flight selection, not filters
                primary_selectors = [
                    'div[class*="TicketStub"] button.bpk-button--primary',
                    'button.BpkButton_bpk-button__NDRjO.bpk-button--primary:not([class*="compact"])',
                    'div[class*="ctaButton"] button',
                ]
                
                for selector in primary_selectors:
                    buttons = page.locator(selector).all()
                    logging.info(f"   Checking selector: {selector} ({len(buttons)} found)")
                    
                    for btn in buttons:
                        try:
                            if btn.is_visible(timeout=3000):
                                text = btn.inner_text(timeout=2000).strip().lower()
                                
                                # Must be exactly "select" - not "select all"
                                if text == 'select':
                                    # Check it's not in a filter/modal context
                                    parent_html = btn.evaluate("el => el.parentElement.parentElement.className")
                                    if 'filter' not in parent_html.lower() and 'checkbox' not in parent_html.lower():
                                        dimensions = btn.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
                                        if dimensions['width'] > 50:
                                            logging.info(f"   V Valid Select button found with selector: {selector}")
                                            button_element = btn
                                            button_found = True
                                            break
                        except:
                            continue
                    
                    if button_found:
                        break
            except Exception as e:
                logging.warning(f"   Strategy 2 failed: {e}")
        
        if not button_found:
            logging.info("   X Select button NOT found on results page")
            return None, None
        
        return page, button_element
        
    except Exception as e:
        logging.error(f"   Error finding button on results page: {e}")
        return None, None

def find_select_button_on_details_page(page: Page):
    """Find BEST Select button on DETAILS page - prioritize external links"""
    try:
        logging.info(f"\n[DETAILS PAGE] Finding Select button...")
        
        current_url = page.url
        if not is_details_page(current_url):
            logging.error(f"   ERROR: Not on details page! Current URL: {current_url[:80]}")
            return None, None
        
        logging.info(f"   V Confirmed on details page (has /config/)")
        
        # Wait for AJAX content
        logging.info("   Waiting for AJAX content...")
        try:
            page.wait_for_function(
                "() => document.querySelectorAll('.loading, .spinner').length === 0",
                timeout=20000
            )
            time.sleep(3)
        except:
            logging.info("   AJAX wait completed")
        
        button_candidates = []
        
        selectors = [
            'div.PricedCta_ctaButton__OTZiN a.BpkButton_bpk-button__NDRjO.bpk-button--primary',
            'div.PricedCta_ctaButton__OTZiN a[data-testid="pricing-item-redirect-button"]',
            'a[data-testid="pricing-item-redirect-button"]',
            'div.PricedCta_ctaButton__OTZiN a',
            'a.BpkButton_bpk-button__NDRjO.bpk-button--primary',
            'a.bpk-button--primary',
        ]
        
        # Collect ALL valid Select buttons
        for selector in selectors:
            try:
                logging.info(f"   Checking selector: {selector}")
                buttons = page.locator(selector).all()
                
                for button in buttons:
                    try:
                        if button.is_visible(timeout=5000):
                            text = button.inner_text(timeout=2000).strip().lower()
                            if 'select' in text:
                                # Get href if it's a link
                                try:
                                    href = button.evaluate("el => el.href || ''")
                                    tag = button.evaluate("el => el.tagName")
                                    
                                    # Prioritize external links (not skyscanner domain)
                                    has_external_href = href and 'http' in href and 'skyscanner' not in href
                                    
                                    dimensions = button.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
                                    if dimensions['width'] > 0 and dimensions['height'] > 0:
                                        priority = 10 if has_external_href else 5
                                        button_candidates.append({
                                            'button': button,
                                            'selector': selector,
                                            'href': href,
                                            'tag': tag,
                                            'external': has_external_href,
                                            'priority': priority
                                        })
                                        logging.info(f"   Found candidate: href={href[:60] if href else 'N/A'}, external={has_external_href}")
                                except:
                                    continue
                    except:
                        continue
            except:
                continue
        
        if not button_candidates:
            logging.info("   X No Select buttons found on details page")
            return None, None
        
        # Sort by priority (external links first)
        button_candidates.sort(key=lambda x: x['priority'], reverse=True)
        
        logging.info(f"   Found {len(button_candidates)} Select button(s)")
        best_candidate = button_candidates[0]
        logging.info(f"   V Using button with href: {best_candidate['href'][:80] if best_candidate['href'] else 'N/A'}")
        logging.info(f"   External link: {best_candidate['external']}")
        
        return page, best_candidate['button']
        
    except Exception as e:
        logging.error(f"   Error finding button on details page: {e}")
        return None, None

def remove_overlays_safely(page: Page):
    """Aggressively remove ALL blocking overlays and scrims"""
    try:
        logging.info("   Removing overlays aggressively...")
        removed_count = page.evaluate("""
            () => {
                let count = 0;
                
                // Remove ALL scrim/overlay elements that block clicks
                const overlaySelectors = [
                    'div.bpk-scrim',
                    'div.bpk-scrim_bpk-scrim__NzY2M',
                    'div[role="presentation"]',
                    'div[class*="scrim"]',
                    '.loading',
                    '.spinner',
                    'div[class*="overlay"]',
                    'div[class*="backdrop"]',
                ];
                
                overlaySelectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => {
                        // Check if it's actually blocking something
                        const rect = el.getBoundingClientRect();
                        const zIndex = window.getComputedStyle(el).zIndex;
                        
                        // If it's large and has high z-index, it's likely a blocker
                        if ((rect.width > 100 || rect.height > 100) && (zIndex === 'auto' || parseInt(zIndex) > 100)) {
                            el.remove();
                            count++;
                        }
                    });
                });
                
                // Also remove modal-container contents if present
                const modalContainer = document.getElementById('modal-container');
                if (modalContainer) {
                    // Don't remove the container itself, just problematic children
                    modalContainer.querySelectorAll('div[role="presentation"]').forEach(el => {
                        el.remove();
                        count++;
                    });
                }
                
                // Make ALL Select buttons accessible (not just visible ones)
                document.querySelectorAll('button, a').forEach(el => {
                    const text = (el.textContent || '').toLowerCase().trim();
                    if (text === 'select') {
                        el.style.visibility = 'visible';
                        el.style.opacity = '1';
                        el.style.pointerEvents = 'auto';
                        el.style.display = 'block';
                    }
                });
                
                return count;
            }
        """)
        logging.info(f"   Removed {removed_count} blocking elements")
        time.sleep(1.5)
        
        # Double-check and remove again if needed
        try:
            still_blocking = page.evaluate("""
                () => {
                    const scrim = document.querySelector('div.bpk-scrim, div[role="presentation"][class*="scrim"]');
                    if (scrim) {
                        scrim.remove();
                        return true;
                    }
                    return false;
                }
            """)
            if still_blocking:
                logging.info("   Removed additional scrim blocker")
        except:
            pass
            
    except Exception as e:
        logging.warning(f"   Overlay removal warning: {e}")

def click_select_button(page: Page, page_type="results"):
    """Click Select button with URL protection and new tab handling"""
    try:
        logging.info(f"\n{'='*60}")
        logging.info(f"CLICKING SELECT BUTTON ON {page_type.upper()} PAGE")
        logging.info(f"{'='*60}")
        
        current_url = page.url
        logging.info(f"Current URL: {current_url[:100]}...")
        
        # Verify page type
        if page_type == "results":
            if not is_results_page(current_url):
                logging.error(f"   ERROR: Not on results page!")
                return False
        elif page_type == "details":
            if not is_details_page(current_url):
                logging.error(f"   ERROR: Not on details page!")
                return False
        
        # Save URL before any operations
        preserved_url = current_url
        logging.info(f"   Preserved URL for protection")
        
        # Get context for tab monitoring
        context = page.context
        initial_page_count = len(context.pages)
        
        # Wait for page load
        page.wait_for_load_state("domcontentloaded", timeout=60000)
        time.sleep(random.uniform(3, 5))
        
        # Close popup with URL protection
        close_popup_safely(page, preserved_url)
        time.sleep(1)
        
        # Verify URL hasn't changed
        if page.url != preserved_url:
            logging.info(f"   WARNING: URL changed after popup close!")
            logging.info(f"   Restoring to: {preserved_url[:80]}")
            try:
                page.goto(preserved_url, timeout=30000, wait_until="domcontentloaded")
                time.sleep(3)
            except:
                logging.warning("   Failed to restore URL")
                return False
        
        # Remove overlays safely
        remove_overlays_safely(page)
        
        # Find button
        if page_type == "results":
            target_frame, button = find_select_button_on_results_page(page)
        else:
            target_frame, button = find_select_button_on_details_page(page)
        
        if not button:
            logging.info(f"   X No Select button found!")
            return False
        
        # Scroll into view
        logging.info("   Scrolling button into view...")
        try:
            button.scroll_into_view_if_needed(timeout=15000)
            time.sleep(random.uniform(1.5, 2.5))
        except Exception as e:
            logging.warning(f"   Scroll warning: {e}")
        
        # Verify URL again after scroll
        if page.url != preserved_url:
            logging.warning(f"   WARNING: URL changed after scroll!")
            return False
        
        # Get button details for debugging
        try:
            button_tag = button.evaluate("el => el.tagName")
            button_href = button.evaluate("el => el.href || 'N/A'") if button_tag.lower() == 'a' else 'N/A'
            button_onclick = button.evaluate("el => el.onclick ? 'has onclick' : 'no onclick'")
            logging.info(f"   Button details: Tag={button_tag}, Href={button_href[:60] if button_href != 'N/A' else 'N/A'}, OnClick={button_onclick}")
        except:
            pass
        
        logging.info("   Clicking Select button...")
        click_success = False
        
        # Set up popup/new tab listener
        new_page_promise = None
        if page_type == "details":
            logging.info("   Setting up new tab listener...")
            try:
                new_page_promise = context.expect_page(timeout=30000)
            except:
                logging.warning("   New tab listener setup failed")
        
        # Multiple click strategies with deeplink handling
        for attempt in range(3):
            logging.info(f"   Click attempt {attempt + 1}/3")
            try:
                # Re-verify button is still present
                expect(button).to_be_visible(timeout=10000)
                expect(button).to_be_enabled(timeout=10000)
                
                # For deeplink URLs, use special handling
                if page_type == "details" and button_href and 'transport_deeplink' in button_href:
                    logging.info(f"   Strategy: Deeplink click with extended wait")
                    try:
                        # Click and wait for redirect
                        button.click(timeout=15000, force=True)
                        click_success = True
                        logging.info("   V Deeplink click initiated")
                        
                        # Wait longer for deeplink to redirect
                        logging.info("   Waiting for deeplink redirect (up to 45s)...")
                        start_wait = time.time()
                        redirected = False
                        
                        while time.time() - start_wait < 45:
                            try:
                                current = page.url
                                # Check if redirected away from Skyscanner or to new page
                                if 'transport_deeplink' not in current and 'skyscanner.co.in/transport/flights/' not in current:
                                    logging.info(f"   V Redirected to: {current[:80]}")
                                    redirected = True
                                    break
                            except:
                                pass
                            time.sleep(1)
                        
                        if not redirected:
                            logging.info("   Deeplink redirect timeout, but click happened")
                        
                        break
                    except Exception as e:
                        logging.warning(f"   Deeplink click failed: {str(e)[:80]}")
                
                # For details page with external href, try direct navigation
                elif page_type == "details" and button_tag and button_tag.lower() == 'a' and button_href and button_href != 'N/A' and 'http' in button_href and 'skyscanner' not in button_href:
                    logging.info(f"   Strategy: Direct navigation to external href")
                    try:
                        target_url = button_href
                        logging.info(f"   Target URL: {target_url[:80]}")
                        page.goto(target_url, timeout=45000, wait_until="load")
                        click_success = True
                        logging.info("   V Direct navigation successful")
                        break
                    except Exception as e:
                        logging.warning(f"   Direct navigation failed: {str(e)[:80]}")
                
                # Try force click
                try:
                    button.click(timeout=15000, force=True)
                    click_success = True
                    logging.info("   V Force click successful")
                    break
                except Exception as e:
                    logging.warning(f"   Force click failed: {str(e)[:80]}")
                
                # Try normal click with mouse movement
                try:
                    box = button.bounding_box(timeout=10000)
                    if box:
                        center_x = box['x'] + box['width'] / 2
                        center_y = box['y'] + box['height'] / 2
                        page.mouse.move(center_x, center_y, steps=random.randint(10, 20))
                        time.sleep(random.uniform(0.3, 0.7))
                        button.click(timeout=15000)
                        click_success = True
                        logging.info("   V Mouse click successful")
                        break
                except Exception as e:
                    logging.warning(f"   Mouse click failed: {str(e)[:80]}")
                
            except Exception as e:
                logging.warning(f"   Attempt {attempt + 1} failed: {str(e)[:100]}")
                
                # Don't retry if button disappeared (likely page changed)
                if 'not found' in str(e).lower():
                    logging.info("   Button disappeared - likely page is changing")
                    click_success = True  # Consider this a success
                    time.sleep(5)
                    break
                
                # Remove overlays again before next attempt
                if attempt < 2:
                    logging.info("   Removing overlays again before retry...")
                    remove_overlays_safely(page)
                    time.sleep(2)
        
        # JS Fallback with deeplink awareness
        if not click_success:
            logging.info("   Trying JavaScript approaches...")
            
            # For deeplinks, try JS click with extended wait
            if page_type == "details" and button_href and 'transport_deeplink' in button_href:
                try:
                    logging.info("   JS: Clicking deeplink button...")
                    button.evaluate("el => el.click()")
                    click_success = True
                    logging.info("   V JS deeplink click successful")
                    
                    # Wait for redirect
                    logging.info("   Waiting for deeplink redirect...")
                    time.sleep(10)
                except Exception as e:
                    logging.warning(f"   JS deeplink click failed: {str(e)[:80]}")
            
            # Try getting href and navigating
            elif page_type == "details":
                try:
                    href = button.evaluate("el => el.href")
                    if href and 'http' in href:
                        logging.info(f"   JS: Navigating to href: {href[:80]}")
                        page.goto(href, timeout=45000, wait_until="load")
                        click_success = True
                        logging.info("   V JS navigation successful")
                    else:
                        logging.info("   JS: No valid href found")
                except Exception as e:
                    logging.warning(f"   JS href navigation failed: {str(e)[:80]}")
            
            # Last resort: JS click
            if not click_success:
                try:
                    button.evaluate("el => el.click()")
                    click_success = True
                    logging.info("   V JS click successful")
                    time.sleep(5)
                except Exception as e:
                    logging.warning(f"   JS click failed: {str(e)[:80]}")
        
        if not click_success:
            logging.info("   X All click attempts failed!")
            return False
        
        # Wait for navigation - CRITICAL FIX with deeplink handling
        logging.info("   Waiting for navigation to complete...")
        
        # Check for new tab/popup (especially for details page)
        active_page = page
        new_tab_opened = False
        
        if page_type == "details":
            try:
                logging.info("   Checking for new tab (extended wait for deeplinks)...")
                # Wait longer for deeplink to potentially open tab
                max_tab_wait = 15  # Extended wait
                tab_check_start = time.time()
                
                while time.time() - tab_check_start < max_tab_wait:
                    current_page_count = len(context.pages)
                    if current_page_count > initial_page_count:
                        new_tab_opened = True
                        latest_page = context.pages[-1]
                        logging.info(f"   V New tab detected after {time.time() - tab_check_start:.1f}s!")
                        logging.info(f"   New tab URL: {latest_page.url[:80]}")
                        
                        # Switch to new tab
                        active_page = latest_page
                        
                        # Wait for new tab to load
                        try:
                            active_page.wait_for_load_state("load", timeout=30000)
                            logging.info("   New tab loaded successfully")
                        except:
                            logging.info("   New tab still loading...")
                            time.sleep(3)
                        break
                    time.sleep(1)
                
                if not new_tab_opened:
                    logging.info("   No new tab detected after extended wait")
            except Exception as e:
                logging.warning(f"   New tab check error: {e}")
        
        # Wait for proper page load with multiple strategies
        navigation_successful = False
        
        # Strategy 1: Wait for load state
        try:
            active_page.wait_for_load_state("load", timeout=20000)
            logging.info("   Page load state reached")
            navigation_successful = True
        except Exception as e:
            logging.warning(f"   Load state timeout: {str(e)[:80]}")
        
        # Strategy 2: Wait for network idle (skip for slow deeplinks)
        if not ('transport_deeplink' in active_page.url):
            try:
                active_page.wait_for_load_state("networkidle", timeout=20000)
                logging.info("   Network idle reached")
                navigation_successful = True
            except Exception as e:
                logging.warning(f"   Network idle timeout: {str(e)[:80]}")
        
        # Strategy 3: Wait for URL change (with deeplink awareness)
        if not navigation_successful and not new_tab_opened:
            logging.info("   Waiting for URL change...")
            max_wait = 30  # Longer wait for deeplinks
            start_wait = time.time()
            url_changed = False
            last_url = preserved_url
            
            while time.time() - start_wait < max_wait:
                try:
                    current = active_page.url
                    if current != last_url:
                        logging.info(f"   URL changed: {current[:80]}")
                        last_url = current
                        url_changed = True
                        
                        # If moved away from deeplink, that's success
                        if 'transport_deeplink' not in current and current != preserved_url:
                            logging.info("   V Moved away from deeplink")
                            break
                except:
                    pass
                time.sleep(1)
            
            if url_changed:
                # Wait for page to stabilize
                time.sleep(3)
                try:
                    active_page.wait_for_load_state("domcontentloaded", timeout=10000)
                except:
                    pass
                navigation_successful = True
        
        # Final wait
        time.sleep(3)
        
        new_url = active_page.url
        logging.info(f"   Final URL: {new_url[:100]}...")
        
        # If new tab opened, that's automatically a success for details page
        if new_tab_opened and page_type == "details":
            logging.info("   V New tab opened - booking site loaded")
            return True, active_page
        
        # Verify navigation for same-page transitions
        if page_type == "results":
            if is_details_page(new_url):
                logging.info("   V Successfully navigated to DETAILS page")
                return True, active_page
            else:
                logging.info("   ⚠ Warning: Expected details page")
                if new_url != preserved_url:
                    logging.info("   URL did change, checking validity...")
                    time.sleep(5)
                    final_url = active_page.url
                    if is_details_page(final_url):
                        logging.info("   V Details page loaded after delay")
                        return True, active_page
                return False, None
        else:  # details page
            # If new tab opened, that's success regardless of URL
            if new_tab_opened:
                logging.info("   V New tab opened (confirmed success)")
                return True, active_page
            
            # Check if we're on external booking site
            if 'skyscanner.co.in' not in new_url:
                logging.info("   V Successfully navigated to external booking site")
                return True, active_page
            
            # Check if moved away from details page
            if not is_details_page(new_url):
                logging.info("   V Successfully navigated away from details page")
                return True, active_page
            
            # Still on details page - but maybe tab opened slowly
            # Do one final comprehensive tab check
            logging.info("   Final comprehensive tab check...")
            time.sleep(3)
            final_page_count = len(context.pages)
            if final_page_count > initial_page_count:
                logging.info(f"   V New tab detected in final check!")
                latest_page = context.pages[-1]
                latest_url = latest_page.url
                logging.info(f"   New tab URL: {latest_url[:80]}")
                
                # This is success!
                return True, latest_page
            
            # Still on details page - check if URL changed at all
            if new_url != preserved_url:
                logging.info("   URL changed within Skyscanner")
                
                # Check if it's a deeplink URL
                if 'transport_deeplink' in new_url:
                    logging.info("   On deeplink page - waiting for external redirect...")
                    time.sleep(10)
                    
                    final_url = active_page.url
                    logging.info(f"   Final check URL: {final_url[:100]}")
                    
                    if 'skyscanner.co.in' not in final_url:
                        logging.info("   V Redirected to external site")
                        return True, active_page
                    else:
                        logging.info("   ⚠ Still on Skyscanner after deeplink wait")
                        # But check tabs one more time
                        if len(context.pages) > initial_page_count:
                            logging.info("   V But new tab exists - SUCCESS!")
                            return True, context.pages[-1]
                        return True, active_page  # Consider success anyway
                else:
                    logging.info("   Waiting for external redirect...")
                    time.sleep(5)
                    
                    final_check_url = active_page.url
                    if not is_details_page(final_check_url):
                        logging.info("   V Redirect completed")
                        return True, active_page
                    else:
                        logging.info("   ⚠ Still on details page")
                        return True, active_page
            else:
                logging.info("   URL did not change on main page")
                # Final desperate tab check
                if len(context.pages) > initial_page_count:
                    logging.info("   V But new tab was opened - SUCCESS!")
                    return True, context.pages[-1]
                
                logging.info("   X No navigation detected")
                return False, None
        
    except Exception as e:
        logging.error(f"   Error clicking button: {e}")
        return False

def parse_proxy_string(s: str):
    s = s.strip()
    parts = s.split()
    proto = parts[0].lower() if len(parts) > 1 else "socks5"
    main = parts[1] if len(parts) > 1 else parts[0]
    
    segs = main.split(":", 3)
    if len(segs) == 4:
        host, port, username, password = segs
        return {"type": proto, "host": host, "port": port, "username": username, "password": password}
    return None

def create_ultimate_stealth_profile(profile_name, proxy_config=None):
    global current_token_idx
    while current_token_idx < len(tokens):
        TOKEN = tokens[current_token_idx]
        try:
            gl = GoLogin({"token": TOKEN})
            logging.info(f"Creating stealth profile: {profile_name}")
            
            profile = gl.createProfileRandomFingerprint({
                "os": random.choice(["win", "mac"]),
                "name": profile_name,
                "webgl": {
                    "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"]),
                    "renderer": random.choice(["Intel Iris OpenGL Engine", "GeForce GTX 1650/PCIe/SSE2"])
                },
                "audioContext": {
                    "enable": True,
                    "noise": random.uniform(0.0001, 0.0005)
                }
            })
            
            if not profile or 'id' not in profile:
                raise Exception("Profile creation failed")
                
            profile_id = profile['id']
            logging.info(f"Profile created: {profile_id}")
            
            if proxy_config:
                try:
                    proxy_data = {
                        "mode": proxy_config['type'],
                        "host": proxy_config['host'],
                        "port": int(proxy_config['port']),
                        "username": proxy_config.get('username', ''),
                        "password": proxy_config.get('password', '')
                    }
                    gl.changeProfileProxy(profile_id, proxy_data)
                    logging.info(f"Proxy configured: {proxy_config['host']}")
                except Exception as e:
                    logging.warning(f"Proxy setup warning: {e}")
            
            return profile_id
            
        except Exception as e:
            logging.error(f"Error with token {current_token_idx}: {e}")
            current_token_idx += 1
            if current_token_idx >= len(tokens):
                logging.error("All tokens exhausted")
                return None
            logging.info(f"Switching to next token {current_token_idx}")

def start_maximum_stealth_browser(profile_id):
    try:
        gl = GoLogin({
            "token": tokens[current_token_idx],
            "profile_id": profile_id
        })
        logging.info(f"Starting browser for: {profile_id}")
        debugger_address = gl.start()
        
        time.sleep(random.uniform(3, 5))
        
        pw = sync_playwright().start()
        cdp_url = f"http://{debugger_address}"
        browser = pw.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0]
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()
        
        context.set_extra_http_headers({
            "DNT": "1",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        })
        
        inject_ultimate_stealth(page)
        
        return gl, pw, browser, page
        
    except Exception as e:
        logging.error(f"Browser start error: {e}")
        return None, None, None, None

def inject_ultimate_stealth(page: Page):
    try:
        logging.info("Injecting stealth...")
        
        page.evaluate("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            delete window.webdriver;
            
            window.chrome = {
                runtime: {
                    onConnect: {addListener: () => {}},
                    onMessage: {addListener: () => {}},
                }
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [{
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    name: "Chrome PDF Plugin"
                }]
            });
        """)
        
        logging.info("Stealth active")
        
    except Exception as e:
        logging.warning(f"Stealth injection warning: {e}")

def handle_captcha_challenge(page: Page, max_retries=5):  # Changed to 5!
    """Handle CAPTCHA"""
    for attempt in range(max_retries):
        try:
            logging.info(f"\nCAPTCHA Handler - Attempt {attempt + 1}/{max_retries}")
            
            current_url = page.url
            if "captcha" not in current_url.lower():
                return False
            
            page.wait_for_load_state("load", timeout=30000)
            time.sleep(3)
            
            button_found = False
            target_frame = page
            button_element = None
            
            # Search main page first
            try:
                button_element = page.locator("text=/PRESS.*HOLD/i").first
                if button_element.is_visible(timeout=5000):
                    button_found = True
                    logging.info("Button found in main page")
            except:
                pass
            
            # Search in iframes
            if not button_found:
                frames = page.frames
                for idx, frame in enumerate(frames):
                    try:
                        button_element = frame.locator("text=/PRESS.*HOLD/i").first
                        if button_element.is_visible(timeout=5000):
                            target_frame = frame
                            button_found = True
                            logging.info(f"Button found in frame {idx}")
                            break
                    except:
                        continue
            
            if not button_found:
                if attempt < max_retries - 1:
                    time.sleep(5)
                continue
            
            bounding_box = button_element.bounding_box()
            if not bounding_box:
                continue
            
            center_x = bounding_box['x'] + bounding_box['width'] / 2
            center_y = bounding_box['y'] + bounding_box['height'] / 2
            
            page.mouse.move(center_x, center_y, steps=25)
            time.sleep(random.uniform(0.3, 0.6))
            page.mouse.down()
            
            hold_duration = 90
            start_time = time.time()
            
            while time.time() - start_time < hold_duration:
                elapsed = time.time() - start_time
                
                try:
                    if "captcha" not in page.url.lower():
                        logging.info(f"\nCAPTCHA solved after {elapsed:.1f}s")
                        page.mouse.up()
                        return True
                except:
                    pass
                
                time.sleep(0.5)
            
            page.mouse.up()
            time.sleep(3)
            
            if "captcha" not in page.url.lower():
                return True
                
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} error: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    
    return False

def ultimate_human_browsing(page: Page):
    try:
        logging.info("Starting human behavior simulation...")
        
        # Go to Google first
        google_url = "https://www.google.co.in/"
        logging.info(f"\nNavigating to Google: {google_url}")
        
        for attempt in range(3):
            try:
                page.goto(google_url, timeout=60000, wait_until="networkidle")
                break
            except:
                if attempt == 2:
                    return False
        
        time.sleep(3)
        
        for url in TARGET_URLS:
            logging.info(f"\n{'='*60}")
            logging.info(f"STEP 1: Affiliate URL")
            logging.info(f"{'='*60}")
            
            for attempt in range(3):
                try:
                    page.goto(url, timeout=60000, wait_until="networkidle")
                    break
                except:
                    if attempt == 2:
                        continue
            
            time.sleep(random.uniform(5, 8))
            
            if "captcha" in page.url.lower():
                if not handle_captcha_challenge(page):
                    continue
            
            # STEP 2: Flight search (RESULTS page)
            logging.info(f"\n{'='*60}")
            logging.info(f"STEP 2: Flight Search (RESULTS PAGE)")
            logging.info(f"{'='*60}")
            
            flight_loaded = False
            
            for flight_attempt in range(3):
                logging.info(f"\nAttempt {flight_attempt + 1}/3")
                
                flight_url = generate_random_flight_url()
                
                for nav_attempt in range(3):
                    try:
                        page.goto(flight_url, timeout=60000, wait_until="networkidle")
                        break
                    except:
                        if nav_attempt == 2:
                            break
                
                time.sleep(random.uniform(5, 8))
                
                current_url = page.url
                
                if "captcha" in current_url.lower():
                    if not handle_captcha_challenge(page):
                        if flight_attempt < 2:
                            continue
                        else:
                            break
                
                if not is_results_page(current_url):
                    if flight_attempt < 2:
                        continue
                    else:
                        break
                
                logging.info("V On RESULTS page")
                
                time.sleep(random.uniform(*PAGE_LOAD_PATIENCE))
                
                # STEP 3: First Select button (RESULTS -> DETAILS)
                logging.info(f"\n{'='*60}")
                logging.info(f"STEP 3: First Select Button")
                logging.info(f"{'='*60}")
                
                if click_select_button(page, "results"):
                    time.sleep(3)
                    new_url = page.url
                    if is_details_page(new_url):
                        logging.info("V Moved to DETAILS page")
                        flight_loaded = True
                        break
                    elif is_results_page(new_url):
                        logging.error("ERROR: Still on results page")
                        if flight_attempt < 2:
                            continue
                else:
                    if flight_attempt < 2:
                        continue
            
            if not flight_loaded:
                logging.info("\nX Failed to reach details page")
                continue
            
            # Now on DETAILS page
            current_url = page.url
            
            if not is_details_page(current_url):
                logging.error(f"ERROR: Not on details page!")
                continue
            
            logging.info("V Confirmed on DETAILS page")
            
            time.sleep(random.uniform(3, 6))
            
            if "captcha" in page.url.lower():
                if not handle_captcha_challenge(page):
                    continue
            
            # Verify still on details page before second click
            if not is_details_page(page.url):
                logging.error("ERROR: Lost details page before second click")
                continue
            
            # STEP 4: Second Select button (DETAILS -> Booking)
            logging.info(f"\n{'='*60}")
            logging.info(f"STEP 4: Second Select Button")
            logging.info(f"{'='*60}")
            
            # Extra verification
            logging.info(f"Pre-click URL check: {page.url[:80]}")
            if not is_details_page(page.url):
                logging.error("ERROR: Not on details page before click!")
                continue
            
            click_result = click_select_button(page, "details")
            if isinstance(click_result, tuple):
                success, booking_page = click_result
            else:
                success = click_result
                booking_page = page
            
            if success:
                logging.info("V Second Select button clicked successfully")
                
                # Use the returned page (might be new tab)
                if booking_page and booking_page != page:
                    logging.info(f"   Using new booking page for human behavior")
                    final_page = booking_page
                else:
                    final_page = page
                
                time.sleep(3)
                
                # Human behavior on final booking page
                human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
                logging.info(f"\nFinal page human behavior for {human_time:.1f}s")
                logging.info(f"Final page URL: {final_page.url[:80]}")
                
                start_time = time.time()
                while time.time() - start_time < human_time:
                    try:
                        action = random.choice(['scroll', 'mouse_move', 'pause'])
                        
                        if action == 'scroll':
                            final_page.evaluate(f"window.scrollBy({{top: {random.randint(50, 150)}, behavior: 'smooth'}});")
                        elif action == 'mouse_move':
                            final_page.mouse.move(random.randint(100, 800), random.randint(100, 600))
                        else:
                            time.sleep(random.uniform(1, 3))
                        
                        time.sleep(random.uniform(1, 2))
                    except Exception as e:
                        # Page might be closed or navigated
                        logging.warning(f"   Human behavior warning: {str(e)[:50]}")
                        break
                
                logging.info("V Human behavior completed on booking page")
            else:
                logging.info("X Failed second click")
                continue
        
        logging.info("\nHuman behavior complete")
        return True
        
    except Exception as e:
        logging.error(f"Human browsing error: {e}")
        logging.error(traceback.format_exc())
        return False

def run_ultimate_stealth_test():
    logging.info("FIXED SKYSCANNER BOT WITH URL PROTECTION")
    logging.info("=" * 60)
    
    successful_runs = 0
    
    for profile_num in range(1, TOTAL_PROFILES + 1):
        logging.info(f"\n=== PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
        profile_name = f"stealth_flight_{profile_num}_{random.randint(100000, 999999)}"
        
        proxy_config = None
        if PROXY_LIST:
            proxy_str = random.choice(PROXY_LIST)
            proxy_config = parse_proxy_string(proxy_str)
        
        profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
        if profile_id:
            time.sleep(random.uniform(4, 8))
            
            gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
            if page:
                try:
                    success = ultimate_human_browsing(page)
                    
                    if success:
                        successful_runs += 1
                        logging.info(f"\nPROFILE {profile_num} - SUCCESS!")
                    else:
                        logging.info(f"\nPROFILE {profile_num} - FAILED")
                    
                    time.sleep(random.uniform(10, 20))
                  
                finally:
                    cleanup_browser(gl, pw, browser)
            else:
                logging.info(f"PROFILE {profile_num} - BROWSER START FAILED")
        else:
            logging.info(f"PROFILE {profile_num} - PROFILE CREATION FAILED")

    logging.info(f"\n{'='*60}")
    logging.info(f"TEST COMPLETE!")
    logging.info(f"Success Rate: {successful_runs}/{TOTAL_PROFILES}")
    logging.info(f"{'='*60}")

def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
    try:
        if browser:
            browser.close()
        time.sleep(1)
        if gl:
            gl.stop()
        if pw:
            pw.stop()
        logging.info("Browser session terminated")
    except Exception as e:
        logging.warning(f"Cleanup warning: {e}")

if __name__ == "__main__":
    logging.info("FIXED ANTI-BOT BYPASS WITH URL PROTECTION")
    logging.info("=" * 60)

    if not GOLOGIN_AVAILABLE:
        logging.error("GoLogin not available!")
        exit(1)
    
    try:
        run_ultimate_stealth_test()
    except KeyboardInterrupt:
        logging.info("\nTest interrupted by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        logging.error(traceback.format_exc())




# import time
# import random
# import uuid
# import datetime
# import re
# from playwright.sync_api import expect
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright
# import json
# import logging
# import traceback
# import sys
# import os

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     logging.error("Install GoLogin: pip install gologin")
#     exit(1)

# # Setup logging
# try:
#     # Clear existing handlers to avoid conflicts
#     for handler in logging.root.handlers[:]:
#         logging.root.removeHandler(handler)

#     # Get the directory where the script is running
#     log_dir = os.getcwd()
#     log_file = os.path.join(log_dir, 'bot.log')

#     # Configure logging to write to bot.log in the current directory and console
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         handlers=[
#             logging.FileHandler(log_file, mode='a'),  # Write to bot.log in current directory
#             logging.StreamHandler(sys.stdout)  # Also output to console
#         ]
#     )
#     logging.info(f"Logging to file: {log_file}")
#     logging.info(f"Current working directory: {os.getcwd()}")
# except Exception as e:
#     print(f"Failed to configure logging: {e}")
#     sys.exit(1)

# # Load config
# try:
#     with open('config.json', 'r') as f:
#         config = json.load(f)
#     tokens = config['tokens']
#     if not tokens:
#         logging.error("No tokens found in config.json")
#         sys.exit(1)
# except FileNotFoundError:
#     logging.error("config.json not found")
#     sys.exit(1)
# except json.JSONDecodeError:
#     logging.error("Invalid JSON in config.json")
#     sys.exit(1)

# current_token_idx = 0

# # ---------- CONFIG ----------
# TARGET_URLS = [
#     "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc",
# ]
# TOTAL_PROFILES = 100
# PAGE_LOAD_PATIENCE = (4, 8)
# HUMAN_BEHAVIOR_TIME = (15, 30)

# PROXY_TEMPLATE = "CHANGE_ME_EMP_ID"

# COUNTRY_CODES = [
#     'in', 'us', 'gb', 'fr', 'de', 'ca', 'au', 'jp', 'kr', 'br',
#     'mx', 'es', 'it', 'nl', 'se', 'no', 'dk', 'fi', 'pl', 'ru',
#     'tr', 'id', 'my', 'ph', 'th'
# ]

# AIRPORT_CODES = {
#     "BLR": "Bengaluru",
#     "BOM": "Mumbai",
#     "DEL": "Delhi",
#     "CCU": "Kolkata",
#     "MAA": "Chennai",
#     "HYD": "Hyderabad",
#     "AMD": "Ahmedabad",
#     "PNQ": "Pune",
#     "GOI": "Goa",
#     "COK": "Kochi",
#     "IXC": "Chandigarh",
#     "IXJ": "Jammu",
#     "SXV": "Srinagar",
#     "GAU": "Guwahati",
#     "PAT": "Patna",
#     "NAG": "Nagpur",
#     "BBI": "Bhubaneswar",
#     "TRV": "Thiruvananthapuram",
#     "VNS": "Varanasi",
#     "ATQ": "Amritsar"
# }

# def is_results_page(url):
#     """Check if current page is results page"""
#     return ("/transport/flights/" in url and "/config/" not in url and "captcha" not in url.lower())

# def is_details_page(url):
#     """Check if current page is details page"""
#     return ("/transport/flights/" in url and "/config/" in url and "captcha" not in url.lower())

# def generate_random_flight_url():
#     """Generate random Skyscanner flight search URL"""
#     airports = list(AIRPORT_CODES.keys())
#     origin = random.choice(airports)
#     destination = random.choice([a for a in airports if a != origin])
    
#     days_ahead = random.randint(1, 90)
#     flight_date = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
#     date_str = flight_date.strftime("%y%m%d")
    
#     adults = random.randint(1, 4)
#     cabin_class = random.choice(["economy", "premium_economy", "business", "first"])
#     one_way = random.choice([True, False])
#     rtn = 0 if one_way else 1
    
#     flight_url = (
#         f"https://www.skyscanner.co.in/transport/flights/"
#         f"{origin.lower()}/{destination.lower()}/{date_str}/"
#         f"?adultsv2={adults}"
#         f"&cabinclass={cabin_class}"
#         f"&childrenv2="
#         f"&ref=home"
#         f"&rtn={rtn}"
#         f"&outboundaltsenabled=false"
#         f"&inboundaltsenabled=false"
#         f"&preferdirects=false"
#     )
    
#     logging.info(f"\nGenerated Flight Search:")
#     logging.info(f"   Route: {AIRPORT_CODES[origin]} -> {AIRPORT_CODES[destination]}")
#     logging.info(f"   Date: {flight_date.strftime('%d %b %Y')}")
#     logging.info(f"   Adults: {adults}, Class: {cabin_class}, {'One-way' if one_way else 'Round-trip'}")
#     logging.info(f"   URL: {flight_url}")
    
#     return flight_url

# def close_popup_safely(page: Page, preserve_url=None):
#     """Close popup while preserving current URL state"""
#     try:
#         logging.info("   Checking for popup...")
        
#         # Save current URL if provided
#         url_before = preserve_url or page.url
        
#         close_selectors = [
#             'button[aria-label="Close"]',
#             'button[title="Close"]', 
#             'button.BpkCloseButton_bpk-close-button__default__ZDA3N',
#             'button.BpkCloseButton_bpk-button__NDQyM',
#             'dialog button[type="button"]',
#         ]
        
#         for selector in close_selectors:
#             try:
#                 close_button = page.locator(selector).first
#                 if close_button.is_visible(timeout=2000):
#                     logging.info(f"   Popup detected! Closing with selector: {selector}")
                    
#                     # Click with force to avoid navigation
#                     close_button.click(timeout=3000, force=True, no_wait_after=True)
#                     time.sleep(0.5)
                    
#                     # Check if URL changed unexpectedly
#                     url_after = page.url
#                     if preserve_url and url_after != url_before:
#                         logging.info(f"   WARNING: URL changed during popup close!")
#                         logging.info(f"   Before: {url_before[:80]}")
#                         logging.info(f"   After: {url_after[:80]}")
                        
#                         # Try to go back to preserved URL
#                         if preserve_url in url_before:
#                             logging.info("   Attempting to restore URL...")
#                             try:
#                                 page.goto(url_before, timeout=30000, wait_until="domcontentloaded")
#                                 time.sleep(2)
#                             except:
#                                 pass
#                     else:
#                         logging.info("   Popup closed successfully")
                    
#                     return True
#             except:
#                 continue
        
#         logging.info("   No popup detected")
#         return False
        
#     except Exception as e:
#         logging.warning(f"   Popup check warning: {e}")
#         return False

# def find_select_button_on_results_page(page: Page):
#     """Find Select button on RESULTS page - FLIGHT CARD only"""
#     try:
#         logging.info(f"\n[RESULTS PAGE] Finding Select button...")
        
#         current_url = page.url
#         if not is_results_page(current_url):
#             logging.error(f"   ERROR: Not on results page! Current URL: {current_url[:80]}")
#             return None, None
        
#         logging.info(f"   ✓ Confirmed on results page")
        
#         button_found = False
#         button_element = None
        
#         # Strategy 1: Find buttons in flight card containers ONLY
#         logging.info("   Strategy 1: Looking for buttons in flight cards...")
#         try:
#             # Flight cards have specific parent containers
#             flight_cards = page.locator('div[data-testid*="flight"], div[class*="FlightCard"], div[class*="Ticket"]').all()
#             logging.info(f"   Found {len(flight_cards)} potential flight cards")
            
#             for idx, card in enumerate(flight_cards):
#                 try:
#                     # Find Select button within this card
#                     select_buttons = card.locator('button:has-text("Select"), a:has-text("Select")').all()
                    
#                     for btn in select_buttons:
#                         if btn.is_visible(timeout=3000):
#                             text = btn.inner_text(timeout=2000).strip().lower()
                            
#                             # CRITICAL: Exclude filter/checkbox buttons
#                             if text == 'select' and 'all' not in text:
#                                 # Verify it's clickable and has proper dimensions
#                                 try:
#                                     dimensions = btn.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
#                                     if dimensions['width'] > 50 and dimensions['height'] > 20:
#                                         logging.info(f"   ✓ Valid Select button found in card {idx}")
#                                         button_element = btn
#                                         button_found = True
#                                         break
#                                 except:
#                                     continue
                    
#                     if button_found:
#                         break
#                 except:
#                     continue
#         except Exception as e:
#             logging.warning(f"   Strategy 1 failed: {e}")
        
#         # Strategy 2: Look for primary action buttons with specific class patterns
#         if not button_found:
#             logging.info("   Strategy 2: Looking for primary action buttons...")
#             try:
#                 # These classes are specifically for flight selection, not filters
#                 primary_selectors = [
#                     'div[class*="TicketStub"] button.bpk-button--primary',
#                     'button.BpkButton_bpk-button__NDRjO.bpk-button--primary:not([class*="compact"])',
#                     'div[class*="ctaButton"] button',
#                 ]
                
#                 for selector in primary_selectors:
#                     buttons = page.locator(selector).all()
#                     logging.info(f"   Checking selector: {selector} ({len(buttons)} found)")
                    
#                     for btn in buttons:
#                         try:
#                             if btn.is_visible(timeout=3000):
#                                 text = btn.inner_text(timeout=2000).strip().lower()
                                
#                                 # Must be exactly "select" - not "select all"
#                                 if text == 'select':
#                                     # Check it's not in a filter/modal context
#                                     parent_html = btn.evaluate("el => el.parentElement.parentElement.className")
#                                     if 'filter' not in parent_html.lower() and 'checkbox' not in parent_html.lower():
#                                         dimensions = btn.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
#                                         if dimensions['width'] > 50:
#                                             logging.info(f"   ✓ Valid Select button found with selector: {selector}")
#                                             button_element = btn
#                                             button_found = True
#                                             break
#                         except:
#                             continue
                    
#                     if button_found:
#                         break
#             except Exception as e:
#                 logging.warning(f"   Strategy 2 failed: {e}")
        
#         if not button_found:
#             logging.info("   ✗ Select button NOT found on results page")
#             return None, None
        
#         return page, button_element
        
#     except Exception as e:
#         logging.error(f"   Error finding button on results page: {e}")
#         return None, None

# def find_select_button_on_details_page(page: Page):
#     """Find BEST Select button on DETAILS page - prioritize external links"""
#     try:
#         logging.info(f"\n[DETAILS PAGE] Finding Select button...")
        
#         current_url = page.url
#         if not is_details_page(current_url):
#             logging.error(f"   ERROR: Not on details page! Current URL: {current_url[:80]}")
#             return None, None
        
#         logging.info(f"   ✓ Confirmed on details page (has /config/)")
        
#         # Wait for AJAX content
#         logging.info("   Waiting for AJAX content...")
#         try:
#             page.wait_for_function(
#                 "() => document.querySelectorAll('.loading, .spinner').length === 0",
#                 timeout=20000
#             )
#             time.sleep(3)
#         except:
#             logging.info("   AJAX wait completed")
        
#         button_candidates = []
        
#         selectors = [
#             'div.PricedCta_ctaButton__OTZiN a.BpkButton_bpk-button__NDRjO.bpk-button--primary',
#             'div.PricedCta_ctaButton__OTZiN a[data-testid="pricing-item-redirect-button"]',
#             'a[data-testid="pricing-item-redirect-button"]',
#             'div.PricedCta_ctaButton__OTZiN a',
#             'a.BpkButton_bpk-button__NDRjO.bpk-button--primary',
#             'a.bpk-button--primary',
#         ]
        
#         # Collect ALL valid Select buttons
#         for selector in selectors:
#             try:
#                 logging.info(f"   Checking selector: {selector}")
#                 buttons = page.locator(selector).all()
                
#                 for button in buttons:
#                     try:
#                         if button.is_visible(timeout=5000):
#                             text = button.inner_text(timeout=2000).strip().lower()
#                             if 'select' in text:
#                                 # Get href if it's a link
#                                 try:
#                                     href = button.evaluate("el => el.href || ''")
#                                     tag = button.evaluate("el => el.tagName")
                                    
#                                     # Prioritize external links (not skyscanner domain)
#                                     has_external_href = href and 'http' in href and 'skyscanner' not in href
                                    
#                                     dimensions = button.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
#                                     if dimensions['width'] > 0 and dimensions['height'] > 0:
#                                         priority = 10 if has_external_href else 5
#                                         button_candidates.append({
#                                             'button': button,
#                                             'selector': selector,
#                                             'href': href,
#                                             'tag': tag,
#                                             'external': has_external_href,
#                                             'priority': priority
#                                         })
#                                         logging.info(f"   Found candidate: href={href[:60] if href else 'N/A'}, external={has_external_href}")
#                                 except:
#                                     continue
#                     except:
#                         continue
#             except:
#                 continue
        
#         if not button_candidates:
#             logging.info("   ✗ No Select buttons found on details page")
#             return None, None
        
#         # Sort by priority (external links first)
#         button_candidates.sort(key=lambda x: x['priority'], reverse=True)
        
#         logging.info(f"   Found {len(button_candidates)} Select button(s)")
#         best_candidate = button_candidates[0]
#         logging.info(f"   ✓ Using button with href: {best_candidate['href'][:80] if best_candidate['href'] else 'N/A'}")
#         logging.info(f"   External link: {best_candidate['external']}")
        
#         return page, best_candidate['button']
        
#     except Exception as e:
#         logging.error(f"   Error finding button on details page: {e}")
#         return None, None

# def remove_overlays_safely(page: Page):
#     """Aggressively remove ALL blocking overlays and scrims"""
#     try:
#         logging.info("   Removing overlays aggressively...")
#         removed_count = page.evaluate("""
#             () => {
#                 let count = 0;
                
#                 // Remove ALL scrim/overlay elements that block clicks
#                 const overlaySelectors = [
#                     'div.bpk-scrim',
#                     'div.bpk-scrim_bpk-scrim__NzY2M',
#                     'div[role="presentation"]',
#                     'div[class*="scrim"]',
#                     '.loading',
#                     '.spinner',
#                     'div[class*="overlay"]',
#                     'div[class*="backdrop"]',
#                 ];
                
#                 overlaySelectors.forEach(selector => {
#                     document.querySelectorAll(selector).forEach(el => {
#                         // Check if it's actually blocking something
#                         const rect = el.getBoundingClientRect();
#                         const zIndex = window.getComputedStyle(el).zIndex;
                        
#                         // If it's large and has high z-index, it's likely a blocker
#                         if ((rect.width > 100 || rect.height > 100) && (zIndex === 'auto' || parseInt(zIndex) > 100)) {
#                             el.remove();
#                             count++;
#                         }
#                     });
#                 });
                
#                 // Also remove modal-container contents if present
#                 const modalContainer = document.getElementById('modal-container');
#                 if (modalContainer) {
#                     // Don't remove the container itself, just problematic children
#                     modalContainer.querySelectorAll('div[role="presentation"]').forEach(el => {
#                         el.remove();
#                         count++;
#                     });
#                 }
                
#                 // Make ALL Select buttons accessible (not just visible ones)
#                 document.querySelectorAll('button, a').forEach(el => {
#                     const text = (el.textContent || '').toLowerCase().trim();
#                     if (text === 'select') {
#                         el.style.visibility = 'visible';
#                         el.style.opacity = '1';
#                         el.style.pointerEvents = 'auto';
#                         el.style.display = 'block';
#                     }
#                 });
                
#                 return count;
#             }
#         """)
#         logging.info(f"   Removed {removed_count} blocking elements")
#         time.sleep(1.5)
        
#         # Double-check and remove again if needed
#         try:
#             still_blocking = page.evaluate("""
#                 () => {
#                     const scrim = document.querySelector('div.bpk-scrim, div[role="presentation"][class*="scrim"]');
#                     if (scrim) {
#                         scrim.remove();
#                         return true;
#                     }
#                     return false;
#                 }
#             """)
#             if still_blocking:
#                 logging.info("   Removed additional scrim blocker")
#         except:
#             pass
            
#     except Exception as e:
#         logging.warning(f"   Overlay removal warning: {e}")

# def click_select_button(page: Page, page_type="results"):
#     """Click Select button with URL protection and new tab handling"""
#     try:
#         logging.info(f"\n{'='*60}")
#         logging.info(f"CLICKING SELECT BUTTON ON {page_type.upper()} PAGE")
#         logging.info(f"{'='*60}")
        
#         current_url = page.url
#         logging.info(f"Current URL: {current_url[:100]}...")
        
#         # Verify page type
#         if page_type == "results":
#             if not is_results_page(current_url):
#                 logging.error(f"   ERROR: Not on results page!")
#                 return False
#         elif page_type == "details":
#             if not is_details_page(current_url):
#                 logging.error(f"   ERROR: Not on details page!")
#                 return False
        
#         # Save URL before any operations
#         preserved_url = current_url
#         logging.info(f"   Preserved URL for protection")
        
#         # Get context for tab monitoring
#         context = page.context
#         initial_page_count = len(context.pages)
        
#         # Wait for page load
#         page.wait_for_load_state("domcontentloaded", timeout=60000)
#         time.sleep(random.uniform(3, 5))
        
#         # Close popup with URL protection
#         close_popup_safely(page, preserved_url)
#         time.sleep(1)
        
#         # Verify URL hasn't changed
#         if page.url != preserved_url:
#             logging.info(f"   WARNING: URL changed after popup close!")
#             logging.info(f"   Restoring to: {preserved_url[:80]}")
#             try:
#                 page.goto(preserved_url, timeout=30000, wait_until="domcontentloaded")
#                 time.sleep(3)
#             except:
#                 logging.warning("   Failed to restore URL")
#                 return False
        
#         # Remove overlays safely
#         remove_overlays_safely(page)
        
#         # Find button
#         if page_type == "results":
#             target_frame, button = find_select_button_on_results_page(page)
#         else:
#             target_frame, button = find_select_button_on_details_page(page)
        
#         if not button:
#             logging.info(f"   ✗ No Select button found!")
#             return False
        
#         # Scroll into view
#         logging.info("   Scrolling button into view...")
#         try:
#             button.scroll_into_view_if_needed(timeout=15000)
#             time.sleep(random.uniform(1.5, 2.5))
#         except Exception as e:
#             logging.warning(f"   Scroll warning: {e}")
        
#         # Verify URL again after scroll
#         if page.url != preserved_url:
#             logging.warning(f"   WARNING: URL changed after scroll!")
#             return False
        
#         # Get button details for debugging
#         try:
#             button_tag = button.evaluate("el => el.tagName")
#             button_href = button.evaluate("el => el.href || 'N/A'") if button_tag.lower() == 'a' else 'N/A'
#             button_onclick = button.evaluate("el => el.onclick ? 'has onclick' : 'no onclick'")
#             logging.info(f"   Button details: Tag={button_tag}, Href={button_href[:60] if button_href != 'N/A' else 'N/A'}, OnClick={button_onclick}")
#         except:
#             pass
        
#         logging.info("   Clicking Select button...")
#         click_success = False
        
#         # Set up popup/new tab listener
#         new_page_promise = None
#         if page_type == "details":
#             logging.info("   Setting up new tab listener...")
#             try:
#                 new_page_promise = context.expect_page(timeout=30000)
#             except:
#                 logging.warning("   New tab listener setup failed")
        
#         # Multiple click strategies with deeplink handling
#         for attempt in range(3):
#             logging.info(f"   Click attempt {attempt + 1}/3")
#             try:
#                 # Re-verify button is still present
#                 expect(button).to_be_visible(timeout=10000)
#                 expect(button).to_be_enabled(timeout=10000)
                
#                 # For deeplink URLs, use special handling
#                 if page_type == "details" and button_href and 'transport_deeplink' in button_href:
#                     logging.info(f"   Strategy: Deeplink click with extended wait")
#                     try:
#                         # Click and wait for redirect
#                         button.click(timeout=15000, force=True)
#                         click_success = True
#                         logging.info("   ✓ Deeplink click initiated")
                        
#                         # Wait longer for deeplink to redirect
#                         logging.info("   Waiting for deeplink redirect (up to 45s)...")
#                         start_wait = time.time()
#                         redirected = False
                        
#                         while time.time() - start_wait < 45:
#                             try:
#                                 current = page.url
#                                 # Check if redirected away from Skyscanner or to new page
#                                 if 'transport_deeplink' not in current and 'skyscanner.co.in/transport/flights/' not in current:
#                                     logging.info(f"   ✓ Redirected to: {current[:80]}")
#                                     redirected = True
#                                     break
#                             except:
#                                 pass
#                             time.sleep(1)
                        
#                         if not redirected:
#                             logging.info("   Deeplink redirect timeout, but click happened")
                        
#                         break
#                     except Exception as e:
#                         logging.warning(f"   Deeplink click failed: {str(e)[:80]}")
                
#                 # For details page with external href, try direct navigation
#                 elif page_type == "details" and button_tag and button_tag.lower() == 'a' and button_href and button_href != 'N/A' and 'http' in button_href and 'skyscanner' not in button_href:
#                     logging.info(f"   Strategy: Direct navigation to external href")
#                     try:
#                         target_url = button_href
#                         logging.info(f"   Target URL: {target_url[:80]}")
#                         page.goto(target_url, timeout=45000, wait_until="load")
#                         click_success = True
#                         logging.info("   ✓ Direct navigation successful")
#                         break
#                     except Exception as e:
#                         logging.warning(f"   Direct navigation failed: {str(e)[:80]}")
                
#                 # Try force click
#                 try:
#                     button.click(timeout=15000, force=True)
#                     click_success = True
#                     logging.info("   ✓ Force click successful")
#                     break
#                 except Exception as e:
#                     logging.warning(f"   Force click failed: {str(e)[:80]}")
                
#                 # Try normal click with mouse movement
#                 try:
#                     box = button.bounding_box(timeout=10000)
#                     if box:
#                         center_x = box['x'] + box['width'] / 2
#                         center_y = box['y'] + box['height'] / 2
#                         page.mouse.move(center_x, center_y, steps=random.randint(10, 20))
#                         time.sleep(random.uniform(0.3, 0.7))
#                         button.click(timeout=15000)
#                         click_success = True
#                         logging.info("   ✓ Mouse click successful")
#                         break
#                 except Exception as e:
#                     logging.warning(f"   Mouse click failed: {str(e)[:80]}")
                
#             except Exception as e:
#                 logging.warning(f"   Attempt {attempt + 1} failed: {str(e)[:100]}")
                
#                 # Don't retry if button disappeared (likely page changed)
#                 if 'not found' in str(e).lower():
#                     logging.info("   Button disappeared - likely page is changing")
#                     click_success = True  # Consider this a success
#                     time.sleep(5)
#                     break
                
#                 # Remove overlays again before next attempt
#                 if attempt < 2:
#                     logging.info("   Removing overlays again before retry...")
#                     remove_overlays_safely(page)
#                     time.sleep(2)
        
#         # JS Fallback with deeplink awareness
#         if not click_success:
#             logging.info("   Trying JavaScript approaches...")
            
#             # For deeplinks, try JS click with extended wait
#             if page_type == "details" and button_href and 'transport_deeplink' in button_href:
#                 try:
#                     logging.info("   JS: Clicking deeplink button...")
#                     button.evaluate("el => el.click()")
#                     click_success = True
#                     logging.info("   ✓ JS deeplink click successful")
                    
#                     # Wait for redirect
#                     logging.info("   Waiting for deeplink redirect...")
#                     time.sleep(10)
#                 except Exception as e:
#                     logging.warning(f"   JS deeplink click failed: {str(e)[:80]}")
            
#             # Try getting href and navigating
#             elif page_type == "details":
#                 try:
#                     href = button.evaluate("el => el.href")
#                     if href and 'http' in href:
#                         logging.info(f"   JS: Navigating to href: {href[:80]}")
#                         page.goto(href, timeout=45000, wait_until="load")
#                         click_success = True
#                         logging.info("   ✓ JS navigation successful")
#                     else:
#                         logging.info("   JS: No valid href found")
#                 except Exception as e:
#                     logging.warning(f"   JS href navigation failed: {str(e)[:80]}")
            
#             # Last resort: JS click
#             if not click_success:
#                 try:
#                     button.evaluate("el => el.click()")
#                     click_success = True
#                     logging.info("   ✓ JS click successful")
#                     time.sleep(5)
#                 except Exception as e:
#                     logging.warning(f"   JS click failed: {str(e)[:80]}")
        
#         if not click_success:
#             logging.info("   ✗ All click attempts failed!")
#             return False
        
#         # Wait for navigation - CRITICAL FIX with deeplink handling
#         logging.info("   Waiting for navigation to complete...")
        
#         # Check for new tab/popup (especially for details page)
#         active_page = page
#         new_tab_opened = False
        
#         if page_type == "details":
#             try:
#                 logging.info("   Checking for new tab (extended wait for deeplinks)...")
#                 # Wait longer for deeplink to potentially open tab
#                 max_tab_wait = 15  # Extended wait
#                 tab_check_start = time.time()
                
#                 while time.time() - tab_check_start < max_tab_wait:
#                     current_page_count = len(context.pages)
#                     if current_page_count > initial_page_count:
#                         new_tab_opened = True
#                         latest_page = context.pages[-1]
#                         logging.info(f"   ✓ New tab detected after {time.time() - tab_check_start:.1f}s!")
#                         logging.info(f"   New tab URL: {latest_page.url[:80]}")
                        
#                         # Switch to new tab
#                         active_page = latest_page
                        
#                         # Wait for new tab to load
#                         try:
#                             active_page.wait_for_load_state("load", timeout=30000)
#                             logging.info("   New tab loaded successfully")
#                         except:
#                             logging.info("   New tab still loading...")
#                             time.sleep(3)
#                         break
#                     time.sleep(1)
                
#                 if not new_tab_opened:
#                     logging.info("   No new tab detected after extended wait")
#             except Exception as e:
#                 logging.warning(f"   New tab check error: {e}")
        
#         # Wait for proper page load with multiple strategies
#         navigation_successful = False
        
#         # Strategy 1: Wait for load state
#         try:
#             active_page.wait_for_load_state("load", timeout=20000)
#             logging.info("   Page load state reached")
#             navigation_successful = True
#         except Exception as e:
#             logging.warning(f"   Load state timeout: {str(e)[:80]}")
        
#         # Strategy 2: Wait for network idle (skip for slow deeplinks)
#         if not ('transport_deeplink' in active_page.url):
#             try:
#                 active_page.wait_for_load_state("networkidle", timeout=20000)
#                 logging.info("   Network idle reached")
#                 navigation_successful = True
#             except Exception as e:
#                 logging.warning(f"   Network idle timeout: {str(e)[:80]}")
        
#         # Strategy 3: Wait for URL change (with deeplink awareness)
#         if not navigation_successful and not new_tab_opened:
#             logging.info("   Waiting for URL change...")
#             max_wait = 30  # Longer wait for deeplinks
#             start_wait = time.time()
#             url_changed = False
#             last_url = preserved_url
            
#             while time.time() - start_wait < max_wait:
#                 try:
#                     current = active_page.url
#                     if current != last_url:
#                         logging.info(f"   URL changed: {current[:80]}")
#                         last_url = current
#                         url_changed = True
                        
#                         # If moved away from deeplink, that's success
#                         if 'transport_deeplink' not in current and current != preserved_url:
#                             logging.info("   ✓ Moved away from deeplink")
#                             break
#                 except:
#                     pass
#                 time.sleep(1)
            
#             if url_changed:
#                 # Wait for page to stabilize
#                 time.sleep(3)
#                 try:
#                     active_page.wait_for_load_state("domcontentloaded", timeout=10000)
#                 except:
#                     pass
#                 navigation_successful = True
        
#         # Final wait
#         time.sleep(3)
        
#         new_url = active_page.url
#         logging.info(f"   Final URL: {new_url[:100]}...")
        
#         # If new tab opened, that's automatically a success for details page
#         if new_tab_opened and page_type == "details":
#             logging.info("   ✓ New tab opened - booking site loaded")
#             return True, active_page
        
#         # Verify navigation for same-page transitions
#         if page_type == "results":
#             if is_details_page(new_url):
#                 logging.info("   ✓ Successfully navigated to DETAILS page")
#                 return True, active_page
#             else:
#                 logging.info("   ⚠ Warning: Expected details page")
#                 if new_url != preserved_url:
#                     logging.info("   URL did change, checking validity...")
#                     time.sleep(5)
#                     final_url = active_page.url
#                     if is_details_page(final_url):
#                         logging.info("   ✓ Details page loaded after delay")
#                         return True, active_page
#                 return False, None
#         else:  # details page
#             # If new tab opened, that's success regardless of URL
#             if new_tab_opened:
#                 logging.info("   ✓ New tab opened (confirmed success)")
#                 return True, active_page
            
#             # Check if we're on external booking site
#             if 'skyscanner.co.in' not in new_url:
#                 logging.info("   ✓ Successfully navigated to external booking site")
#                 return True, active_page
            
#             # Check if moved away from details page
#             if not is_details_page(new_url):
#                 logging.info("   ✓ Successfully navigated away from details page")
#                 return True, active_page
            
#             # Still on details page - but maybe tab opened slowly
#             # Do one final comprehensive tab check
#             logging.info("   Final comprehensive tab check...")
#             time.sleep(3)
#             final_page_count = len(context.pages)
#             if final_page_count > initial_page_count:
#                 logging.info(f"   ✓ New tab detected in final check!")
#                 latest_page = context.pages[-1]
#                 latest_url = latest_page.url
#                 logging.info(f"   New tab URL: {latest_url[:80]}")
                
#                 # This is success!
#                 return True, latest_page
            
#             # Still on details page - check if URL changed at all
#             if new_url != preserved_url:
#                 logging.info("   URL changed within Skyscanner")
                
#                 # Check if it's a deeplink URL
#                 if 'transport_deeplink' in new_url:
#                     logging.info("   On deeplink page - waiting for external redirect...")
#                     time.sleep(10)
                    
#                     final_url = active_page.url
#                     logging.info(f"   Final check URL: {final_url[:100]}")
                    
#                     if 'skyscanner.co.in' not in final_url:
#                         logging.info("   ✓ Redirected to external site")
#                         return True, active_page
#                     else:
#                         logging.info("   ⚠ Still on Skyscanner after deeplink wait")
#                         # But check tabs one more time
#                         if len(context.pages) > initial_page_count:
#                             logging.info("   ✓ But new tab exists - SUCCESS!")
#                             return True, context.pages[-1]
#                         return True, active_page  # Consider success anyway
#                 else:
#                     logging.info("   Waiting for external redirect...")
#                     time.sleep(5)
                    
#                     final_check_url = active_page.url
#                     if not is_details_page(final_check_url):
#                         logging.info("   ✓ Redirect completed")
#                         return True, active_page
#                     else:
#                         logging.info("   ⚠ Still on details page")
#                         return True, active_page
#             else:
#                 logging.info("   URL did not change on main page")
#                 # Final desperate tab check
#                 if len(context.pages) > initial_page_count:
#                     logging.info("   ✓ But new tab was opened - SUCCESS!")
#                     return True, context.pages[-1]
                
#                 logging.info("   ✗ No navigation detected")
#                 return False, None
        
#     except Exception as e:
#         logging.error(f"   Error clicking button: {e}")
#         return False

# def parse_proxy_string(s: str):
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     global current_token_idx
#     while current_token_idx < len(tokens):
#         TOKEN = tokens[current_token_idx]
#         try:
#             gl = GoLogin({"token": TOKEN})
#             logging.info(f"Creating stealth profile: {profile_name}")
            
#             profile = gl.createProfileRandomFingerprint({
#                 "os": random.choice(["win", "mac"]),
#                 "name": profile_name,
#                 "timezone": "Asia/Kolkata",
#                 "webgl": {
#                     "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"]),
#                     "renderer": random.choice(["Intel Iris OpenGL Engine", "GeForce GTX 1650/PCIe/SSE2"])
#                 },
#                 "audioContext": {
#                     "enable": True,
#                     "noise": random.uniform(0.0001, 0.0005)
#                 }
#             })
            
#             if not profile or 'id' not in profile:
#                 raise Exception("Profile creation failed")
                
#             profile_id = profile['id']
#             logging.info(f"Profile created: {profile_id}")
            
#             if proxy_config:
#                 try:
#                     proxy_data = {
#                         "mode": proxy_config['type'],
#                         "host": proxy_config['host'],
#                         "port": int(proxy_config['port']),
#                         "username": proxy_config.get('username', ''),
#                         "password": proxy_config.get('password', '')
#                     }
#                     gl.changeProfileProxy(profile_id, proxy_data)
#                     logging.info(f"Proxy configured: {proxy_config['host']}")
#                 except Exception as e:
#                     logging.warning(f"Proxy setup warning: {e}")
            
#             return profile_id
            
#         except Exception as e:
#             logging.error(f"Error with token {current_token_idx}: {e}")
#             current_token_idx += 1
#             if current_token_idx >= len(tokens):
#                 logging.error("All tokens exhausted")
#                 return None
#             logging.info(f"Switching to next token {current_token_idx}")

# def start_maximum_stealth_browser(profile_id):
#     try:
#         gl = GoLogin({
#             "token": tokens[current_token_idx],
#             "profile_id": profile_id
#         })
#         logging.info(f"Starting browser for: {profile_id}")
#         debugger_address = gl.start()
        
#         time.sleep(random.uniform(3, 5))
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         context.set_extra_http_headers({
#             "DNT": "1",
#             "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
#         })
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         logging.error(f"Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     try:
#         logging.info("Injecting stealth...")
        
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
#         """)
        
#         logging.info("Stealth active")
        
#     except Exception as e:
#         logging.warning(f"Stealth injection warning: {e}")

# def handle_captcha_challenge(page: Page, max_retries=3):
#     """Handle CAPTCHA"""
#     for attempt in range(max_retries):
#         try:
#             logging.info(f"\nCAPTCHA Handler - Attempt {attempt + 1}/{max_retries}")
            
#             current_url = page.url
#             if "captcha" not in current_url.lower():
#                 return False
            
#             page.wait_for_load_state("load", timeout=30000)
#             time.sleep(3)
            
#             button_found = False
#             target_frame = page
#             button_element = None
            
#             # Search main page first
#             try:
#                 button_element = page.locator("text=/PRESS.*HOLD/i").first
#                 if button_element.is_visible(timeout=5000):
#                     button_found = True
#                     logging.info("Button found in main page")
#             except:
#                 pass
            
#             # Search in iframes
#             if not button_found:
#                 frames = page.frames
#                 for idx, frame in enumerate(frames):
#                     try:
#                         button_element = frame.locator("text=/PRESS.*HOLD/i").first
#                         if button_element.is_visible(timeout=5000):
#                             target_frame = frame
#                             button_found = True
#                             logging.info(f"Button found in frame {idx}")
#                             break
#                     except:
#                         continue
            
#             if not button_found:
#                 if attempt < max_retries - 1:
#                     time.sleep(5)
#                 continue
            
#             bounding_box = button_element.bounding_box()
#             if not bounding_box:
#                 continue
            
#             center_x = bounding_box['x'] + bounding_box['width'] / 2
#             center_y = bounding_box['y'] + bounding_box['height'] / 2
            
#             page.mouse.move(center_x, center_y, steps=25)
#             time.sleep(random.uniform(0.3, 0.6))
#             page.mouse.down()
            
#             hold_duration = 90
#             start_time = time.time()
            
#             while time.time() - start_time < hold_duration:
#                 elapsed = time.time() - start_time
                
#                 try:
#                     if "captcha" not in page.url.lower():
#                         logging.info(f"\nCAPTCHA solved after {elapsed:.1f}s")
#                         page.mouse.up()
#                         return True
#                 except:
#                     pass
                
#                 time.sleep(0.5)
            
#             page.mouse.up()
#             time.sleep(3)
            
#             if "captcha" not in page.url.lower():
#                 return True
                
#         except Exception as e:
#             logging.error(f"Attempt {attempt + 1} error: {e}")
#             if attempt < max_retries - 1:
#                 time.sleep(5)
    
#     return False

# def ultimate_human_browsing(page: Page):
#     try:
#         logging.info("Starting human behavior simulation...")
        
#         # Go to Google first
#         google_url = "https://www.google.co.in/"
#         logging.info(f"\nNavigating to Google: {google_url}")
        
#         for attempt in range(3):
#             try:
#                 page.goto(google_url, timeout=60000, wait_until="networkidle")
#                 break
#             except:
#                 if attempt == 2:
#                     return False
        
#         time.sleep(3)
        
#         for url in TARGET_URLS:
#             logging.info(f"\n{'='*60}")
#             logging.info(f"STEP 1: Affiliate URL")
#             logging.info(f"{'='*60}")
            
#             for attempt in range(3):
#                 try:
#                     page.goto(url, timeout=60000, wait_until="networkidle")
#                     break
#                 except:
#                     if attempt == 2:
#                         continue
            
#             time.sleep(random.uniform(5, 8))
            
#             if "captcha" in page.url.lower():
#                 if not handle_captcha_challenge(page):
#                     continue
            
#             # STEP 2: Flight search (RESULTS page)
#             logging.info(f"\n{'='*60}")
#             logging.info(f"STEP 2: Flight Search (RESULTS PAGE)")
#             logging.info(f"{'='*60}")
            
#             flight_loaded = False
            
#             for flight_attempt in range(3):
#                 logging.info(f"\nAttempt {flight_attempt + 1}/3")
                
#                 flight_url = generate_random_flight_url()
                
#                 for nav_attempt in range(3):
#                     try:
#                         page.goto(flight_url, timeout=60000, wait_until="networkidle")
#                         break
#                     except:
#                         if nav_attempt == 2:
#                             break
                
#                 time.sleep(random.uniform(5, 8))
                
#                 current_url = page.url
                
#                 if "captcha" in current_url.lower():
#                     if not handle_captcha_challenge(page):
#                         if flight_attempt < 2:
#                             continue
#                         else:
#                             break
                
#                 if not is_results_page(current_url):
#                     if flight_attempt < 2:
#                         continue
#                     else:
#                         break
                
#                 logging.info("✓ On RESULTS page")
                
#                 time.sleep(random.uniform(*PAGE_LOAD_PATIENCE))
                
#                 # STEP 3: First Select button (RESULTS -> DETAILS)
#                 logging.info(f"\n{'='*60}")
#                 logging.info(f"STEP 3: First Select Button")
#                 logging.info(f"{'='*60}")
                
#                 if click_select_button(page, "results"):
#                     time.sleep(3)
#                     new_url = page.url
#                     if is_details_page(new_url):
#                         logging.info("✓ Moved to DETAILS page")
#                         flight_loaded = True
#                         break
#                     elif is_results_page(new_url):
#                         logging.error("ERROR: Still on results page")
#                         if flight_attempt < 2:
#                             continue
#                 else:
#                     if flight_attempt < 2:
#                         continue
            
#             if not flight_loaded:
#                 logging.info("\n✗ Failed to reach details page")
#                 continue
            
#             # Now on DETAILS page
#             current_url = page.url
            
#             if not is_details_page(current_url):
#                 logging.error(f"ERROR: Not on details page!")
#                 continue
            
#             logging.info("✓ Confirmed on DETAILS page")
            
#             time.sleep(random.uniform(3, 6))
            
#             if "captcha" in page.url.lower():
#                 if not handle_captcha_challenge(page):
#                     continue
            
#             # Verify still on details page before second click
#             if not is_details_page(page.url):
#                 logging.error("ERROR: Lost details page before second click")
#                 continue
            
#             # STEP 4: Second Select button (DETAILS -> Booking)
#             logging.info(f"\n{'='*60}")
#             logging.info(f"STEP 4: Second Select Button")
#             logging.info(f"{'='*60}")
            
#             # Extra verification
#             logging.info(f"Pre-click URL check: {page.url[:80]}")
#             if not is_details_page(page.url):
#                 logging.error("ERROR: Not on details page before click!")
#                 continue
            
#             click_result = click_select_button(page, "details")
#             if isinstance(click_result, tuple):
#                 success, booking_page = click_result
#             else:
#                 success = click_result
#                 booking_page = page
            
#             if success:
#                 logging.info("✓ Second Select button clicked successfully")
                
#                 # Use the returned page (might be new tab)
#                 if booking_page and booking_page != page:
#                     logging.info(f"   Using new booking page for human behavior")
#                     final_page = booking_page
#                 else:
#                     final_page = page
                
#                 time.sleep(3)
                
#                 # Human behavior on final booking page
#                 human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#                 logging.info(f"\nFinal page human behavior for {human_time:.1f}s")
#                 logging.info(f"Final page URL: {final_page.url[:80]}")
                
#                 start_time = time.time()
#                 while time.time() - start_time < human_time:
#                     try:
#                         action = random.choice(['scroll', 'mouse_move', 'pause'])
                        
#                         if action == 'scroll':
#                             final_page.evaluate(f"window.scrollBy({{top: {random.randint(50, 150)}, behavior: 'smooth'}});")
#                         elif action == 'mouse_move':
#                             final_page.mouse.move(random.randint(100, 800), random.randint(100, 600))
#                         else:
#                             time.sleep(random.uniform(1, 3))
                        
#                         time.sleep(random.uniform(1, 2))
#                     except Exception as e:
#                         # Page might be closed or navigated
#                         logging.warning(f"   Human behavior warning: {str(e)[:50]}")
#                         break
                
#                 logging.info("✓ Human behavior completed on booking page")
#             else:
#                 logging.info("✗ Failed second click")
#                 continue
        
#         logging.info("\nHuman behavior complete")
#         return True
        
#     except Exception as e:
#         logging.error(f"Human browsing error: {e}")
#         logging.error(traceback.format_exc())
#         return False

# def run_ultimate_stealth_test():
#     logging.info("FIXED SKYSCANNER BOT WITH URL PROTECTION")
#     logging.info("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         logging.info(f"\n=== PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_flight_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         random_country = random.choice(COUNTRY_CODES)
#         proxy_str = PROXY_TEMPLATE.replace('country-in', f'country-{random_country}')
#         proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             time.sleep(random.uniform(4, 8))
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         logging.info(f"\nPROFILE {profile_num} - SUCCESS!")
#                     else:
#                         logging.info(f"\nPROFILE {profile_num} - FAILED")
                    
#                     time.sleep(random.uniform(10, 20))
                  
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 logging.info(f"PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             logging.info(f"PROFILE {profile_num} - PROFILE CREATION FAILED")

#     logging.info(f"\n{'='*60}")
#     logging.info(f"TEST COMPLETE!")
#     logging.info(f"Success Rate: {successful_runs}/{TOTAL_PROFILES}")
#     logging.info(f"{'='*60}")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         logging.info("Browser session terminated")
#     except Exception as e:
#         logging.warning(f"Cleanup warning: {e}")

# if __name__ == "__main__":
#     logging.info("FIXED ANTI-BOT BYPASS WITH URL PROTECTION")
#     logging.info("=" * 60)

#     if not GOLOGIN_AVAILABLE:
#         logging.error("GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         logging.info("\nTest interrupted by user")
#     except Exception as e:
#         logging.error(f"Fatal error: {e}")
#         logging.error(traceback.format_exc())    




# import time
# import random
# import uuid
# import datetime
# import re
# from playwright.sync_api import expect
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright
# import json
# import logging
# import traceback
# import sys
# import os
# import threading
# from concurrent.futures import ThreadPoolExecutor, as_completed

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     logging.error("Install GoLogin: pip install gologin")
#     exit(1)

# # Setup logging
# try:
#     for handler in logging.root.handlers[:]:
#         logging.root.removeHandler(handler)

#     log_dir = os.getcwd()
#     log_file = os.path.join(log_dir, 'bot.log')

#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - [Thread-%(thread)d] - %(levelname)s - %(message)s',
#         handlers=[
#             logging.FileHandler(log_file, mode='a'),
#             logging.StreamHandler(sys.stdout)
#         ]
#     )
#     logging.info(f"Logging to file: {log_file}")
#     logging.info(f"Current working directory: {os.getcwd()}")
# except Exception as e:
#     print(f"Failed to configure logging: {e}")
#     sys.exit(1)

# # Load config
# try:
#     with open('config.json', 'r') as f:
#         config = json.load(f)
#     tokens = config['tokens']
#     if not tokens:
#         logging.error("No tokens found in config.json")
#         sys.exit(1)
# except FileNotFoundError:
#     logging.error("config.json not found")
#     sys.exit(1)
# except json.JSONDecodeError:
#     logging.error("Invalid JSON in config.json")
#     sys.exit(1)

# # Thread-safe token rotation
# token_lock = threading.Lock()
# current_token_idx = 0

# def get_next_token():
#     global current_token_idx
#     with token_lock:
#         token = tokens[current_token_idx % len(tokens)]
#         current_token_idx += 1
#         return token

# # ---------- CONFIG ----------
# TARGET_URLS = [
#     "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc",
# ]

# # BATCH CONFIGURATION
# TOTAL_VISITS = 1000  # Total number of visits to perform
# SESSIONS_PER_BATCH = 10  # Number of concurrent sessions in each batch
# DELAY_BETWEEN_SESSIONS = (5, 15)  # Random delay between starting each session (seconds)
# DELAY_BETWEEN_BATCHES = (30, 60)  # Random delay between batches (seconds)

# PAGE_LOAD_PATIENCE = (4, 8)
# HUMAN_BEHAVIOR_TIME = (15, 30)

# PROXY_TEMPLATE = "CHANGE_ME_EMP_ID"

# COUNTRY_CODES = [
#     'us', 'gb', 'fr', 'de', 'ca', 'au', 'jp', 'kr', 'br',
#     'mx', 'es', 'it', 'nl', 'se', 'no', 'dk', 'fi', 'pl', 'ru',
#     'tr', 'id', 'my', 'ph', 'th'
# ]

# AIRPORT_CODES = {
#     "BLR": "Bengaluru",
#     "BOM": "Mumbai",
#     "DEL": "Delhi",
#     "CCU": "Kolkata",
#     "MAA": "Chennai",
#     "HYD": "Hyderabad",
#     "AMD": "Ahmedabad",
#     "PNQ": "Pune",
#     "GOI": "Goa",
#     "COK": "Kochi",
#     "IXC": "Chandigarh",
#     "IXJ": "Jammu",
#     "SXV": "Srinagar",
#     "GAU": "Guwahati",
#     "PAT": "Patna",
#     "NAG": "Nagpur",
#     "BBI": "Bhubaneswar",
#     "TRV": "Thiruvananthapuram",
#     "VNS": "Varanasi",
#     "ATQ": "Amritsar"
# }

# def is_results_page(url):
#     """Check if current page is results page"""
#     return ("/transport/flights/" in url and "/config/" not in url and "captcha" not in url.lower())

# def is_details_page(url):
#     """Check if current page is details page"""
#     return ("/transport/flights/" in url and "/config/" in url and "captcha" not in url.lower())

# def generate_random_flight_url():
#     """Generate random Skyscanner flight search URL"""
#     airports = list(AIRPORT_CODES.keys())
#     origin = random.choice(airports)
#     destination = random.choice([a for a in airports if a != origin])
    
#     days_ahead = random.randint(1, 90)
#     flight_date = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
#     date_str = flight_date.strftime("%y%m%d")
    
#     adults = random.randint(1, 4)
#     cabin_class = random.choice(["economy", "premium_economy", "business", "first"])
#     one_way = random.choice([True, False])
#     rtn = 0 if one_way else 1
    
#     flight_url = (
#         f"https://www.skyscanner.co.in/transport/flights/"
#         f"{origin.lower()}/{destination.lower()}/{date_str}/"
#         f"?adultsv2={adults}"
#         f"&cabinclass={cabin_class}"
#         f"&childrenv2="
#         f"&ref=home"
#         f"&rtn={rtn}"
#         f"&outboundaltsenabled=false"
#         f"&inboundaltsenabled=false"
#         f"&preferdirects=false"
#     )
    
#     logging.info(f"\nGenerated Flight Search:")
#     logging.info(f"   Route: {AIRPORT_CODES[origin]} -> {AIRPORT_CODES[destination]}")
#     logging.info(f"   Date: {flight_date.strftime('%d %b %Y')}")
#     logging.info(f"   Adults: {adults}, Class: {cabin_class}, {'One-way' if one_way else 'Round-trip'}")
#     logging.info(f"   URL: {flight_url}")
    
#     return flight_url

# def close_popup_safely(page: Page, preserve_url=None):
#     """Close popup while preserving current URL state"""
#     try:
#         logging.info("   Checking for popup...")
        
#         url_before = preserve_url or page.url
        
#         close_selectors = [
#             'button[aria-label="Close"]',
#             'button[title="Close"]', 
#             'button.BpkCloseButton_bpk-close-button__default__ZDA3N',
#             'button.BpkCloseButton_bpk-button__NDQyM',
#             'dialog button[type="button"]',
#         ]
        
#         for selector in close_selectors:
#             try:
#                 close_button = page.locator(selector).first
#                 if close_button.is_visible(timeout=2000):
#                     logging.info(f"   Popup detected! Closing with selector: {selector}")
                    
#                     close_button.click(timeout=3000, force=True, no_wait_after=True)
#                     time.sleep(0.5)
                    
#                     url_after = page.url
#                     if preserve_url and url_after != url_before:
#                         logging.info(f"   WARNING: URL changed during popup close!")
#                         logging.info(f"   Before: {url_before[:80]}")
#                         logging.info(f"   After: {url_after[:80]}")
                        
#                         if preserve_url in url_before:
#                             logging.info("   Attempting to restore URL...")
#                             try:
#                                 page.goto(url_before, timeout=30000, wait_until="domcontentloaded")
#                                 time.sleep(2)
#                             except:
#                                 pass
#                     else:
#                         logging.info("   Popup closed successfully")
                    
#                     return True
#             except:
#                 continue
        
#         logging.info("   No popup detected")
#         return False
        
#     except Exception as e:
#         logging.warning(f"   Popup check warning: {e}")
#         return False

# def find_select_button_on_results_page(page: Page):
#     """Find Select button on RESULTS page - FLIGHT CARD only"""
#     try:
#         logging.info(f"\n[RESULTS PAGE] Finding Select button...")
        
#         current_url = page.url
#         if not is_results_page(current_url):
#             logging.error(f"   ERROR: Not on results page! Current URL: {current_url[:80]}")
#             return None, None
        
#         logging.info(f"   ✓ Confirmed on results page")
        
#         button_found = False
#         button_element = None
        
#         logging.info("   Strategy 1: Looking for buttons in flight cards...")
#         try:
#             flight_cards = page.locator('div[data-testid*="flight"], div[class*="FlightCard"], div[class*="Ticket"]').all()
#             logging.info(f"   Found {len(flight_cards)} potential flight cards")
            
#             for idx, card in enumerate(flight_cards):
#                 try:
#                     select_buttons = card.locator('button:has-text("Select"), a:has-text("Select")').all()
                    
#                     for btn in select_buttons:
#                         if btn.is_visible(timeout=3000):
#                             text = btn.inner_text(timeout=2000).strip().lower()
                            
#                             if text == 'select' and 'all' not in text:
#                                 try:
#                                     dimensions = btn.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
#                                     if dimensions['width'] > 50 and dimensions['height'] > 20:
#                                         logging.info(f"   ✓ Valid Select button found in card {idx}")
#                                         button_element = btn
#                                         button_found = True
#                                         break
#                                 except:
#                                     continue
                    
#                     if button_found:
#                         break
#                 except:
#                     continue
#         except Exception as e:
#             logging.warning(f"   Strategy 1 failed: {e}")
        
#         if not button_found:
#             logging.info("   Strategy 2: Looking for primary action buttons...")
#             try:
#                 primary_selectors = [
#                     'div[class*="TicketStub"] button.bpk-button--primary',
#                     'button.BpkButton_bpk-button__NDRjO.bpk-button--primary:not([class*="compact"])',
#                     'div[class*="ctaButton"] button',
#                 ]
                
#                 for selector in primary_selectors:
#                     buttons = page.locator(selector).all()
#                     logging.info(f"   Checking selector: {selector} ({len(buttons)} found)")
                    
#                     for btn in buttons:
#                         try:
#                             if btn.is_visible(timeout=3000):
#                                 text = btn.inner_text(timeout=2000).strip().lower()
                                
#                                 if text == 'select':
#                                     parent_html = btn.evaluate("el => el.parentElement.parentElement.className")
#                                     if 'filter' not in parent_html.lower() and 'checkbox' not in parent_html.lower():
#                                         dimensions = btn.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
#                                         if dimensions['width'] > 50:
#                                             logging.info(f"   ✓ Valid Select button found with selector: {selector}")
#                                             button_element = btn
#                                             button_found = True
#                                             break
#                         except:
#                             continue
                    
#                     if button_found:
#                         break
#             except Exception as e:
#                 logging.warning(f"   Strategy 2 failed: {e}")
        
#         if not button_found:
#             logging.info("   ✗ Select button NOT found on results page")
#             return None, None
        
#         return page, button_element
        
#     except Exception as e:
#         logging.error(f"   Error finding button on results page: {e}")
#         return None, None

# def find_select_button_on_details_page(page: Page):
#     """Find BEST Select button on DETAILS page - prioritize external links"""
#     try:
#         logging.info(f"\n[DETAILS PAGE] Finding Select button...")
        
#         current_url = page.url
#         if not is_details_page(current_url):
#             logging.error(f"   ERROR: Not on details page! Current URL: {current_url[:80]}")
#             return None, None
        
#         logging.info(f"   ✓ Confirmed on details page (has /config/)")
        
#         logging.info("   Waiting for AJAX content...")
#         try:
#             page.wait_for_function(
#                 "() => document.querySelectorAll('.loading, .spinner').length === 0",
#                 timeout=20000
#             )
#             time.sleep(3)
#         except:
#             logging.info("   AJAX wait completed")
        
#         button_candidates = []
        
#         selectors = [
#             'div.PricedCta_ctaButton__OTZiN a.BpkButton_bpk-button__NDRjO.bpk-button--primary',
#             'div.PricedCta_ctaButton__OTZiN a[data-testid="pricing-item-redirect-button"]',
#             'a[data-testid="pricing-item-redirect-button"]',
#             'div.PricedCta_ctaButton__OTZiN a',
#             'a.BpkButton_bpk-button__NDRjO.bpk-button--primary',
#             'a.bpk-button--primary',
#         ]
        
#         for selector in selectors:
#             try:
#                 logging.info(f"   Checking selector: {selector}")
#                 buttons = page.locator(selector).all()
                
#                 for button in buttons:
#                     try:
#                         if button.is_visible(timeout=5000):
#                             text = button.inner_text(timeout=2000).strip().lower()
#                             if 'select' in text:
#                                 try:
#                                     href = button.evaluate("el => el.href || ''")
#                                     tag = button.evaluate("el => el.tagName")
                                    
#                                     has_external_href = href and 'http' in href and 'skyscanner' not in href
                                    
#                                     dimensions = button.evaluate("el => ({ width: el.clientWidth, height: el.clientHeight })")
#                                     if dimensions['width'] > 0 and dimensions['height'] > 0:
#                                         priority = 10 if has_external_href else 5
#                                         button_candidates.append({
#                                             'button': button,
#                                             'selector': selector,
#                                             'href': href,
#                                             'tag': tag,
#                                             'external': has_external_href,
#                                             'priority': priority
#                                         })
#                                         logging.info(f"   Found candidate: href={href[:60] if href else 'N/A'}, external={has_external_href}")
#                                 except:
#                                     continue
#                     except:
#                         continue
#             except:
#                 continue
        
#         if not button_candidates:
#             logging.info("   ✗ No Select buttons found on details page")
#             return None, None
        
#         button_candidates.sort(key=lambda x: x['priority'], reverse=True)
        
#         logging.info(f"   Found {len(button_candidates)} Select button(s)")
#         best_candidate = button_candidates[0]
#         logging.info(f"   ✓ Using button with href: {best_candidate['href'][:80] if best_candidate['href'] else 'N/A'}")
#         logging.info(f"   External link: {best_candidate['external']}")
        
#         return page, best_candidate['button']
        
#     except Exception as e:
#         logging.error(f"   Error finding button on details page: {e}")
#         return None, None

# def remove_overlays_safely(page: Page):
#     """Aggressively remove ALL blocking overlays and scrims"""
#     try:
#         logging.info("   Removing overlays aggressively...")
#         removed_count = page.evaluate("""
#             () => {
#                 let count = 0;
                
#                 const overlaySelectors = [
#                     'div.bpk-scrim',
#                     'div.bpk-scrim_bpk-scrim__NzY2M',
#                     'div[role="presentation"]',
#                     'div[class*="scrim"]',
#                     '.loading',
#                     '.spinner',
#                     'div[class*="overlay"]',
#                     'div[class*="backdrop"]',
#                 ];
                
#                 overlaySelectors.forEach(selector => {
#                     document.querySelectorAll(selector).forEach(el => {
#                         const rect = el.getBoundingClientRect();
#                         const zIndex = window.getComputedStyle(el).zIndex;
                        
#                         if ((rect.width > 100 || rect.height > 100) && (zIndex === 'auto' || parseInt(zIndex) > 100)) {
#                             el.remove();
#                             count++;
#                         }
#                     });
#                 });
                
#                 const modalContainer = document.getElementById('modal-container');
#                 if (modalContainer) {
#                     modalContainer.querySelectorAll('div[role="presentation"]').forEach(el => {
#                         el.remove();
#                         count++;
#                     });
#                 }
                
#                 document.querySelectorAll('button, a').forEach(el => {
#                     const text = (el.textContent || '').toLowerCase().trim();
#                     if (text === 'select') {
#                         el.style.visibility = 'visible';
#                         el.style.opacity = '1';
#                         el.style.pointerEvents = 'auto';
#                         el.style.display = 'block';
#                     }
#                 });
                
#                 return count;
#             }
#         """)
#         logging.info(f"   Removed {removed_count} blocking elements")
#         time.sleep(1.5)
        
#         try:
#             still_blocking = page.evaluate("""
#                 () => {
#                     const scrim = document.querySelector('div.bpk-scrim, div[role="presentation"][class*="scrim"]');
#                     if (scrim) {
#                         scrim.remove();
#                         return true;
#                     }
#                     return false;
#                 }
#             """)
#             if still_blocking:
#                 logging.info("   Removed additional scrim blocker")
#         except:
#             pass
            
#     except Exception as e:
#         logging.warning(f"   Overlay removal warning: {e}")

# def click_select_button(page: Page, page_type="results"):
#     """Click Select button with URL protection and new tab handling"""
#     try:
#         logging.info(f"\n{'='*60}")
#         logging.info(f"CLICKING SELECT BUTTON ON {page_type.upper()} PAGE")
#         logging.info(f"{'='*60}")
        
#         current_url = page.url
#         logging.info(f"Current URL: {current_url[:100]}...")
        
#         if page_type == "results":
#             if not is_results_page(current_url):
#                 logging.error(f"   ERROR: Not on results page!")
#                 return False
#         elif page_type == "details":
#             if not is_details_page(current_url):
#                 logging.error(f"   ERROR: Not on details page!")
#                 return False
        
#         preserved_url = current_url
#         logging.info(f"   Preserved URL for protection")
        
#         context = page.context
#         initial_page_count = len(context.pages)
        
#         page.wait_for_load_state("domcontentloaded", timeout=60000)
#         time.sleep(random.uniform(3, 5))
        
#         close_popup_safely(page, preserved_url)
#         time.sleep(1)
        
#         if page.url != preserved_url:
#             logging.info(f"   WARNING: URL changed after popup close!")
#             logging.info(f"   Restoring to: {preserved_url[:80]}")
#             try:
#                 page.goto(preserved_url, timeout=30000, wait_until="domcontentloaded")
#                 time.sleep(3)
#             except:
#                 logging.warning("   Failed to restore URL")
#                 return False
        
#         remove_overlays_safely(page)
        
#         if page_type == "results":
#             target_frame, button = find_select_button_on_results_page(page)
#         else:
#             target_frame, button = find_select_button_on_details_page(page)
        
#         if not button:
#             logging.info(f"   ✗ No Select button found!")
#             return False
        
#         logging.info("   Scrolling button into view...")
#         try:
#             button.scroll_into_view_if_needed(timeout=15000)
#             time.sleep(random.uniform(1.5, 2.5))
#         except Exception as e:
#             logging.warning(f"   Scroll warning: {e}")
        
#         if page.url != preserved_url:
#             logging.warning(f"   WARNING: URL changed after scroll!")
#             return False
        
#         try:
#             button_tag = button.evaluate("el => el.tagName")
#             button_href = button.evaluate("el => el.href || 'N/A'") if button_tag.lower() == 'a' else 'N/A'
#             button_onclick = button.evaluate("el => el.onclick ? 'has onclick' : 'no onclick'")
#             logging.info(f"   Button details: Tag={button_tag}, Href={button_href[:60] if button_href != 'N/A' else 'N/A'}, OnClick={button_onclick}")
#         except:
#             pass
        
#         logging.info("   Clicking Select button...")
#         click_success = False
        
#         new_page_promise = None
#         if page_type == "details":
#             logging.info("   Setting up new tab listener...")
#             try:
#                 new_page_promise = context.expect_page(timeout=30000)
#             except:
#                 logging.warning("   New tab listener setup failed")
        
#         for attempt in range(3):
#             logging.info(f"   Click attempt {attempt + 1}/3")
#             try:
#                 expect(button).to_be_visible(timeout=10000)
#                 expect(button).to_be_enabled(timeout=10000)
                
#                 if page_type == "details" and button_href and 'transport_deeplink' in button_href:
#                     logging.info(f"   Strategy: Deeplink click with extended wait")
#                     try:
#                         button.click(timeout=15000, force=True)
#                         click_success = True
#                         logging.info("   ✓ Deeplink click initiated")
                        
#                         logging.info("   Waiting for deeplink redirect (up to 45s)...")
#                         start_wait = time.time()
#                         redirected = False
                        
#                         while time.time() - start_wait < 45:
#                             try:
#                                 current = page.url
#                                 if 'transport_deeplink' not in current and 'skyscanner.co.in/transport/flights/' not in current:
#                                     logging.info(f"   ✓ Redirected to: {current[:80]}")
#                                     redirected = True
#                                     break
#                             except:
#                                 pass
#                             time.sleep(1)
                        
#                         if not redirected:
#                             logging.info("   Deeplink redirect timeout, but click happened")
                        
#                         break
#                     except Exception as e:
#                         logging.warning(f"   Deeplink click failed: {str(e)[:80]}")
                
#                 elif page_type == "details" and button_tag and button_tag.lower() == 'a' and button_href and button_href != 'N/A' and 'http' in button_href and 'skyscanner' not in button_href:
#                     logging.info(f"   Strategy: Direct navigation to external href")
#                     try:
#                         target_url = button_href
#                         logging.info(f"   Target URL: {target_url[:80]}")
#                         page.goto(target_url, timeout=45000, wait_until="load")
#                         click_success = True
#                         logging.info("   ✓ Direct navigation successful")
#                         break
#                     except Exception as e:
#                         logging.warning(f"   Direct navigation failed: {str(e)[:80]}")
                
#                 try:
#                     button.click(timeout=15000, force=True)
#                     click_success = True
#                     logging.info("   ✓ Force click successful")
#                     break
#                 except Exception as e:
#                     logging.warning(f"   Force click failed: {str(e)[:80]}")
                
#                 try:
#                     box = button.bounding_box(timeout=10000)
#                     if box:
#                         center_x = box['x'] + box['width'] / 2
#                         center_y = box['y'] + box['height'] / 2
#                         page.mouse.move(center_x, center_y, steps=random.randint(10, 20))
#                         time.sleep(random.uniform(0.3, 0.7))
#                         button.click(timeout=15000)
#                         click_success = True
#                         logging.info("   ✓ Mouse click successful")
#                         break
#                 except Exception as e:
#                     logging.warning(f"   Mouse click failed: {str(e)[:80]}")
                
#             except Exception as e:
#                 logging.warning(f"   Attempt {attempt + 1} failed: {str(e)[:100]}")
                
#                 if 'not found' in str(e).lower():
#                     logging.info("   Button disappeared - likely page is changing")
#                     click_success = True
#                     time.sleep(5)
#                     break
                
#                 if attempt < 2:
#                     logging.info("   Removing overlays again before retry...")
#                     remove_overlays_safely(page)
#                     time.sleep(2)
        
#         if not click_success:
#             logging.info("   Trying JavaScript approaches...")
            
#             if page_type == "details" and button_href and 'transport_deeplink' in button_href:
#                 try:
#                     logging.info("   JS: Clicking deeplink button...")
#                     button.evaluate("el => el.click()")
#                     click_success = True
#                     logging.info("   ✓ JS deeplink click successful")
                    
#                     logging.info("   Waiting for deeplink redirect...")
#                     time.sleep(10)
#                 except Exception as e:
#                     logging.warning(f"   JS deeplink click failed: {str(e)[:80]}")
            
#             elif page_type == "details":
#                 try:
#                     href = button.evaluate("el => el.href")
#                     if href and 'http' in href:
#                         logging.info(f"   JS: Navigating to href: {href[:80]}")
#                         page.goto(href, timeout=45000, wait_until="load")
#                         click_success = True
#                         logging.info("   ✓ JS navigation successful")
#                     else:
#                         logging.info("   JS: No valid href found")
#                 except Exception as e:
#                     logging.warning(f"   JS href navigation failed: {str(e)[:80]}")
            
#             if not click_success:
#                 try:
#                     button.evaluate("el => el.click()")
#                     click_success = True
#                     logging.info("   ✓ JS click successful")
#                     time.sleep(5)
#                 except Exception as e:
#                     logging.warning(f"   JS click failed: {str(e)[:80]}")
        
#         if not click_success:
#             logging.info("   ✗ All click attempts failed!")
#             return False
        
#         logging.info("   Waiting for navigation to complete...")
        
#         active_page = page
#         new_tab_opened = False
        
#         if page_type == "details":
#             try:
#                 logging.info("   Checking for new tab (extended wait for deeplinks)...")
#                 max_tab_wait = 15
#                 tab_check_start = time.time()
                
#                 while time.time() - tab_check_start < max_tab_wait:
#                     current_page_count = len(context.pages)
#                     if current_page_count > initial_page_count:
#                         new_tab_opened = True
#                         latest_page = context.pages[-1]
#                         logging.info(f"   ✓ New tab detected after {time.time() - tab_check_start:.1f}s!")
#                         logging.info(f"   New tab URL: {latest_page.url[:80]}")
                        
#                         active_page = latest_page
                        
#                         try:
#                             active_page.wait_for_load_state("load", timeout=30000)
#                             logging.info("   New tab loaded successfully")
#                         except:
#                             logging.info("   New tab still loading...")
#                             time.sleep(3)
#                         break
#                     time.sleep(1)
                
#                 if not new_tab_opened:
#                     logging.info("   No new tab detected after extended wait")
#             except Exception as e:
#                 logging.warning(f"   New tab check error: {e}")
        
#         navigation_successful = False
        
#         try:
#             active_page.wait_for_load_state("load", timeout=20000)
#             logging.info("   Page load state reached")
#             navigation_successful = True
#         except Exception as e:
#             logging.warning(f"   Load state timeout: {str(e)[:80]}")
        
#         if not ('transport_deeplink' in active_page.url):
#             try:
#                 active_page.wait_for_load_state("networkidle", timeout=20000)
#                 logging.info("   Network idle reached")
#                 navigation_successful = True
#             except Exception as e:
#                 logging.warning(f"   Network idle timeout: {str(e)[:80]}")
        
#         if not navigation_successful and not new_tab_opened:
#             logging.info("   Waiting for URL change...")
#             max_wait = 30
#             start_wait = time.time()
#             url_changed = False
#             last_url = preserved_url
            
#             while time.time() - start_wait < max_wait:
#                 try:
#                     current = active_page.url
#                     if current != last_url:
#                         logging.info(f"   URL changed: {current[:80]}")
#                         last_url = current
#                         url_changed = True
                        
#                         if 'transport_deeplink' not in current and current != preserved_url:
#                             logging.info("   ✓ Moved away from deeplink")
#                             break
#                 except:
#                     pass
#                 time.sleep(1)
            
#             if url_changed:
#                 time.sleep(3)
#                 try:
#                     active_page.wait_for_load_state("domcontentloaded", timeout=10000)
#                 except:
#                     pass
#                 navigation_successful = True
        
#         time.sleep(3)
        
#         new_url = active_page.url
#         logging.info(f"   Final URL: {new_url[:100]}...")
        
#         if new_tab_opened and page_type == "details":
#             logging.info("   ✓ New tab opened - booking site loaded")
#             return True, active_page
        
#         if page_type == "results":
#             if is_details_page(new_url):
#                 logging.info("   ✓ Successfully navigated to DETAILS page")
#                 return True, active_page
#             else:
#                 logging.info("   ⚠ Warning: Expected details page")
#                 if new_url != preserved_url:
#                     logging.info("   URL did change, checking validity...")
#                     time.sleep(5)
#                     final_url = active_page.url
#                     if is_details_page(final_url):
#                         logging.info("   ✓ Details page loaded after delay")
#                         return True, active_page
#                 return False, None
#         else:
#             if new_tab_opened:
#                 logging.info("   ✓ New tab opened (confirmed success)")
#                 return True, active_page
            
#             if 'skyscanner.co.in' not in new_url:
#                 logging.info("   ✓ Successfully navigated to external booking site")
#                 return True, active_page
            
#             if not is_details_page(new_url):
#                 logging.info("   ✓ Successfully navigated away from details page")
#                 return True, active_page
            
#             logging.info("   Final comprehensive tab check...")
#             time.sleep(3)
#             final_page_count = len(context.pages)
#             if final_page_count > initial_page_count:
#                 logging.info(f"   ✓ New tab detected in final check!")
#                 latest_page = context.pages[-1]
#                 latest_url = latest_page.url
#                 logging.info(f"   New tab URL: {latest_url[:80]}")
                
#                 return True, latest_page
            
#             if new_url != preserved_url:
#                 logging.info("   URL changed within Skyscanner")
                
#                 if 'transport_deeplink' in new_url:
#                     logging.info("   On deeplink page - waiting for external redirect...")
#                     time.sleep(10)
                    
#                     final_url = active_page.url
#                     logging.info(f"   Final check URL: {final_url[:100]}")
                    
#                     if 'skyscanner.co.in' not in final_url:
#                         logging.info("   ✓ Redirected to external site")
#                         return True, active_page
#                     else:
#                         logging.info("   ⚠ Still on Skyscanner after deeplink wait")
#                         if len(context.pages) > initial_page_count:
#                             logging.info("   ✓ But new tab exists - SUCCESS!")
#                             return True, context.pages[-1]
#                         return True, active_page
#                 else:
#                     logging.info("   Waiting for external redirect...")
#                     time.sleep(5)
                    
#                     final_check_url = active_page.url
#                     if not is_details_page(final_check_url):
#                         logging.info("   ✓ Redirect completed")
#                         return True, active_page
#                     else:
#                         logging.info("   ⚠ Still on details page")
#                         return True, active_page
#             else:
#                 logging.info("   URL did not change on main page")
#                 if len(context.pages) > initial_page_count:
#                     logging.info("   ✓ But new tab was opened - SUCCESS!")
#                     return True, context.pages[-1]
                
#                 logging.info("   ✗ No navigation detected")
#                 return False, None
        
#     except Exception as e:
#         logging.error(f"   Error clicking button: {e}")
#         return False

# def parse_proxy_string(s: str):
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None, max_retries=3):
#     """Create profile with retry mechanism"""
#     for retry in range(max_retries):
#         TOKEN = get_next_token()
#         try:
#             logging.info(f"Creating stealth profile: {profile_name} (Attempt {retry + 1}/{max_retries})")
#             logging.info(f"Using token: {TOKEN[:20]}...")
            
#             gl = GoLogin({"token": TOKEN})
            
#             # Add delay to avoid API rate limits
#             if retry > 0:
#                 delay = random.uniform(2, 5)
#                 logging.info(f"Waiting {delay:.1f}s before retry...")
#                 time.sleep(delay)
            
#             profile = gl.createProfileRandomFingerprint({
#                 "os": random.choice(["win", "mac"]),
#                 "name": profile_name,
#                 "timezone": "Asia/Kolkata",
#                 "webgl": {
#                     "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"]),
#                     "renderer": random.choice(["Intel Iris OpenGL Engine", "GeForce GTX 1650/PCIe/SSE2"])
#                 },
#                 "audioContext": {
#                     "enable": True,
#                     "noise": random.uniform(0.0001, 0.0005)
#                 }
#             })
            
#             # Validate response
#             if not profile:
#                 raise Exception("Empty profile response from API")
            
#             if isinstance(profile, dict) and 'id' in profile:
#                 profile_id = profile['id']
#                 logging.info(f"✓ Profile created successfully: {profile_id}")
                
#                 # Configure proxy
#                 if proxy_config:
#                     try:
#                         proxy_data = {
#                             "mode": proxy_config['type'],
#                             "host": proxy_config['host'],
#                             "port": int(proxy_config['port']),
#                             "username": proxy_config.get('username', ''),
#                             "password": proxy_config.get('password', '')
#                         }
#                         gl.changeProfileProxy(profile_id, proxy_data)
#                         logging.info(f"✓ Proxy configured: {proxy_config['host']}")
#                     except Exception as e:
#                         logging.warning(f"Proxy setup warning: {e}")
                
#                 return profile_id, TOKEN
#             else:
#                 raise Exception(f"Invalid profile response: {type(profile)}")
                
#         except json.JSONDecodeError as e:
#             logging.error(f"JSON decode error on attempt {retry + 1}: {e}")
#             if retry < max_retries - 1:
#                 logging.info(f"Retrying with next token...")
#                 continue
#         except Exception as e:
#             logging.error(f"Error creating profile (attempt {retry + 1}): {e}")
#             if retry < max_retries - 1:
#                 logging.info(f"Retrying with next token...")
#                 continue
    
#     logging.error(f"Failed to create profile after {max_retries} attempts")
#     return None, None

# def start_maximum_stealth_browser(profile_id, token):
#     try:
#         gl = GoLogin({
#             "token": token,
#             "profile_id": profile_id
#         })
#         logging.info(f"Starting browser for: {profile_id}")
#         debugger_address = gl.start()
        
#         time.sleep(random.uniform(3, 5))
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         context.set_extra_http_headers({
#             "DNT": "1",
#             "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
#         })
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         logging.error(f"Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     try:
#         logging.info("Injecting stealth...")
        
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
#         """)
        
#         logging.info("Stealth active")
        
#     except Exception as e:
#         logging.warning(f"Stealth injection warning: {e}")

# def handle_captcha_challenge(page: Page, max_retries=3):
#     """Handle CAPTCHA"""
#     for attempt in range(max_retries):
#         try:
#             logging.info(f"\nCAPTCHA Handler - Attempt {attempt + 1}/{max_retries}")
            
#             current_url = page.url
#             if "captcha" not in current_url.lower():
#                 return False
            
#             page.wait_for_load_state("load", timeout=30000)
#             time.sleep(3)
            
#             button_found = False
#             target_frame = page
#             button_element = None
            
#             try:
#                 button_element = page.locator("text=/PRESS.*HOLD/i").first
#                 if button_element.is_visible(timeout=5000):
#                     button_found = True
#                     logging.info("Button found in main page")
#             except:
#                 pass
            
#             if not button_found:
#                 frames = page.frames
#                 for idx, frame in enumerate(frames):
#                     try:
#                         button_element = frame.locator("text=/PRESS.*HOLD/i").first
#                         if button_element.is_visible(timeout=5000):
#                             target_frame = frame
#                             button_found = True
#                             logging.info(f"Button found in frame {idx}")
#                             break
#                     except:
#                         continue
            
#             if not button_found:
#                 if attempt < max_retries - 1:
#                     time.sleep(5)
#                 continue
            
#             bounding_box = button_element.bounding_box()
#             if not bounding_box:
#                 continue
            
#             center_x = bounding_box['x'] + bounding_box['width'] / 2
#             center_y = bounding_box['y'] + bounding_box['height'] / 2
            
#             page.mouse.move(center_x, center_y, steps=25)
#             time.sleep(random.uniform(0.3, 0.6))
#             page.mouse.down()
            
#             hold_duration = 90
#             start_time = time.time()
            
#             while time.time() - start_time < hold_duration:
#                 elapsed = time.time() - start_time
                
#                 try:
#                     if "captcha" not in page.url.lower():
#                         logging.info(f"\nCAPTCHA solved after {elapsed:.1f}s")
#                         page.mouse.up()
#                         return True
#                 except:
#                     pass
                
#                 time.sleep(0.5)
            
#             page.mouse.up()
#             time.sleep(3)
            
#             if "captcha" not in page.url.lower():
#                 return True
                
#         except Exception as e:
#             logging.error(f"Attempt {attempt + 1} error: {e}")
#             if attempt < max_retries - 1:
#                 time.sleep(5)
    
#     return False

# def ultimate_human_browsing(page: Page):
#     try:
#         logging.info("Starting human behavior simulation...")
        
#         google_url = "https://www.google.co.in/"
#         logging.info(f"\nNavigating to Google: {google_url}")
        
#         for attempt in range(3):
#             try:
#                 page.goto(google_url, timeout=60000, wait_until="networkidle")
#                 break
#             except:
#                 if attempt == 2:
#                     return False
        
#         time.sleep(3)
        
#         for url in TARGET_URLS:
#             logging.info(f"\n{'='*60}")
#             logging.info(f"STEP 1: Affiliate URL")
#             logging.info(f"{'='*60}")
            
#             for attempt in range(3):
#                 try:
#                     page.goto(url, timeout=60000, wait_until="networkidle")
#                     break
#                 except:
#                     if attempt == 2:
#                         continue
            
#             time.sleep(random.uniform(5, 8))
            
#             if "captcha" in page.url.lower():
#                 if not handle_captcha_challenge(page):
#                     continue
            
#             logging.info(f"\n{'='*60}")
#             logging.info(f"STEP 2: Flight Search (RESULTS PAGE)")
#             logging.info(f"{'='*60}")
            
#             flight_loaded = False
            
#             for flight_attempt in range(3):
#                 logging.info(f"\nAttempt {flight_attempt + 1}/3")
                
#                 flight_url = generate_random_flight_url()
                
#                 for nav_attempt in range(3):
#                     try:
#                         page.goto(flight_url, timeout=60000, wait_until="networkidle")
#                         break
#                     except:
#                         if nav_attempt == 2:
#                             break
                
#                 time.sleep(random.uniform(5, 8))
                
#                 current_url = page.url
                
#                 if "captcha" in current_url.lower():
#                     if not handle_captcha_challenge(page):
#                         if flight_attempt < 2:
#                             continue
#                         else:
#                             break
                
#                 if not is_results_page(current_url):
#                     if flight_attempt < 2:
#                         continue
#                     else:
#                         break
                
#                 logging.info("✓ On RESULTS page")
                
#                 time.sleep(random.uniform(*PAGE_LOAD_PATIENCE))
                
#                 logging.info(f"\n{'='*60}")
#                 logging.info(f"STEP 3: First Select Button")
#                 logging.info(f"{'='*60}")
                
#                 if click_select_button(page, "results"):
#                     time.sleep(3)
#                     new_url = page.url
#                     if is_details_page(new_url):
#                         logging.info("✓ Moved to DETAILS page")
#                         flight_loaded = True
#                         break
#                     elif is_results_page(new_url):
#                         logging.error("ERROR: Still on results page")
#                         if flight_attempt < 2:
#                             continue
#                 else:
#                     if flight_attempt < 2:
#                         continue
            
#             if not flight_loaded:
#                 logging.info("\n✗ Failed to reach details page")
#                 continue
            
#             current_url = page.url
            
#             if not is_details_page(current_url):
#                 logging.error(f"ERROR: Not on details page!")
#                 continue
            
#             logging.info("✓ Confirmed on DETAILS page")
            
#             time.sleep(random.uniform(3, 6))
            
#             if "captcha" in page.url.lower():
#                 if not handle_captcha_challenge(page):
#                     continue
            
#             if not is_details_page(page.url):
#                 logging.error("ERROR: Lost details page before second click")
#                 continue
            
#             logging.info(f"\n{'='*60}")
#             logging.info(f"STEP 4: Second Select Button")
#             logging.info(f"{'='*60}")
            
#             logging.info(f"Pre-click URL check: {page.url[:80]}")
#             if not is_details_page(page.url):
#                 logging.error("ERROR: Not on details page before click!")
#                 continue
            
#             click_result = click_select_button(page, "details")
#             if isinstance(click_result, tuple):
#                 success, booking_page = click_result
#             else:
#                 success = click_result
#                 booking_page = page
            
#             if success:
#                 logging.info("✓ Second Select button clicked successfully")
                
#                 if booking_page and booking_page != page:
#                     logging.info(f"   Using new booking page for human behavior")
#                     final_page = booking_page
#                 else:
#                     final_page = page
                
#                 time.sleep(3)
                
#                 human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#                 logging.info(f"\nFinal page human behavior for {human_time:.1f}s")
#                 logging.info(f"Final page URL: {final_page.url[:80]}")
                
#                 start_time = time.time()
#                 while time.time() - start_time < human_time:
#                     try:
#                         action = random.choice(['scroll', 'mouse_move', 'pause'])
                        
#                         if action == 'scroll':
#                             final_page.evaluate(f"window.scrollBy({{top: {random.randint(50, 150)}, behavior: 'smooth'}});")
#                         elif action == 'mouse_move':
#                             final_page.mouse.move(random.randint(100, 800), random.randint(100, 600))
#                         else:
#                             time.sleep(random.uniform(1, 3))
                        
#                         time.sleep(random.uniform(1, 2))
#                     except Exception as e:
#                         logging.warning(f"   Human behavior warning: {str(e)[:50]}")
#                         break
                
#                 logging.info("✓ Human behavior completed on booking page")
#             else:
#                 logging.info("✗ Failed second click")
#                 continue
        
#         logging.info("\nHuman behavior complete")
#         return True
        
#     except Exception as e:
#         logging.error(f"Human browsing error: {e}")
#         logging.error(traceback.format_exc())
#         return False

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         logging.info("Browser session terminated")
#     except Exception as e:
#         logging.warning(f"Cleanup warning: {e}")

# def run_single_session(session_num, total_sessions):
#     """Run a single session in a thread"""
#     try:
#         logging.info(f"\n{'='*80}")
#         logging.info(f"SESSION {session_num}/{total_sessions} STARTING")
#         logging.info(f"{'='*80}")
        
#         profile_name = f"stealth_flight_{session_num}_{random.randint(100000, 999999)}"
        
#         random_country = random.choice(COUNTRY_CODES)
#         proxy_str = PROXY_TEMPLATE.replace('country-in', f'country-{random_country}')
#         proxy_config = parse_proxy_string(proxy_str)
        
#         logging.info(f"Session {session_num}: Creating profile with proxy country={random_country}")
        
#         profile_id, token = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if not profile_id:
#             logging.error(f"Session {session_num}: Profile creation failed")
#             return False
        
#         time.sleep(random.uniform(2, 4))
        
#         gl, pw, browser, page = start_maximum_stealth_browser(profile_id, token)
        
#         if not page:
#             logging.error(f"Session {session_num}: Browser start failed")
#             return False
        
#         try:
#             success = ultimate_human_browsing(page)
            
#             if success:
#                 logging.info(f"\n{'='*80}")
#                 logging.info(f"SESSION {session_num} - SUCCESS ✓")
#                 logging.info(f"{'='*80}")
#                 return True
#             else:
#                 logging.info(f"\n{'='*80}")
#                 logging.info(f"SESSION {session_num} - FAILED ✗")
#                 logging.info(f"{'='*80}")
#                 return False
#         finally:
#             time.sleep(random.uniform(3, 6))
#             cleanup_browser(gl, pw, browser)
            
#     except Exception as e:
#         logging.error(f"Session {session_num} error: {e}")
#         logging.error(traceback.format_exc())
#         return False

# def run_batch_sessions(batch_num, sessions_in_batch, total_batches):
#     """Run a batch of concurrent sessions"""
#     logging.info(f"\n{'#'*100}")
#     logging.info(f"BATCH {batch_num}/{total_batches} - Starting {sessions_in_batch} concurrent sessions")
#     logging.info(f"{'#'*100}")
    
#     results = []
#     threads = []
    
#     for i in range(sessions_in_batch):
#         session_num = (batch_num - 1) * SESSIONS_PER_BATCH + i + 1
        
#         # Add random delay between starting each session
#         if i > 0:
#             delay = random.uniform(*DELAY_BETWEEN_SESSIONS)
#             logging.info(f"\nWaiting {delay:.1f}s before starting next session in batch...")
#             time.sleep(delay)
        
#         thread = threading.Thread(
#             target=lambda snum=session_num, total=sessions_in_batch: results.append(
#                 run_single_session(snum, TOTAL_VISITS)
#             )
#         )
#         thread.start()
#         threads.append(thread)
        
#         logging.info(f"Thread started for Session {session_num}")
    
#     # Wait for all threads in this batch to complete
#     logging.info(f"\nWaiting for all {len(threads)} sessions in Batch {batch_num} to complete...")
#     for thread in threads:
#         thread.join()
    
#     success_count = sum(1 for r in results if r)
#     logging.info(f"\n{'#'*100}")
#     logging.info(f"BATCH {batch_num} COMPLETE - {success_count}/{sessions_in_batch} sessions successful")
#     logging.info(f"{'#'*100}")
    
#     return success_count

# def run_ultimate_stealth_test():
#     logging.info(f"\n{'*'*100}")
#     logging.info("MULTI-SESSION BATCH SKYSCANNER BOT")
#     logging.info(f"{'*'*100}")
#     logging.info(f"Configuration:")
#     logging.info(f"  Total Visits: {TOTAL_VISITS}")
#     logging.info(f"  Sessions Per Batch: {SESSIONS_PER_BATCH}")
#     logging.info(f"  Delay Between Sessions: {DELAY_BETWEEN_SESSIONS[0]}-{DELAY_BETWEEN_SESSIONS[1]}s")
#     logging.info(f"  Delay Between Batches: {DELAY_BETWEEN_BATCHES[0]}-{DELAY_BETWEEN_BATCHES[1]}s")
#     logging.info(f"{'*'*100}\n")
    
#     total_batches = (TOTAL_VISITS + SESSIONS_PER_BATCH - 1) // SESSIONS_PER_BATCH
#     total_successful = 0
    
#     for batch_num in range(1, total_batches + 1):
#         # Calculate how many sessions for this batch
#         remaining_visits = TOTAL_VISITS - (batch_num - 1) * SESSIONS_PER_BATCH
#         sessions_in_batch = min(SESSIONS_PER_BATCH, remaining_visits)
        
#         # Run the batch
#         successful_in_batch = run_batch_sessions(batch_num, sessions_in_batch, total_batches)
#         total_successful += successful_in_batch
        
#         # Delay between batches (except after last batch)
#         if batch_num < total_batches:
#             delay = random.uniform(*DELAY_BETWEEN_BATCHES)
#             logging.info(f"\n{'~'*100}")
#             logging.info(f"Batch {batch_num} complete. Waiting {delay:.1f}s before starting Batch {batch_num + 1}...")
#             logging.info(f"{'~'*100}\n")
#             time.sleep(delay)
    
#     logging.info(f"\n{'*'*100}")
#     logging.info(f"ALL BATCHES COMPLETE!")
#     logging.info(f"Total Success Rate: {total_successful}/{TOTAL_VISITS} visits")
#     logging.info(f"Success Percentage: {(total_successful/TOTAL_VISITS*100):.2f}%")
#     logging.info(f"{'*'*100}")

# if __name__ == "__main__":
#     logging.info("MULTI-SESSION BATCH SKYSCANNER BOT WITH CONCURRENT EXECUTION")
#     logging.info("=" * 100)

#     if not GOLOGIN_AVAILABLE:
#         logging.error("GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         logging.info("\nTest interrupted by user")
#     except Exception as e:
#         logging.error(f"Fatal error: {e}")
#         logging.error(traceback.format_exc())