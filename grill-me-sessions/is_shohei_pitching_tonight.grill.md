# Grill Session: is_shohei_pitching_tonight

Started: 2026-05-03
Last updated: 2026-05-03
Status: complete
Domain: Software Development (Automation Tool/Scripting)

## Summary

Completed plan to create a Python script that checks the MLB Stats API once daily for the Dodgers' probable starting pitcher. If Shohei Ohtani (MLB ID 660271) is scheduled to start, send a push notification via ntfy.sh. The script runs automatically using GitHub Actions on a cron schedule.

All key decisions finalized:
- **Language**: Python 3.x with `requests` library
- **Data Source**: MLB Stats API with dynamic date parameter (`&date=YYYY-MM-DD` UTC)
- **Team IDs**: Dodgers (119), Ohtani (660271 - checked via pitcher ID, not name)
- **Runner**: GitHub Actions (ubuntu-latest)
- **Notification**: ntfy.sh REST API with hardcoded topic (privacy not required)
- **Cron schedule**: Adjusted to `0 17 * * *` (17:00 UTC = 10:00 AM PT) for better probable pitcher availability
- **No-game behavior**: Silent exit when no Dodgers game today
- **API failure handling**: Log failures, retry 2-3 times with 5-second delays, track consecutive failures, notify after 3 consecutive days
- **Testing**: Manual testing with live API (no formal test framework)
- **Failure notification**: Rely on GitHub Actions failed run indicator (no ntfy on failure)

## DEFERRED ITEMS (Open Risks)

### DEFERRED: Retry Logic for Missing probablePitcher
- **Reason**: User does not know exact time probable pitchers are posted; suggests checking again later if field is missing. Current plan is once-daily check at 10 AM PT.
- **Open questions**: What retry interval? How many retries? Should the cron job run multiple times per day? What is the typical posting time for MLB probable pitchers?
- **Risk if ignored**: Script may miss Ohtani's starts if probable pitcher is announced after the daily cron run
- **Date**: 2026-05-03

### DEFERRED: Consecutive Failure Counter Persistence
- **Reason**: GitHub Actions is stateless; need to persist a counter across runs for the 3-day failure notification rule.
- **Open questions**: Use repo file, GitHub Artifact, or GitHub Secret?
- **Risk if ignored**: 3-day notification rule will not work correctly
- **Date**: 2026-05-03

## Decision Log

### DECIDED: Project Name & Repository
- **Decision**: Project named "is_shohei_pitching_tonight", private GitHub repo
- **Rationale**: User provided session name matching project name
- **Date**: 2026-05-03

### DECIDED: Notification Topic Security
- **Decision**: Use unique, non-guessable ntfy.sh topic (e.g., brants-dodgers-alert-99)
- **Rationale**: Public ntfy.sh topics can be accessed by anyone who guesses the name
- **Date**: 2026-05-03

### DECIDED: Use Pitcher ID for Ohtani Detection
- **Decision**: Use MLB ID 660271 to identify Shohei Ohtani instead of string matching "Ohtani" in fullName
- **Rationale**: More reliable, avoids potential name collision with other players
- **Date**: 2026-05-03

### DECIDED: Add Dynamic Date Parameter to API Call
- **Decision**: Always add `&date=YYYY-MM-DD` (UTC date) to the API URL to ensure we check today's games
- **Rationale**: Without date parameter, API returned yesterday's games; dynamic date ensures correct day
- **Date**: 2026-05-03

### DECIDED: Adjust Cron Schedule to Later Time
- **Decision**: Change cron from `0 14 * * *` (7 AM PT) to later time (e.g., `0 17 * * *` = 10 AM PT) so probable pitchers are more likely to be posted
- **Rationale**: Probable pitchers typically announced by 10 AM local time; 7 AM may be too early
- **Date**: 2026-05-03

### DECIDED: ntfy Topic Can Be Hardcoded
- **Decision**: ntfy.sh topic can be hardcoded in the script (not a GitHub secret); user doesn't care if others receive the alert
- **Rationale**: User explicitly stated they don't care about topic privacy
- **Date**: 2026-05-03

