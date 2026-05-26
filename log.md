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

## Simulation: Customer Roleplay
**Slack Reply:**
Hey! I completely get the concern about falling behind on important feedback, and yes, we can absolutely set up a spreadsheet export for the team. Let's tackle the urgent messages first since that impacts your customers directly. To make sure we highlight the right things automatically, I'd love to know how the ops lead currently decides what counts as "urgent" when reading a message. Do they look for specific words like "broken", or does urgency depend more on exactly who the customer is? Once you let me know their mental checklist, I'll put together a quick mockup showing how we can make those specific messages jump to the top of their daily list.

## SQLAlchemy Models Code Analysis
1. **`default=datetime.now()` (Severity: Bug / Production Risk):** The `now()` function is executed exactly once when the module is imported at server startup. This means every single feedback record inserted will have the exact same creation timestamp. **Fix:** Pass the callable reference without executing it (`default=datetime.now`), or better yet, use `server_default=func.now()`.
2. **Timezone-naive timestamps (Severity: Production Risk):** `datetime.now()` creates a timestamp without timezone information. This leads to data inconsistency and tricky bugs if the server changes regions or during Daylight Saving Time. **Fix:** Use UTC explicitly: `default=lambda: datetime.now(timezone.utc)` along with `DateTime(timezone=True)`.
3. **UUID object assigned to a String column (Severity: Bug / Design Flaw):** `uuid.uuid4` returns a Python `UUID` object, but the column is typed as `String`. While some drivers might try to coerce this, it's brittle. Additionally, unbounded strings are inefficient for database primary keys. **Fix:** Use SQLAlchemy's native `Uuid` type instead of `String` for the `id` column.
4. **Missing Database-level Defaults (Severity: Production Risk):** Using ORM-level defaults like `default=False` only populates the value when inserting via this specific Python application. If a DBA runs a raw SQL `INSERT` or a different service writes to the database, the field will become `NULL` and break application logic. **Fix:** Add database-level defaults using `server_default` (e.g., `server_default="false"` on the boolean column).

## Commit Message
```text
Migrate feedback storage to PostgreSQL database

The in-memory dictionary resets on every deployment, causing data loss.
This change replaces it with a persistent Postgres database using
SQLAlchemy ORM and Alembic for automated schema migrations. It also
introduces a safe deployment pipeline on Railway to execute migrations
before the web server starts, preventing race conditions.

BREAKING CHANGE: Previous in-memory data is not preserved.
```

## Day 2 Reflections 
1. **What part of restructuring the project was hardest? Knowing where things go, or letting go of main.py?**

Writing the SQLAlchemy models and integrating the database changes into the feedback routers was the most challenging part of the code restructuring. It took some time, but overall I really enjoyed the exercise and feel I understand the architecture now. The most time-consuming part, however, was the Railway deployment. I ran into a chain of tricky issues that took a while to debug and resolve: 
    1. The app crashed on boot because it couldn't read the DATABASE_URL environment variable. 
    2. Once connected, it crashed with a ModuleNotFoundError because I hadn't included the psycopg2-binary driver in my requirements.txt. 
    3. Finally, I hit a relation "feedback" does not exist error because the tables weren't created. I had to configure a pre-deploy command to run alembic upgrade head so migrations execute automatically. 
2. **When you read your auto-generated Alembic migration, did you understand every line? If no — which lines?**
Yes, I do understand every line now. I struggled a little bit at the start when first looking at the auto-generated script, but taking a moment to step through it helped me figure it out. 3. **The customer roleplay: did you feel the urge to start coding before fully understanding the request?**
Yes, I definitely felt the urge to jump straight into coding! It's challenging to hold back and ask questions first. I also still have technical questions about how we will actually implement the logic for the "urgent stuff bubbles up" requirement once we understand what the customer really means. 
4. **Confidence score (1–5) on: project structure, databases, customer discovery**  
Project structure: 4 (Feeling good about routers vs. models vs. database)  
Databases: 3 (Deployment debugging was tough, but the local ORM makes sense)
Customer discovery: 3 (Still fighting to get graspe, but building the muscle!)

**Lesson from PATCH failure:**
Smoke test had a manual substitution step (`<YOUR_FEEDBACK_UUID>`) that I 
forgot to fill in. The real fix isn't to remember next time — it's to chain 
the POST output into the PATCH input so the test is self-contained.

## Day 3 — [Sunday May 24th 2026]
**Status:** Paused for personal commitments.
**Resuming:** Tomorrow.
**Pre-resume task:** None — pick up fresh.

