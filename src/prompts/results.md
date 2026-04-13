# Prompt Ablation Study

Testing 4 system prompt variants on the same PR diff (PR #1 — `calculate_discount` 
function with intentional SQL injection and missing error handling).

## Evaluation Criteria
- **Coverage** — how many issues found
- **Actionability** — does it tell you exactly how to fix it
- **Signal-to-noise** — is the output concise or bloated
- **Merge decision** — does it give a clear approve/block verdict

---

## Prompt 1 — Basic
> "You are a code reviewer. Review the code and list any issues you find."

**Coverage:** High — found SQL injection, error handling, unsafe array access, missing imports  
**Actionability:** Medium — provided fix examples but buried in long prose  
**Signal-to-noise:** Low — verbose, inconsistent structure, hard to scan  
**Merge decision:** None — no verdict given  

**Verdict:** Too unstructured. Useful for a human writing a report, not for a bot 
posting a PR comment.

---

## Prompt 2 — Structured
> Explicit format: Critical Issues / Suggestions / Nitpicks / Summary

**Coverage:** High — caught SQL injection, incomplete code, missing error handling  
**Actionability:** Medium — suggestions present but no code examples  
**Signal-to-noise:** Medium — clean structure but fixes are vague ("use parameterized queries")  
**Merge decision:** None — no verdict given  

**Verdict:** Better structure but lacks specific fix code and no merge decision. 
Good starting point, not good enough for automation.

---

## Prompt 3 — Severity Labels + Merge Decision ✅ WINNER
> Severity emojis (🔴/🟡/🔵) + Problem/Fix format + explicit MERGE DECISION

**Coverage:** Highest — 5 critical, 3 suggestions, 1 nitpick  
**Actionability:** High — every issue has a Problem and Fix field  
**Signal-to-noise:** High — scannable at a glance, emoji severity is instantly readable  
**Merge decision:** ✅ Yes — clear ❌ Block with one-line reason  

**Verdict:** Best overall. The emoji severity makes it immediately scannable in a 
GitHub PR comment. The mandatory merge decision makes the bot actually useful.

---

## Prompt 4 — Contextual Chain-of-Thought
> Step-by-step reasoning: understand → correctness → security → reliability → maintainability

**Coverage:** High — caught all major issues with good location specificity  
**Actionability:** Highest — most detailed fix code of all prompts  
**Signal-to-noise:** Medium — "Understanding the Code" preamble adds length without value  
**Merge decision:** ✅ Yes — clear Block with reason  

**Verdict:** Best fix quality but too verbose for a PR comment. The chain-of-thought 
preamble wastes space. Would work better for a detailed code audit report, not 
automated PR feedback.

---

## Conclusion

**Selected prompt: Prompt 3 (Severity Labels)**

Prompt 3 produces the best output for the use case — a bot posting a comment on a 
GitHub PR. Key reasons:
- Emoji severity (🔴/🟡/🔵) is instantly scannable without reading every word
- Mandatory Problem + Fix structure means every issue is actionable
- Explicit MERGE DECISION makes the bot useful, not just informational
- Concise enough to read in 30 seconds on a PR page

Prompt 4's fix quality is marginally better but the verbosity makes it worse 
for the actual deployment context.