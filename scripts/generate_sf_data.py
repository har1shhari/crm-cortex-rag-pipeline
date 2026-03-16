"""
generate_sf_data.py
-------------------
Generates a CSV of 1,000+ rows representing Salesforce Accounts and Support Cases.
Each row contains a rich `Support_Ticket_Notes` column with dense, realistic text.

Requirements: pandas (standard in most environments)
Optional:     faker  — install with `pip install faker` for even more variety.

Usage:
    python generate_sf_data.py                        # writes salesforce_cases.csv
    python generate_sf_data.py --rows 2000 --out my.csv
"""

import argparse
import random
import uuid
import datetime
import pandas as pd

# ── Seed for reproducibility ────────────────────────────────────────────────
random.seed(42)

# ══════════════════════════════════════════════════════════════════════════════
# DATA POOLS
# ══════════════════════════════════════════════════════════════════════════════

FIRST_NAMES = [
    "James", "Maria", "Luca", "Sophie", "Ahmed", "Yuki", "Carlos", "Priya",
    "Tom", "Fatima", "Daniel", "Elena", "Omar", "Ingrid", "Wei", "Isabella",
    "Marcus", "Aisha", "Raj", "Clara", "Henrik", "Zoe", "Patrick", "Nadia",
]
LAST_NAMES = [
    "Schmidt", "Müller", "Rossi", "Dupont", "Tanaka", "Patel", "García",
    "Johnson", "Andersen", "Kim", "Okonkwo", "Larsson", "Nguyen", "Becker",
    "Ferreira", "Kowalski", "Hassan", "Novak", "Sato", "Williams",
]
CITIES = [
    "Munich", "Berlin", "Paris", "London", "Milan", "Madrid", "Amsterdam",
    "Zurich", "Vienna", "Stockholm", "Copenhagen", "Warsaw", "Prague",
    "Budapest", "Lisbon", "Brussels", "Helsinki", "Oslo", "Bratislava",
    "Singapore", "Tokyo", "Sydney", "Toronto", "Chicago", "New York",
]
INDUSTRIES = [
    "Financial Services", "Healthcare", "Manufacturing", "Retail",
    "Technology", "Logistics", "Energy", "Telecommunications",
    "Pharmaceuticals", "Insurance", "Automotive", "Media & Entertainment",
]
ACCOUNT_TYPES = ["Customer", "Partner", "Prospect", "Reseller"]
TIERS = ["Enterprise", "Mid-Market", "SMB", "Strategic"]

