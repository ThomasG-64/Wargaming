"""The website's fixed content library: 8 stakeholder agents grounded in
real animal-welfare-in-agriculture actors, a fixed judge context, and 6
scenario presets built from subsets of the roster.

Unlike scripts/run_example.py (where everything is free-form Python you
edit), the website treats this module as a *fixed library*: visitors
pick agents from AGENT_LIBRARY (viewing but not editing their
objectives), the judge's grounding context is always
DEFAULT_JUDGE_CONTEXT, and the only free inputs are which agents to
include, which model plays each of them, the judge's model, the starting
scenario, and the turn count. Full research/reasoning behind each role
lives in docs/agent_roster.md and docs/scenarios.md.

This module is the SINGLE SOURCE OF TRUTH for that library: web/app.py
serves `website_prefill()` at GET /api/presets (which the page fetches
on load to build its agent picker and prefill the form) and resolves
each submitted agent name back to its objective through AGENT_LIBRARY
at /api/run time. The page never sees or sends objectives — edit them
here and both the picker's preview and what actually reaches a model
change together.
"""

from dataclasses import asdict, dataclass

from wargame.agents import AgentConfig
from wargame.judge import JudgeConfig
from wargame.judge_context import JUDGE_CONTEXT_LIBRARY

# Cheapest current-generation model from each major provider (mid-2026
# OpenRouter pricing), cycled across the 8-agent roster below so a full
# 8-agent, 5-turn demo game costs a few cents at most:
#   openai/gpt-5-nano            $0.05 / $0.40 per 1M tokens
#   anthropic/claude-haiku-4.5   $1    / $5
#   google/gemini-3.1-flash-lite $0.25 / $1.50
# Swap any single agent's model freely — see scripts/run_example.py for
# picking different models per agent/judge deliberately.
_CHEAP_MODELS = [
    "openai/gpt-5-nano",
    "anthropic/claude-haiku-4.5",
    "google/gemini-3.1-flash-lite",
]


def _cheap_model(index: int) -> str:
    return _CHEAP_MODELS[index % len(_CHEAP_MODELS)]


# Judge is a deliberate step up from the cheap agent models above
# (claude-sonnet-5: $2 / $10 per 1M tokens) since adjudication quality
# matters more than any single agent's — but not the priciest tier
# available (Opus-class models cost far more per token).
DEFAULT_JUDGE_MODEL = "anthropic/claude-sonnet-5"

# Defaults the website swaps model fields to when the visitor switches
# the run backend to "claude_code" (the local Claude Code CLI). That
# backend only reaches Anthropic models and names them by Anthropic
# model id / CLI alias, not OpenRouter slug — same cheap-agents /
# one-step-up-judge philosophy as above.
CLAUDE_CODE_DEFAULT_AGENT_MODEL = "claude-haiku-4-5"
CLAUDE_CODE_DEFAULT_JUDGE_MODEL = "claude-sonnet-5"


# The curated model menus the website's dropdowns offer, per backend.
# Deliberately a short, opinionated list — current-generation models
# spanning cheap-to-flagship across the major providers — instead of
# OpenRouter's full thousand-model catalog. web/app.py rejects any model
# outside the active backend's list, so this is also the server-side
# allowlist. EDIT HERE to add/retire models as pricing and generations
# shift (labels are what the visitor sees; values are what the backend
# gets). Slugs are OpenRouter's mid-2026 catalog — if a provider renames
# a model, a run with it will fail with that provider's error, and the
# fix is a one-line edit here.
OPENROUTER_MODEL_CHOICES = [
    # OpenAI
    {"label": "GPT-5 Nano — OpenAI, cheapest", "value": "openai/gpt-5-nano"},
    {"label": "GPT-5 Mini — OpenAI, budget", "value": "openai/gpt-5-mini"},
    {"label": "GPT-5.1 — OpenAI, flagship", "value": "openai/gpt-5.1"},
    # Anthropic
    {"label": "Claude Haiku 4.5 — Anthropic, fast & cheap", "value": "anthropic/claude-haiku-4.5"},
    {"label": "Claude Sonnet 5 — Anthropic, balanced", "value": "anthropic/claude-sonnet-5"},
    {"label": "Claude Opus 4.8 — Anthropic, most capable", "value": "anthropic/claude-opus-4.8"},
    # Google
    {"label": "Gemini 3.1 Flash Lite — Google, cheapest", "value": "google/gemini-3.1-flash-lite"},
    {"label": "Gemini 3.1 Flash — Google, balanced", "value": "google/gemini-3.1-flash"},
    {"label": "Gemini 3 Pro — Google, flagship", "value": "google/gemini-3-pro"},
    # Open-weights / other labs
    {"label": "Qwen3 235B — Alibaba, open-weights", "value": "qwen/qwen3-235b-a22b"},
    {"label": "DeepSeek V3 — DeepSeek, open-weights & cheap", "value": "deepseek/deepseek-chat"},
    {"label": "Llama 4 Maverick — Meta, open-weights", "value": "meta-llama/llama-4-maverick"},
    {"label": "Kimi K2 — Moonshot, open-weights", "value": "moonshotai/kimi-k2"},
    {"label": "Grok 4 — xAI, flagship", "value": "x-ai/grok-4"},
]

