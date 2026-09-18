# import asyncio
# import json
# from datetime import datetime
# from playwright.async_api import async_playwright

# async def scrape_sportskeeda_cricket():
#     print("🚀 Sportskeeda Cricket Scraper Started...")
    
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         context = await browser.new_context(
#             viewport={"width": 1440, "height": 1000},
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
#         )
#         page = await context.new_page()
        
#         try:
#             await page.goto("https://www.sportskeeda.com/cricket", timeout=90000, wait_until="domcontentloaded")
#             await page.wait_for_timeout(8000)  # Dynamic content load hone do
            
#             print("✅ Page Loaded")

#             # === 1. Extract All Tabs ===
#             tabs = await page.evaluate("""
#                 () => {
#                     const tabContainer = document.querySelector('.keeda_carousel_tab_container');
#                     if (!tabContainer) return [];
                    
#                     return Array.from(tabContainer.querySelectorAll('.keeda_carousel_tab_item')).map(tab => ({
#                         name: tab.innerText.trim(),
#                         event_slug: tab.getAttribute('data-event-slug'),
#                         event_name: tab.getAttribute('data-event-name'),
#                         is_active: tab.classList.contains('active')
#                     }));
#                 }
#             """)
            
#             print(f"📋 Found {len(tabs)} Tabs:")
#             for t in tabs:
#                 print(f"   • {t['name']} ({t['event_slug']})")

#             all_matches = []

#             # === 2. Scrape Matches from Featured (default) + other tabs ===
#             for tab in tabs[:6]:  # Pehle 6 tabs (Featured + important series)
#                 print(f"\n🔄 Switching to Tab: {tab['name']}")
                
#                 # Click on tab if not active
#                 if not tab['is_active']:
#                     try:
#                         await page.click(f'[data-event-slug="{tab["event_slug"]}"]', timeout=5000)
#                         await page.wait_for_timeout(4000)
#                     except:
#                         print("   ⚠️ Could not click tab, continuing...")
                
#                 # Extract match cards
#                 matches = await page.evaluate("""
#                     () => {
#                         const matches = [];
#                         const cards = document.querySelectorAll('.keeda_cricket_single_match_container, .keeda_cricket_single_match');
                        
#                         cards.forEach(card => {
#                             const matchId = card.getAttribute('data-match-id') || 
#                                            card.querySelector('.keeda_cricket_match_list')?.getAttribute('data-match-id');
                            
#                             const team1El = card.querySelector('[data-team-name]');
#                             const team2El = Array.from(card.querySelectorAll('[data-team-name]')).find(el => 
#                                 el !== team1El);
                            
#                             const matchType = card.querySelector('.cricket-match-card--match-type')?.innerText.trim();
#                             const venue = card.querySelector('.cricket-match-card--match-venue')?.innerText.trim();
                            
#                             const dateEl = card.querySelector('.match-date');
#                             const timeEl = card.querySelector('.match-time');
#                             const statusEl = card.querySelector('.keeda_widget_result_info, .scorecard-countdown-timer');
                            
#                             const linkEl = card.querySelector('a.keeda_cricket_match_link, a[href*="/live-cricket-score"]');
                            
#                             const team1 = team1El ? {
#                                 name: team1El.getAttribute('data-team-name') || team1El.querySelector('.keeda_widget_team_name')?.innerText.trim(),
#                                 flag: team1El.querySelector('img')?.src || ''
#                             } : null;
                            
#                             const team2 = team2El ? {
#                                 name: team2El.getAttribute('data-team-name') || team2El.querySelector('.keeda_widget_team_name')?.innerText.trim(),
#                                 flag: team2El.querySelector('img')?.src || ''
#                             } : null;
                            
#                             if (team1 && team2) {
#                                 matches.push({
#                                     match_id: matchId,
#                                     tab: document.querySelector('.keeda_carousel_tab_item.active')?.innerText.trim() || '',
#                                     team1: team1,
#                                     team2: team2,
#                                     match_type: matchType || '',
#                                     venue_info: venue || '',
#                                     date: dateEl ? dateEl.innerText.trim() : '',
#                                     time: timeEl ? timeEl.innerText.trim() : '',
#                                     status: statusEl ? statusEl.innerText.trim() : 'Upcoming',
#                                     full_link: linkEl ? linkEl.href : '',
#                                     scraped_at: new Date().toISOString()
#                                 });
#                             }
#                         });
#                         return matches;
#                     }
#                 """)
                
#                 all_matches.extend(matches)
#                 print(f"   ✅ Extracted {len(matches)} matches from {tab['name']}")
#                 await page.wait_for_timeout(2000)

#             # Remove duplicate matches based on match_id or link
#             unique_matches = {m['full_link'] or m['match_id']: m for m in all_matches if m['full_link'] or m['match_id']}
#             final_matches = list(unique_matches.values())

#             # === Save to JSON ===
#             output = {
#                 "site": "sportskeeda.com/cricket",
#                 "total_tabs": len(tabs),
#                 "total_matches": len(final_matches),
#                 "scraped_at": datetime.now().isoformat(),
#                 "tabs": tabs,
#                 "matches": final_matches
#             }
            
#             with open("sportskeeda_cricket_matches.json", "w", encoding="utf-8") as f:
#                 json.dump(output, f, indent=2, ensure_ascii=False)
            
#             print(f"\n🎉 Scraping Completed!")
#             print(f"   📊 Total Unique Matches: {len(final_matches)}")
#             print(f"   💾 Saved: sportskeeda_cricket_matches.json")
            
#             # Quick Preview
#             print("\n🔍 First 3 Matches:")
#             for i, m in enumerate(final_matches[:3]):
#                 print(f"   {i+1}. {m['team1']['name']} vs {m['team2']['name']} | {m['match_type']} | {m['date']} {m['time']}")
                
#         except Exception as e:
#             print(f"❌ Error: {e}")
#         finally:
#             await browser.close()

# if __name__ == "__main__":
#     asyncio.run(scrape_sportskeeda_cricket())




import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

async def clean_team_name(name):
    if not name:
        return ""
    # Remove scores and extra text
    name = re.sub(r"\d+/\d+\s*\(\d+\)", "", name)
    name = re.sub(r"\n.*", "", name)
    return name.strip()

async def scrape_match_details(page, base_url):
    try:
        match_center_url = base_url.rstrip('/') + '/match-center'
        print(f"   🔍 Scraping: {match_center_url}")
        
        await page.goto(match_center_url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)

        data = await page.evaluate("""
            () => {
                const clean = (t) => t ? t.replace(/\\s+/g, ' ').trim() : '';
                
                const getAfterLabel = (label) => {
                    const els = Array.from(document.querySelectorAll('h2, h3, strong, div, span, p'));
                    for (let el of els) {
                        if (el.innerText && el.innerText.trim().includes(label)) {
                            let sibling = el.nextElementSibling;
                            while (sibling) {
                                const text = clean(sibling.innerText);
                                if (text.length > 5 && !text.includes('{') && !text.includes('.message-card')) {
                                    return text;
                                }
                                sibling = sibling.nextElementSibling;
                            }
                            // Fallback to parent text
                            const parentText = clean(el.parentElement ? el.parentElement.innerText : '');
                            if (parentText.includes(label)) {
                                return parentText.split(label)[1]?.trim().split('\\n')[0] || '';
                            }
                        }
                    }
                    return '';
                };

                const date_time = getAfterLabel('Date & Time') || getAfterLabel('Date') || '';
                const venue = getAfterLabel('Venue') || '';
                const match_info = getAfterLabel('Match') || '';
                const toss = getAfterLabel('Toss') || '';
                
                // Pitch Report
                let pitch = '';
                const pitchHeaders = Array.from(document.querySelectorAll('h2, h3'));
                for (let h of pitchHeaders) {
                    if (h.innerText.toLowerCase().includes('pitch') || h.innerText.toLowerCase().includes('venue stats')) {
                        pitch = clean(h.parentElement ? h.parentElement.innerText : h.innerText);
                        break;
                    }
                }

                return {
                    date_time: clean(date_time),
                    venue: clean(venue),
                    match_info: clean(match_info),
                    toss: clean(toss),
                    pitch_report: pitch,
                    squads_available: document.body.innerText.includes('Squads') || document.body.innerText.includes('Playing XI'),
                    full_url: window.location.href
                };
            }
        """)

        return data
    except Exception as e:
        print(f"   ❌ Detail error: {e}")
        return {"error": str(e)}


async def scrape_sportskeeda_cricket():
    print("🚀 Sportskeeda Cricket Scraper (Fixed Version)")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 1000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto("https://www.sportskeeda.com/cricket", timeout=90000, wait_until="domcontentloaded")
            await page.wait_for_timeout(8000)
            print("✅ Page Loaded")

            # Tabs
            tabs = await page.evaluate("""
                () => Array.from(document.querySelectorAll('.keeda_carousel_tab_item')).map(tab => ({
                    name: tab.innerText.trim(),
                    slug: tab.getAttribute('data-event-slug')
                }))
            """)

            all_matches = []

            for tab in tabs[:6]:
                print(f"\n🔄 Tab: {tab['name']}")
                if tab['slug']:
                    try:
                        await page.click(f'[data-event-slug="{tab["slug"]}"]', timeout=5000)
                        await page.wait_for_timeout(4000)
                    except:
                        pass

                matches = await page.evaluate("""
                    () => {
                        const results = [];
                        const cards = document.querySelectorAll('.keeda_cricket_single_match_container, .keeda_cricket_single_match, .keeda_cricket_match_list');
                        
                        cards.forEach(card => {
                            const link = card.querySelector('a[href*="/live-cricket-score"]');
                            if (!link) return;
                            
                            const href = link.href;
                            const teamEls = Array.from(card.querySelectorAll('.keeda_widget_team_name, [data-team-name], .team-name'));
                            
                            let team1 = teamEls[0] ? teamEls[0].innerText.trim() : '';
                            let team2 = teamEls[1] ? teamEls[1].innerText.trim() : '';
                            
                            if (!team2) {
                                const allText = card.innerText;
                                const teams = allText.match(/[A-Z][A-Z0-9-]+\s*[A-Z]?/g) || [];
                                if (teams.length >= 2) {
                                    team1 = teams[0];
                                    team2 = teams[1];
                                }
                            }
                            
                            if (team1 && team2) {
                                results.push({
                                    match_id: href.split('/').pop(),
                                    tab: document.querySelector('.keeda_carousel_tab_item.active')?.innerText.trim() || '',
                                    team1_raw: team1,
                                    team2_raw: team2,
                                    match_type: card.querySelector('.cricket-match-card--match-type, .match-type')?.innerText.trim() || '',
                                    date: card.querySelector('.match-date')?.innerText.trim() || '',
                                    time: card.querySelector('.match-time')?.innerText.trim() || '',
                                    base_link: href
                                });
                            }
                        });
                        return results;
                    }
                """)

                all_matches.extend(matches)
                print(f"   ✅ {len(matches)} matches")
                await page.wait_for_timeout(2000)

            # Clean & Unique
            unique = {}
            for m in all_matches:
                key = m['base_link']
                if key:
                    m['team1'] = await clean_team_name(m['team1_raw'])
                    m['team2'] = await clean_team_name(m['team2_raw'])
                    unique[key] = m

            final_matches = list(unique.values())
            print(f"\n📊 Total Unique Matches: {len(final_matches)}")

            # Detailed Scraping (limit for testing)
            detailed = []
            for i, match in enumerate(final_matches[:10]):   # Badhao jab confident ho
                print(f"   [{i+1}/{len(final_matches)}] {match['team1']} vs {match['team2']}")
                detail_page = await context.new_page()
                try:
                    details = await scrape_match_details(detail_page, match['base_link'])
                    match.update(details)
                    detailed.append(match)
                finally:
                    await detail_page.close()
                await asyncio.sleep(3)

            # Save
            output = {
                "site": "sportskeeda.com/cricket",
                "total_matches": len(detailed),
                "scraped_at": datetime.now().isoformat(),
                "matches": detailed
            }

            filename = f"sportskeeda_cricket_clean_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

            print(f"\n🎉 Saved: {filename}")

            # Preview
            for m in detailed[:3]:
                print(f"\n{m['team1']} vs {m['team2']}")
                print(f"   📅 {m.get('date_time')}")
                print(f"   📍 {m.get('venue')}")

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(scrape_sportskeeda_cricket())