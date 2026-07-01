"""Ready-to-use example content: 8 stakeholder agents grounded in real
animal-welfare-in-agriculture actors, and 3 scenario presets built from
subsets of them.

This is *example* data, same spirit as scripts/run_example.py — a
starting roster and a few worked scenarios to run as-is or edit, not a
fixed "the" roster. Full research/reasoning behind each role and each
scenario's judge context lives in docs/agent_roster.md and
docs/scenarios.md.

This module is the SINGLE SOURCE OF TRUTH for the content the website
form loads pre-filled with: web/app.py serves `website_prefill()` at
GET /api/presets, and web/static/index.html fetches it on load to
populate its agent rows, judge context, scenario, and turn count. The
page no longer hardcodes its own copy of any of this — edit the presets
here and the website's prefill changes with it. (These used to be two
separate hand-maintained copies that silently drifted apart, which is
exactly what made the rich objectives below never actually reach a
model.)
"""

from dataclasses import asdict, dataclass

from wargame.agents import AgentConfig
from wargame.judge import JudgeConfig

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
    judge=JudgeConfig(
        model=DEFAULT_JUDGE_MODEL,
        context=(
            "This is a wargame about corporate animal-welfare commitments and accountability in "
            "the US egg supply chain. Roughly half of the US egg-laying flock is now cage-free, "
            "up from a small fraction a decade ago, driven by corporate pledges won through "
            "advocacy pressure starting around 2015. But cage-free hen capacity has repeatedly "
            "lagged the combined demand from every company that pledged a deadline. At least one "
            "major retailer has already publicly abandoned a stated cage-free deadline, citing "
            "supply and cost, and absorbed real but survivable reputational damage for doing so. "
            "Advocacy organizations publish periodic public leader/laggard reports naming "
            "companies by their progress and transparency. Avian flu outbreaks periodically wipe "
            "out large fractions of the laying flock within weeks, which can erase months of "
            "cage-free conversion progress and spike egg prices industry-wide — treat a flu "
            "shock as a plausible event you may introduce if agents' actions don't create enough "
            "tension on their own."
        ),
    ),
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
    judge=JudgeConfig(
        model=DEFAULT_JUDGE_MODEL,
        context=(
            "This is a wargame about the regulatory and labeling fight over cultivated (lab-grown) "
            "meat in the US. Cultivated meat companies need pre-market safety approval from a "
            "joint USDA/FDA process before a product can be sold, and separately need USDA label "
            "approval for the product's name and claims. Conventional meat trade groups have "
            "lobbied at both the state and federal level to restrict cultivated and plant-based "
            "products from using words like \"meat,\" \"burger,\" or species names on their "
            "labels, with mixed legislative success. Alt-protein advocates argue restrictive "
            "labeling suppresses consumer understanding and deliberately handicaps a nascent "
            "category; incumbent industry argues it prevents consumer confusion. Public and "
            "investor sentiment toward alt-protein has been volatile — funding and media "
            "coverage in the sector cooled noticeably after early hype outran commercial "
            "traction. Treat regulatory decisions and legislative votes as taking multiple turns "
            "to resolve, not one; a single turn's actions should move the needle, not resolve the "
            "fight."
        ),
    ),
    scenario=(
        "A cultivated meat company has just received joint USDA/FDA pre-market safety clearance "
        "for its first product — a cultivated chicken cell-mass — and has filed for "
        "USDA label approval to market it as \"cultivated chicken.\" A state where the company had "
        "planned to launch first passed a law last year banning any product not derived from a "
        "\"slaughtered animal\" from using species-specific meat terms on its label. The company "
        "must decide how to enter the market; conventional poultry trade groups are already "
        "publicly framing the safety clearance as regulators \"rubber-stamping an unproven "
        "product,\" and investor sentiment toward the alt-protein sector broadly has cooled over "
        "the past two years after several high-profile companies missed commercialization "
        "targets."
    ),
)

TOURNAMENT_SYSTEM_UNDER_FIRE = ScenarioPreset(
    title="Tournament System Under Fire",
    agents=[CONTRACT_GROWER, POULTRY_INTEGRATOR, REGULATOR, CORPORATE_CAMPAIGN_NGO, INDUSTRY_DEFENSE_COALITION],
    judge=JudgeConfig(
        model=DEFAULT_JUDGE_MODEL,
        context=(
            "This is a wargame about the poultry contract-growing \"tournament\" pay system and "
            "USDA rulemaking under the Packers and Stockyards Act. Contract growers don't own the "
            "birds, feed, or medicine they raise; integrators pay them by ranking their flock's "
            "feed-conversion performance against other growers in a tournament group each week, "
            "docking below-average growers and paying above-average ones a bonus from the docked "
            "pool. Growers argue this makes them compete blindfolded since the integrator controls "
            "the input quality that heavily determines performance, and some report retaliation "
            "after complaining. USDA finalized a rule in the mid-2020s requiring more contract "
            "transparency and limiting some tournament practices, but enforcement and further "
            "rulemaking remain contested and slow-moving; a full ban on the tournament system is "
            "not currently on the table and shouldn't resolve in fewer than several turns if it "
            "comes up at all. Many growers carry six- or seven-figure debt on barns the integrator "
            "required as a condition of the contract."
        ),
    ),
    scenario=(
        "A regional coalition of contract growers has organized for the first time, sharing "
        "tournament pay data with each other privately and finding wide, hard-to-explain variance "
        "in the inputs (chick weight, feed quality) they were assigned relative to top-performing "
        "growers in their tournament group. Three growers who raised the issue with their "
        "integrator's field representative were switched to a lower-quality feed supplier the "
        "following cycle. The coalition is now deciding whether to file a formal complaint under "
        "the Packers and Stockyards Act, go to agricultural press, or both — and an advocacy "
        "organization focused on farm justice has offered to help amplify their case publicly."
    ),
)

SCENARIO_PRESETS = [
    CAGE_FREE_RECKONING,
    REGULATORY_PATHWAY_FIGHT,
    TOURNAMENT_SYSTEM_UNDER_FIRE,
]


def website_prefill() -> dict:
    """The default game the website form loads pre-filled with.

    Served by web/app.py at GET /api/presets and consumed by
    web/static/index.html on load — the one place the page's prefilled
    content comes from, so the rich rosters/objectives here can't drift
    away from what a visitor actually sees and submits to a model.

    It's the full 8-agent starter roster, framed by the first scenario
    preset's judge context, scenario, and turn count. The result is a
    plain JSON-serializable dict whose shape matches exactly what the
    /api/run request body expects (minus the visitor-supplied API key).
    """
    default_scenario = SCENARIO_PRESETS[0]
    return {
        "agents": [asdict(agent) for agent in STARTER_AGENTS],
        "judge": asdict(default_scenario.judge),
        "scenario": default_scenario.scenario,
        "num_turns": default_scenario.num_turns,
    }
