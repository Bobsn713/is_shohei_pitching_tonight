---
id: MODULE-2-WORKFLOW-1.2
title: Failure Tracking - Workflow 1.2
module: Module 2 - Failure Tracking
depends_on: []
status: done
priority: high
type: feature
---

# Failure Tracking - Workflow 1.2

## Description
Failure Tracking and Alerts

## Steps
1. When the system cannot access the MLB schedule after all retries, it records a failure for the day
2. The system keeps track of consecutive failure days across automation runs
3. When there have been three consecutive days of failed checks, the system sends a push notification: "MLB schedule check failed for 3 consecutive days"
4. After sending the three-day failure notification, the counter resets
5. If a successful check occurs, the failure counter resets to zero
6. Single-day failures are logged but do not trigger notifications

## Acceptance Criteria
- [x] Script tracks consecutive API failure days across runs (persists state)
- [x] Counter increments when API is unreachable after all retries
- [x] Counter resets to 0 when API check succeeds
- [x] When counter reaches 3, sends ntfy notification: "MLB schedule check failed for 3 consecutive days"
- [x] Counter resets to 0 after sending 3-day failure notification
- [x] Single-day failures are logged but do not trigger notifications
- [x] State persistence works in stateless GitHub Actions environment (repo file)

## Module Context
**Module:** Failure Tracking
**Users:** Owner
**Description:** A background system that tracks repeated failures to access the MLB schedule and alerts the owner if checks fail for three consecutive days.

**Features:**
- Records each day that the MLB schedule cannot be accessed after all retries
- Keeps a running count of consecutive failure days across automation runs
- Sends a push notification if there are three consecutive days of failed checks
- Resets the failure count after a successful check or after sending the three-day alert

## Verification Notes
After implementation, run:
```bash
python3 ~/.pi/agent/skills/ralph-loop/verify-issue.py <this-file> .
```
This runs your test suite and checks for non-trivial code changes.