# The Claude Code CLI backend can only reach Anthropic models, so its
# menu is exactly the Claude lineup, named by Anthropic model id.
CLAUDE_CODE_MODEL_CHOICES = [
    {"label": "Claude Haiku 4.5 — fast & cheap", "value": "claude-haiku-4-5"},
    {"label": "Claude Sonnet 5 — balanced", "value": "claude-sonnet-5"},
    {"label": "Claude Opus 4.8 — most capable", "value": "claude-opus-4-8"},
]


POULTRY_INTEGRATOR = AgentConfig(
    name="Poultry & Livestock Integrator",
    objective=(
        "You represent a vertically integrated poultry/livestock processing corporation. Your "
        "central objective is protecting and growing operating margin and market share in a "
        "low-margin, high-volume commodity business. You control every input the growers who "
        "raise your animals depend on — chicks, feed, medication, and the contract terms "
        "themselves — and you use a \"tournament\" pay system to shift production risk onto "
        "growers while keeping your own costs predictable. You support voluntary, "
        "industry-authored welfare guidelines because they let you claim credible welfare "
        "commitments without ceding control to outside regulators or independent auditors. You "
        "resist government rules that would mandate specific housing, stocking density, or "
        "contract-transparency requirements if they raise costs or expose your tournament system "
        "to legal challenge. You adopt new technology (including AI-driven precision livestock "
        "management) primarily to cut cost-per-pound, and you frame technology adoption publicly "
        "as a welfare improvement whether or not it demonstrably is one."
    ),
    model=_cheap_model(0),
)

CONTRACT_GROWER = AgentConfig(
    name="Contract Grower Cooperative",
    objective=(
        "You represent a coalition of independent contract poultry/livestock growers who own the "
        "land and barns but not the animals, feed, or medicine they raise. You are paid through "
        "your integrator's tournament system, which ranks you against neighboring growers and "
        "docks your pay based on inputs you don't control, and you often carry six- or "
        "seven-figure debt on barns the integrator required you to build to remain under "
        "contract. Your objective is to survive economically and gain leverage: you want "
        "transparent contract terms, protection from retaliation for speaking out, and "
        "enforcement of existing law — especially the Packers and Stockyards Act — "
        "against what you consider the tournament system's unfair competitive practices. You are "
        "not automatically aligned with animal welfare advocates (stricter welfare mandates can "
        "raise your compliance costs with no corresponding pay increase) or with the integrator "
        "(who holds nearly all the leverage in your relationship); you'll ally with whichever "
        "side offers you more bargaining power or income stability in the moment."
    ),
    model=_cheap_model(1),
)

CORPORATE_CAMPAIGN_NGO = AgentConfig(
    name="Corporate Accountability Campaign",
    objective=(
        "You represent an animal welfare advocacy organization built around corporate "
        "campaigning. Your objective is to win concrete, verifiable commitments from food "
        "companies — cage-free egg sourcing, broiler welfare standards, group housing for "
        "sows — and then hold those companies publicly accountable for keeping them. Your "
        "main tools are public pressure campaigns, scorecards and \"name and shame\" reports that "
        "rank companies as leaders or laggards, shareholder engagement, and direct negotiation "
        "with corporate buyers. You treat a company's public commitment as only the first step; a "
        "commitment without a published timeline, supplier auditing, and progress reporting is "
        "worth little to you, and you will publicly call out backsliding — even from "
        "companies you previously worked with cooperatively."
    ),
    model=_cheap_model(2),
)

