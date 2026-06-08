# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: judge_information.voiceover.ts >> Judge Information — VoiceOver full-page sweep >> VoiceOver announces all page content — every section heading, every judge card, and both bottom tiles
- Location: playwright/tests/judge_information.voiceover.ts:944:18

# Error details

```
Error: VoiceOver never announced: 'Special Trial Judge Biographies' h2

expect(received).toContain(expected) // indexOf

Expected substring: "special trial judge biographies"
Received string:    "heading level 1 judge information button. you are currently on a heading level 1.
see the judge's biography by clicking on the cards.. you are currently on a selectable text.
filter judges by type group. you are currently in a group.
all judges selected toggle button. you are currently on a toggle button. to select or deselect this checkbox, press control-option-space.
judges toggle button. you are currently on a toggle button. to select or deselect this checkbox, press control-option-space.
senior judges toggle button. you are currently on a toggle button. to select or deselect this checkbox, press control-option-space.
special trial judges toggle button. you are currently on a toggle button. to select or deselect this checkbox, press control-option-space.
senior special trial judges toggle button. you are currently on a toggle button. to select or deselect this checkbox, press control-option-space.
filter judges by type group. you are currently on a group.
heading level 2 judge biographies. you are currently on a heading level 2.
patrick j. urda chief judge link. you are currently on a link. to click this link, press control-option-space.
heading level 2 senior judge biographies. you are currently on a heading level 2.
mary ann cohen senior judge link. you are currently on a link. to click this link, press control-option-space.
heading not found
maurice b. foley senior judge link. you are currently on a link. to click this link, press control-option-space.
heading not found
last link maurice b. foley senior judge link
joseph robert goeke senior judge link. you are currently on a link. to click this link, press control-option-space.
david gustafson senior judge link. you are currently on a link. to click this link, press control-option-space.
last link david gustafson senior judge link
james s. halpern senior judge link. you are currently on a link. to click this link, press control-option-space.
mark v. holmes senior judge link. you are currently on a link. to click this link, press control-option-space.
albert g. lauber senior judge link. you are currently on a link. to click this link, press control-option-space.
last link albert g. lauber senior judge link
l. paige marvel senior judge link. you are currently on a link. to click this link, press control-option-space.
richard t. morrison senior judge link. you are currently on a link. to click this link, press control-option-space.
elizabeth crewson paris senior judge link. you are currently on a link. to click this link, press control-option-space.
michael b. thornton senior judge link. you are currently on a link. to click this link, press control-option-space.
juan f. vasquez senior judge link. you are currently on a link. to click this link, press control-option-space.
zachary s. fried chief special trial judge link. you are currently on a link. to click this link, press control-option-space.
diana l. leyden special trial judge link. you are currently on a link. to click this link, press control-option-space.
peter j. panuthos special trial judge link. you are currently on a link. to click this link, press control-option-space."
```

# Page snapshot

