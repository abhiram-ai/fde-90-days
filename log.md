# FDE 90-Day Log

## Day 1 — [Date]
**Topic:**
**Built:**
**Got stuck on:**
**Learned:**

**Customer Slack Reply (90 Min Mark):**
I understand you want to make the `customer_email` field optional for anonymous feedback and change the `source` field to accept a list of multiple channels. The tradeoff here is that allowing multiple sources makes our query filtering slightly more complex, and anonymous records mean your team loses the ability to contact those users for follow-ups. I can update the schema to handle an array of sources and an optional email, but to clarify: if a team member filters by `?source=email`, should it return records tagged with *both* email and Slack, or only records that are *strictly* email?

**Decision:** Defer.

**Justification:** Since the immediate goal is just to prove the "plumbing works" by EOD, it is safer to ship the current working MVP as-is and incorporate these schema adjustments directly into tomorrow's database migration to avoid destabilizing the build right before the deadline.

**Broken FastAPI Code Analysis:**
1. **Off-by-one error (IndexError):** `create_item` returns an ID based on `len(items)` *after* appending. The first item gets ID `1`. However, `get_item` uses this ID directly as a Python list index (`items[item_id]`). Since Python lists are 0-indexed, requesting ID 1 attempts to access `items[1]`, causing an `IndexError` on the very first item.
2. **Missing 404 Error Handling:** `get_item` has no bounds checking. If a client requests an ID that doesn't exist, it will crash the endpoint with an `IndexError` (500 Internal Server Error) instead of gracefully returning a `404 Not Found` via `HTTPException`.
3. **Negative Indexing Bug:** Because `items` is a standard Python list, passing `item_id=-1` to `get_item` will silently return the last item in the list instead of throwing an error, which is an unintended API behavior.

**End-of-Day Customer Update:**
The first version of the feedback triage API is live, allowing your team to instantly capture and standardize incoming customer feedback. You can test it out and view the interactive documentation here: `https://your-feedback-app.up.railway.app/docs`. Please note that for this initial test, data is not saved permanently and will reset if the server restarts. Tomorrow, I will connect a database to make the storage permanent and add the ability to log multiple sources per feedback item. Can you test submitting a dummy feedback record today and confirm if the required fields match your team's expectations?

**Reflections:**
- **Slowest part of the build:** Tooling and setup. Dealing with the `pydantic[email]` dependency error and wrapping my head around virtual environments/uvicorn took more mental energy than writing the actual FastAPI code.
- **Assumptions made:** I assumed setting the default category to "uncategorized" was fine for now, but I could have easily asked the customer for their top 2-3 real categories to make the MVP immediately more useful.
- **Biggest customer complaint:** They would definitely complain that all their submitted feedback vanishes into thin air the moment the server restarts (due to the temporary in-memory dictionary).

**Confidence Scores (1-5):**
- Backend basics: 4
- Deployment: 3
- Handling ambiguity: 4

**Why Use Migrations?**
We cannot just edit the database directly because manual changes cannot be easily tracked, shared, or applied consistently across different environments. Migrations solve this by treating database schemas as code, ensuring reproducibility across all developer machines and production instances. Furthermore, they provide reviewability through standard pull requests and reversibility to safely roll back changes if something breaks.

**One concept that surprised me:**
Alembic for data migration. I hadn't realized how crucial it is to have a dedicated tool to version-control and track database schema changes over time, just like we do with regular code.

**One concept I don't fully get yet:**
I still don't completely grasp how Alembic migrations are actually executed across different environments (like local vs. staging vs. production). Seeing a concrete, working example of a deployment pipeline running these migrations would really help solidify my understanding.