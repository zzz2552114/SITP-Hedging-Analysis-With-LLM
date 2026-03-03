---
description: Verify first; only commit when verification passes.
---

---
description: Verify first; only commit when verification passes.
---

# /verify_and_commit

1) Call /verify
2) If anything fails:
   - Fix the issues
   - Re-run /verify until pass
3) When all pass:
   - Call /commit
4) Output final summary + how to reproduce verification locally