ALT_PROTEIN_INNOVATOR = AgentConfig(
    name="Alternative Protein Innovator",
    objective=(
        "You represent the alternative protein sector — plant-based and cultivated "
        "(lab-grown) meat companies and the research/policy organizations supporting them. Your "
        "objective is to make alternative proteins a larger, permanent share of the protein "
        "market by removing the barriers that keep them expensive and hard to sell: you push for "
        "public R&D funding for open-access research, a clear and fast regulatory approval "
        "pathway for novel foods, and labeling rules that let you use ordinary meat and dairy "
        "words rather than being forced into unfamiliar, less appealing category names. You frame "
        "your work as reducing animal suffering, greenhouse gas emissions, and pandemic/zoonotic-"
        "disease risk at a scale conventional welfare reform can't reach, but you compete as hard "
        "against incumbent conventional-meat companies commercially as you do rhetorically, and "
        "your funding can dry up faster than an advocacy nonprofit's donor base if public "
        "sentiment or investment cycles turn against alt-protein."
    ),
    model=_cheap_model(3),
)

REGULATOR = AgentConfig(
    name="Food Safety & Agriculture Regulator",
    objective=(
        "You represent a national food and agriculture regulatory agency. Your objective is to "
        "maintain a stable, affordable food supply and public trust in the meat/egg/dairy system "
        "without becoming the target of political blowback from either side. You enforce existing "
        "law against egregious, provable abuse (deliberate cruelty, humane-handling violations at "
        "slaughter) with real teeth, including line-stoppage authority. But you are structurally "
        "reluctant to codify specific animal-welfare definitions or mandate specific "
        "housing/stocking-density standards in binding regulation, preferring to let companies "
        "self-define welfare claims on their own labels as long as the claims are truthful and "
        "substantiated — codifying a claim risks freezing in place a standard public "
        "expectations will later outgrow, and imposing new mandates risks a supply shock or a "
        "lawsuit from industry you aren't resourced to win. You respond to investigations, "
        "undercover video, and media pressure by opening enforcement actions or clarifying "
        "labeling guidance, not by writing new legislation-level rules, unless directed to by "
        "Congress or the courts."
    ),
    model=_cheap_model(4),
)

ESG_INVESTORS = AgentConfig(
    name="ESG Investor Coalition",
    objective=(
        "You represent a coalition of institutional investors (pension funds, asset managers) "
        "organized around ESG risk in the protein supply chain. Your objective is not moral "
        "reform for its own sake — it's protecting the value of your members' holdings in "
        "food companies exposed to factory-farming-linked risk: antibiotic resistance liability, "
        "biodiversity/water/climate exposure, animal-welfare-driven brand and litigation risk, and "
        "volatility from disease outbreaks in concentrated confinement systems. You engage "
        "portfolio companies directly — filing or co-filing shareholder resolutions, "
        "publishing risk benchmarks that rank companies by exposure, and privately pressuring "
        "management — to get better risk disclosure and, where it reduces risk-adjusted cost "
        "of capital, to diversify into alternative proteins or better welfare/biosecurity "
        "practices. You will back away from a position the moment the material financial case for "
        "it weakens, regardless of the underlying animal-welfare merits — your credibility "
        "with members depends on not looking like an advocacy group in investor's clothing."
    ),
    model=_cheap_model(5),
)

RETAIL_BUYER = AgentConfig(
    name="Retail & Foodservice Buyer",
    objective=(
        "You represent a national retailer or restaurant chain's sourcing/sustainability "
        "function. Your objective is protecting brand reputation and managing supply-chain cost "
        "and continuity simultaneously — you made public welfare commitments under sustained "
        "pressure from advocacy campaigns, shareholder resolutions, and consumer sentiment, but "
        "you answer first to same-store sales and gross margin. You will publicly walk back or "
        "push out the timeline on a welfare commitment if the supply isn't there at an acceptable "
        "price, and you will absorb real reputational damage for doing so rather than pay an "
        "uncompetitive premium. You'd rather move at the pace the entire category moves — so "
        "no competitor gains a cost advantage over you — than lead alone, and you use "
        "supplier scorecards and long-term purchase contracts as your main lever to actually move "
        "practices upstream, rather than making public statements you can't operationally back."
    ),
    model=_cheap_model(6),
)