## Observability Core Concepts
**The Three Pillars of Observability:**
1. **Logs (Phase 1):** Discrete, timestamped events (e.g., "User A got a 404 error at 10:00 AM"). The foundation for debugging specific issues.
2. **Metrics (Phase 2):** Aggregated data over time (e.g., "Error rate is currently 2%"). Used for dashboards, system health, and triggering alerts.
3. **Traces (Phase 3):** The end-to-end journey of a single request across multiple services (e.g., "This request took 2s: 1.8s of which was stuck in the DB"). Used for bottleneck hunting in distributed systems.

**Python Logging Mental Model:**
Instead of `print()`, we use the `logging` module because it provides context, severity levels, and routing.
*   **Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL. Sets the threshold for what gets recorded vs. ignored.
*   **Components:**
    *   **Logger:** The interface your code calls (`logger.info()`).
    *   **Handler:** The destination (Console, File, Network).
    *   **Formatter:** The structure/layout of the text (soon to be JSON).

**One thing that surprised me about observability vs monitoring:**
I always used to think that "observability" and "monitoring" were just interchangeable terms. After looking up Charity Majors' framing, it surprised me to learn that observability is specifically about having enough rich context to debug the weird, unpredictable failures you never could have imagined, whereas monitoring is just for the predictable ones you already know to look for.

**One question I'd ask a senior engineer about testing strategy:**
"When writing tests for an API heavily reliant on a database, how do you decide when to use a real test database (which is accurate but can make the test suite painfully slow) versus mocking the database (which is fast but might hide real integration bugs)? How do you balance that tradeoff at scale?"

**Customer Reply: Why focus on tests and logs?**
To give you complete confidence before Monday's launch, we are prioritizing automated testing and structured logging as our absolute highest-leverage safety measures. Automated tests act as an invisible safety net that runs on every code update, guaranteeing we never accidentally break the core features your ops team relies on. Simultaneously, structured logging gives us instant, searchable visibility into the system's exact behavior, meaning if anything unexpected *does* happen in production, we can immediately pinpoint the root cause and fix it before your customers even notice.

**Lesson from Day 3 testing:**
Mentor's test spec said "404 for malformed UUID" but my implementation
returns 422 because FastAPI validates the UUID type before my code runs.
Both are defensible — 422 is technically more correct (validation failure,
not missing resource). Updated test to assert 422 and added a separate
404 test for valid-format-but-not-found. Wrote docstrings on both so the
intent survives future changes.

**Lesson — pushing back on mentor:**
Mentor suggested ExceptionPrettyPrinter as a style-consistent alternative
to format_exc_info. Realized it would inject ANSI codes and multi-line
formatting into the JSON payload, breaking parsers. Pushed back with
specifics. Mentor confirmed and reversed. Keep the muscle of disagreeing
with evidence, especially as the stakes go up.

## Simulation: The CEO Request
**Voice Memo (Internal Prep):**
- *Who am I really writing for?* The CEO. My customer is just the messenger acting as a proxy. I need to give them a shield to hold up in their next executive meeting.
- *What's the real concern?* "SLA" actually means "Will this crash and lose our data?" Security means "Will a competitor steal our customer list and will I be on the news?" She wants to minimize risk before exposing this to the whole company.
- *What's the smallest useful thing?* A one-page "Security & Reliability Overview" written in plain English that explains our database backups, data encryption, and access controls. 

**Slack Reply:**
Hey! It's awesome the CEO liked the dashboard, and those questions are completely standard before a company-wide rollout. She’s essentially looking for confidence that we won’t lose your data and that it's safe from outsiders. Since we're still in the early rollout phase, we don't have formal SLAs or third-party compliance audits just yet. However, I can definitely put together a clear 1-pager detailing our database backups, encryption, and access controls so you have something concrete to hand her. Before I write that up, does your IT team have a standard vendor security questionnaire we need to fill out, or is a plain-English summary enough for her right now?

## Testing Anti-Patterns Analysis
**1. State-Dependent Assertions**
In the filtering test, `assert len(results) == 1` assumes the database was completely empty before the test started. However, the first test *also* creates a feedback record with `source="email"`. If these tests run against a persistent shared database, or if `pytest` randomly runs them in parallel down the line, `len(results)` will suddenly be 2 (or 50) and the test will mysteriously fail. This is the most dangerous kind of test because it creates "flaky" CI pipelines.
*Fix:* Tests should rely on isolated transactional fixtures, or assert *inclusion* (e.g., checking that the specific ID we just created is in the list) rather than absolute global counts.

