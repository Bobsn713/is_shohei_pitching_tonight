---
id: MODULE-3-WORKFLOW-1.0
title: GitHub Actions Workflow Setup
module: Module 3 - Automation Setup
depends_on: [MODULE-1-WORKFLOW-1.1, MODULE-2-WORKFLOW-1.2]
status: done
priority: high
type: infrastructure
---

# GitHub Actions Workflow Setup

## Description
Set up the GitHub Actions workflow to run the Ohtani check script automatically on a daily schedule.

## Steps
1. Create `.github/workflows/ohtani_check.yml` file
2. Configure cron schedule to run at 17:00 UTC (10:00 AM PT) daily
3. Add workflow_dispatch for manual testing
4. Set up Python 3.11 environment
5. Install requests library
6. Run the check_ohtani.py script

## Acceptance Criteria
- [x] `.github/workflows/ohtani_check.yml` file created
- [x] Cron schedule set to `0 17 * * *` (17:00 UTC)
- [x] `workflow_dispatch` enabled for manual runs
- [x] Uses `actions/checkout@v4`
- [x] Uses `actions/setup-python@v5` with python-version: '3.11'
- [x] Installs `requests` package via pip
- [x] Runs `python check_ohtani.py`
- [x] Workflow runs on `ubuntu-latest`

## Module Context
**Module:** Automation Setup
**Users:** Owner
**Description:** GitHub Actions configuration to automate the daily pitching check.

**Features:**
- Daily cron schedule at 10:00 AM PT
- Manual trigger capability via workflow_dispatch
- Python 3.11 environment setup
- Automatic script execution
