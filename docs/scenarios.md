# System prompts and scenario examples

## The general agent system prompt

This is already implemented in `src/wargame/agents.py` (`build_agent_system_prompt`) and applies
to every agent regardless of which of the 8 roles below they're playing. Reproduced here for
reference — only the `name` and `objective` lines are user-supplied per agent; everything after
that is fixed:

> You are role-playing as {name} in a multi-stakeholder wargame simulation.
>
> Your objective: {objective}
>
> Stay in character. Respond with concrete, realistic actions this actor would actually take
> given the situation you're shown — not a list of options, not a balanced overview. Be specific:
> name the action, who it targets, and what outcome you're hoping for. Keep your response to 2-4
> sentences.

**Optional tuning note:** with 8 agents instead of 3, transcripts get long fast. If a judge or
reader starts losing track of who's who, consider adding a line like *"Reference other actors by
name when your action responds to something they did or are likely to do."* — this makes each
agent's action legible as a reaction within the same turn rather than 8 parallel monologues.

## The judge system prompt

Already implemented in `src/wargame/judge.py` (`build_judge_system_prompt`). Only the
"Background context" line is user-supplied per game:

> You are the neutral judge of a multi-stakeholder wargame simulation.
>
> Background context to ground your rulings in reality: {context}
>
> You are given the situation at the start of this turn and the actions every stakeholder just
> took. Determine realistically what happens as a result: who succeeds, who doesn't, what
> unintended consequences emerge, and how the situation has changed. Write 1 short paragraph as a
> news-style situation update that will be shown to all players as the start of the next turn. Be
> concrete and specific, not vague.

**Judge context is one shared library, not per-scenario.** Every game — website runs and
code/batch runs alike — grounds the judge in the same factual "precedent library"
(`src/wargame/judge_context.py`, exposed as `presets.DEFAULT_JUDGE_CONTEXT`): real cases, events,
numbers, and trends framed as *what actors tried and what actually happened*, so the judge has
base rates to pattern-match against instead of trivia or genre priors. The rules for *how* to
adjudicate (pacing — e.g. that a Congressional bill doesn't pass in one turn — when to introduce
shocks, taking scenario premises as given) live in the fixed judge prompt in `judge.py`, not in
the context. Earlier drafts gave each scenario its own bespoke context; that was removed because
the website always substituted the shared one anyway, so per-scenario contexts only created a
train/serve mismatch for batch runs.

The six presets below differ only in **which agents** play and the **opening situation** — the
judge context is identical across all of them.

---

## Scenario 1 — "Cage-Free Reckoning"

**Suggested agents:** Retail & Foodservice Buyer, Corporate Accountability Campaign, Poultry &
Livestock Integrator, ESG Investor Coalition, Industry Reputation Defense Coalition.

**Opening situation:**
> A national grocery retailer set a public 100%-cage-free-eggs-by-this-year commitment eight years
> ago. With the deadline now three months away, the retailer's supply chain is at 61% cage-free —
> improving, but not on pace to hit 100%. An advocacy organization's field team has just finished
> auditing the retailer's public disclosures for its annual "leader/laggard" report, due to publish
> in six weeks, and the retailer's draft entry currently reads "laggard." A confirmed avian flu
> outbreak in a major egg-producing state two weeks ago has already pushed wholesale egg prices up
> 18% and taken an unknown number of cage-free layers offline along with conventional ones.

**Plausibility:** Grounded. ~Half the US flock is cage-free, ~92% of pledges due by 2024 were kept,
but capacity has lagged combined pledged demand and companies have walked back deadlines under
avian-flu cover (Chick-fil-A signaled doubt; Aldi was sued over "cage-free by 2025" marketing). A
retailer at 61% three months out is a realistic near-miss, not a caricature.

---

## Scenario 2 — "The Regulatory Pathway Fight"

**Suggested agents:** Alternative Protein Innovator, Food Safety & Agriculture Regulator,
Industry Reputation Defense Coalition, Poultry & Livestock Integrator, ESG Investor Coalition.

**Opening situation:**
> A cultivated meat company has just cleared the joint FDA/USDA regulatory process for its first
> product — a cultivated chicken cell-mass — and filed for USDA label approval to sell it as
> "cultivated chicken." But the commercial ground has shifted under it: seven states have now
> banned the sale of cultivated meat outright, a federal appeals court recently upheld the first of
> those bans against a constitutional preemption challenge, and a better-funded competitor folded
> last quarter after failing to bring bioreactor costs down to anything near price parity. The
> state the company had planned to launch in is one of the seven. Its investors, already spooked by
> a sector-wide funding winter, want a credible path to revenue this year; conventional poultry
> trade groups are publicly framing the clearance as regulators "rubber-stamping an unproven
> product"; and the company must decide whether to challenge the state bans in court, launch only
> where sales are permitted, pivot to foodservice or overseas markets, or fight the labeling
> restrictions head-on — with only enough runway to pursue one or two of these at once.

