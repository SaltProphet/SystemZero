
---

# System//Zero  
**A local-first protocol for logging, pattern detection, and system behavior analysis.**

## Overview  
System//Zero is a tactical clarity tool for tracking how systems behave — platforms, processes, or people. It is built in phases, with each phase delivering a functional, testable layer. The protocol is designed for operators who need visibility, not assumptions.

---

## Current Status: Phase 2  
Manual logging is active. Core directory structure is in place. Phase 2 focuses on real-time logging, pattern detection, and operator feedback loops.

---

## Repository Structure

| Path | Purpose |
|------|---------|
| **`systemzero/`** | Core logic, scripts, and modules for logging and analysis |
| **`.vscode/`** | Editor config for consistent development |
| **`.github/`** | GitHub workflows and issue templates |
| **`README.md`** | This file |
| **`ROADMAP`** | High-level development plan across phases |
| **`ARCHITECTURE.md`** | System design, module layout, and data flow |
| **`PHASE1_ANALYSIS.md`** | Postmortem and findings from Phase 1 |
| **`PHASE2_PLAN.md`** | Objectives and scope for Phase 2 |
| **`PHASE2_DEBRIEF.md`** | Mid-phase analysis and adjustments |
| **`PHASE2_SUMMARY.md`** | Summary of Phase 2 outcomes |
| **`PHASE3_PLAN.md`** | Draft plan for Phase 3 (UI and automation) |
| **`TESTING_STRATEGY_DEBRIEF.md`** | Notes on testing methodology and results |
| **`CHANGELOG.md`** | Commit-level change tracking |
| **`LEGAL.md`** | Licensing and usage terms |
| **`SECURITY.md`** | Security policy and disclosure process |

---

## Phase Breakdown

### ✅ Phase 1: Baseline Logging  
- Manual offer logging (timestamp, type, outcome)  
- Local-only storage  
- No UI, CLI-only  
- Initial breach tracking logic  
- Analysis of suppression patterns

### 🔄 Phase 2: Pattern Detection + Feedback  
- Real-time logging interface (CLI)  
- Pattern recognition (decline clusters, offer gaps, system behavior)  
- Operator feedback loop: log → analyze → adjust  
- Debrief and recalibration modules  
- Prep for UI scaffolding

### 🔜 Phase 3: UI + Automation  
- Local-first UI with immutable log views  
- Screenshot parsing and notification hooks  
- Breach detection heuristics  
- Operator-defined filters and triggers  
- Exportable logs and summaries

---

## Usage (Phase 2)

1. **Log Offers**  
   Manually enter offer data (timestamp, payout, distance, outcome).  
2. **Review Logs**  
   Use CLI tools to view logs, filter by outcome, and detect patterns.  
3. **Debrief**  
   Run post-shift summaries to identify suppression or drift.  
4. **Adjust**  
   Use insights to change strategy or escalate.

---

## License  
This protocol is for personal use only. Redistribution or repackaging without consent is not permitted. See `LEGAL.md` for details.

---

