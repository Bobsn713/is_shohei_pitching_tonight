# Shohei Ohtani Pitching Notifier — Product Requirements Document (PRD)

> Purpose: Document the requirements for an automated daily notification system that alerts when Shohei Ohtani is scheduled to pitch for the Dodgers
> Scope: Complete automation tool including daily check, notification, and failure tracking
> Detail level: Happy path flows and edge cases

---

## Platform Overview

A lightweight automation tool that checks daily whether Shohei Ohtani is the probable starting pitcher for the Los Angeles Dodgers. When he is scheduled to pitch, the system sends a push notification to the user's phone. The entire system runs in the cloud using a hosted automation service, requiring no desktop or server maintenance.

---

## User Roles
| Role | Description | Access |
|------|-------------|--------|
| Owner | The person who sets up the tool and receives pitching notifications | Full access to configure the system, view logs, and receive alerts |

---

## Module 1 — Daily Pitching Check
**Who uses it:** Owner
**What it is:** A daily automated check that looks up today's Dodgers game, identifies the probable starting pitcher, and sends a notification if it's Shohei Ohtani.

### Feature Overview
- Runs automatically once per day at 10:00 AM Pacific Time
- Looks up today's scheduled Dodgers game from the official MLB schedule
- Identifies the probable starting pitcher for the Dodgers
- Compares the pitcher to Shohei Ohtani's official league ID (660271)
- Sends a push notification to the owner's phone if Ohtani is pitching
- Exits silently if there is no Dodgers game today
- Retries temporarily failed schedule lookups up to three times before giving up

### Workflow 1.1 — Daily Check and Notification
1. At 10:00 AM Pacific Time, the automation triggers automatically
2. The system looks up today's Dodgers game information from the official MLB schedule, including probable pitcher details
3. If the schedule lookup is temporarily unreachable, the system retries up to three times with a five-second wait between attempts
4. If there is no Dodgers game today, the system exits silently with no notification
5. If the probable pitcher information is missing, the system skips notification (once-daily timing limitation)
6. If the probable pitcher is identified and their ID matches Shohei Ohtani's official league ID, the system sends a push notification with the message: "Shohei Ohtani is the probable pitcher today vs [Opponent Team Name]!"
7. The notification includes a baseball emoji and high priority setting
8. If the pitcher is not Ohtani, the system exits silently

---

## Module 2 — Failure Tracking
**Who uses it:** Owner
**What it is:** A background system that tracks repeated failures to access the MLB schedule and alerts the owner if checks fail for three consecutive days.

### Feature Overview
- Records each day that the MLB schedule cannot be accessed after all retries
- Keeps a running count of consecutive failure days across automation runs
- Sends a push notification if there are three consecutive days of failed checks
- Resets the failure count after a successful check or after sending the three-day alert

### Workflow 1.2 — Failure Tracking and Alerts
1. When the system cannot access the MLB schedule after all retries, it records a failure for the day
2. The system keeps track of consecutive failure days across automation runs
3. When there have been three consecutive days of failed checks, the system sends a push notification: "MLB schedule check failed for 3 consecutive days"
4. After sending the three-day failure notification, the counter resets
5. If a successful check occurs, the failure counter resets to zero
6. Single-day failures are logged but do not trigger notifications

---

## Edge Cases and Error Handling

| Scenario | Behavior |
|----------|----------|
| No Dodgers game today | Silent exit, no notification |
| Probable pitcher not announced yet | Silent exit, no notification (once-daily check limitation) |
| MLB schedule temporarily down | Retry 2-3 times with 5-second delays, then log failure |
| MLB schedule down for 3+ consecutive days | Send failure notification via push alert |
| Network timeout | Retry with delay (same as server error) |
| Ohtani is playing but not pitching (designated hitter) | No notification (probable pitcher field indicates starting pitcher only) |
| Script crashes unexpectedly | Automation service shows failed run; no push notification (owner checks automation logs) |

---

## Planned Features (Not Yet Live)
| Feature | Intended Purpose |
|---------|-----------------|
| Retry logic for missing probable pitcher | Check again later in the day if pitcher not announced at 10 AM |
| Multiple pitcher tracking | Notify for other favorite pitchers in addition to Ohtani |
| Email notifications | Add email as a backup notification method |

---

## Key Capabilities (Cross-Module)
| Capability | Where It Appears |
|-----------|-----------------|
| Push notifications | Module 1 (pitching alerts), Module 2 (failure alerts) |
| Consecutive failure tracking | Module 2 |
| Retry logic for temporary failures | Module 1 |
