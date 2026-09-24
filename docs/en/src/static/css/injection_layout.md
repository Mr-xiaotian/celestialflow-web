# src/celestialflow_web/static/css/injection_layout.css

> 📅 Last Updated: 2026/09/24

Handles the search filtering, two-column layout, and responsive breakpoint styles of the task injection page.

## Two-Column Layout (`.card-grid`)

```css
.card-grid {
  display: grid;
  grid-template-columns: minmax(18rem, 22rem) minmax(0, 1fr);
  gap: 1.5rem;
}
```

- The left node list is fixed at 18–22rem, and the right editor fills the remaining width adaptively.

## Search Filtering

- **Search container (`.search-container`)**: Relatively positioned, used to host the search icon.
- **Search input (`.search-input`)**:
  - The left padding `2.5rem` leaves room for the search icon.
  - The border color switches to `--cornflower-400` on focus.
  - Dark mode: `--carbon-700` background.
- **Search icon (`.search-icon`)**: Absolutely positioned on the left side of the input, `1rem`, `color: --carbon-400`.

## Injectable Node Toggle (`.injectable-toggle`)

- `flex` layout, `gap: 0.5rem`, `font-size: 0.75rem`.
- Located below the search box and above the node list.

## Responsive (`@media (max-width: 2048px)`)

On narrow screens (≤2048px):
- `.card-grid` switches to a single column (`grid-template-columns: 1fr`).
- `.node-list` removes the `max-height` restriction.
- `.editor-header` and `.submit-section` switch to vertical stacking.
- `.editor-actions` switches to a vertical arrangement.

## Related Modules

- The layout structure is dynamically filled by `renderInjectionPage()` in `injection.ts`.
- Search and filter events are bound by `setupEventListeners()`.