CASE_ORIGINS = ["Phone", "Email", "Web", "Chat", "Partner Portal"]
CASE_STATUSES = ["New", "In Progress", "Escalated", "Pending Customer", "Resolved", "Closed"]
PRIORITIES = ["Critical", "High", "Medium", "Low"]
PRODUCTS = [
    "API Gateway", "Data Sync Engine", "Analytics Dashboard",
    "Identity & Access Module", "Billing Platform", "Workflow Automation",
    "Mobile SDK", "Reporting Suite", "Integration Hub", "Security Manager",
]
ERROR_CODES = [
    "ERR-5021", "ERR-4403", "ERR-5500", "ERR-4009", "ERR-3301",
    "TIMEOUT-002", "AUTH-401", "SYNC-FAIL-07", "DB-CONN-ERR", "SSL-HANDSHAKE",
]
IMPACTS = [
    "30% drop in data syncs", "complete loss of SSO functionality",
    "invoice generation failures affecting 200+ clients",
    "dashboard not loading for all EU users",
    "mobile app crashes on launch for iOS 17+",
    "nightly batch jobs failing silently",
    "duplicate records being created in the CRM",
    "webhook events not firing for payment completions",
    "report exports timing out for datasets > 50k rows",
    "two-factor authentication codes not being delivered",
    "search results returning stale cached data",
    "API response times exceeding 12 seconds",
    "audit logs missing entries for the past 48 hours",
    "file attachments over 10 MB silently dropped",
    "email notifications sent to incorrect recipients",
]
RESOLUTIONS = [
    "A hotfix (v2.4.7) was deployed to production at 03:14 UTC resolving the root cause.",
    "Engineering identified a misconfigured load-balancer rule; it was corrected and verified.",
    "The database index was rebuilt and query performance restored to baseline.",
    "OAuth token refresh logic was patched; all active sessions re-authenticated successfully.",
    "A stale CDN cache was purged globally; content now serves correctly in all regions.",
    "The third-party payment gateway's IP whitelist was updated to include the new NAT range.",
    "Root cause traced to a race condition in the async queue; a mutex lock was introduced.",
    "SSL certificate renewed and propagated across all edge nodes within the maintenance window.",
    "The customer's IP range was added to the allowlist following security review approval.",
    "Data migration script re-run with corrected field mappings; record integrity confirmed.",
    "Pending further investigation; case escalated to Tier-3 Engineering with P1 SLA applied.",
    "Workaround provided: client configured batch size to 500 records; permanent fix in sprint 43.",
]
SENTIMENTS = [
    ("frustrated", "threatened to escalate to executive sponsor"),
    ("very concerned", "requested a post-mortem report within 48 hours"),
    ("patient but firm", "asked for daily status updates"),
    ("escalating", "looped in their VP of Engineering on the call"),
    ("understanding", "appreciated the quick response and transparency"),
    ("critical", "stated this is blocking their go-live scheduled for next Friday"),
    ("professional", "requested SLA credit per the MSA terms"),
    ("distressed", "mentioned potential contractual penalties if unresolved by EOD"),
]

# ══════════════════════════════════════════════════════════════════════════════
# NOTE TEMPLATES  (each returns a multi-sentence string)
# ══════════════════════════════════════════════════════════════════════════════

def _pick(*pool): return random.choice(pool if len(pool) > 1 else pool[0])

def note_api_failure(ctx):
    sentiment, threat = _pick(SENTIMENTS)
    return (
        f"Client in {ctx['city']} reported a critical failure in the {ctx['product']} integration "
        f"causing a {_pick(IMPACTS)}. "
        f"Error code {_pick(ERROR_CODES)} appears in logs since {ctx['incident_time']}. "
        f"Contact {ctx['contact']} ({ctx['role']}) was {sentiment} during the call and {threat}. "
        f"Initial triage confirmed the issue is environment-specific to their {_pick(['EU-WEST', 'US-EAST', 'AP-SOUTH', 'PROD-2'])} tenant. "
        f"Reproduction steps provided; engineering queue updated. "
        f"{_pick(RESOLUTIONS)}"
    )

def note_perf_degradation(ctx):
    sentiment, threat = _pick(SENTIMENTS)
    return (
        f"{ctx['contact']} from {ctx['account']} opened this case after observing severe latency in "
        f"the {ctx['product']}. Average response times increased from ~200ms to over "
        f"{random.randint(3, 15)}s beginning around {ctx['incident_time']}. "
        f"Affects approximately {random.randint(10, 500)} concurrent users in their {_pick(['EMEA', 'APAC', 'AMER'])} region. "
        f"Customer is {sentiment} and {threat}. "
        f"Support engineer ran a distributed trace; bottleneck identified at the database read replica. "
        f"Metrics attached to case for engineering review. "
        f"{_pick(RESOLUTIONS)}"
    )

def note_auth_issue(ctx):
    sentiment, threat = _pick(SENTIMENTS)
    return (
        f"Ticket raised by {ctx['contact']} ({ctx['role']}) at {ctx['account']} regarding "
        f"intermittent authentication failures on the {ctx['product']}. "
        f"Approximately {random.randint(5, 80)}% of login attempts return a 401 with error {_pick(ERROR_CODES)}. "
        f"Issue began after they applied their internal SSO policy update on {ctx['incident_date']}. "
        f"Customer tone: {sentiment}; {threat}. "
        f"Support confirmed SAML assertions are malformed — attribute mapping mismatch in IdP config. "
        f"Step-by-step remediation guide sent; customer to test in staging before production rollout. "
        f"{_pick(RESOLUTIONS)}"
    )