### DECIDED: Log Exceptions (Specific)
- **Decision**: Log exceptions with specific exception types (not bare `except Exception`); log to stdout for GitHub Actions capture
- **Rationale**: Better debugging without exposing bare exception handling
- **Date**: 2026-05-03

### DECIDED: No Game Today Behavior
- **Decision**: When there's no Dodgers game today (API returns empty `dates` array), exit silently with no output or notification
- **Rationale**: User confirmed silent exit is desired behavior
- **Date**: 2026-05-03

### DECIDED: API Failure Handling
- **Decision**: Log API failures to stdout. Track consecutive failure days; if 3 consecutive days of API failure, send ntfy notification.
- **Rationale**: User wants visibility into persistent API issues without being spammed by single failures.
- **Date**: 2026-05-03

### DECIDED: Failure Notification
- **Decision**: No ntfy notification on script failure; rely on GitHub Actions failed run indicator
- **Rationale**: User prefers checking GitHub Actions tab rather than receiving failure notifications via ntfy
- **Date**: 2026-05-03

### DECIDED: API Retry Logic
- **Decision**: Retry API call 2-3 times with a 5-second delay between attempts before giving up
- **Rationale**: User confirmed retries are desired for transient network/API failures
- **Date**: 2026-05-03

### DECIDED: Testing Strategy
- **Decision**: Test manually with the live MLB API (no formal test framework, no mock files)
- **Rationale**: Public API with no auth needed; user prefers simplicity over formal testing
- **Date**: 2026-05-03

### RESOLVED: Ohtani as Pitcher vs Position Player
- **Resolution**: The `probablePitcher` field should already indicate starting pitcher role; no additional position check needed
- **Date**: 2026-05-03

### DEFERRED: Retry Logic for Missing probablePitcher
- **Reason**: User does not know exact time probable pitchers are posted; suggests checking again later if field is missing. Current plan is once-daily check.
- **Open questions**: What retry interval? How many retries? Should the cron job run multiple times per day? What is the typical posting time for MLB probable pitchers?
- **Risk if ignored**: Script may miss Ohtani's starts if probable pitcher is announced after the daily cron run
- **Date**: 2026-05-03

## Open Threads

### API Reliability & Edge Cases
- [Decided] Add dynamic date parameter `&date=YYYY-MM-DD` (UTC) to API call
- [Decided] Use Ohtani's MLB ID 660271 instead of name string match
- [Resolved] Ohtani as pitcher: `probablePitcher` field indicates starting pitcher
- [Deferred] **Missing probablePitcher field**: User suggests checking again later, but timing unknown. Current plan is once-daily check.
- [Decided] Retry API calls: 2-3 retries with 5-second delay between attempts
- [Decided] API down/unresponsive: Log failure, track consecutive days, notify after 3 consecutive failures (see Decision Log). Need to persist failure count across GitHub Actions runs (stateless environment).
- [Decided] What if there's no Dodgers game today? (API returns empty `dates` array - silent exit, per user decision)
- [Open] Should we retry API calls on failure? (Simple retry with backoff?)

### Cron Schedule Timing
- [Decided] Adjust cron to later time (e.g., `0 17 * * *` = 10 AM PT) for better probable pitcher availability
- [Open] What if the schedule changes after the cron job runs? (Once-daily may miss late changes)

### Error Handling & Logging
- [Decided] Log exceptions with specific types (not bare `except Exception`)
- [Open] Should we add a success log message when Ohtani is NOT pitching? (For visibility in GitHub Actions)
- [Open] Should we retry on API failures?

### Testing Strategy
- [Decided] Testing: Manual testing with live API (no formal test framework)

### GitHub Actions Configuration
- [Decided] ntfy topic can be hardcoded (no secrets needed)
- [Decided] No ntfy on failure: Rely on GitHub Actions failed run indicator (user decision)

## Parking Lot

- Potential future features: email notifications, multiple pitchers, other teams
- iOS/Android ntfy app setup (user mentioned this, but it's a usage step, not development)