**Plausibility:** Updated to mid-2026 reality. The earlier draft framed this as a pure labeling
fight; by 2026 the bigger story is outright state *sales* bans (7 states), the Eleventh Circuit
upholding Florida's ban (March 2026), and a funding winter that took down Believer Meats and
shelved UPSIDE's large plant. Approval-but-no-market is exactly where the sector sits.

---

## Scenario 3 — "Tournament System Under Fire"

**Suggested agents:** Contract Grower Cooperative, Poultry & Livestock Integrator, Food Safety &
Agriculture Regulator, Corporate Accountability Campaign, Industry Reputation Defense Coalition.

**Opening situation:**
> USDA's new poultry tournament rule took effect just weeks ago — guaranteeing growers a disclosed
> base pay rate, barring deductions below it, and imposing a "duty of fair comparison" on how
> integrators rank them against each other. A regional coalition of contract growers, newly
> organized and pooling their pay data for the first time, believes their integrator is already
> engineering around the rule: recasting old deductions as "base-rate adjustments" and assigning
> the growers who complained loudest visibly worse chick quality and feed the following cycle. The
> coalition is deciding whether to file one of the first enforcement complaints under the new rule,
> take their data to the agricultural press, or both — while a farm-justice advocacy organization
> offers to amplify their case, and the growers weigh that public escalation could cost them their
> contracts entirely and leave them holding seven-figure barn debt with no birds to raise.

**Plausibility:** Updated. The Packers & Stockyards tournament-payment rule actually took effect
July 1, 2026, so the live conflict is no longer "will there be a rule" but early-days enforcement
and integrator circumvention — a sharper, more current framing than the original.

---

## Scenario 4 — "The Pandemic on the Farm"

**Suggested agents:** Food Safety & Agriculture Regulator, Poultry & Livestock Integrator,
Corporate Accountability Campaign, ESG Investor Coalition, Industry Reputation Defense Coalition.

**Opening situation:**
> H5N1 avian influenza, already entrenched in poultry and circulating in dairy cattle across more
> than a dozen states, has just produced its most alarming signal yet: a cluster of human
> infections among farmworkers at a single large egg complex, with genomic sequencing showing a
> mutation associated with easier spread between mammals. There is still no confirmed sustained
> human-to-human transmission, but public-health officials have called an emergency briefing and
> the story is leading the news. The government has ordered expanded depopulation of exposed
> flocks; a poultry vaccine exists but using it would trigger export bans from major trading
> partners that refuse product from vaccinated flocks. Egg and poultry prices are climbing again
> after only months of relief, animal advocates are pointing at mass-depopulation methods and the
> sheer density of birds per site as the underlying accelerant, and the integrator at the center of
> the cluster must decide how to respond before the next confirmed human case — or the next viral
> video of a cull — makes the decision for it.

**Plausibility:** Low-probability, high-stakes, and firmly grounded. H5N1 is in ~1,000 dairy herds
across 17 states with ~40 confirmed human cases and no sustained human-to-human spread; virologists
have openly warned about 2026 pandemic potential. The vaccine-vs-export-ban tension and the
ventilation-shutdown depopulation controversy are both real. A mammal-adaptation mutation triggering
a scare is a plausible tail event, not sci-fi.

---

## Scenario 5 — "The Expanding Circle"

**Suggested agents:** Corporate Accountability Campaign, Retail & Foodservice Buyer, Food Safety &
Agriculture Regulator, Industry Reputation Defense Coalition, Alternative Protein Innovator.

**Opening situation:**
> Aquatic animal welfare has crossed from fringe cause to boardroom issue faster than almost anyone
> expected. Several major supermarket chains have committed to require electrical stunning of farmed
> shrimp — animals slaughtered in the hundreds of billions each year — an aquaculture certification
> body now recognizes stunning as a standard, and octopus-farming bans have moved from one US state
> to federal legislation and other countries, riding a wave of published science on invertebrate
> sentience. Emboldened, an advocacy coalition has just presented a national seafood retailer and
> its largest farmed-shrimp importer with the first welfare commitment to combine humane-slaughter,
> stocking-density, and water-quality standards for both finfish and shrimp, backed by an open
> letter from a hundred scientists and a media campaign ready to launch. The importer calls the
> underlying welfare science immature and warns the standards would raise costs in a price-driven
> category; the retailer is weighing its brand against its margins; and a plant-based and
> cultivated-seafood company is circling the moment, hoping the fight brands conventional
> aquaculture as cruel the way earlier campaigns branded battery cages.

