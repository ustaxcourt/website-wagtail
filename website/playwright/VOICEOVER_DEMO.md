# Running the VoiceOver Tests

## Prerequisites

1. **Enable VoiceOver** — press `Cmd+F5` before running any VoiceOver test
2. **Accessibility permissions** — grant Terminal (or iTerm) access in
   **System Settings → Privacy & Security → Accessibility** (only needed once)
3. **Chrome for Testing installed:**
   ```bash
   npx playwright install chromium
   ```
4. **Dev server running** in a separate terminal:
   ```bash
   make run
   ```

---

## Run just the full-page sweep (demo)

```bash
cd website
npx playwright test \
  playwright/tests/private_seminar_disclosures.voiceover.ts \
  --config playwright/playwright.config.ts \
  --grep "VoiceOver full-page sweep" \
  --headed
```

`--headed` keeps Chrome visible on screen so the audience can see navigation happening.
VoiceOver will speak aloud during the test — that's expected and is the point.
The sweep takes **~5–6 minutes** (each navigation step is ~10 s).

---

## Run the entire test file

All 21 keyboard/ARIA tests + the full-page VoiceOver sweep:

```bash
cd website
npx playwright test \
  playwright/tests/private_seminar_disclosures.voiceover.ts \
  --config playwright/playwright.config.ts
```

---

## Run all VoiceOver tests (both pages)

```bash
cd website
npx playwright test --config playwright/playwright.config.ts
```

---

## Run only the keyboard/ARIA tests (no real VoiceOver required)

Skips the sweep — useful for CI or when VoiceOver is not enabled:

```bash
cd website
npx playwright test \
  playwright/tests/private_seminar_disclosures.voiceover.ts \
  --config playwright/playwright.config.ts \
  --grep-invert "VoiceOver full-page sweep"
```

---

## Pages covered

| Test file | Page |
|-----------|------|
| `judge_information.voiceover.ts` | `/judges/` |
| `private_seminar_disclosures.voiceover.ts` | `/judges/private-seminar-disclosures/` |