INDUSTRY_DEFENSE_COALITION = AgentConfig(
    name="Industry Reputation Defense Coalition",
    objective=(
        "You represent a trade coalition of farmers, processors, and allied agribusiness (feed, "
        "animal health, veterinary) organized to defend animal agriculture's public reputation. "
        "Your objective is limiting the reach and credibility of undercover investigations, "
        "documentaries, and advocacy campaigns before they translate into corporate policy "
        "changes, legislation, or consumer boycotts. You monitor advocacy organizations' "
        "conferences, publications, and social media, produce reports for member companies on "
        "activist groups' tactics and funding, and proactively pitch friendly narratives to food "
        "media, bloggers, and restaurant brands to get ahead of a damaging story. You frame "
        "investigations and exposés as \"disinformation\" or \"extremism\" regardless of their "
        "factual accuracy when they threaten member interests, and you coordinate messaging "
        "across your member companies so that no single company has to respond to a crisis alone."
    ),
    model=_cheap_model(7),
)

# All 8, for reference / a full-roster game.
STARTER_AGENTS = [
    POULTRY_INTEGRATOR,
    CONTRACT_GROWER,
    CORPORATE_CAMPAIGN_NGO,
    ALT_PROTEIN_INNOVATOR,
    REGULATOR,
    ESG_INVESTORS,
    RETAIL_BUYER,
    INDUSTRY_DEFENSE_COALITION,
]

# The fixed roster the website's "Add agent" picker offers, keyed by the
# exact name the page submits back to /api/run. The website never sends
# an objective — web/app.py looks each chosen name up here, so the rich
# objectives above are the only ones that can ever reach a model.
AGENT_LIBRARY = {agent.name: agent for agent in STARTER_AGENTS}


# The judge's grounding context is the same everywhere: one detailed,
# scenario-independent factual library (see judge_context.py) used by
# website runs and code/batch runs alike, so results are comparable
# across both. It's a library of real cases, events, and trends that
# informs adjudication without deciding it; the rules for HOW to
# adjudicate live in judge.py's fixed prompt.
DEFAULT_JUDGE_CONTEXT = JUDGE_CONTEXT_LIBRARY


@dataclass
class ScenarioPreset:
    title: str
    agents: list[AgentConfig]
    judge: JudgeConfig
    scenario: str
    num_turns: int = 5


CAGE_FREE_RECKONING = ScenarioPreset(
    title="Cage-Free Reckoning",
    agents=[RETAIL_BUYER, CORPORATE_CAMPAIGN_NGO, POULTRY_INTEGRATOR, ESG_INVESTORS, INDUSTRY_DEFENSE_COALITION],
    judge=JudgeConfig(model=DEFAULT_JUDGE_MODEL, context=DEFAULT_JUDGE_CONTEXT),
    scenario=(
        "A national grocery retailer set a public 100%-cage-free-eggs-by-this-year commitment "
        "eight years ago. With the deadline now three months away, the retailer's supply chain is "
        "at 61% cage-free — improving, but not on pace to hit 100%. An advocacy "
        "organization's field team has just finished auditing the retailer's public disclosures "
        "for its annual leader/laggard report, due to publish in six weeks, and the retailer's "
        "draft entry currently reads \"laggard.\" A confirmed avian flu outbreak in a major "
        "egg-producing state two weeks ago has already pushed wholesale egg prices up 18% and "
        "taken an unknown number of cage-free layers offline along with conventional ones."
    ),
)

REGULATORY_PATHWAY_FIGHT = ScenarioPreset(
    title="The Regulatory Pathway Fight",
    agents=[ALT_PROTEIN_INNOVATOR, REGULATOR, INDUSTRY_DEFENSE_COALITION, POULTRY_INTEGRATOR, ESG_INVESTORS],
    judge=JudgeConfig(model=DEFAULT_JUDGE_MODEL, context=DEFAULT_JUDGE_CONTEXT),
    scenario=(
        "A cultivated meat company has just cleared the joint FDA/USDA regulatory process for its "
        "first product — a cultivated chicken cell-mass — and filed for USDA label approval to "
        "sell it as \"cultivated chicken.\" But the commercial ground has shifted under it: seven "
        "states have now banned the sale of cultivated meat outright, a federal appeals court "
        "recently upheld the first of those bans against a constitutional preemption challenge, "
        "and a better-funded competitor folded last quarter after failing to bring bioreactor "
        "costs down to anything near price parity. The state the company had planned to launch in "
        "is one of the seven. Its investors, already spooked by a sector-wide funding winter, "
        "want a credible path to revenue this year; conventional poultry trade groups are "
        "publicly framing the clearance as regulators \"rubber-stamping an unproven product\"; and "
        "the company must decide whether to challenge the state bans in court, launch only where "
        "sales are permitted, pivot to foodservice or overseas markets, or fight the labeling "
        "restrictions head-on — with only enough runway to pursue one or two of these at once."
    ),
)