**Plausibility:** Grounded and genuinely forward-looking. Supermarkets have committed to shrimp
stunning by end of 2026, the ASC recognized stunning in 2025, California's octopus-farming ban is in
effect with a bipartisan federal OCTOPUS Act and Mexico/Chile bills following, and ~100 scientists
publicly backed the science. This is the welfare frontier expanding to the most numerous farmed
animals — improbable a few years ago, active now.

---

## Scenario 6 — "AGI Arrives, Superintelligence Doesn't"

**Suggested agents:** Poultry & Livestock Integrator, Corporate Accountability Campaign, Food Safety
& Agriculture Regulator, ESG Investor Coalition, Alternative Protein Innovator.

**Opening situation:** (see `AGI_WITHOUT_ASI` in `src/wargame/presets.py` for the full text) — a
poultry integrator hands full operational control of its supply chain to a commodity-priced AGI and
files to certify a fully "autonomous facility" with no human welfare officer, the same week an
advocacy group publishes an AGI-built investigation documenting violations at unprecedented scale,
landing on a regulator facing mass layoffs of human inspectors.

**Plausibility:** The deliberate "big stakes, lower probability" entry — speculative on the AGI
premise but constrained: it explicitly rules out superintelligence and holds physical/institutional
constraints fixed, and its near-term half (AI-run precision livestock management) is already a real,
fast-growing market (~$3.5B in 2026, growing ~28%/yr). On-brand for a "futures" audience; take the
tech premise as given and reason from realistic incentives within it.

---

## References

- [The Humane League — 2026 Cage-Free Eggsposé](https://www.prnewswire.com/news-releases/the-humane-leagues-new-2026-eggspose-reveals-foodservice-providers-failing-to-deliver-on-cage-free-commitments-and-recognizes-industry-leaders-302769084.html)
- [Farm Progress — Walmart's cage-free commitment and its 2022 delay](https://www.farmprogress.com/farm-business/walmart-to-transition-to-100-cage-free-eggs-by-2025)
- [WATTPoultry — McDonald's meets cage-free pledge early](https://www.wattagnet.com/egg/article/15663828/mcdonalds-meets-us-cagefree-pledge-goal-two-years-early)
- [GFI Europe — Policy priorities (R&D, regulatory pathway, labeling)](https://gfieurope.org/policy/)
- [Federal Register — Transparency in Poultry Grower Contracting and Tournaments](https://www.federalregister.gov/documents/2023/11/28/2023-24922/transparency-in-poultry-grower-contracting-and-tournaments)
- [RAFI-USA — New rule under the Packers and Stockyards Act finalized](https://www.rafiusa.org/new-rule-under-the-packers-and-stockyards-act-finalized/)
- [Grist — Does the chicken industry pluck farmers?](https://grist.org/food/does-the-chicken-industry-pluck-farmers/)
- [AMS/USDA — Poultry Grower Payment Systems rule (effective July 1, 2026)](https://www.ams.usda.gov/rules-regulations/poultry-grower-payment-systems-and-capital-improvement-systems)
- [PSU Ag Law — Status of cell-cultured meat regulations and state bans](https://aglaw.psu.edu/ag-law-in-the-spotlight/the-status-of-cell-cultured-meat-regulations/)
- [UNMC — Scientists warn bird flu could spark a human pandemic in 2026](https://www.unmc.edu/healthsecurity/transmission/2026/01/07/its-completely-out-of-control-scientists-warn-bird-flu-could-spark-a-human-pandemic-in-2026/)
- [Innovate Animal Ag — HPAI egg-shortage costs](https://innovateanimalag.org/hpai-costs-2025)
- [Shrimp Welfare Project — retailer stunning commitments](https://www.shrimpwelfareproject.org/)
- [World Animal News — California's octopus-farming ban in effect](https://worldanimalnews.com/2026/02/06/californias-octopus-farming-ban-now-in-effect-protecting-highly-intelligent-creatures/)
- [Sen. Whitehouse — bipartisan federal OCTOPUS Act](https://www.whitehouse.senate.gov/news/release/ahead-of-world-ocean-day-whitehouse-and-murkowski-reintroduce-bipartisan-legislation-to-ban-commercial-octopus-farming/)
- [The Business Research Company — AI in precision livestock farming market 2026](https://www.globenewswire.com/news-release/2026/01/29/3228385/0/en/artificial-intelligence-ai-in-precision-livestock-farming-research-report-2026-8-bn-market-opportunities-trends-competitive-analysis-strategies-and-forecasts-2020-2025-2025-2030f-2.html)
