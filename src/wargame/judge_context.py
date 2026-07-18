"""The judge's context library: one shared, scenario-independent body of
factual background about animal welfare, animal agriculture, and
alternative proteins.

Framing: this is a *precedent library*, not an encyclopedia. The judge's
whole job each turn is "these actors attempted these things — what
happens?", so nearly every entry is shaped as attempt -> outcome -> why,
giving the judge base rates to pattern-match against rather than trivia.
It informs adjudication, never decides it; rules about HOW to adjudicate
(pacing, shocks, tone) live in the fixed prompt in judge.py, not here.

Why include facts a strong model may already know: (1) the 2025-2026
events are past most models' training cutoffs; (2) the judge can be any
model the user picks, including cheap ones with patchy knowledge — the
library equalizes them; (3) even for known facts, in-prompt presence
makes the judge actually reason from them instead of from vague genre
priors. Facts current as of mid-2026; update in place as the world moves.

Every game — website runs and code/batch runs alike — uses this same
library, so results are comparable across both.

Cost note: this string is included in the judge's system prompt only
(once per turn plus the final summary — agents never see it), so its
length adds a couple thousand tokens to a handful of calls per game.
"""

JUDGE_CONTEXT_LIBRARY = """\
PRECEDENT LIBRARY: WHAT ACTORS IN THIS DOMAIN HAVE TRIED, AND WHAT ACTUALLY HAPPENED

=== The playing field ===
Roughly 80 billion land animals are slaughtered for food globally each
year, plus trillions of farmed fish and shrimp; chickens are over 90% of
land animals by count, so moves affecting broilers or layers dwarf
equivalent moves for pigs or cattle. US annually: ~9.5 billion broilers,
~370-380 million laying hens in flock, ~130 million hogs, ~33 million
cattle, mostly in industrial confinement. Production is consolidated and
vertically integrated: Tyson, Pilgrim's Pride (JBS), Wayne-Sanderson and
Perdue dominate broilers; Cal-Maine alone produces about a fifth of US
eggs; Smithfield (China's WH Group) leads pork. In poultry, integrators
own the birds, feed, and medicine while contract growers own the barns
and the debt (often six or seven figures, upgrades required by
contract), paid through "tournament" rankings against peer growers even
though the integrator controls the inputs that largely determine
performance; growers who complain report retaliation (worse inputs,
fewer flocks).

The legal terrain shapes every fight: the US has no federal law on
on-farm treatment — the Humane Methods of Slaughter Act excludes poultry
(~98% of slaughtered land animals), the Animal Welfare Act excludes farm
animals, and state cruelty laws carve out "customary agricultural
practices." So US welfare rules come almost entirely from state ballot
measures and corporate pledges, which is where the conflict
concentrates. The EU, by contrast, has binding on-farm directives
(battery cages banned 2012, sow stall limits, broiler density caps) with
uneven member-state enforcement.

=== When companies pledge — and when they break their word ===
Advocacy campaigns starting ~2015 extracted hundreds of corporate
cage-free pledges. Result: the cage-free share of the US flock rose from
~6% (2015) to roughly half (2026), and ~92% of pledges due by 2024 were
kept — McDonald's, Starbucks, and Conagra delivered on time or early.
Where pledges broke: supply never matched the combined pledged demand,
and avian flu supplied cover — companies that abandoned or pushed back
deadlines (or signaled doubt, as Chick-fil-A did on its 2026 date) took
real but survivable reputational hits, with no lasting boycott damage.
What keeps pressure on: annual leader/laggard rankings naming companies
(e.g., The Humane League's "Eggsposé"), and a newer legal frontier —
false-advertising suits (Animal Outlook's case against Aldi over a
decade of "cage-free by 2025" marketing) testing whether pledges are
enforceable in court rather than just reputationally.

The broiler version shows the failure mode. The Better Chicken
Commitment / European Chicken Commitment (slower-growing breeds, lower
density) drew 200+ signatories, but the breed change is structural and
expensive: most 2024/2026 deadlines are being missed, 2025-2026 brought
open withdrawals in the UK/EU (Burger King, KFC, Pizza Hut, Nando's,
Wagamama, Unilever), and roughly a third of tracked signatories simply
stopped reporting — quiet non-compliance drew less blowback than loud
withdrawal. The pattern: pledges get made and kept where change is
visible and cheap (eggs); they stall or die where it is structural and
costly (broiler genetics).

=== When advocates attack: campaigns, investigations, lawsuits, rescues ===
Corporate pressure campaigns (private ask, then public ranking, then
escalating mobilization against a named brand) are the movement's most
reliable lever — they produced most of the pledges above at far lower
cost per animal than legislation. Undercover investigations reliably
trigger supplier terminations, new pledges, and occasional prosecutions;
industry's legislative counter — "ag-gag" laws criminalizing
investigation — has repeatedly lost in court on First Amendment grounds
(Idaho 2015, Iowa 2019, North Carolina at the Fourth Circuit), keeping
the tactic viable, now supplemented by satellite imagery, procurement
records, and FOIA. Open-rescue prosecutions have sometimes backfired on
prosecutors: juries acquitted activists despite strong evidence
(Smithfield piglet case, Utah 2022; Foster Farms 2023), converting
trials into publicity wins. What works less well: welfare shareholder
resolutions typically draw only low-double-digit support, and the US
anti-ESG backlash has quieted institutional investors (European ones,
organized around the BBFAW welfare benchmark, engage more). Resource
reality: the movement runs on hundreds of millions of dollars a year
globally against an industry with far larger lobbying budgets — it wins
through targeted leverage, not attrition.

=== When the fight goes to law: how long things take and how they end ===
Prop 12 is the canonical timeline. 2018 ballot win (sales ban on
under-spaced pork, veal, eggs) -> years of litigation -> Supreme Court
upheld it (NPPC v. Ross, 2023) -> fresh cert petition denied (June 2025)
-> industry pivoted to Congress for preemption (EATS Act-style riders)
-> the House passed a 2026 farm bill with a Prop 12 "fix" (224-200; the
pork lobby said it got 100% of its asks) but the Senate draft omitted it
— eight years in, still not settled. Compliance meanwhile raised
California pork prices sharply and pushed some small sow operations out.
USDA rulemaking runs on similar clocks: reform of tournament pay was
attempted for over a decade before three Packers & Stockyards rules
landed in 2023-2025, and the tournament payment rule (guaranteed
disclosed base pay, no deductions below it, a "duty of fair comparison,"
capital-improvement disclosure) only took effect July 1, 2026 — with
enforcement that historically swings between administrations, and a full
tournament ban never on the table. The EU shows that even a *won*
commitment can stall indefinitely: the End the Cage Age initiative (1.4M
signatures) extracted a 2021 Commission promise to propose a cage
phase-out by 2023 -> delayed for years while 2024 farmer protests
softened the whole green agenda -> revived in the 2026 Livestock
Strategy promising a laying-hen/broiler proposal by end-2026 and pig
rules by mid-2027 — still only a promise of a proposal. The meta-pattern:
a favorable decision is the middle of a fight, not the end; enforcement,
implementation, and counter-legislation each take additional years.

=== When challengers take on incumbents: the alt-protein record ===
Cultivated meat proves regulatory approval is not market entry: UPSIDE
Foods and GOOD Meat cleared US regulators in 2023 (Wildtype's salmon and
Mission Barns' pork fat followed in 2025), yet volumes stayed at
restaurant-pilot scale because bioreactor scale-up is brutally
capital-intensive — Believer Meats ceased operations in December 2025
and UPSIDE shelved its large Illinois plant. Incumbents fought on two
tracks at once: state sales bans (Florida and Alabama in 2024, then
Mississippi, Montana, Nebraska, and Texas through 2027, plus an Indiana
moratorium) — which survived a federal preemption challenge when the
Eleventh Circuit upheld Florida's ban in March 2026 — and labeling
restrictions on "meat"/"burger"/species names with mixed court
outcomes, while simultaneously hedging with their own alt-protein
investments (Tyson, JBS). Plant-based shows the demand ceiling: after
the 2019-2021 hype peak (Beyond Meat's IPO), US retail fell roughly
7-10% a year through 2024-2025 (refrigerated plant-based burgers down
~26% year over year), beaten by price premium, taste, and effective
"ultra-processed" counter-messaging; foodservice and some non-US markets
held up better. Investor patience is thin — funding now follows
milestones and foreign government backing (Singapore, Israel,
Netherlands).

=== When shocks hit ===
Avian flu is the template shock. Since February 2022, ~175 million US
birds have been destroyed (laying hens ~75% of losses) under whole-flock
"stamping out" with indemnities (raised from ~$7 to ~$17 per layer in
2025, within a $1 billion USDA strategy that includes vaccine
exploration). Egg prices topped $8/dozen wholesale in early 2025, retail
peaked ~$6.23 in March 2025, fell to ~$2.19 by May 2026 — and mid-2026
detections across a dozen states threaten another climb. A single
outbreak moves every piece on the board at once: it erases months of
cage-free conversion capacity, hands companies cover for missing welfare
deadlines, makes price the only food story politicians care about,
creates scandal risk around depopulation methods (ventilation shutdown
is a recurring one), raises pandemic stakes (H5N1 jumped to dairy cattle
in 2024 with sporadic human cases), and revives critiques of flock
concentration itself. Other recurring shocks with the same
multi-directional effects: undercover investigation releases, recalls,
feed price swings, labor shortages, extreme-heat mass mortality, barn
fires.

=== The demand-side constraint on everyone ===
Large majorities tell pollsters farm animal welfare matters — and
majorities even vote for bans when asked directly — but at the shelf,
price wins: premium welfare products stay niche, certifications (Global
Animal Partnership, Certified Humane, Animal Welfare Approved) cover a
minority of production, and weakly regulated terms ("free range,"
"humanely raised") blur the signal. US meat consumption is at or near
record highs with chicken growing fastest — a welfare paradox, since
substituting chicken for beef multiplies animals per meal. Meat politics
polarizes along age and geography. The consequence for every actor:
strategies premised on consumers paying more or changing diets fail more
often than strategies that change what companies or governments do.
"""
