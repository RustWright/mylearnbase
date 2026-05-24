+++
title = "Account list with multi-currency balance aggregation"
slug = "account-list-multi-currency"
date = 2026-05-23
draft = true

[taxonomies]
tags = ["dioxus", "ledger", "multi-currency", "fx"]
+++

## What does this feature do?

The Accounts screen, inside the Finances tab, lists the balances of
the user's tracked accounts at a glance. Each row shows the account
name, its per-commodity holdings (e.g. `42.18 CAD`, `100.00 USD`), and
a single aggregated total converted into the user's base currency
using the latest available exchange rate. When an account was last
reconciled against a statement, the row also surfaces the
reconciliation date and the statement-balance figure. The screen uses
an explicit allowlist of accounts to surface — including the top-level
`Unmatched` clearing account — so newly-discovered sub-accounts from
auto-import don't pollute the view until they earn a place. Commodity
rows without an available rate stay visible in their native amount but
drop out of the base-currency total, which renders as `—` when nothing
converts.

## Why was it added now?

The user holds money in several currencies, at multiple banks. A
typical mix today spans CAD, USD, EUR, and NGN, and that set tends to
grow as new activities come up. Without a surface that converts those
holdings into one figure, "how much do I have right now" requires
re-doing the FX math across banking apps or a spreadsheet. The
Accounts screen collapses that lookup into a glance. The moment was
right because the rate sources the journal needed had landed alongside
the recent auto-import push: a daily-rate fetcher writing price
directives for the major currencies, plus the auto-import review flow
capturing manual rates for the long-tail currencies at the moment a
statement arrives. Both wrote the same hledger `P`-directive shape, so
a single aggregator could fold them in without further infrastructure.
The financial-health dashboard queued up next would need the same
aggregator for net worth, so shipping the Accounts screen first kept
the surface narrow enough to prove the converging-rate path on a
useful screen in its own right.

## What's in scope (and what's not)?

**In:** balance listing, per-commodity rows with base-currency
aggregation, latest reconciliation date and statement balance.

**Not in:**

- Per-account drill-down — the Transactions screen handles that via
  its account-filter chip.
- Historical balance trends — the dashboard owns trend.
- Editing reconciliation status — the screen surfaces what previous
  statement imports already wrote.

## How do we know it works?

The pure aggregation function carries 8 tests covering the categories
the screen promises:

```bash
cargo test -p omni-me-core --lib balances::
```

```output

running 8 tests
test balances::tests::account_summaries_handles_empty_journal ... ok
test balances::tests::is_listable_account_includes_user_allowlist_only ... ok
test balances::tests::account_summaries_aggregates_cad_passthrough ... ok
test balances::tests::account_summaries_keeps_unmatched_clearing_account ... ok
test balances::tests::account_summaries_includes_declared_account_with_zero_balance ... ok
test balances::tests::account_summaries_splices_declared_metadata ... ok
test balances::tests::account_summaries_marks_unconvertible_commodity_with_none ... ok
test balances::tests::account_summaries_converts_foreign_commodity_via_p_directive ... ok

test result: ok. 8 passed; 0 failed; 0 ignored; 0 measured; 309 filtered out; finished in 0.00s

```

Three buckets. **Convertibility math** — base-currency passthrough,
`P`-directive conversion, the unconvertible-commodity fallback that
keeps a row visible in native units when no rate is available.
**Account surfacing** — the allowlist drop-by-default, declared
accounts surfaced even when balance is zero, the `Unmatched` clearing
account preserved alongside the rest. **Declared-account metadata
splicing** — joining the reconciliation date and statement balance
onto the computed balance so the screen can show "last reconciled
through X · statement Y."

[`core/src/balances.rs:93`](https://github.com/RustWright/omni-me/blob/a43610db99545c992aebb9917387449a358a5bae/core/src/balances.rs#L93) at `a43610d`
> `pub fn account_summaries(`
>
> Pure-function entry point — takes journal content + declared accounts + base currency, returns one summary per surfaced account with per-commodity rows and a base-currency total.

[`core/src/balances.rs:180`](https://github.com/RustWright/omni-me/blob/a43610db99545c992aebb9917387449a358a5bae/core/src/balances.rs#L180) at `a43610d`
> `mod tests {`
>
> Test module — fixtures + the 8 test cases that exercise the three buckets above.

The rendered screen shows the multi-commodity row in context — the
Wise account folds CAD, EUR, and USD into a single CAD total, and the
Standard Chartered NGN account shows the `—` badge where no rate is
available to convert the native amount:


![Accounts screen showing five cards — the Wise row folds CAD, EUR, and USD into a single CAD total; the Standard Chartered NGN row shows the `—` badge where no rate is available to convert the native amount.](./01-accounts-multi-currency.png)

## What's worth remembering or doing next?

- The surfaced-accounts list lives in `LISTABLE_ACCOUNTS` as a
  hard-coded slice for now; lifting it into a Settings-managed table
  is queued for the next round of polish. Revisit when a
  newly-discovered account becomes a surface the user wants to glance
  at regularly.
- How `P` directives compose into a `Prices` lookup could be a
  concepts demo — visualizing what a single price entry contributes
  vs. the accumulated table, why "latest rate ≤ date" wins, and what
  `insert_from` actually does when a journal carries multiple rates
  for the same currency pair.
