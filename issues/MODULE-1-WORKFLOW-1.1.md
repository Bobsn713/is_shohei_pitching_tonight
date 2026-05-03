---
id: MODULE-1-WORKFLOW-1.1
title: Daily Pitching Check - Workflow 1.1
module: Module 1 - Daily Pitching Check
depends_on: []
status: done
priority: high
type: feature
---

# Daily Pitching Check - Workflow 1.1

## Description
Daily Check and Notification

## Steps
1. At 10:00 AM Pacific Time, the automation triggers automatically
2. The system looks up today's Dodgers game information from the official MLB schedule, including probable pitcher details
3. If the schedule lookup is temporarily unreachable, the system retries up to three times with a five-second wait between attempts
4. If there is no Dodgers game today, the system exits silently with no notification
5. If the probable pitcher information is missing, the system skips notification (once-daily timing limitation)
6. If the probable pitcher is identified and their ID matches Shohei Ohtani's official league ID, the system sends a push notification with the message: "Shohei Ohtani is the probable pitcher today vs [Opponent Team Name]!"
7. The notification includes a baseball emoji and high priority setting
8. If the pitcher is not Ohtani, the system exits silently

## Acceptance Criteria
- [x] Script can be run with `python check_ohtani.py`
- [x] Script fetches today's Dodgers game from MLB API with dynamic date parameter (YYYY-MM-DD UTC)
- [x] Script correctly identifies probable pitcher by checking both home and away teams for Dodgers (team ID 119)
- [x] Script uses Ohtani's MLB ID (660271) to identify him, not name string matching
- [x] Script sends ntfy.sh notification with correct message format when Ohtani is probable pitcher
- [x] Notification includes Title "Dodgers Alert ⚾️" and Priority "high" headers
- [x] Script exits silently when no Dodgers game today (empty dates array)
- [x] Script retries API call 2-3 times with 5-second delays on failure
- [x] Script logs specific exceptions (not bare except Exception)
- [ ] Cron schedule set to 0 17 * * * (17:00 UTC = 10:00 AM PT)
- [x] ntfy.sh topic is hardcoded in script (user approved no secrets)
**Module:** Daily Pitching Check
**Users:** Owner
**Description:** A daily automated check that looks up today's Dodgers game, identifies the probable starting pitcher, and sends a notification if it's Shohei Ohtani.

**Features:**
- Runs automatically once per day at 10:00 AM Pacific Time
- Looks up today's scheduled Dodgers game from the official MLB schedule
- Identifies the probable starting pitcher for the Dodgers
- Compares the pitcher to Shohei Ohtani's official league ID (660271)
- Sends a push notification to the owner's phone if Ohtani is pitching
- Exits silently if there is no Dodgers game today
- Retries temporarily failed schedule lookups up to three times before giving up

## Verification Notes
After implementation, run:
```bash
python3 ~/.pi/agent/skills/ralph-loop/verify-issue.py <this-file> .
```
This runs your test suite and checks for non-trivial code changes.
