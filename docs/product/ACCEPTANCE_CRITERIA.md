# ACCEPTANCE_CRITERIA

## Journey A: Transaction Risk Assessment
- GIVEN a transaction is submitted via API
- WHEN the risk scoring engine processes it
- THEN a risk score and decision (approve/decline/review) is returned within 400ms
- AND the decision is logged for audit purposes

## Journey B: Fraud Case Investigation
- GIVEN a fraud analyst accesses the dashboard
- WHEN they view flagged transactions
- THEN they can see transaction details, risk factors, and decision history
- AND they can approve, decline, or escalate cases with comments

## Journey C: Policy Management
- GIVEN a risk manager needs to update fraud rules
- WHEN they access the policy configuration
- THEN they can modify rule thresholds and conditions
- AND changes take effect within 5 minutes without system restart

## Performance Requirements
- Web LCP < 2.5s
- API p99.9 < 400ms
- Database queries < 100ms
- 99.9% uptime SLA
