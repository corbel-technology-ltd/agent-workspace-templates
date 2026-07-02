---
id: <<workspace_slug>>.doctrine.non-goals
name: Non-goals — the safety rails
type: doctrine
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [doctrine, non-goals, boundaries, safety]
related:
  - {ref: 10_doctrine/autonomy-and-gates.md, dimension: how, polarity: requires}
---

# Non-goals

What this system must not do. These are hard rails. **Preparation can be automated. Authority
remains gated.**

The system must not:

1. Auto-send external emails without approval.
2. Conduct automated outreach.
3. Scrape platforms in ways that violate terms or create account risk.
4. Auto-publish public content.
5. Auto-pay invoices.
6. Auto-sign contracts.
7. Auto-commit to partnerships.
8. Make legal, financial, tax, or compliance decisions independently. (signpost, don't advise)
9. Deploy production changes without explicit approval.
10. Replace founder judgement.
11. Optimise for a broad SaaS market before the internal workflow is proven by hand.
12. Depend on one large autonomous agent making hidden decisions.
13. Make irreversible actions without human confirmation.
14. Turn every business signal into a notification.
15. Create an uncontrolled swamp of low-value memory. (the reaper + homeostasis enforce this)

Non-goal 11 is why there is no SaaS / "AI Chief of Staff product" positioning here: this is
internal infrastructure for the founder until internal value is proven. Non-goal 15 is why the
memory layer is event-sourced with a reaper rather than an append-everything store.

## Related

- [Autonomy & gates — the single decision gate](autonomy-and-gates.md)
