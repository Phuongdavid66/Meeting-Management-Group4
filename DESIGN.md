# Design System (ICTU Meeting)

## Core Identity
**Tone & Mood:** Công nghệ, chuyên nghiệp, hiện đại, thanh lịch, đáng tin cậy. (Tech, professional, modern, elegant, reliable).
**Metaphor:** The University Ledger. A strict calendar matrix where time flows horizontally or vertically in precise grids.

## Palette
- **Deep Navy (`#0f172a`):** Primary brand color, used for the main topbar and modal headers. Represents authority and structure.
- **Tech Blue (`#1e3a8a` / `#2563eb`):** Used for booked slots, primary buttons, and active states.
- **Accent Amber (`#f59e0b`):** Used sparingly to draw attention to brand elements and specific actionable highlights.
- **Light Slate (`#f8fafc` / `#f1f5f9` / `#e2e8f0`):** Backgrounds, grid lines, and empty cells. Keeps the interface clean and readable.
- **Restricted Red (`#fee2e2` / `#fef2f2`):** A distinct repeating linear gradient hatch pattern used for restricted rooms to visually communicate "unavailable" without reading as an error.

## Typography
- **Primary Face:** `Inter` (or system `Roboto` / `sans-serif`). A workhorse UI face that ensures high legibility in dense data grids.
- **Weights:** 
  - Regular (400) for time labels and small text.
  - Medium (500) for buttons and inputs.
  - Semi-Bold (600) for headers and booking titles.

## Topology & Layout
- **The Grid:** A strict table layout (`display: grid`) where the X-axis is rooms and the Y-axis is time slots. Columns have a minimum width of `180px` to allow titles to remain readable.
- **Sticky Headers:** Room headers and time labels stick to the top and left edges, maintaining context during scroll.

## Controls & State
- **Booking Cells:** Empty cells invite interaction. Hover states slightly darken the background.
- **Restricted Cells:** Striated hatch pattern, cursor changes to `not-allowed`.
- **Booked Cells:** Solid Tech Blue blocks with a left border accent, displaying title and organizer.
- **Depth Hierarchy:** The booking modal appears on the front plane (`z-index: 50`) with a dark, blurred backdrop (`backdrop-filter: blur(4px)`), elevating the task out of the dense grid. The modal slides up subtly to feel physical.
