# WAG-1246 — Figma Mobile Width vs. Real Device Widths

**Author:** Greg Brown
**Last updated:** 2026-05-31
**Audience:** UX team, for review on Monday discussion
**Related Figma:** [Judges Pages — Mobile QAT](https://www.figma.com/design/MpYvDySIPULl7f1RQBvb3y/US-Tax-Court-Website-Redesign?node-id=13945-4914)

## TL;DR

The Figma mobile mockup for the JudgeIndex bottom Quick Access Tiles was designed
at a **320 px viewport** (iPhone SE / older Android), but most users browse on
**375 px (iPhone 13/14) or 414 px (iPhone XR / Plus / Pro Max) viewports**.
The tile width and title-wrap behavior shown in Figma can't reproduce 1:1 on
those larger phones without an explicit constraint — and even with that
constraint, two of the four tile lines required by the WAG-1246 AC don't fit at
the Figma-specified font size because the AC text is longer than the Figma
placeholder text.

We need a UX call on whether to (a) re-mock the tiles at 375/414, (b) accept the
current implementation's wrap behavior on larger phones, or (c) shrink the font
on mobile so the AC text fits the Figma wrap intent.

## Where the discrepancy comes from

### Figma mobile QAT spec (node 13945-4914)

| Element | Figma value |
|---|---|
| Mobile mockup viewport | 320 px (`Mobile: Judges` artboard width) |
| Tile width | **288 px** (fixed) |
| Tile padding | 22 px on all sides |
| Inner content width | 244 px |
| Icon container | 40 × 40 px |
| Gap (icon → text) | 18 px |
| Text container | **186 px wide × 44 px tall** |
| Title font | Source Sans 3 600, 20 px / 22 px line-height |
| Title color | `#162E51` (Tax Court navy) |
| Text alignment | left horizontal, center vertical |

Figma's text frame is **fixed** at 186 px wide. The placeholder text wraps cleanly
to two lines inside that 186 × 44 box because Figma's content is shorter than
ours:

| Tile | Figma placeholder | Wraps to |
|---|---|---|
| 1 | `Private Seminar Disclosure` (singular) | "Private Seminar" / "Disclosure" |
| 2 | `Judicial Conduct and Disability Procedures` | "Judicial Conduct and" / "Disability Procedures" |

### WAG-1246 acceptance criteria text

Per the ticket, the tiles must display:

| Tile | AC title | Δ vs. Figma |
|---|---|---|
| 1 | **Private Seminar Disclosures** | + "s" |
| 2 | **Judicial Conduct and Disability Complaint Procedures** | + "Complaint" |

The AC text is **9 characters longer** on tile 2 than Figma's mock, and adds an
additional word ("Complaint") that does not fit on the same 186 px line as
"Disability ... Procedures".

### Real-world iOS mobile viewport widths

| Device | CSS viewport width |
|---|---|
| iPhone SE (2nd/3rd gen) | 375 px |
| iPhone 13 / 14 / 15 standard | 390 px |
| iPhone XR / 11 / Plus / Pro Max | 414 px |
| iPhone 14 Pro Max / 15 Pro Max | 430 px |
| Older iPhone SE / iPhone 5/6/7/8 | **320 px** ← Figma artboard |

iPhone XR — the device the regression screenshot was taken on — is **414 px wide**,
**29 % wider** than the Figma artboard.

## Why the wrap doesn't reproduce

If we let the tile fill the viewport (standard responsive behavior), the math on
a 414 px screen is:

```
viewport         414 px
grid-container  -32 px (16 px page padding × 2)
tile             382 px
tile padding    -44 px (22 px × 2)
icon column     -40 px
gap             -18 px
─────────────────────
text column     280 px   (vs. Figma's 186 px)
```

At a **280 px** text column, the title "Private Seminar Disclosures"
(~270 px at Source Sans 3 600 / 20 px) **fits on a single line**. Same for
"Judicial Conduct and Disability" running together on one line before wrap.
That's the regression the team flagged on iPhone XR.

To force the Figma-spec wrap on every mobile width, we have to override the
"fill-the-tile" default and pin the title column to 186 px regardless of the
viewport (committed: `max-width: 186 px` on the mobile `h2`). That fixes tile 1
("Private Seminar" / "Disclosures") but exposes a second issue on tile 2.

## Tile 2: AC text exceeds the Figma container

At Source Sans 3 600 / 20 px, the AC text on tile 2 measures roughly:

| Phrase | Approx. width |
|---|---|
| "Judicial Conduct and" | ~170 px |
| "Disability Complaint" | ~190 px |
| "Disability Complaint Procedures" | ~280 px |
| "Procedures" alone | ~100 px |

**No single column width can produce the Figma-intended 2-line wrap of "Judicial
Conduct and" / "Disability Complaint Procedures" at the Figma-spec 20 px font**
because "Disability Complaint Procedures" alone is wider than any column that
also forces "Private Seminar Disclosures" to wrap on tile 1.

Practical implication:

- Pin column to ~190 px (close to Figma's 186 px) → both tiles wrap, but tile 2
  wraps to **3 lines**: "Judicial Conduct and" / "Disability Complaint" /
  "Procedures".
- Pin column to ~290 px → tile 2 wraps to **2 lines** matching Figma intent, but
  tile 1 fits on a single line, breaking the Figma intent.

To get **both** tiles wrapping as Figma shows on every mobile viewport at 20 px,
we need to **force the line break explicitly** in the title text (e.g., a `<br>`
or a stored newline rendered via Django's `linebreaksbr` filter) rather than
rely on natural wrap.

## Options for the UX team

### Option A — Force explicit line breaks (engineering recommendation)

Store the tile titles with embedded line breaks at the intended wrap points:

| Tile | Stored title |
|---|---|
| 1 | `Private Seminar\nDisclosures` |
| 2 | `Judicial Conduct and\nDisability Complaint Procedures` |

Render with `{{ value.title|linebreaksbr }}` in the shared block template (safe
— `linebreaksbr` only converts `\n` to `<br>` and escapes everything else).
Set the mobile column width wide enough to fit the longer line
("Disability Complaint Procedures" ≈ 285 px) and the icon column shrinks to fill
the rest.

- **Pro:** Wrap matches Figma intent on every mobile viewport, font stays
  20 px / 22 px as designed.
- **Con:** Title is not "wrappable text" anymore — if UX or comms changes the
  copy in Wagtail admin they must remember to re-insert the line break.

### Option B — Re-mock at 375 px (iPhone 13/14 baseline)

Have UX rebuild the mobile artboard at 375 px (the dominant iOS viewport),
keeping the actual AC text. Tile and column widths grow accordingly, and the
wrap behavior gets designed against the real content.

- **Pro:** Single source of truth, no engineering tricks.
- **Con:** New Figma work, may also require 414 px and 320 px variants.

### Option C — Drop the Figma 20 px spec on mobile

Reduce mobile title to ~14 – 16 px so the AC text fits inside 186 px naturally
in 2 lines. Diverges from the documented Figma type spec.

- **Pro:** No content changes, no template changes, no scope creep.
- **Con:** Visually noticeably smaller than the Figma mockup; would need a
  formal UX exception.

### Option D — Accept 3-line wrap on tile 2

Keep the current `max-width: 186 px` constraint and let tile 2 grow vertically
to 3 lines: "Judicial Conduct and" / "Disability Complaint" / "Procedures".
Tile gets ~22 px taller than Figma; icon stays centered.

- **Pro:** Zero new work, faithful to Figma's font spec.
- **Con:** Does not match Figma's 2-line intent.

## Currently shipped (as of 2026-05-31, after Option A rollback)

**Option A was implemented and then rolled back per visual review.** Final
state on the branch:

- Tile titles are plain text (no embedded `\n`):
  - `Private Seminar Disclosures`
  - `Judicial Conduct and Disability Complaint Procedures`
- The shared `quick_access_tile_block.html` template renders titles plainly
  (`{{ value.title }}`), with no `linebreaksbr` filter.
- Mobile title column is pinned to **186 px** via `max-width` on
  `#judge-information-page .quick-access-tile h2` inside the `≤640 px` media
  query (Figma node 13945-4914 spec).
- Tile 1 wraps to **2 lines** (`Private Seminar` / `Disclosures`) on every
  mobile viewport.
- Tile 2 wraps to **3 lines** (`Judicial Conduct and` / `Disability Complaint` /
  `Procedures`) on every mobile viewport — accepted as the Option D outcome
  while UX decides on a long-term path.

Migration history for the record:

| Migration | Action |
|---|---|
| `0120_seed_judge_index_bottom_tiles` | Initial seed (StreamBlock-format tiles, rendered empty grid) |
| `0121_reseed_judge_index_bottom_tiles` | Fixed ListBlock data format |
| `0122_fix_judicial_conduct_tile_link` | Pointed JCDP tile to `/jcdp/` |
| `0123_force_reset_judge_index_bottom_tiles` | Reset after sandbox admin edits |
| `0124_reseed_judge_index_bottom_tiles_with_linebreaks` | **Option A:** titles with `\n` |
| `0125_revert_linebreak_titles_in_bottom_tiles` | **Rollback:** plain titles again |

Pending UX direction on whether to keep current 3-line tile 2 (Option D),
re-mock at 375 px (Option B), or shrink mobile font (Option C).

## Open questions for UX

1. Is the Figma mobile mockup expected to be reproduced at 320 px only, or
   should it hold on 375 / 414 / 430 viewports too?
2. Was "Disability Complaint Procedures" intended as the wrapping unit on
   tile 2, or was Figma's "Disability Procedures" the canonical title (and the
   AC ticket needs to be updated)?
3. Is forcing the line break in stored copy (Option A) acceptable, or do you
   want copy to be free-form editable in Wagtail admin without an embedded `\n`?
