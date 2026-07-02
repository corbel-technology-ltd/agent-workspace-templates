---
id: <<workspace_slug>>.workflow.email-triage-approve
name: Email triage and approve — thin wrapper over the email loop
type: workflow
layer: C2
status: current
owner: shared
staging: v1-now
created: <<CREATED_DATE>>
tags: [workflow, email, triage, decision-packet, human-in-the-loop, signpost-dont-advise]
related:
  - {ref: 30_schemas/decision-packet.md, dimension: what, polarity: requires}
  - {ref: 50_registers/decision-queue.md, dimension: where, polarity: enables}
  - {ref: 50_registers/decision-log.md, dimension: where, polarity: enables}
  - {ref: 50_registers/blocked-actions.md, dimension: where, polarity: enables}
  - {ref: 30_schemas/event.md, dimension: how, polarity: requires}
  - {ref: 40_templates/decision-packet.md, dimension: what, polarity: explains}
  - {ref: 70_integrations/README.md, dimension: where, polarity: requires}
---

# Email triage and approve

A **thin wrapper** over the instance's email loop (the poller + sender wired in `70_integrations/`).
It does not replace it, re-implement send logic, or invent an email API. It reads inbound mail
through the live IMAP poller, classifies it with rules first, summarises threads, drafts replies only
when one is needed, and routes any reply that leaves the workspace through a **Decision Packet**. The
agent runs the steps by hand; the founder commits.

**Hard invariant:** no external send happens without explicit founder approval. This is the
`External send / publish` gate from `AGENTS.md` and is not overridable by any soft default
(batching, recency, "obvious" reply). A draft is preparation; sending is authority. See
[`../50_registers/blocked-actions.md`](../50_registers/blocked-actions.md).

## The existing tools (do not rebuild)

The instance wires two tools in [`../70_integrations/README.md`](../70_integrations/README.md):

- **Poller** — opens the mailbox read-only (never sets `\Seen`), matches the relevant mail, dedupes
  via a local UID watermark. A `--commit` mode advances the watermark past what it printed; without
  it the run is non-destructive and re-pollable.

- **Sender** — the single send path (e.g. SMTP via the workspace mailbox). The **only** way mail
  leaves; nothing else sends.

If those tools live outside the workspace, running them is the `Run a tool from outside the
workspace` gate (confirm).

## Plan -> Validate -> Execute

Steps 1-5 are **Plan** (deterministic plumbing + summarise + draft, no side effect). Step 6 is the
**Validate** gate. Step 7 is the **Execute** action, and it runs *only* after approval.

## Steps

1. **Poll (read-only).** Run the poller **without** `--commit`. If it prints nothing new, stop and
   log nothing. Otherwise capture each new message verbatim. Do not advance the watermark yet, so a
   crash mid-run loses nothing.

2. **Classify (rules-first, AI-minimisation).** Apply deterministic rules before any LLM step:
   - sender, subject markers, and a known-counterparty list;
   - obvious categories first: `auto-handled` (notification/receipt/no action),
     `fyi` (read, no reply), `needs-reply`, `needs-decision` (commitment, money, scheduling, legal).
   Only mail that no rule resolves is handed to the LLM for a judgement call. The LLM classifies;
   it never sends. **signpost, don't advise** — it proposes a category and reason, it does not act.

3. **Summarise the thread.** For each `needs-reply` / `needs-decision` item, write a one-paragraph
   thread summary: who, what they are asking, any deadline, and what (if anything) we owe them.
   Keep claims **source-or-abstain** — quote the mail; if a fact is asserted that we cannot verify
   from the thread or an atom, say so rather than guessing.

4. **Decide if a reply is needed.** `auto-handled` and `fyi` items are batched into the daily brief
   (**anti-noise batching**) and need no further action here. Only `needs-reply` / `needs-decision`
   continue.

5. **Draft (preparation only).** Draft a reply in the agent's voice to a body file (e.g. under
   `90_runs/`). A draft is inert: writing it triggers no gate and sends nothing. Mark anything
   uncertain in the draft for the founder rather than asserting it.

6. **Create a Decision Packet (the gate).** Fill [`../40_templates/decision-packet.md`](../40_templates/decision-packet.md)
   per [`../30_schemas/decision-packet.md`](../30_schemas/decision-packet.md) into `90_runs/` and open
   a row in [`../50_registers/decision-queue.md`](../50_registers/decision-queue.md). The packet must
   carry: the thread summary, the proposed classification, the draft body verbatim, the
   `reversibility` (an external send is **low-reversibility**), and an exact `if_approved` action,
   namely the precise send-tool invocation (subject, recipient, body-file path). The founder
   commits or declines in one read; the source thread is one link away but never required.

7. **On approval, send (Execute).** Only when the founder approves the packet:
   - run the exact send-tool command from `if_approved` (the sole send path);
   - append the outcome and the action taken to [`../50_registers/decision-log.md`](../50_registers/decision-log.md);
   - **then** re-run the poller **with** `--commit` to advance the watermark past handled mail;
   - write a journal entry per [`../30_schemas/event.md`](../30_schemas/event.md) recording the
     inbound item, the decision, and the send (**capture-back**). The reaper folds it into atoms later.
   If the founder declines: log the decline, send nothing, and move the item to
   [`../50_registers/blocked-actions.md`](../50_registers/blocked-actions.md) with the reason.

## Gates that apply (from `AGENTS.md`)

| Action in this workflow | Gate |
|---|---|
| Poll (read-only), classify, summarise, draft, write a packet | proceed, log |
| Run the poller or the send tool (outside-workspace tool) | confirm |
| External send of a reply | **blocked without explicit founder approval** |

## Escalate-with-context

If classification is ambiguous after the rules and the LLM pass, do **not** guess a category to
keep the queue moving. Raise it in the packet as `needs-decision` with the ambiguity named, and let
the founder disambiguate. Two failed send attempts (SMTP error) escalate rather than retry
indefinitely.

## Out of scope (deferred)

No connectors, no inbound webhook, no auto-reply, no rules engine as software, no new mailbox or
email API. The poller and the send tool are the integration surface. Promotion to software is
fenced behind the value-gate (design-spec §9): only after this has run by hand for >=4 weeks and
consistently costs >20 minutes or the mail volume exceeds a stated threshold.

## Related

- [Decision Packet schema](../30_schemas/decision-packet.md)
- [Decision queue — open founder decisions](../50_registers/decision-queue.md)
- [Decision log (append-only)](../50_registers/decision-log.md)
- [Blocked actions register](../50_registers/blocked-actions.md)
- [Journal event schema](../30_schemas/event.md)
- [Decision packet (blank instance)](../40_templates/decision-packet.md)
- [Integrations — what-runs-where map (instance-specific slots)](../70_integrations/README.md)
