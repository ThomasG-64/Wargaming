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

**Judge context is scenario-specific** — it's where you ground the judge in whatever real-world
facts, base rates, and constraints should discipline its rulings for *this* game (so it doesn't
invent, say, a Congressional bill passing in a single turn when the real legislative calendar
makes that implausible). See each scenario below for a worked example.

---

## Scenario 1 — "Cage-Free Reckoning"

**Suggested agents:** Retail & Foodservice Buyer, Corporate Accountability Campaign, Poultry &
Livestock Integrator, ESG Investor Coalition, Industry Reputation Defense Coalition.

**Judge context:**
> This is a wargame about corporate animal-welfare commitments and accountability in the US egg
> supply chain. Roughly half of the US egg-laying flock is now cage-free, up from a small
> fraction a decade ago, driven by corporate pledges won through advocacy pressure starting around
> 2015. But cage-free hen capacity has repeatedly lagged the combined demand from every company
> that pledged a deadline — industry estimates have put required capacity in the hundreds of
> millions of hens against actual cage-free flocks well under half that. At least one major
> retailer has already publicly abandoned a stated cage-free deadline, citing supply and cost, and
> absorbed real but survivable reputational damage for doing so. Advocacy organizations publish
> periodic public "leader/laggard" reports naming companies by their progress and whether they
> report transparently. Avian flu outbreaks periodically wipe out large fractions of the laying
> flock within weeks, which can wipe out months of cage-free conversion progress and spike egg
> prices industry-wide — treat a flu shock as a plausible event you may introduce if agents'
> actions don't create enough tension on their own.

**Opening situation:**
> A national grocery retailer set a public 100%-cage-free-eggs-by-this-year commitment eight years
> ago. With the deadline now three months away, the retailer's supply chain is at 61% cage-free —
> improving, but not on pace to hit 100%. An advocacy organization's field team has just finished
> auditing the retailer's public disclosures for its annual "leader/laggard" report, due to publish
> in six weeks, and the retailer's draft entry currently reads "laggard." A confirmed avian flu
> outbreak in a major egg-producing state two weeks ago has already pushed wholesale egg prices up
> 18% and taken an unknown number of cage-free layers offline along with conventional ones.

---

## Scenario 2 — "The Regulatory Pathway Fight"

**Suggested agents:** Alternative Protein Innovator, Food Safety & Agriculture Regulator,
Industry Reputation Defense Coalition, Poultry & Livestock Integrator, ESG Investor Coalition.

**Judge context:**
> This is a wargame about the regulatory and labeling fight over cultivated (lab-grown) meat in
> the US. Cultivated meat companies need pre-market safety approval from a joint
> USDA/FDA process before a product can be sold, and separately need USDA label approval for the
> product's name and claims. Conventional meat trade groups have lobbied at both the state and
> federal level to restrict cultivated and plant-based products from using words like "meat,"
< "burger," or species names on their labels, with mixed legislative success — several states
> have passed such restrictions, some have been challenged or blocked in court on commercial-speech
> grounds. Alt-protein advocates argue restrictive labeling suppresses consumer understanding and
> deliberately handicaps a nascent category; incumbent industry argues it prevents consumer
> confusion. Public and investor sentiment toward alt-protein has been volatile — funding and
> media coverage in the sector cooled noticeably in the mid-2020s after early hype outran
> commercial traction. Treat regulatory decisions and legislative votes as taking multiple turns
> to resolve, not one; a single turn's actions should move the needle, not resolve the fight.

**Opening situation:**
> A cultivated meat company has just received joint USDA/FDA pre-market safety clearance for its
> first product — a cultivated chicken cell-mass — and has filed for USDA label approval to market
> it as "cultivated chicken." A state where the company had planned to launch first passed a law
> last year banning any product not derived from a "slaughtered animal" from using species-specific
> meat terms on its label. The company must decide how to enter the market; conventional poultry
> trade groups are already publicly framing the safety clearance as regulators "rubber-stamping an
> unproven product," and investor sentiment toward the alt-protein sector broadly has cooled over
> the past two years after several high-profile companies missed commercialization targets.

---

## Scenario 3 — "Tournament System Under Fire"

**Suggested agents:** Contract Grower Cooperative, Poultry & Livestock Integrator, Food Safety &
Agriculture Regulator, Corporate Accountability Campaign, Industry Reputation Defense Coalition.

**Judge context:**
> This is a wargame about the poultry contract-growing "tournament" pay system and USDA rulemaking
> under the Packers and Stockyards Act. Contract growers don't own the birds, feed, or medicine
> they raise; integrators pay them by ranking their flock's feed-conversion performance against
> other growers in a "tournament group" each week, docking below-average growers and paying
> above-average ones a bonus from the docked pool. Growers argue this makes them compete
> "blindfolded" since the integrator controls the input quality (chick genetics, feed, veterinary
> support) that heavily determines performance, and some report retaliation (worse inputs) after
> complaining. USDA finalized a rule in the mid-2020s requiring more contract transparency and
> limiting some tournament practices, but enforcement and further rulemaking remain contested and
> slow-moving; a full ban on the tournament system is not currently on the table and shouldn't
> resolve in fewer than several turns if it comes up at all. Many growers carry six- or
> seven-figure debt on barns the integrator required as a condition of the contract.

**Opening situation:**
> A regional coalition of contract growers has organized for the first time, sharing tournament
> pay data with each other privately and finding wide, hard-to-explain variance in the inputs
> (chick weight, feed quality) they were assigned relative to top-performing growers in their
> tournament group. Three growers who raised the issue with their integrator's field
> representative were switched to a lower-quality feed supplier the following cycle. The coalition
> is now deciding whether to file a formal complaint under the Packers and Stockyards Act, go to
> agricultural press, or both — and an advocacy organization focused on farm justice has offered to
> help amplify their case publicly.

---

## References

- [The Humane League — 2026 Cage-Free Eggsposé](https://www.prnewswire.com/news-releases/the-humane-leagues-new-2026-eggspose-reveals-foodservice-providers-failing-to-deliver-on-cage-free-commitments-and-recognizes-industry-leaders-302769084.html)
- [Farm Progress — Walmart's cage-free commitment and its 2022 delay](https://www.farmprogress.com/farm-business/walmart-to-transition-to-100-cage-free-eggs-by-2025)
- [WATTPoultry — McDonald's meets cage-free pledge early](https://www.wattagnet.com/egg/article/15663828/mcdonalds-meets-us-cagefree-pledge-goal-two-years-early)
- [GFI Europe — Policy priorities (R&D, regulatory pathway, labeling)](https://gfieurope.org/policy/)
- [Federal Register — Transparency in Poultry Grower Contracting and Tournaments](https://www.federalregister.gov/documents/2023/11/28/2023-24922/transparency-in-poultry-grower-contracting-and-tournaments)
- [RAFI-USA — New rule under the Packers and Stockyards Act finalized](https://www.rafiusa.org/new-rule-under-the-packers-and-stockyards-act-finalized/)
- [Grist — Does the chicken industry pluck farmers?](https://grist.org/food/does-the-chicken-industry-pluck-farmers/)