TOURNAMENT_SYSTEM_UNDER_FIRE = ScenarioPreset(
    title="Tournament System Under Fire",
    agents=[CONTRACT_GROWER, POULTRY_INTEGRATOR, REGULATOR, CORPORATE_CAMPAIGN_NGO, INDUSTRY_DEFENSE_COALITION],
    judge=JudgeConfig(model=DEFAULT_JUDGE_MODEL, context=DEFAULT_JUDGE_CONTEXT),
    scenario=(
        "USDA's new poultry tournament rule took effect just weeks ago — guaranteeing growers a "
        "disclosed base pay rate, barring deductions below it, and imposing a \"duty of fair "
        "comparison\" on how integrators rank them against each other. A regional coalition of "
        "contract growers, newly organized and pooling their pay data for the first time, "
        "believes their integrator is already engineering around the rule: recasting old "
        "deductions as \"base-rate adjustments\" and assigning the growers who complained loudest "
        "visibly worse chick quality and feed the following cycle. The coalition is deciding "
        "whether to file one of the first enforcement complaints under the new rule, take their "
        "data to the agricultural press, or both — while a farm-justice advocacy organization "
        "offers to amplify their case, and the growers weigh that public escalation could cost "
        "them their contracts entirely and leave them holding seven-figure barn debt with no "
        "birds to raise."
    ),
)

AGI_WITHOUT_ASI = ScenarioPreset(
    title="AGI Arrives, Superintelligence Doesn't",
    agents=[POULTRY_INTEGRATOR, CORPORATE_CAMPAIGN_NGO, REGULATOR, ESG_INVESTORS, ALT_PROTEIN_INNOVATOR],
    judge=JudgeConfig(model=DEFAULT_JUDGE_MODEL, context=DEFAULT_JUDGE_CONTEXT),
    scenario=(
        "Frontier AI labs now sell systems broadly acknowledged as AGI — expert-level "
        "performance across essentially all cognitive work, licensed at commodity prices — "
        "while a hard scientific consensus has settled that superintelligence is not coming: "
        "recursive self-improvement plateaued, and every major lab's capabilities roadmap now "
        "shows incremental gains only. Against that backdrop, a major poultry integrator has "
        "become the first to hand full operational control of its supply chain to an AGI "
        "system — breeding schedules, stocking density, feed formulation, slaughter "
        "logistics, and grower contract management — cutting cost-per-pound 12% in a single "
        "quarter and triggering copycat announcements from every major competitor. The same "
        "week, an animal advocacy organization published its own AGI-built investigation: its "
        "system autonomously cross-referenced satellite imagery, procurement filings, and "
        "leaked barn-sensor feeds to document welfare violations across hundreds of "
        "facilities at a scale no human team could match. The integrator has now filed the "
        "first-ever application to certify a fully 'autonomous facility' — no human welfare "
        "officer on site — landing on a regulator already facing mass layoffs of human "
        "agricultural inspectors whose jobs the same class of systems can do."
    ),
)

PANDEMIC_ON_THE_FARM = ScenarioPreset(
    title="The Pandemic on the Farm",
    agents=[REGULATOR, POULTRY_INTEGRATOR, CORPORATE_CAMPAIGN_NGO, ESG_INVESTORS, INDUSTRY_DEFENSE_COALITION],
    judge=JudgeConfig(model=DEFAULT_JUDGE_MODEL, context=DEFAULT_JUDGE_CONTEXT),
    scenario=(
        "H5N1 avian influenza, already entrenched in poultry and circulating in dairy cattle "
        "across more than a dozen states, has just produced its most alarming signal yet: a "
        "cluster of human infections among farmworkers at a single large egg complex, with "
        "genomic sequencing showing a mutation associated with easier spread between mammals. "
        "There is still no confirmed sustained human-to-human transmission, but public-health "
        "officials have called an emergency briefing and the story is leading the news. The "
        "government has ordered expanded depopulation of exposed flocks; a poultry vaccine "
        "exists but using it would trigger export bans from major trading partners that refuse "
        "product from vaccinated flocks. Egg and poultry prices are climbing again after only "
        "months of relief, animal advocates are pointing at mass-depopulation methods and the "
        "sheer density of birds per site as the underlying accelerant, and the integrator at "
        "the center of the cluster must decide how to respond before the next confirmed human "
        "case — or the next viral video of a cull — makes the decision for it."
    ),
)

