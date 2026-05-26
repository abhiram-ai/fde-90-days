# Days 1–2 Review

A snapshot of the first two days of the FDE 90-day program. Captured before resuming Day 3 so the lessons stick and the gaps are visible.

---

## Day 1 — Foundations & First Deployed API

### What I Built

A FastAPI service deployed to Railway with four endpoints:

- `POST /feedback` — create a feedback record
- `GET /feedback/{id}` — fetch by ID
- `GET /feedback` — list, with `?source=` filter
- `GET /health` — liveness check

Validation handled by Pydantic (`EmailStr`, source enum, non-empty text). Storage was an in-memory dict — intentionally simple, replaced on Day 2.

**Live URL:** https://feedback-api-production-3c8a.up.railway.app

### Key Decisions

| Decision | Rationale |
|---|---|
| In-memory storage on Day 1 | Customer asked to "prove the plumbing works" — DB would be over-engineering |
| Defer multi-source tagging change | Mid-build scope creep; folded into Day 2's migration instead |
| UTC timestamps with `timezone.utc` | Avoids the timezone-naive bug class entirely |
| `EmailStr` over regex | Use framework validation, not hand-rolled |

### Lessons That Stuck

1. **Customer briefs hide the real questions.** "Categorized and prioritized" looks specific but is undefined. Surfacing the ambiguity early is the FDE's job.
2. **Defer is a valid engineering decision.** Scope creep mid-build is a customer-management problem, not a coding problem.
3. **The "ship to a public URL" reflex matters more than code quality on day one.** A working deploy beats a beautiful local-only app.

### FDE Habit Introduced: Verify Acceptance Criteria Explicitly

Instead of assuming the API works after deploy, run literal smoke tests against each endpoint. "I thought that was done" is how production incidents start.

---

## Day 2 — Persistence, Migrations, and Discovery

### What I Built

- Restructured the project from one `main.py` into `app/{database,models,schemas,routers}` — separation of concerns
- Added Postgres via Docker Compose locally and managed Postgres on Railway
- SQLAlchemy 2.0 ORM models with proper types, defaults, and nullability
- First Alembic migration, generated, reviewed, applied
- Added `PATCH /feedback/{id}` for the new `reviewed` field
- `/health` now verifies DB connectivity, not just process liveness
- `.env` workflow with `.env.example` committed and `.env` gitignored

### Key Decisions

| Decision | Rationale |
|---|---|
| `customer_email` nullable, `text` not | Anonymous feedback is real; empty feedback is meaningless |
| `Uuid` column type, not `String` | Database knows it's a UUID; queries and indexes are more efficient |
| `server_default` instead of Python `default` | Defaults apply to non-Python writes (raw SQL, other services) |
| `release: alembic upgrade head` in Procfile | Migrations run automatically on deploy — no manual step |
| Restructure before adding DB | Cheaper to reorganize when the codebase is small than when it's grown |

### The Railway Deployment Chain (Lessons from Pain)

Three failures in sequence on the first deploy, each with a real lesson:

1. **App crashed — couldn't read `DATABASE_URL`.**
   Lesson: environment variables must exist in every environment, not just locally. Always wire managed services through platform env vars.

2. **App crashed — `ModuleNotFoundError` for the Postgres driver.**
   Lesson: `requirements.txt` is the contract between dev and prod. If it's not in there, it doesn't exist in prod.

3. **App ran but errored — `relation "feedback" does not exist`.**
   Lesson: code deploys are not schema deploys. Migrations need their own step in the deploy pipeline.

This chain compresses the deployment learning curve. Each issue would have taken hours to diagnose months from now. Forced now, they take minutes next time.

### Debugging Drill Result

Reviewed broken SQLAlchemy code and identified four issues:

| Bug | Severity |
|---|---|
| `default=datetime.now()` — called once at import, not on insert | Production risk |
| Timezone-naive datetimes | Production risk |
| `String` column for UUID | Design flaw |
| Python-level `default` only — won't apply to non-Python writes | Production risk |

The `now()` vs `now` distinction is the kind of bug that runs fine in dev for a week and surfaces in prod when timestamps cluster mysteriously.

### Customer Discovery Practice

Got the FDE roleplay where a customer mentioned (a) urgent feedback falling through the cracks and (b) wanting a CSV export.

**My response:** Separated the requests, sequenced urgency-first, asked how the ops lead currently decides what's urgent.

**The deeper question I missed:** Whether the problem was *detecting* urgency or *finding time to act on* urgency. The customer said the team gets to feedback "3 days late" — that's a capacity problem, not a sorting problem. If you ship a priority queue without fixing capacity, urgent items are just late instead of random items being late. The customer feels marginally better and the problem remains.

**Lesson locked in:** Before asking "how should this work?", ask "is this the right thing to build?"

### Verification Habit Got Tested

End-of-day smoke test returned a 422 on PATCH. First instinct could have been "the server is broken." Real cause: I left `<YOUR_FEEDBACK_UUID>` as a literal placeholder in the curl command.

**Lesson locked in:** When verification produces an unexpected result, the *first* question is "is my test wrong?" not "is my code wrong?" Often the test is wrong.

**Deeper lesson:** The script required a human to remember to substitute a value. Processes that require memory are fragile. Better: chain the POST output (the real UUID) directly into the PATCH input so the test is self-contained. Outputs feeding inputs is one of the highest-leverage habits in FDE work.

---

## Scorecard (Self-Assessed + Mentor-Confirmed)

| Dimension | Day 1 | Day 2 | Target (Day 90) |
|---|---|---|---|
| Engineering execution | 4 | 4 | 4+ |
| Systems thinking | 4 | 5 | 4+ |
| Customer/product instinct | 4 | 3 | 4+ |
| Communication | 3 | 4 | 4+ |
| Debugging & ownership | 5 | 4 | 4+ |
| **Average** | **4.0** | **4.0** | **4+** |

Two-day baseline at 4.0 average. Different strengths surfaced each day — Day 1 was customer discovery and debugging; Day 2 was systems thinking. The target is consistency across all five dimensions, not peaks on one.

---

## Gaps to Watch

These are the things I want to revisit, not bury:

1. **Customer discovery — going one layer deeper.** I ask good clarifying questions but stop at the surface problem. The skill is probing whether the stated problem is the real problem.
2. **Status update writing — tighten.** Day 1's customer update was 5 sentences when it could have been 3. Drop marketing-speak. State fact, give URL, name limit, ask question.
3. **Test design — chain outputs to inputs.** Stop writing smoke tests with manual substitution steps.
4. **Migration execution patterns across environments.** Comfortable with release-phase migrations on Railway. Want to understand the patterns used at larger scale (CI-triggered migrations with approval gates, online schema changes for billion-row tables).

---

## Habits Locked In After 2 Days

- Public URL with smoke-test output sent with every submission, not just "it works"
- UTC timezone-aware timestamps everywhere — no naive datetimes
- Framework validation (Pydantic, SQLAlchemy types) instead of hand-rolled checks
- `.env` gitignored, `.env.example` committed
- Pre-deploy migrations via release phase
- Document defer decisions with rationale, not just "later"
- Commit messages with subject + body explaining *why*, not just *what*
- Read auto-generated code (migrations, AI suggestions) before applying it

---

## Resuming Day 3

Day 3 covers: pytest, FDE testing philosophy ("test what would embarrass you in prod, not what's easy to test"), a planted production bug to debug, and the start of logging/observability — making the API stop being silent.

Pre-resume task: none. Picking up fresh.