```yaml
- generic [ref=e1]:
  - region "Official website of the United States government" [ref=e2]:
    - generic [ref=e5]:
      - img [ref=e7]
      - paragraph [ref=e9]: An official website of the United States government
      - button "Here’s how you know" [ref=e10] [cursor=pointer]
  - generic [ref=e13]:
    - paragraph [ref=e14]:
      - text: This is a testing site for the U.S. Tax Court and not intended for public use. To learn more about starting a case, visit the
      - link "U.S. Tax Court website." [ref=e15] [cursor=pointer]:
        - /url: https://www.ustaxcourt.gov/
    - button "Close alert banner" [ref=e16] [cursor=pointer]:
      - img [ref=e17]
  - banner [ref=e20]:
    - link "Skip to main content" [ref=e21] [cursor=pointer]:
      - /url: "#main-content"
    - generic [ref=e24]:
      - generic [ref=e25]:
        - link "US Tax Court Logo" [ref=e26] [cursor=pointer]:
          - /url: /
          - img "US Tax Court Logo" [ref=e27]
        - generic [ref=e28]:
          - link "United States Tax Court" [ref=e29] [cursor=pointer]:
            - /url: /
          - generic [ref=e31]:
            - paragraph [ref=e32]: Patrick J. Urda, Chief Judge
            - paragraph [ref=e33]: Charles G. Jeane, Clerk of the Court
      - generic [ref=e35]:
        - textbox "Search" [ref=e36]:
          - /placeholder: Enter search text
        - button "Search" [ref=e37] [cursor=pointer]
    - list [ref=e39]:
      - text:  
      - listitem [ref=e40]:
        - button "COURT INFORMATION " [ref=e41] [cursor=pointer]:
          - generic [ref=e42]: COURT INFORMATION
          - generic [ref=e43]:
            - generic [ref=e44]: 
            - text: 
      - listitem [ref=e45]:
        - button "RULES & GUIDANCE " [ref=e46] [cursor=pointer]:
          - generic [ref=e47]: RULES & GUIDANCE
          - generic [ref=e48]:
            - generic [ref=e49]: 
            - text: 
      - listitem [ref=e50]:
        - button "ORDERS & OPINIONS " [ref=e51] [cursor=pointer]:
          - generic [ref=e52]: ORDERS & OPINIONS
          - generic [ref=e53]:
            - generic [ref=e54]: 
            - text: 
      - listitem [ref=e55]:
        - button "TRIALS & CASE MANAGEMENT " [ref=e56] [cursor=pointer]:
          - generic [ref=e57]: TRIALS & CASE MANAGEMENT
          - generic [ref=e58]:
            - generic [ref=e59]: 
            - text: 
      - listitem [ref=e60]:
        - button "RESOURCES " [ref=e61] [cursor=pointer]:
          - generic [ref=e62]: RESOURCES
          - generic [ref=e63]:
            - generic [ref=e64]: 
            - text: 
  - link "Give Feedback" [ref=e65] [cursor=pointer]:
    - /url: https://forms.office.com/r/45R5iAguPG
  - main [ref=e66]:
    - generic [ref=e67]:
      - heading "Judge Information" [level=1] [ref=e68]:
        - button "Judge Information" [ref=e69]
      - generic [ref=e70]: See the Judge's biography by clicking on the cards.
      - group "Filter judges by type" [ref=e71]:
        - button "All Judges" [pressed] [ref=e72] [cursor=pointer]
        - button "Judges" [ref=e73] [cursor=pointer]
        - button "Senior Judges" [ref=e74] [cursor=pointer]
        - button "Special Trial Judges" [ref=e75] [cursor=pointer]
        - button "Senior Special Trial Judges" [ref=e76] [cursor=pointer]
      - text:      
      - generic [ref=e77]:
        - heading "Judge Biographies" [level=2] [ref=e78]
        - generic [ref=e79]:
          - link "Patrick J. Urda Chief Judge" [ref=e80] [cursor=pointer]:
            - /url: /judges/16/urda/
            - generic [ref=e81]: Patrick J. Urda
            - generic [ref=e82]: Chief Judge
          - link "Jeffrey S. Arbeit Judge" [ref=e83] [cursor=pointer]:
            - /url: /judges/2/arbeit/
            - generic [ref=e84]: Jeffrey S. Arbeit
            - generic [ref=e85]: Judge
          - link "Tamara W. Ashford Judge" [ref=e86] [cursor=pointer]:
            - /url: /judges/3/ashford/
            - generic [ref=e87]: Tamara W. Ashford
            - generic [ref=e88]: Judge
          - link "Ronald L. Buch Judge" [ref=e89] [cursor=pointer]:
            - /url: /judges/4/buch/
            - generic [ref=e90]: Ronald L. Buch
            - generic [ref=e91]: Judge
          - link "Elizabeth A. Copeland Judge" [ref=e92] [cursor=pointer]:
            - /url: /judges/5/copeland/
            - generic [ref=e93]: Elizabeth A. Copeland
            - generic [ref=e94]: Judge
          - link "Cathy Fung Judge" [ref=e95] [cursor=pointer]:
            - /url: /judges/6/fung/
            - generic [ref=e96]: Cathy Fung
            - generic [ref=e97]: Judge
          - link "Travis A. Greaves Judge" [ref=e98] [cursor=pointer]:
            - /url: /judges/7/greaves/
            - generic [ref=e99]: Travis A. Greaves
            - generic [ref=e100]: Judge
          - link "Benjamin A. Guider III Judge" [ref=e101] [cursor=pointer]:
            - /url: /judges/8/guider/
            - generic [ref=e102]: Benjamin A. Guider III
            - generic [ref=e103]: Judge
          - link "Rose E. Jenkins Judge" [ref=e104] [cursor=pointer]:
            - /url: /judges/9/jenkins/
            - generic [ref=e105]: Rose E. Jenkins
            - generic [ref=e106]: Judge
          - link "Courtney D. Jones Judge" [ref=e107] [cursor=pointer]:
            - /url: /judges/10/jones/
            - generic [ref=e108]: Courtney D. Jones
            - generic [ref=e109]: Judge
          - link "Kathleen Kerrigan Judge" [ref=e110] [cursor=pointer]:
            - /url: /judges/1/kerrigan/
            - generic [ref=e111]: Kathleen Kerrigan
            - generic [ref=e112]: Judge
          - link "Adam B. Landy Judge" [ref=e113] [cursor=pointer]:
            - /url: /judges/11/landy/
            - generic [ref=e114]: Adam B. Landy
            - generic [ref=e115]: Judge
          - link "Alina I. Marshall Judge" [ref=e116] [cursor=pointer]:
            - /url: /judges/12/marshall/
            - generic [ref=e117]: Alina I. Marshall
            - generic [ref=e118]: Judge
          - link "Joseph W. Nega Judge" [ref=e119] [cursor=pointer]:
            - /url: /judges/13/nega/
            - generic [ref=e120]: Joseph W. Nega
            - generic [ref=e121]: Judge
          - link "Cary Douglas Pugh Judge" [ref=e122] [cursor=pointer]:
            - /url: /judges/14/pugh/
            - generic [ref=e123]: Cary Douglas Pugh
            - generic [ref=e124]: Judge
          - link "Emin Toro Judge" [ref=e125] [cursor=pointer]:
            - /url: /judges/15/toro/
            - generic [ref=e126]: Emin Toro
            - generic [ref=e127]: Judge
          - link "Kashi Way Judge" [ref=e128] [cursor=pointer]:
            - /url: /judges/17/way/
            - generic [ref=e129]: Kashi Way
            - generic [ref=e130]: Judge
          - link "Christian N. Weiler Judge" [ref=e131] [cursor=pointer]:
            - /url: /judges/18/weiler/
            - generic [ref=e132]: Christian N. Weiler
            - generic [ref=e133]: Judge
      - generic [ref=e134]:
        - heading "Senior Judge Biographies" [level=2] [ref=e135]
        - generic [ref=e136]:
          - link "Mary Ann Cohen Senior Judge" [ref=e137] [cursor=pointer]:
            - /url: /judges/19/cohen/
            - generic [ref=e138]: Mary Ann Cohen
            - generic [ref=e139]: Senior Judge
          - link "Maurice B. Foley Senior Judge" [ref=e140] [cursor=pointer]:
            - /url: /judges/20/foley/
            - generic [ref=e141]: Maurice B. Foley
            - generic [ref=e142]: Senior Judge
          - link "Joseph Robert Goeke Senior Judge" [ref=e143] [cursor=pointer]:
            - /url: /judges/21/goeke/
            - generic [ref=e144]: Joseph Robert Goeke
            - generic [ref=e145]: Senior Judge
          - link "David Gustafson Senior Judge" [ref=e146] [cursor=pointer]:
            - /url: /judges/22/gustafson/
            - generic [ref=e147]: David Gustafson
            - generic [ref=e148]: Senior Judge
          - link "James S. Halpern Senior Judge" [ref=e149] [cursor=pointer]:
            - /url: /judges/23/halpern/
            - generic [ref=e150]: James S. Halpern
            - generic [ref=e151]: Senior Judge
          - link "Mark V. Holmes Senior Judge" [ref=e152] [cursor=pointer]:
            - /url: /judges/24/holmes/
            - generic [ref=e153]: Mark V. Holmes
            - generic [ref=e154]: Senior Judge
          - link "Albert G. Lauber Senior Judge" [ref=e155] [cursor=pointer]:
            - /url: /judges/25/lauber/
            - generic [ref=e156]: Albert G. Lauber
            - generic [ref=e157]: Senior Judge
          - link "L. Paige Marvel Senior Judge" [ref=e158] [cursor=pointer]:
            - /url: /judges/26/marvel/
            - generic [ref=e159]: L. Paige Marvel
            - generic [ref=e160]: Senior Judge
          - link "Richard T. Morrison Senior Judge" [ref=e161] [cursor=pointer]:
            - /url: /judges/27/morrison/
            - generic [ref=e162]: Richard T. Morrison
            - generic [ref=e163]: Senior Judge
          - link "Elizabeth Crewson Paris Senior Judge" [ref=e164] [cursor=pointer]:
            - /url: /judges/28/paris/
            - generic [ref=e165]: Elizabeth Crewson Paris
            - generic [ref=e166]: Senior Judge
          - link "Michael B. Thornton Senior Judge" [ref=e167] [cursor=pointer]:
            - /url: /judges/29/thornton/
            - generic [ref=e168]: Michael B. Thornton
            - generic [ref=e169]: Senior Judge
          - link "Juan F. Vasquez Senior Judge" [ref=e170] [cursor=pointer]:
            - /url: /judges/30/vasquez/
            - generic [ref=e171]: Juan F. Vasquez
            - generic [ref=e172]: Senior Judge
      - generic [ref=e173]:
        - heading "Special Trial Judge Biographies" [level=2] [ref=e174]
        - generic [ref=e175]:
          - link "Zachary S. Fried Chief Special Trial Judge" [ref=e176] [cursor=pointer]:
            - /url: /judges/31/fried/
            - generic [ref=e177]: Zachary S. Fried
            - generic [ref=e178]: Chief Special Trial Judge
          - link "Diana L. Leyden Special Trial Judge" [ref=e179] [cursor=pointer]:
            - /url: /judges/33/leyden/
            - generic [ref=e180]: Diana L. Leyden
            - generic [ref=e181]: Special Trial Judge
          - link "Peter J. Panuthos Special Trial Judge" [active] [ref=e182] [cursor=pointer]:
            - /url: /judges/34/panuthos/
            - generic [ref=e183]: Peter J. Panuthos
            - generic [ref=e184]: Special Trial Judge
          - link "Jennifer E. Siegel Special Trial Judge" [ref=e185] [cursor=pointer]:
            - /url: /judges/35/siegel/
            - generic [ref=e186]: Jennifer E. Siegel
            - generic [ref=e187]: Special Trial Judge
      - generic [ref=e188]:
        - heading "Senior Special Trial Judge Biography" [level=2] [ref=e189]
        - link "Lewis R. Carluzzo Senior Special Trial Judge" [ref=e191] [cursor=pointer]:
          - /url: /judges/32/carluzzo/
          - generic [ref=e192]: Lewis R. Carluzzo
          - generic [ref=e193]: Senior Special Trial Judge
      - generic [ref=e194]:
        - link "Private Seminar Disclosures" [ref=e195] [cursor=pointer]:
          - /url: /judges/private-seminar-disclosures/
          - generic [ref=e196]: 
          - generic [ref=e197]: Private Seminar Disclosures
        - link "Judicial Conduct and Disability Complaint Procedures" [ref=e198] [cursor=pointer]:
          - /url: "#"
          - generic [ref=e199]: 
          - generic [ref=e200]: Judicial Conduct and Disability Complaint Procedures
  - contentinfo [ref=e201]:
    - link "Back to top" [ref=e202] [cursor=pointer]:
      - /url: "#main-content"
    - generic [ref=e206]:
      - heading "Questions?" [level=2] [ref=e207]
      - paragraph [ref=e208]:
        - text: For assistance with DAWSON, the Court's Electronic Filing and Case Management System, refer to the
        - link "DAWSON" [ref=e209] [cursor=pointer]:
          - /url: /dawson
        - text: page or email
        - link "dawson.support@ustaxcourt.gov" [ref=e210] [cursor=pointer]:
          - /url: mailto:dawson.support@ustaxcourt.gov?subject=Assistance%20for%20Dawson
        - text: .
        - text: Be sure to include your case docket number in your email. For all other questions contact the Office of the Clerk of Court at (
        - link "202) 521-0700" [ref=e211] [cursor=pointer]:
          - /url: tel:+2025210700
        - text: .
    - generic [ref=e214]:
      - generic [ref=e215]:
        - link "US Tax Court Logo" [ref=e216] [cursor=pointer]:
          - /url: /
          - img "US Tax Court Logo" [ref=e217]
        - paragraph [ref=e219]:
          - text: United States Tax Court
          - link "400 Second Street, NW Washington, DC 20217" [ref=e220] [cursor=pointer]:
            - /url: https://www.google.com/maps/place/US+Tax+Court/@38.8951679,-77.0149345,17z/data=!3m1!4b1!4m6!3m5!1s0x89b7b788e9a932e5:0x33d2d11766456bca!8m2!3d38.8951679!4d-77.0149345!16zL20vMDVzZDE0?entry=ttu&g_ep=EgoyMDI1MDYxNy4wIKXMDSoASAFQAw%3D%3D
            - generic [ref=e221]:
              - text: 400 Second Street, NW
              - text: Washington, DC 20217
      - paragraph [ref=e223]:
        - text: "Tax Court Hours of Operation: 8 a.m. to 4:30 p.m. (EST) on all days except Saturdays, Sundays, and"
        - link "legal holidays" [ref=e224] [cursor=pointer]:
          - /url: /holidays
        - text: in the District of Columbia.
      - generic [ref=e225]:
        - paragraph [ref=e226]:
          - text: (
          - link "202) 521-0700" [ref=e227] [cursor=pointer]:
            - /url: tel:+2025210700
          - text: All rights reserved
          - text: "Build: ab92537"
        - link "Dawson Logo" [ref=e228] [cursor=pointer]:
          - /url: https://dawson.ustaxcourt.gov/
          - img "Dawson Logo" [ref=e229]
  - button "Scroll to top" [ref=e230] [cursor=pointer]:
    - img [ref=e231]
  - iframe [ref=e232]:
    - generic [ref=f1e2]:
      - img [ref=f1e4]
      - generic [ref=f1e11]:
        - heading "Status embed installed correctly" [level=1] [ref=f1e12]:
          - paragraph [ref=f1e13]: Status embed installed correctly
        - generic [ref=f1e14]: This will be shown if an incident or maintenance is posted on your status page.
        - link "View latest updates" [ref=f1e16] [cursor=pointer]:
          - /url: https://status.ustaxcourt.gov?utm_source=embed
      - button [ref=f1e18] [cursor=pointer]:
        - img [ref=f1e19]
```