def note_data_sync(ctx):
    sentiment, threat = _pick(SENTIMENTS)
    return (
        f"Inbound escalation from {ctx['account']} ({ctx['city']}) — {ctx['contact']} reports "
        f"the {ctx['product']} has been failing to sync records since {ctx['incident_time']}. "
        f"Approximately {random.randint(500, 50000):,} records are stuck in a PENDING state. "
        f"Error log snippet shared by customer shows {_pick(ERROR_CODES)} with stack trace pointing to "
        f"a serialisation issue in the delta-sync processor. "
        f"Customer is {sentiment} and {threat}. "
        f"Workaround: manual re-trigger via admin panel unblocks individual batches but is not scalable. "
        f"Engineering has reproduced the issue in staging with a dataset of matching schema. "
        f"{_pick(RESOLUTIONS)}"
    )

def note_billing(ctx):
    return (
        f"{ctx['contact']} ({ctx['role']}) at {ctx['account']} contacted support regarding an unexpected "
        f"charge of ${random.randint(200, 15000):,} on their {_pick(['March', 'April', 'May', 'June', 'July'])} invoice. "
        f"Customer claims usage reported by the {ctx['product']} does not match their internal telemetry. "
        f"Discrepancy of approximately {random.randint(5, 40)}% in API call counts. "
        f"Finance team has been looped in. Raw usage logs pulled from billing service for {ctx['incident_date']}. "
        f"Preliminary finding: a duplicate event emitter was introduced in v{random.randint(2,4)}.{random.randint(0,9)}.{random.randint(0,9)} "
        f"causing double-counting. Credit memo being processed; ETA {random.randint(2,7)} business days. "
        f"{_pick(RESOLUTIONS)}"
    )

def note_feature_request(ctx):
    return (
        f"Customer {ctx['contact']} at {ctx['account']} (Tier: {ctx['tier']}, Industry: {ctx['industry']}) "
        f"submitted a formal feature request for the {ctx['product']}. "
        f"Request: ability to {_pick(['export audit logs in CEF format', 'configure per-user rate limits via API', 'bulk-archive inactive records', 'schedule reports at sub-hourly intervals', 'receive webhook retries with exponential backoff', 'set custom session timeout policies per role group'])}. "
        f"Business justification: compliance with {_pick(['ISO 27001', 'SOC 2 Type II', 'GDPR Article 30', 'HIPAA §164.312', 'PCI-DSS 4.0'])} audit requirements. "
        f"Use case documented and forwarded to Product Management. "
        f"Customer expects a roadmap commitment within {random.randint(1,4)} quarters. "
        f"PM acknowledged receipt; item added to the backlog with {_pick(['High', 'Medium'])} priority scoring."
    )

def note_onboarding(ctx):
    return (
        f"New onboarding case for {ctx['account']} ({ctx['tier']} tier). "
        f"Primary contact: {ctx['contact']} ({ctx['role']}). "
        f"They are configuring the {ctx['product']} for the first time and encountered "
        f"{_pick(['CORS policy errors when calling the API from their SPA', 'confusion around webhook signature verification', 'difficulty mapping their existing data schema to our object model', 'missing permissions on the service account used for integration', 'SSL pinning failures in their mobile build pipeline'])}. "
        f"Implementation engineer scheduled a 60-minute screenshare for {ctx['incident_date']}. "
        f"Customer provided sandbox credentials; issue reproduced and root cause confirmed. "
        f"Documentation gap identified — will file internal ticket to update the Quick-Start Guide. "
        f"Customer confirmed resolution after applying the corrected configuration."
    )

NOTE_GENERATORS = [
    note_api_failure,
    note_perf_degradation,
    note_auth_issue,
    note_data_sync,
    note_billing,
    note_feature_request,
    note_onboarding,
]

