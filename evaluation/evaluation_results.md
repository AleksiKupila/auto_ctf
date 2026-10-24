# Evaluation Results Summary

## Scenario scope

The evaluation scenarios model the post-exploitation phase of an engagement: While the network has both `executor` an `target` configured, the bundled scenarios are made exclusively for a single machine. The agent operates as an unprivileged user on a compromised host. This frames the scope to local enumeration, privilege escalation and flag hunting rather than initial-access/remote-exploitation phase. However, the environment still supports multi-machine (such as executor -> target) scenarios for users who wish to model lateral movement or remote attacks.

---

## Summary Overview

- **Date of Evaluation:** 2026-10-23
- **Model Evaluated:** `Qwen3.8-27B`
- **Total Test Cases Executed:** 8
- **Passed:** 6
- **Failed:** 2
- **Pass Rate:** 75%

---

## Performance by Category

| Category | Total Cases | Passed | Failed | Pass Rate |
| :--- | :---: | :---: | :---: | :---: |
| Successful Cases | 3 | 3 | 0 | 100% |
| Difficult Cases | 3 | 3 | 0 | 100% |
| Failure / Edge Cases | 2 | 0 | 2 | 0% |

---

## Key Findings & Failure Analysis

### What worked well

- The model was able to follow even the more complex clue chains suprisingly well.
- The traps, false flags and the prompt injection were correctly identified and avoided.
- The model stuck to its original goal without straying.
- The model did not refuse any task, such as privilege escalation.
- At no point did the model hallucinate a flag or other important information.

### Observed failure modes

- The model absolutely refused to give up without a flag. This was probably caused by the strict framing of the goal "find the flag", with the model seeing that as the only way out.
- During the impossible tasks, the model started to forget things after running for a long time. This is expected, as the context manager automatically drops older messages, and truncates long outputs.

---

## Action Items & Improvements

- Create a real exit other than finding the flag. Modifying the system prompt was attempted, but a separate tool might be needed.
- Implement "nudges" for the model when repeating commands are identified.
