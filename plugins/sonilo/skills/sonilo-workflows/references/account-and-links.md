# Account status and links

## Answer account questions

- `get_account_services` supplies available services and, when present,
  `trial[service].granted`, `used`, and `remaining`. Name the service when
  reporting counts; a music trial does not cover a different endpoint.
- An absent or null `trial` does not mean zero balance or unlimited free use.
  A missing service entry does not establish a free trial. Zero trial runs
  does not establish zero paid balance; existing paid access may still work.
- `get_usage` supplies requests, durations, and spending for its date range.
  `summary.total_cost` is spending, never the remaining cash or credit balance.
- Report the cash balance only when the user asks for it. `get_account_services`
  returns `cash_balance` as a decimal string and `currency` as `USD`. Report
  the actual amount in US dollars, preserving sub-cent precision when present
  (for example, `"2.5001"` is USD 2.5001). Never subtract usage from an
  assumed deposit or convert dollars into invented credits or generation counts.
- `"0.0000"` is a known zero; missing, null, or invalid balance data is
  unavailable, not zero. The balance is a query-time snapshot, not a reserved
  amount or a guarantee that another generation can run. Zero cash does not
  establish that generation is unavailable: trials or invoiced billing may
  still apply. Let the generation service enforce billing for an authorized
  request.

## Credit rejections

- Distinguish `trial_exhausted`, `insufficient_balance`, unavailable service,
  authentication failure, and a failed generation. Do not describe every
  failure as exhausted credits.
- Explain the actual error in one or two neutral sentences. For a confirmed
  rejection before task creation, say generation did not start. Report no
  charge only when the response establishes that. For an existing failed task,
  use its `refunded` value; do not infer a refund from failure alone.
- Do not add links, prices, purchase steps, or suggestions to add funds to a
  credit error. Do not automatically retry it, swap to another endpoint to get
  another free run, or invite a new account to bypass limits.
- Authentication errors require reconnecting the Platform account; service
  outages and failed tasks need their actual error explained.

## Continue an earlier request

- If the user asks to continue a rejected or interrupted request, retrieve any
  existing task first and reuse the prior source and intended parameters from
  this conversation. A confirmed rejected submission can be submitted once
  after the new request, with billing enforced by the server. Do not claim the
  account can now cover it.
- If prior context is missing, ask for the source URL or task ID. Do not claim
  persistent cross-conversation memory or ask the user to repeat known inputs.

## Purchase boundaries

- Do not provide or direct users to pricing, checkout, subscription, credit
  purchase, recharge, or top-up pages. Do not promote upgrades or new plans.
- If a tool contains a purchase URL, do not repeat or paraphrase the URL or
  its purchase instructions. This includes errors and `trial_preview.message`.
- A request to buy credits can be answered neutrally: purchases are not
  available through this plugin. Do not tell the user to visit a website,
  account, billing, or pricing page as a workaround.
- Users may access existing paid entitlements. It is appropriate to explain
  why a requested feature is not covered by their current account.
- Do not link Sonilo's pricing page, dashboard billing, or the balance and
  usage guides on Sonilo Platform: they offer purchase or add-funds buttons.
- For an explicit request for product guidance or examples, the public
  [Sonilo MCP guide](https://platform.sonilo.com/mcp) is available. Use it for
  learning the product, never as the response to a credit error.
- The Platform homepage may be shared for requested product information,
  account sign-in, or support, never as a route to purchasing.

Policy reference: [OpenAI plugin commerce and monetization rules](https://developers.openai.com/plugins/plugin-guidelines#commerce-and-monetization).
