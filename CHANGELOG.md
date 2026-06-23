# Changelog

All notable changes to Sabiá will be documented in this file.

See [Conventional Commits](https://www.conventionalcommits.org/) for commit guidelines.

## [Unreleased]

### Added
- Command center dashboard with dense grid layout
- Mini overview map with NDVI-colored region pins
- 6-metric KPI strip with sparklines
- Real-time activity feed (alerts + history + monitors)
- Quick actions bar (search, refresh, CSV export, clear history)
- Skeleton loading components for dashboard and modules
- Spinner component for consistent loading indicators
- SidebarSection component for collapsible sidebar panels
- Shared utilities: `getNdviColor`, `formatTimeAgo`, CSV export
- Keyboard shortcut: Ctrl+K to open map
- Success toasts for export, delete, and clear actions
- Help button to replay onboarding tutorial
- Aria-live regions for dynamic content updates
- Focus management in AlertBell dropdown
- 50+ unit tests for stores, helpers, and products

### Fixed
- ActivityFeed `$derived` bug (was wrapping function instead of value)
- Dark mode toggle removed (was non-functional)
- Active navigation indicator in header
- All Portuguese strings normalized to English
- confirm() dialogs replaced with inline confirmation UI
- Module export feedback (was using window.print() without feedback)
- Mousemove handler throttled with requestAnimationFrame
- Dashboard store mutations batched for fewer re-renders
- alerts.unreadCount cached for O(1) access
- localStorage persist debounced (100ms)
- ImageGallery selection check optimized to O(n) with Set
- OverviewMap marker updates skipped when profiles unchanged
- TimelapsePlayer now processes 3 frames in parallel

### Changed
- Dashboard layout: full-width command center grid
- Station cards: dense 3-column grid with status dots
- Module sidebar: collapsible with skeleton loading
- Chart Y-axis: auto-scales based on data range
- BarChart/DonutChart: added hover tooltips
- Architecture docs updated with command center patterns

### Removed
- Dead Scorecard.svelte component
- Empty +page.svelte at root route
- Broken dark mode toggle and ModeWatcher
- Redundant class-variance-authority package
- Hardcoded NDVI trend data in dashboard