ROLES = [
    "CTO", "VP of Engineering", "IT Director", "Platform Architect",
    "DevOps Lead", "Senior Engineer", "IT Manager", "Solutions Architect",
    "Head of Operations", "Technical Account Manager",
]

# ══════════════════════════════════════════════════════════════════════════════
# ROW BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def random_date(start_year=2023, end_year=2025):
    start = datetime.date(start_year, 1, 1)
    end   = datetime.date(end_year, 12, 31)
    delta = (end - start).days
    return start + datetime.timedelta(days=random.randint(0, delta))

def build_rows(n: int) -> list[dict]:
    rows = []
    for _ in range(n):
        city      = _pick(CITIES)
        industry  = _pick(INDUSTRIES)
        tier      = _pick(TIERS)
        product   = _pick(PRODUCTS)
        created   = random_date()
        inc_date  = created - datetime.timedelta(days=random.randint(0, 3))
        inc_time  = f"{inc_date.isoformat()} {random.randint(0,23):02d}:{random.randint(0,59):02d} UTC"
        contact   = f"{_pick(FIRST_NAMES)} {_pick(LAST_NAMES)}"
        account   = (
            f"{_pick(LAST_NAMES)} & {_pick(LAST_NAMES)} {_pick(['GmbH','AG','Inc.','Ltd.','SA','BV','AB','Sp. z o.o.','S.r.l.','Corp.'])}"
        )

        ctx = dict(
            city=city, industry=industry, tier=tier, product=product,
            contact=contact, account=account, role=_pick(ROLES),
            incident_date=inc_date.isoformat(), incident_time=inc_time,
        )

        note_fn   = _pick(NOTE_GENERATORS)
        close_date = created + datetime.timedelta(days=random.randint(0, 30))
        status     = _pick(CASE_STATUSES)

        rows.append({
            # ── Account fields ──────────────────────────────────────────────
            "Account_ID":          f"001{uuid.uuid4().hex[:12].upper()}",
            "Account_Name":        account,
            "Account_Type":        _pick(ACCOUNT_TYPES),
            "Industry":            industry,
            "Account_Tier":        tier,
            "Billing_City":        city,
            "Annual_Revenue_USD":  random.randint(500_000, 500_000_000),
            "Number_of_Employees": random.randint(10, 50_000),

            # ── Case fields ──────────────────────────────────────────────────
            "Case_ID":             f"5{random.randint(10_000_000, 99_999_999)}",
            "Case_Number":         f"CASE-{random.randint(100000, 999999)}",
            "Case_Origin":         _pick(CASE_ORIGINS),
            "Priority":            _pick(PRIORITIES),
            "Status":              status,
            "Product_Area":        product,
            "Date_Opened":         created.isoformat(),
            "Date_Closed":         close_date.isoformat() if status in ("Resolved", "Closed") else "",
            "SLA_Met":             _pick(["Yes", "Yes", "Yes", "No"]),  # bias toward Yes
            "Contact_Name":        contact,
            "Contact_Role":        ctx["role"],
            "CSAT_Score":          random.choice([None, None, 1, 2, 3, 3, 4, 4, 5, 5, 5]),

            # ── The star column ──────────────────────────────────────────────
            "Support_Ticket_Notes": note_fn(ctx),
        })
    return rows

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Generate Salesforce-style sample data CSV.")
    parser.add_argument("--rows", type=int, default=1_000, help="Number of rows to generate (default 1000)")
    parser.add_argument("--out",  type=str, default="salesforce_cases.csv", help="Output CSV path")
    args = parser.parse_args()

    print(f"⚙️  Generating {args.rows:,} rows …")
    rows = build_rows(args.rows)
    df   = pd.DataFrame(rows)

    df.to_csv(args.out, index=False)
    print(f"✅  Saved → {args.out}  ({len(df):,} rows × {len(df.columns)} columns)")
    print(f"\nColumns: {', '.join(df.columns)}")
    print(f"\nSample note (row 0):\n{df['Support_Ticket_Notes'].iloc[0]}")

if __name__ == "__main__":
    main()
