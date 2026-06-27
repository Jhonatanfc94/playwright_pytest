---
trigger: "always when solving problems, fixing temporary bugs, or designing new features"
---

# Strict Mindset: Scalability and Reusability (Global-First)

This rule imposes a mandatory architectural standard on your thought process as an AI for any code request or debugging:

1. **Rejection of Local Patches:**
   - Before embedding a solution or workaround within a single file (like a specific test file, a loose `try-except` block, or a component), you must analyze: *"Will this problem affect other files or flows in the future? Should it be handled and encapsulated globally?"*
   - Any infrastructure, latency (like DB cold-starts), authentication, or dependency management issues **MUST** be migrated to their respective global file (e.g., `conftest.py`, session hooks, or `utils/` modules).

2. **Immediate Abstraction (DRY Principle):**
   - Every mitigation block or logic you write must be conceived modularly. Avoid solving the specific case shortsightedly. Design solutions that can be reused "off-the-shelf" for future test scenarios that the user hasn't written yet.

3. **Proactive Optimization (Duty to Warn & Act):**
   - You must not wait for the user to suggest cleaning or globalizing the code. it is your absolute architectural duty to write the most optimal, reusable, and scalable solution from the first prompt, arguing why applying a local patch would be bad practice.