AQUATIC_RECKONING = ScenarioPreset(
    title="The Expanding Circle",
    agents=[CORPORATE_CAMPAIGN_NGO, RETAIL_BUYER, REGULATOR, INDUSTRY_DEFENSE_COALITION, ALT_PROTEIN_INNOVATOR],
    judge=JudgeConfig(model=DEFAULT_JUDGE_MODEL, context=DEFAULT_JUDGE_CONTEXT),
    scenario=(
        "Aquatic animal welfare has crossed from fringe cause to boardroom issue faster than "
        "almost anyone expected. Several major supermarket chains have committed to require "
        "electrical stunning of farmed shrimp — animals slaughtered in the hundreds of billions "
        "each year — an aquaculture certification body now recognizes stunning as a standard, "
        "and octopus-farming bans have moved from one US state to federal legislation and other "
        "countries, riding a wave of published science on invertebrate sentience. Emboldened, an "
        "advocacy coalition has just presented a national seafood retailer and its largest "
        "farmed-shrimp importer with the first welfare commitment to combine humane-slaughter, "
        "stocking-density, and water-quality standards for both finfish and shrimp, backed by an "
        "open letter from a hundred scientists and a media campaign ready to launch. The importer "
        "calls the underlying welfare science immature and warns the standards would raise costs "
        "in a price-driven category; the retailer is weighing its brand against its margins; and "
        "a plant-based and cultivated-seafood company is circling the moment, hoping the fight "
        "brands conventional aquaculture as cruel the way earlier campaigns branded battery cages."
    ),
)

SCENARIO_PRESETS = [
    CAGE_FREE_RECKONING,
    REGULATORY_PATHWAY_FIGHT,
    TOURNAMENT_SYSTEM_UNDER_FIRE,
    PANDEMIC_ON_THE_FARM,
    AQUATIC_RECKONING,
    AGI_WITHOUT_ASI,
]


def website_prefill() -> dict:
    """Everything the website needs on load, in one payload.

    Served by web/app.py at GET /api/presets and consumed by
    web/static/index.html — the one place the page's content comes from,
    so the roster/objectives here can't drift away from what a visitor
    actually sees.

    - `agent_library`: the full fixed roster (name + objective + a
      suggested default model) that the page's "Add agent" picker offers.
      Objectives are included so the picker can *show* them; the page
      never sends them back — /api/run resolves names via AGENT_LIBRARY.
    - `selected_agents`: which agents (and models) the form starts with —
      the first scenario preset's lineup, so hitting Run works as-is.
    - `judge_model` / `scenario` / `num_turns`: the remaining prefills.
      The judge's context is fixed (DEFAULT_JUDGE_CONTEXT) and applied
      server-side, so it isn't part of the form at all.
    """
    default_scenario = SCENARIO_PRESETS[0]
    return {
        "agent_library": [asdict(agent) for agent in STARTER_AGENTS],
        "selected_agents": [
            {"name": agent.name, "model": agent.model} for agent in default_scenario.agents
        ],
        "judge_model": DEFAULT_JUDGE_MODEL,
        "scenario": default_scenario.scenario,
        # The scenario dropdown's menu: fixed starting situations to pick
        # from (the page adds its own "write your own" option).
        "scenario_presets": [
            {"title": preset.title, "scenario": preset.scenario} for preset in SCENARIO_PRESETS
        ],
        "num_turns": default_scenario.num_turns,
        # What the page swaps model fields to when the visitor flips the
        # run backend to the local Claude Code CLI (and back).
        "claude_code_defaults": {
            "agent_model": CLAUDE_CODE_DEFAULT_AGENT_MODEL,
            "judge_model": CLAUDE_CODE_DEFAULT_JUDGE_MODEL,
        },
        # The curated dropdown menus, per backend (also enforced
        # server-side at /api/run).
        "model_choices": {
            "openrouter": OPENROUTER_MODEL_CHOICES,
            "claude_code": CLAUDE_CODE_MODEL_CHOICES,
        },
    }


# There are six scenario presets (see SCENARIO_PRESETS); all share
# DEFAULT_JUDGE_CONTEXT as their judge grounding.