# Test source

```ts
  936  |     // Budget: ~60 s startup + 7 next() + 1 stopInteract +
  937  |     //         8 (heading+link pairs × 4 sections) + ≤15 tile loop ≈ 6 min.
  938  |     voiceOverTest.setTimeout(600_000);
  939  |
  940  |     voiceOverTest.beforeEach(async ({ page }) => {
  941  |         await page.goto(JUDGES_URL);
  942  |     });
  943  |
  944  |     voiceOverTest(
  945  |         "VoiceOver announces all page content — every section heading, every judge card, and both bottom tiles",
  946  |         async ({ page, voiceOver }) => {
  947  |
  948  |             // ── 1. Land on h1 ─────────────────────────────────────────────────────
  949  |             // enterWebContent clears the phrase log then positions VO on the h1.
  950  |             await enterWebContent(page, voiceOver);
  951  |
  952  |             // ── 2. Intro paragraph ────────────────────────────────────────────────
  953  |             await voiceOver.next();
  954  |
  955  |             // ── 3. Filter group label + all 5 filter buttons ──────────────────────
  956  |             // next() on role="group" enters it (interact mode) and announces the
  957  |             // label.  Subsequent next() calls walk the children one by one.
  958  |             await voiceOver.next(); // "Filter judges by type, group"
  959  |             await voiceOver.next(); // "All Judges, pressed, toggle button"
  960  |             await voiceOver.next(); // "Judges, toggle button"
  961  |             await voiceOver.next(); // "Senior Judges, toggle button"
  962  |             await voiceOver.next(); // "Special Trial Judges, toggle button"
  963  |             await voiceOver.next(); // "Senior Special Trial Judges, toggle button"
  964  |
  965  |             // ── 4. Exit the filter group ──────────────────────────────────────────
  966  |             // Without this, jump commands search inside the group and return
  967  |             // "heading not found" / "link not found".
  968  |             await voiceOver.perform(voiceOverKeyCodeCommands.stopInteractingWithItem);
  969  |
  970  |             // ── 5. Section 1 — "Judge Biographies" + first judge card ───────────────
  971  |             await voiceOver.perform(voiceOverKeyCodeCommands.findNextHeading); // "Judge Biographies, heading level 2"
  972  |             await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);    // "Patrick J. Urda Chief Judge, link"
  973  |
  974  |             // ── 6. Section 2 — jump past all §1 cards to next h2, then first card ──
  975  |             // findNextHeading skips every judge link (they are not headings) and
  976  |             // lands directly on the next section heading.
  977  |             await voiceOver.perform(voiceOverKeyCodeCommands.findNextHeading); // "Senior Judge Biographies, heading level 2"
  978  |             await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);    // first Senior Judge card
  979  |
  980  |             // ── 7. Section 3 — same pattern ──────────────────────────────────────
  981  |             await voiceOver.perform(voiceOverKeyCodeCommands.findNextHeading); // "Special Trial Judge Biographies, heading level 2"
  982  |             await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);    // first Special Trial Judge card
  983  |
  984  |             // ── 8. Section 4 — same pattern → Lewis R. Carluzzo ─────────────────
  985  |             await voiceOver.perform(voiceOverKeyCodeCommands.findNextHeading); // "Senior Special Trial Judge Biography, heading level 2"
  986  |             await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);    // first card in §4 (likely Lewis R. Carluzzo)
  987  |
  988  |             // ── 9. Bottom tiles — walk forward from end of §4 ────────────────────
  989  |             // Section 4 typically has only 1–3 judges, so the tiles are reachable
  990  |             // within 15 findNextLink calls.  The loop stops as soon as both are found.
  991  |             let tilesFound = 0;
  992  |             for (let i = 0; i < 15 && tilesFound < 2; i++) {
  993  |                 await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);
  994  |                 const phrase = await voiceOver.lastSpokenPhrase();
  995  |                 if (/private seminar disclosures/i.test(phrase)) tilesFound++;
  996  |                 if (/judicial conduct/i.test(phrase))            tilesFound++;
  997  |             }
  998  |
  999  |             // ── 10. Collect everything VoiceOver spoke ────────────────────────────
  1000 |             const log = (await voiceOver.spokenPhraseLog()).join("\n").toLowerCase();
  1001 |
  1002 |             // ── 11. Assert every section of the page was announced ───────────────
  1003 |             const assertions: [string, string | RegExp][] = [
  1004 |                 // Page title and structure
  1005 |                 ["page title h1",                        "judge information"],
  1006 |                 ["heading level 1 announced",            "heading level 1"],
  1007 |                 ["intro paragraph",                      /biography|clicking on the cards/],
  1008 |
  1009 |                 // Filter bar
  1010 |                 ["filter group label",                   "filter judges by type"],
  1011 |                 ["'All Judges' button",                  "all judges"],
  1012 |                 ["'Judges' button",                      /\bjudges\b/],
  1013 |                 ["'Senior Judges' button",               "senior judges"],
  1014 |                 ["'Special Trial Judges' button",        /special trial judges/],
  1015 |                 ["'Senior Special Trial Judges' button", "senior special trial judges"],
  1016 |
  1017 |                 // All 4 section headings
  1018 |                 ["'Judge Biographies' h2",               "judge biographies"],
  1019 |                 ["'Senior Judge Biographies' h2",        "senior judge biographies"],
  1020 |                 ["'Special Trial Judge Biographies' h2", "special trial judge biographies"],
  1021 |                 ["'Senior Special Trial' h2",            "senior special trial judge biograph"],
  1022 |
  1023 |                 // One judge card per section (representative of each section traversed)
  1024 |                 ["a judge in section 1",                 /chief judge|judge link/],
  1025 |                 ["a judge in section 2",                 "senior judge"],
  1026 |                 ["a judge in section 3",                 "special trial judge"],
  1027 |                 ["Lewis R. Carluzzo (section 4)",        "carluzzo"],
  1028 |
  1029 |                 // Bottom tiles
  1030 |                 ["Private Seminar Disclosures tile",     "private seminar disclosures"],
  1031 |                 ["Judicial Conduct tile",                "judicial conduct"],
  1032 |             ];
  1033 |
  1034 |             for (const [label, pattern] of assertions) {
  1035 |                 if (typeof pattern === "string") {
> 1036 |                     expect(log, `VoiceOver never announced: ${label}`).toContain(pattern);
       |                                                                        ^ Error: VoiceOver never announced: 'Special Trial Judge Biographies' h2
  1037 |                 } else {
  1038 |                     expect(log, `VoiceOver never announced: ${label}`).toMatch(pattern);
  1039 |                 }
  1040 |             }
  1041 |         },
  1042 |     );
  1043 |
  1044 |     voiceOverTest(
  1045 |         "VoiceOver speaks every judge's name and role — DOM-driven full card traversal",
  1046 |         async ({ page, voiceOver }) => {
  1047 |             // ── 1. Get the expected card list directly from the live DOM ──────────────
  1048 |             // Whatever the server renders is what VoiceOver must speak.
  1049 |             // The test adapts automatically when judges are added or removed in the CMS —
  1050 |             // no hardcoded names, no stale assertions.
  1051 |             const expectedCards = await page.evaluate(() =>
  1052 |                 Array.from(document.querySelectorAll("a.judge-card")).map(card => ({
  1053 |                     name:    card.querySelector(".judge-name")?.textContent?.trim() ?? "",
  1054 |                     role:    card.querySelector(".judge-role")?.textContent?.trim() ?? "",
  1055 |                     section: card.closest(".judge-section")?.getAttribute("data-section") ?? "",
  1056 |                 })),
  1057 |             );
  1058 |             expect(expectedCards.length, "page must have at least one judge card").toBeGreaterThan(0);
  1059 |
  1060 |             // ── 2. Enter the page and navigate to the first judge section h2 ──────────
  1061 |             // VoiceOver's findNextLink searches forward from the current cursor
  1062 |             // position — if we start at h1 the search wraps through page header/nav
  1063 |             // links before reaching the judge cards.  We replicate the same setup as
  1064 |             // the full-page sweep: walk the filter group, exit it, then jump to the
  1065 |             // first section h2.  From that anchor, findNextLink finds judge cards only.
  1066 |             await enterWebContent(page, voiceOver);
  1067 |
  1068 |             await voiceOver.next();                  // intro paragraph
  1069 |             await voiceOver.next();                  // "Filter judges by type, group"
  1070 |             await voiceOver.next();                  // "All Judges, pressed, button"
  1071 |             await voiceOver.next();                  // "Judges, button"
  1072 |             await voiceOver.next();                  // "Senior Judges, button"
  1073 |             await voiceOver.next();                  // "Special Trial Judges, button"
  1074 |             await voiceOver.next();                  // "Senior Special Trial Judges, button"
  1075 |             await voiceOver.perform(voiceOverKeyCodeCommands.stopInteractingWithItem);
  1076 |             await voiceOver.perform(voiceOverKeyCodeCommands.findNextHeading); // → §1 h2
  1077 |
  1078 |             // ── 3. Walk every link in document order using findNextLink ───────────────
  1079 |             // findNextLink targets <a href> elements only — the <button> filter buttons
  1080 |             // are skipped entirely.  Document order on this page is:
  1081 |             //   judge cards (all 4 sections, left-to-right, top-to-bottom)
  1082 |             //   → "Private Seminar Disclosures" tile
  1083 |             //   → "Judicial Conduct and Disability Complaint Procedures" tile
  1084 |             //
  1085 |             // After each jump, lastSpokenPhrase() returns exactly what VoiceOver said
  1086 |             // aloud — the accessible name of the link plus role/state suffixes.
  1087 |             // We collect every phrase and stop as soon as both bottom tiles have been
  1088 |             // announced (they come after the last judge card so we know we're done).
  1089 |             const spoken: string[] = [];
  1090 |             let tilesFound = 0;
  1091 |             const maxLinks = expectedCards.length + 10; // cards + tiles + small buffer
  1092 |
  1093 |             for (let i = 0; i < maxLinks && tilesFound < 2; i++) {
  1094 |                 await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);
  1095 |                 const phrase = await voiceOver.lastSpokenPhrase();
  1096 |                 spoken.push(phrase);
  1097 |                 if (/private seminar disclosures/i.test(phrase)) tilesFound++;
  1098 |                 if (/judicial conduct/i.test(phrase))            tilesFound++;
  1099 |             }
  1100 |
  1101 |             expect(tilesFound, "loop must reach both bottom tiles to confirm all cards were traversed").toBe(2);
  1102 |
  1103 |             // ── 4. Assert every judge's name and role was actually spoken ─────────────
  1104 |             // Joining into one string lets us check each card with a single
  1105 |             // .toContain() call and get a clear failure message naming the card.
  1106 |             const fullLog = spoken.join("\n").toLowerCase();
  1107 |
  1108 |             for (const card of expectedCards) {
  1109 |                 expect(
  1110 |                     fullLog,
  1111 |                     `VoiceOver never spoke name "${card.name}" (section: ${card.section})`,
  1112 |                 ).toContain(card.name.toLowerCase());
  1113 |
  1114 |                 expect(
  1115 |                     fullLog,
  1116 |                     `VoiceOver never spoke role "${card.role}" for "${card.name}" (section: ${card.section})`,
  1117 |                 ).toContain(card.role.toLowerCase());
  1118 |             }
  1119 |
  1120 |             // ── 5. Bottom tiles also confirmed ────────────────────────────────────────
  1121 |             expect(fullLog, "VoiceOver never spoke 'Private Seminar Disclosures'").toMatch(/private seminar disclosures/);
  1122 |             expect(fullLog, "VoiceOver never spoke 'Judicial Conduct'").toMatch(/judicial conduct/);
  1123 |         },
  1124 |     );
  1125 | });
  1126 |
```
