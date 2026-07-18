# Red-team: AI-Assisted Wargaming for Animal Welfare

A hostile-but-fair review of the project as it stands, aimed at the goal you named: **gain publicity, and be as realistic, user-forward, and "reasonable / scientifically accurate" as possible.** Each item is written as *the criticism a smart skeptic would make*, why it lands, and the concrete fix. Ordered roughly by how badly it threatens credibility.

The literature grounding the validity critiques is cited inline and collected at the end. Two references worth internalizing before you read further, because they *are* the attack a domain expert will make: Rivera et al. on LLM escalation and construct validity in wargames, and the "Six Fallacies in Substituting LLMs for Human Participants" paper. If a reviewer knows this space, they've read those.

---

## 0. What this is, and what I'm assuming your goal is

The project is a configurable multi-agent policy wargame. You define N stakeholder agents (name + free-text objective + model), a neutral judge (model + background context), a starting scenario, and a turn count. Each turn every agent privately picks 1–3 actions from the current situation; the judge folds all actions into a one-paragraph "news-style" outcome; that outcome becomes the next turn's situation. Everything routes through OpenRouter so each agent can run a different model. There's a FastAPI backend and a form-driven local website prefilled with an 8-role animal-agriculture roster and three worked scenarios.

Inferred goal (your words, restated so we're aligned): a **public-facing, credible foresight tool** for the AI × animal-welfare community that (a) draws attention/publicity, (b) *feels* realistic and is pleasant to drive, and (c) can survive the sentence "but is this actually scientifically valid, or is it just LLMs making up a story?"

The whole review hangs on that third point, because it's the one that can sink the first two.

---

## 1. The one attack that matters most: "this is a story generator wearing a lab coat"

**The criticism.** There is no ground truth, no validation, no calibration, and no measure of uncertainty. An LLM agent role-plays "the poultry integrator," another LLM adjudicates, and the output reads like a plausible news story — but plausibility is exactly what LLMs optimize for and exactly what has *no* necessary relationship to what would really happen. A domain expert will say: you've built a very fluent random-narrative engine and dressed it as forecasting. The research backs the skeptic here — LLM-based human simulations "have not yet been reliable," they reflect socially-desirable / idealized behavior rather than real behavior, and their realism itself *risks* validity because the output is "too detailed to be an abstract model, too artificial to be an explanation" (the uncanny-valley critique).

**Why it lands.** Nothing in the current design distinguishes a run that tracks reality from one that doesn't. A user can't tell a good run from a hallucinated one, and neither can you.

**Fixes, cheapest first.**

- **Reframe honestly and prominently.** Adopt the framing the serious papers use: this is a tool to *surface assumptions, expose blind spots, and generate hypotheses* — not to predict. Put that in the header tagline and the About box, not buried. Counterintuitively, this *increases* credibility with the exact expert audience you want, because it signals you know the literature. The military-wargaming papers explicitly call their own results "an illustrative proof-of-concept rather than a comprehensive evaluation" — borrow that posture.
- **Run-to-run variance as a first-class feature.** Run the same scenario K times (e.g. 5–10) and show users the *distribution* of outcomes, not one transcript. "In 7/10 runs the retailer walked back the deadline; in 3/10 it paid the premium" is a legitimately interesting, defensible output. A single transcript presented as "what happens" is the indefensible version. This is the single highest-leverage change for scientific credibility and it's mostly a loop + an aggregation view.
- **Backtesting / face-validity harness.** Pick 3–5 scenarios whose real outcome is now known (Walmart walking back its 2025 cage-free deadline; McDonald's hitting cage-free early; the P&S tournament rule finalizing then stalling). Run them "blind" (scenario framed as of an earlier date) and check whether the modal outcome matches history. Even a small, honestly-reported hit-rate is a *massive* credibility asset and a great publicity artifact ("we tested it against 5 real cases").
- **Sensitivity display.** Because prompt sensitivity and construct validity are the named weaknesses in the literature, show how much the outcome swings when you perturb a single objective or the judge context. Fragility that you *surface* reads as rigor; fragility you hide reads as fraud when someone finds it.

---

## 2. The judge is a single point of failure — and a biased one

**The criticism.** One model, with a user-written "context" blurb, silently decides who wins every turn. That's an enormous amount of load on one component. Worse, LLMs carry documented systematic biases — left-leaning and "WEIRD" (Western/Educated/Industrialized/Rich/Democratic) framings, plus social-desirability skew. On an animal-welfare topic specifically, the default sympathies of a base model are unlikely to be neutral. A critic will say your "neutral judge" has a thumb on the scale and you have no way to know which way it's pressing.

**Why it lands.** `build_judge_system_prompt` just says "be neutral" and "be realistic." Telling an LLM to be neutral does not make it neutral; it makes it *claim* neutrality. And the judge has no grounding beyond one free-text paragraph, so it will happily invent specifics (a bill passing, a number moving) with false precision.

**Fixes.**

- **Constrain the judge with base rates, not vibes.** The scenario docs already gesture at this ("don't invent a Congressional bill passing in a single turn"). Make it structural: give the judge an explicit list of "things that cannot happen in one turn" and rough probabilities/timescales for the ones that can. Consider a two-call judge: first extract *what each actor attempted*, then rule on *what succeeds given real-world constraints* — separating narration from adjudication reduces the "fluent story" failure mode.
- **Adversarial / panel judging.** Run the judge as 2–3 models (or one model, multiple times) and reconcile. Disagreement between judges is itself signal you can surface. This directly answers the "single biased adjudicator" attack.
- **Bias probe.** Ship a small test: run neutral/empty-objective agents through a scenario and see which way outcomes drift. Report it. "We measured the judge's default lean and here's how we correct for it" is exactly the move that converts a skeptic.
- **Ground the judge in retrievable facts**, not just a pasted paragraph — even a small curated fact sheet per scenario (real capacity numbers, real timelines) cuts hallucinated precision.

---

## 3. Agents have no memory, no interaction, and no private information

**The criticism.** Three design holes any wargaming person will spot instantly:

1. **No memory.** Each turn an agent is re-instantiated from scratch with only the current situation. It can't remember what it did last turn, whether it worked, or that another actor betrayed it. Real strategic behavior is *path-dependent*; this isn't. (Your own roadmap lists "agent memory" as not-built — a reviewer will read that as "the core of a strategy sim is missing.")
2. **No interaction within a turn.** All agents act simultaneously and privately, then the judge merges. There's no negotiation, no coalition-forming, no reacting to what another actor *just said* — which the roster explicitly wants (the integrator vs. grower vs. NGO tensions are all *relational*). The docs even note agents produce "8 parallel monologues."
3. **No private information / asymmetry.** Every agent sees the same public situation. But the entire interest of these stakeholders is *asymmetric information* (the integrator knows the feed quality it assigned; the grower doesn't). A wargame without hidden information isn't really a wargame — it's a chorus.

**Why it lands.** These three together mean the sim can't produce the emergent, surprising dynamics that justify wargaming over just asking one model "what might happen?" The Food Chain Reaction game your own research doc cites gets its value precisely from teams negotiating with asymmetric positions over time.

**Fixes.**

- **Add per-agent memory** (a running private scratchpad of "what I've done and observed"), fed back each turn. Cheap, high impact, already on your roadmap — prioritize it.
- **Add at least one interaction channel.** Simplest: a "public statements" phase where agents can post messages other agents see before choosing final actions. Richer: allow directed proposals/deals the judge can ratify. Even one round of visible back-and-forth transforms the output from monologues to dynamics.
- **Give the judge private state per agent** and reveal only what each agent should plausibly know when building that agent's prompt. This is more work but it's the difference between "toy" and "credible."

---

## 4. Realism gaps a domain expert will pick at

**The criticism.** Several modeling choices will read as naïve to someone who knows food-systems policy:

- **Actions resolve instantly and cleanly.** The escalation-wargame literature flags "actions assumed to occur without delay" as a core validity weakness. A lawsuit, a rulemaking, a supply-chain conversion all take *months-to-years*; here they resolve in a paragraph. Turns have no defined time-scale.
- **Fixed roster, no exogenous shocks except the one hinted (avian flu).** Real systems get hit by things no stakeholder chose. Only the flu shock is scripted in, and only in one scenario.
- **Objectives are static.** Real actors' goals shift as conditions change; here the objective text is frozen for the whole game.
- **"2–4 sentences" caps depth.** It keeps transcripts readable but forces every actor into a soundbite, which flattens the strategic reasoning you're trying to showcase.
- **Caricature risk.** The roster is thoughtfully written (credit — the "everyone has an internal conflict of interest" framing is genuinely good and pre-empts the "industry=evil" strawman). But the CoMPosT work shows LLMs still tend to *caricature* assigned personas, and the "identity-essentialization" critique applies: an LLM told "you are the industry defense coalition, you frame exposés as disinformation regardless of accuracy" will play a flatter villain than the real, media-savvy operation.

**Fixes.**

- **Give turns an explicit clock** ("each turn = one quarter") and let the judge track that slow processes span multiple turns. You already tell the judge this in prose — make it a rule and show the date advancing.
- **Add an exogenous-event system**: a small library of shocks (flu, price spike, viral undercover video, election, feed-cost shock) the judge can roll in with some probability, disclosed to the user. Turns randomness into a feature and increases surprise.
- **Let objectives drift**: allow the judge (or a meta-step) to update an agent's private priorities when the situation materially changes.
- **Vary response length by role/phase** — let the judge and "set-piece" moments run longer.
- **Counter caricature**: instruct agents to act *competently and in their own sophisticated self-interest* rather than to their stereotype, and consider a "steelman" instruction so each actor is played as its smartest real-world version. Test for caricature by asking a separate model to guess the role from the action text — if it's trivially obvious, you're caricaturing.

---

## 5. Product / UX — the "user-forward" gap

**The criticism.** As a product it's a bare form + a wall-of-text transcript, and the interaction model actively fights the "wait for it" nature of LLM calls:

- **Submit-and-wait with no progress.** You flagged this yourself. An 8-agent, 5-turn game is ~45 sequential model calls; the user stares at a "Running…" string for a long time with no feedback and no way to tell it's not hung. This is the fastest way to lose a first-time visitor.
- **Sequential calls.** `run_turn` loops agents one at a time. Agents within a turn are independent — they can run concurrently, cutting wall-clock time by ~Nx.
- **"Bring your own OpenRouter key" is a brutal onboarding wall** for a *publicity* tool. A journalist, advocate, or funder you want to impress will not create an OpenRouter account and paste a key to try your demo. This single requirement probably kills 90%+ of casual traffic.
- **Output is undifferentiated text.** No way to follow a single actor across turns, no highlighting of turning points, no visual of how the situation escalated/de-escalated, no export.
- **No shareability.** Nothing to link, embed, or screenshot cleanly — fatal for the publicity goal.

**Fixes.**

- **Stream per-turn (and ideally per-agent) results** as they complete. Even without true streaming, return each turn as it finishes. This is the biggest UX win.
- **Run each turn's agents concurrently** (async/gather). Straightforward given the LLM wrapper is already isolated.
- **Offer a hosted demo with a rate-limited server key** (a few free runs, cheap models only — you already default to gpt-5-nano / haiku / flash-lite at cents per game). Keep BYO-key for heavy users. This is the difference between a tool people *try* and a repo people *read about*.
- **Design the transcript as an artifact**: a shareable, permalinked run page; a per-actor "storyline" view; a simple timeline/escalation chart; one-click "share this run." Make the *output* the marketing.
- **Add a "compare runs" view** — which pairs perfectly with the variance feature from §1.

---

## 6. Engineering / robustness

**The criticism.** The core is clean and well-commented (genuinely — the "EDIT HERE" markers, the `from_dict` docstring, the duplicate-name guard, the mock-based test suite are all above-average for a solo project). But for something public:

- **No cost/rate guardrails.** Nothing stops a user from requesting 20 agents × 50 turns and detonating their key (or your server key on a hosted demo). No token/turn/agent caps, no cost estimate shown before running.
- **No timeouts or retries** in `call_agent`. One slow or failed provider call stalls or kills an entire multi-call game after you've already spent money on earlier calls.
- **Whole-game failure is all-or-nothing.** If call #40 fails, the user gets a 502 and loses the 39 completed calls. Partial results should be returned.
- **API key handling.** The key is posted to your backend in the request body. For a hosted version, be explicit about not logging it; for the local tool it's fine, but say so.
- **Untested against a live model.** Your README is admirably honest that only mocked calls are verified. That's a real gap: mocks confirm plumbing, not that real models obey the "2–4 sentences / stay in character / news-paragraph" contract. Prompt-following is exactly where LLMs misbehave.
- **No output schema.** The judge returns free text; there's nothing structured to compute on (who won, what moved), which blocks the scoring/variance features above.

**Fixes.**

- Add configurable caps (max agents, turns, tokens) and a **pre-run cost estimate** ("~$0.04, ~40 calls, ~2 min").
- Add timeouts, bounded retries with backoff, and **return partial transcripts** on failure with a clear "turn 4 failed" marker.
- Do one **real end-to-end run** per supported model tier and snapshot the outputs as fixtures — this both validates prompt-following and gives you regression tests.
- Add an optional **structured judge output** (JSON: per-actor outcome, key events, a 0–100 "situation state" or per-actor scorecard) alongside the prose. Everything in §1 and §5 depends on having this.

---

## 7. Framing, positioning, and the publicity play

**The criticism.** Two framing risks:

- **Credibility-by-association is thin.** The About box says "inspired in part by … Sentient Futures" and the research doc leans on the EA/animal-welfare funding wave. If you're courting that audience, a hand-wave isn't enough; if you're *not* affiliated, implying closeness can backfire. Either deepen the relationship (get a real quote/collaboration) or state clearly it's independent and inspired-by.
- **"Wargaming" sets an expectation you don't yet meet.** The term implies rigor (red-teaming, adjudication doctrine, validated outcomes). Right now it's a role-play narrative generator. That gap is the headline a critical journalist writes. Close it (via §1–§4) *or* soften the term to "scenario exploration" until you have.

**The publicity opportunities (the flip side).**

- **The variance/backtest work IS the story.** "We ran an AI stakeholder simulation against 5 real food-policy fights and it called 4 of them" is a headline. "We built a thing that writes plausible stories" is not. Fund the validation and you get the press for free.
- **Ship provocative, well-chosen preset scenarios** and publish the resulting run analyses as short posts — the tool becomes a content engine.
- **Make one flagship interactive scenario embeddable** so others can run it on their own site/newsletter.
- **Publish a short, honest methods note** citing the limitations literature. In the AI-safety-adjacent world you're targeting, visible epistemic humility is a credibility multiplier, not a weakness.

---

## Prioritized fix list (impact × effort)

**Do first — high impact, low/medium effort**
1. Stream/return results per turn + run agents in a turn concurrently (§5) — fixes the worst UX problem and speeds everything up.
2. Multi-run variance view (§1) — the single biggest credibility gain; mostly a loop + aggregation.
3. Add cost caps + pre-run estimate + timeouts/retries + partial results (§6) — makes it safe to put in front of strangers.
4. Add per-agent memory (§3) — cheap, already roadmapped, big realism gain.
5. Reframe honestly (hypothesis tool, not oracle) + methods note (§1, §7) — free, and converts the skeptic audience.

**Do next — high impact, higher effort**
6. Structured judge output (§6) — unlocks scoring, variance, charts.
7. Backtest harness against known real outcomes (§1) — your best publicity asset.
8. One interaction phase between agents (§3) — turns monologues into dynamics.
9. Hosted demo with a rate-limited server key (§5) — removes the onboarding wall.

**Do when maturing**
10. Panel/adversarial judge + bias probe (§2).
11. Turn clock, exogenous shocks, drifting objectives (§4).
12. Private information / asymmetric agent views (§3) — the deepest change, the one that most earns the word "wargame."

**Cheapest single thing that most improves the demo:** concurrent per-turn execution with results streamed in as each turn resolves. **Cheapest single thing that most improves credibility:** run every scenario 10× and show the distribution instead of one transcript.

---

## What's already good (so you don't regress it)

The roster design is the strongest part: giving every actor a genuine internal conflict of interest, and explicitly refusing the "industry evil / NGO good" caricature, is exactly right and pre-empts a common criticism. The code is clean, honestly commented, and the seams (single LLM wrapper, `GameConfig.from_dict`, presets as single source of truth) are well-placed for the changes above. The test discipline (mocked end-to-end) is unusually good for a prototype. The honesty in the README about what's *not* built is an asset — keep that tone and extend it into a public methods note.

---

## References

- [Rivera et al. — Escalation Risks from Language Models in Military and Diplomatic Decision-Making (arXiv 2401.03408)](https://arxiv.org/pdf/2401.03408)
- [Stanford HAI — policy brief on escalation risks from LLMs](https://hai.stanford.edu/policy/policy-brief-escalation-risks-llms-military-and-diplomatic-contexts)
- [LLM-based Human Simulations Have Not Yet Been Reliable (arXiv 2501.08579)](https://arxiv.org/pdf/2501.08579)
- [Lin — Six Fallacies in Substituting Large Language Models for Human Participants (2025)](https://journals.sagepub.com/doi/10.1177/25152459251357566)
- [Too human to model: the uncanny valley of LLMs in simulating human systems (npj Complexity)](https://www.nature.com/articles/s44260-026-00075-1)
- [CoMPosT: Characterizing and Evaluating Caricature in LLM Simulations (arXiv 2310.11501)](https://arxiv.org/pdf/2310.11501)
- [Social Simulations with Large Language Models Risk Utopian Illusion (arXiv 2510.21180)](https://arxiv.org/abs/2510.21180)
- [Human vs Machine: Wargame Simulation Insights (arXiv 2403.03407)](https://www.emergentmind.com/papers/2403.03407)