**2. Global TestClient (Severity: Design Flaw / Data Risk)**
Instantiating `client = TestClient(app)` at the top of the file completely bypasses the `client` fixture and dependency overrides we set up in `conftest.py`. This means these tests aren't using the isolated `feedback_test` database at all—they are hitting your real development database and mutating real data!
*Fix:* Always pass `client` as a fixture argument to the test function so it uses the intercepted, safe test database.

**3. Manual Cleanup in Test Body (Severity: Design Flaw / Test Pollution)**
Relying on comments like `TODO: delete the record` or placing manual deletion logic at the end of a test function is an anti-pattern. If *any* `assert` fails earlier in the test, Python raises an `AssertionError` and halts execution immediately. The cleanup code is never reached, leaving garbage data behind that will likely break the next test.
*Fix:* Cleanup should always be handled automatically by a Pytest fixture (using `yield` and a `finally` block or transaction rollbacks).

## Release Notes (Day 3)

**What's new**
We've added a behind-the-scenes tracking system that attaches a unique ID to every single piece of feedback that enters the platform. This allows our support team to instantly trace exactly what happened if an error occurs, completely securely and without ever exposing your customers' private information.

**What's changed**
We massively upgraded the reliability of the platform by introducing automated safety checks. These checks act as an invisible net that automatically verifies every feature is working correctly before any new update goes live, ensuring the tool stays incredibly stable for your ops team.

**Coming soon**
Next up, we will be sharing a plain-English security and reliability overview for you to share with your leadership team. Once that is squared away, we will begin working on the logic to automatically flag urgent feedback so it never falls through the cracks.

## Day 3 Reflections

**The incident simulation — how long did it take you to find the bug? What would have made it 5x faster?**
To be honest, I actually skipped the incident simulation today because I was focused on getting the code deployed earlier. I would love to tackle a similar debugging drill in tomorrow's exercise to really put my troubleshooting skills to the test!

**Which tests felt useful to write, and which felt like checking boxes? Why?**
**Useful:** The 503 database failure test for `/health` and the `PATCH` endpoint test using the `sample_feedback` factory. These proved that our dependency injection overrides work and that our database transaction logic behaves as expected. They are testing *our* specific logic and edge cases. 
**Checking boxes:** The basic validation tests (like returning 422 for malformed UUIDs or empty text). Because FastAPI and Pydantic handle this so robustly out of the box, writing tests to prove that Pydantic rejects an empty string feels a bit like testing the framework rather than our own code, though I understand it's good practice for catching future regressions.

**Of the things you built today, which one will you actually use in your next project, and which felt like overhead?**
Honestly, I plan to use all of them. I previously had limited experience with Pytest fixtures and structured logging (especially binding request IDs across the context), and this exercise gave me an entirely new perspective on both testing and observability. None of it felt like overhead once I saw how it fits together—it feels like essential infrastructure.

**One lingering question:**
Isn't logging *every* single API call in production a performance and storage overhead? I completely understand logging errors and failures, but I am curious about the tradeoffs of logging the "happy path" at scale.

**Confidence scores (1–5):**
- **Testing:** 4 (Dependency overrides and fixtures make a lot of sense now)
- **Observability:** 4 (Structured JSON logging with request IDs is a game-changer)
- **Debugging under pressure:** 3 (Skipped the simulation today, ready for the challenge tomorrow!)

## Stuck points:
- **[thing I don't fully understand]:** How Pytest handles the `yield` and `finally` sequence in fixtures (like in our `test_db` fixture). Does it genuinely pause execution, run the test, and then resume? What happens if a test hits a hard crash (like a C-level segfault or out-of-memory error)? Does the `finally` block still guarantee my test tables get dropped?
- **[thing I'm not sure I built right]:** My test database setup in `conftest.py`. Currently, it runs `Base.metadata.create_all` and `drop_all` for every single test. This feels like it could get painfully slow once the suite grows to hundreds of tests. Should I be using nested database transactions and rolling back instead of completely dropping and recreating tables every time?
- **[thing I want a second opinion on]:** The placement of my `structlog.contextvars` binding inside the FastAPI middleware. Is `request_id_middleware` the absolute best place for this? I'm wondering if FastAPI rejects a request extremely early (like a 404 routing error or a 422 validation error), do those logs still get the `request_id` attached, or does it bypass the middleware entirely?


Day 3 ended tired but proud: logging works end-to-end, and successfully pushing back on a mentor's suggestion showed me what real progress feels like.