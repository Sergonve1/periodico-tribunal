"""
Evaluation dataset for the "hard" v2 RAG experiment.

Unlike the original 50-question set (each question written almost verbatim
from a single source article, which made retrieval trivially easy and
caused Precision@k/Recall@k/MRR to saturate at k=1 for all four similarity
functions), this dataset is designed so that:

  1. Questions are paraphrased and use vocabulary that does not copy the
     source article's wording, forcing the embedding model to rely on
     semantic rather than lexical overlap.
  2. The corpus is chunked at paragraph level (see build_corpus_v2 in
     experiment_v2.py), producing many more, shorter, variable-length
     passages than the whole-article corpus used in the first experiment.
     This increases embedding-norm variance, which is what allows cosine,
     dot product, Euclidean and Manhattan to disagree on rankings.
  3. Roughly half of the questions are "single-hop" (one relevant article)
     drawn from topic clusters with several similar distractor articles
     (e.g. multiple Tesla delivery/lawsuit stories, multiple Microsoft
     cloud-earnings stories), making the retrieval task harder than in v1.
  4. The other half are "multi-hop" questions whose answer requires
     combining information from 2-3 different articles (|Rel(q)| > 1),
     so Recall@k cannot trivially saturate at k=1 and larger k values have
     a real chance of outperforming k=1.

Each entry has:
  - id: question id
  - question: English question
  - reference_answer: English reference answer used for the
    answer-similarity generation metric
  - gold_ids: list of article ids (from the merged, deduplicated corpus of
    Anthropic / Artificial intelligence / ia / Meta / Microsoft / NVIDIA /
    OpenAI / Tesla) considered relevant to the question. len(gold_ids) == 1
    for single-hop questions, 2 or 3 for multi-hop questions.
  - hop_type: "single" or "multi", for reporting purposes only.
"""

EVAL_DATASET_V2 = [
    # ---------------------------------------------------------------
    # MULTI-HOP QUESTIONS (|Rel(q)| = 2 or 3)
    # ---------------------------------------------------------------
    {
        "id": "mh01",
        "question": "Between Anthropic and OpenAI, which company reached the higher valuation in the funding round described in the articles, and roughly how far apart were the two figures?",
        "reference_answer": "OpenAI reached a much higher valuation than Anthropic: OpenAI's funding round with SoftBank valued it at about $300bn, while Anthropic's round valued it at a little over $60bn (around $61.5bn), so OpenAI's valuation was roughly five times larger.",
        "gold_ids": ["05c90475-84fb-4f88-bbfc-6b1a60af90db", "d21037d1-7b84-4f07-8d82-b417badbe96e"],
        "hop_type": "multi",
    },
    {
        "id": "mh02",
        "question": "Comparing Elon Musk's xAI with Anthropic, whose valuation was higher after their most recent funding rounds described in the articles?",
        "reference_answer": "Anthropic's valuation was higher: it was valued at roughly $60-61.5bn after its funding round, while xAI was valued at about $45bn after raising $5bn.",
        "gold_ids": ["342e304b-4c09-4951-8bba-bc9a27ddb726", "05c90475-84fb-4f88-bbfc-6b1a60af90db"],
        "hop_type": "multi",
    },
    {
        "id": "mh03",
        "question": "How did Google's financial backing of Anthropic evolve over time according to the two funding stories, from its first stake to its later top-up?",
        "reference_answer": "Google first invested about $300mn in Anthropic in exchange for roughly a 10% stake, and later added more than $1bn on top of an existing commitment of about $2bn, deepening its position in the AI start-up.",
        "gold_ids": ["583ead66-467c-4bd5-84d0-ed5df7b5bf9c", "ed631513-dd37-44a3-a536-b2002f5727cc"],
        "hop_type": "multi",
    },
    {
        "id": "mh04",
        "question": "By what factor did OpenAI's valuation grow between the funding round mentioned when SoftBank bought a stake from employees and the later SoftBank-led round?",
        "reference_answer": "OpenAI's valuation roughly doubled: it was valued at about $150bn (a $6.6bn raise) when SoftBank bought up to $1.5bn of employee shares, and later reached about $300bn after the $40bn SoftBank-led round.",
        "gold_ids": ["1a2a9b25-a7f1-4ce0-b537-e67b3853e5ad", "d21037d1-7b84-4f07-8d82-b417badbe96e"],
        "hop_type": "multi",
    },
    {
        "id": "mh05",
        "question": "How do Microsoft and Amazon differ in their approach to reducing dependence on Nvidia for AI computing hardware?",
        "reference_answer": "Microsoft has leaned into Nvidia rather than reducing dependence on it, reportedly buying about twice as many Nvidia AI chips as its rivals in 2024, whereas Amazon is trying to cut its reliance on Nvidia by developing its own custom AI chips through its Annapurna Labs unit, such as the Trainium line.",
        "gold_ids": ["668883d6-f5ad-4512-874e-2741807caf49", "3d9b5c6d-f1ae-4f6f-adc3-51e5f1dfb008"],
        "hop_type": "multi",
    },
    {
        "id": "mh06",
        "question": "What was the overall sequence of Elon Musk's legal action against OpenAI: did he abandon it, and what happened afterward?",
        "reference_answer": "Musk first withdrew his lawsuit against OpenAI and Sam Altman a few months after filing it, then filed a new lawsuit reviving similar claims (including racketeering allegations), and later a judge rejected OpenAI's attempt to dismiss that case, allowing it to move toward trial.",
        "gold_ids": [
            "03b9fb65-5f12-41a8-9d8e-e2243b72466d",
            "bcfc3cc8-6465-4fd3-b44a-bdf22996fc3a",
            "a57fc9e7-d4b8-4a14-aa5d-331fd7935f89",
        ],
        "hop_type": "multi",
    },
    {
        "id": "mh07",
        "question": "How has OpenAI described Microsoft's ownership position, and what complication arose from that position when OpenAI tried to restructure as a for-profit company?",
        "reference_answer": "OpenAI changed how it described Microsoft's role, from calling it a 'minority owner' to a 'minority economic interest' amid regulatory scrutiny, and when OpenAI later tried to convert into a for-profit company its board struggled to determine exactly how much equity to assign Microsoft as part of that conversion.",
        "gold_ids": ["458b162d-c97a-4464-8afc-72d65afb28ed", "7dcd4095-717e-49f8-8d12-6c8673eb73d7"],
        "hop_type": "multi",
    },
    {
        "id": "mh08",
        "question": "As OpenAI moved toward becoming a for-profit company, what two separate equity questions were being negotiated at the same time?",
        "reference_answer": "OpenAI was simultaneously negotiating how much equity to grant chief executive Sam Altman for the first time, and how large a stake to give Microsoft, its biggest investor, in the restructured public benefit corporation.",
        "gold_ids": ["78b7e7a7-7428-4c5e-bfa2-0921c9d6cd25", "7dcd4095-717e-49f8-8d12-6c8673eb73d7"],
        "hop_type": "multi",
    },
    {
        "id": "mh09",
        "question": "What was Amazon's cumulative investment in Anthropic after its second capital injection, and how does that compare with Google's stake in the same company?",
        "reference_answer": "Amazon doubled its total investment in Anthropic to $8bn after adding a further $4bn, making it Amazon's biggest-ever venture investment, while Google had separately built up a position of more than $1bn on top of an earlier roughly $2bn commitment.",
        "gold_ids": ["01da4ed8-0371-44b0-a07d-63e07f32939e", "ed631513-dd37-44a3-a536-b2002f5727cc"],
        "hop_type": "multi",
    },
    {
        "id": "mh10",
        "question": "How are US chip policy moves pulling the semiconductor industry in opposite directions, according to the export-curb story and the US manufacturing pledge story?",
        "reference_answer": "One policy move restricts the industry by clamping down on Nvidia's chip exports to China, costing it an estimated $5.5bn hit, while a separate move encourages US-based investment, with TSMC pledging an extra $100bn to build advanced chip plants in the US.",
        "gold_ids": ["66e6abfa-2b79-407c-bda6-d04d19b3b814", "68a0da9b-ffc7-4c67-8249-d7c452efa864"],
        "hop_type": "multi",
    },
    {
        "id": "mh11",
        "question": "What do the Figure AI funding round and the OpenAI-CoreWeave agreement have in common in terms of the companies involved?",
        "reference_answer": "Both deals involve OpenAI and Nvidia as key players: Microsoft, OpenAI and Nvidia together backed the $2.6bn humanoid-robot start-up Figure AI, while separately OpenAI struck a near-$12bn computing deal with CoreWeave, a cloud provider that itself relies heavily on Nvidia chips.",
        "gold_ids": ["3f7e86e1-123a-4fba-af0a-680d955125c0", "4b52fdbb-ca8e-4208-bb99-f1e7f9313863"],
        "hop_type": "multi",
    },
    {
        "id": "mh12",
        "question": "SoftBank made two large AI-related moves described in the articles: acquiring a chip company and buying into OpenAI. What were the two deals and their approximate sizes?",
        "reference_answer": "SoftBank agreed to acquire the chip start-up Ampere Computing for $6.5bn, and separately arranged to buy up to $1.5bn of OpenAI employee stock through a tender offer that valued OpenAI at about $150bn.",
        "gold_ids": ["235a02b0-bbb1-4f2e-a181-57a3907f36e3", "1a2a9b25-a7f1-4ce0-b537-e67b3853e5ad"],
        "hop_type": "multi",
    },
    {
        "id": "mh13",
        "question": "Elon Musk's xAI appears in a large infrastructure fund alongside Nvidia and also raised its own funding round separately. What are the two deals?",
        "reference_answer": "xAI and Nvidia joined the BlackRock- and Microsoft-backed AI Infrastructure Partnership, which aims to raise about $30bn (with a goal of up to $100bn including debt), and separately xAI itself raised $5bn in its own round at a $45bn valuation.",
        "gold_ids": ["53eeadd8-8fec-4f1b-991e-642e24959e02", "342e304b-4c09-4951-8bba-bc9a27ddb726"],
        "hop_type": "multi",
    },
    {
        "id": "mh14",
        "question": "What two separate regulatory bodies are scrutinising Big Tech's ties to AI start-ups, and what is each one looking into?",
        "reference_answer": "The European Commission is examining whether Microsoft's investment in OpenAI should be reviewed under EU merger rules, while the US Federal Trade Commission has launched a broader inquiry into partnerships between major cloud providers (Amazon, Microsoft, Google) and generative AI companies including OpenAI.",
        "gold_ids": ["27f641cd-eefd-4486-8005-d7e388f4a616", "6046292f-1c6d-499b-8ed5-7e7c337c5bbd"],
        "hop_type": "multi",
    },
    {
        "id": "mh15",
        "question": "What motivated Elon Musk to found xAI, and how does that motivation connect to the arguments he later made in his legal dispute with OpenAI?",
        "reference_answer": "Musk launched xAI explicitly to challenge the dominance of Sam Altman's OpenAI, and in his later lawsuit against OpenAI he argued the company had abandoned its founding non-profit mission of benefiting humanity by pursuing a for-profit, Microsoft-aligned path instead.",
        "gold_ids": ["19cce4b5-b2dd-4c1e-a109-b500e504dbb6", "a57fc9e7-d4b8-4a14-aa5d-331fd7935f89"],
        "hop_type": "multi",
    },
    {
        "id": "mh16",
        "question": "How does Musk's public criticism of the Stargate project relate to the broader OpenAI-Microsoft relationship described elsewhere?",
        "reference_answer": "Musk publicly cast doubt on the $500bn Stargate infrastructure project, claiming the backers did not actually have the funding, which added to public friction around OpenAI even as the company's deep multibillion-dollar alliance with Microsoft continued to be its central financial and infrastructure backer.",
        "gold_ids": ["b2899d25-9b16-461d-b406-89cfcadf3afc", "458b162d-c97a-4464-8afc-72d65afb28ed"],
        "hop_type": "multi",
    },
    {
        "id": "mh17",
        "question": "What objection did former OpenAI employees raise about the company's restructuring, and how does it relate to Sam Altman's own equity discussions at the time?",
        "reference_answer": "Former OpenAI staff and AI experts including Geoffrey Hinton sought to block OpenAI's conversion to a for-profit public benefit corporation over safety concerns, at the same time that OpenAI was separately discussing giving chief executive Sam Altman a personal equity stake in the newly restructured company for the first time.",
        "gold_ids": ["6b8e7eb5-d300-4c1f-8915-686d7449cae4", "78b7e7a7-7428-4c5e-bfa2-0921c9d6cd25"],
        "hop_type": "multi",
    },
    {
        "id": "mh18",
        "question": "Both Perplexity and Anthropic saw their valuations triple. What were the resulting valuations for each company?",
        "reference_answer": "Perplexity's valuation tripled to $9bn in its latest funding round, while Anthropic's valuation also roughly tripled, to about $60-61.5bn.",
        "gold_ids": ["d4fb70f9-b971-433b-884c-2f01d1d08968", "05c90475-84fb-4f88-bbfc-6b1a60af90db"],
        "hop_type": "multi",
    },
    {
        "id": "mh19",
        "question": "How does Microsoft's public stance on AI chip export controls contrast with the financial impact those controls had on Nvidia?",
        "reference_answer": "Microsoft publicly urged the Trump administration to reconsider AI chip export controls, warning they would push US allies toward Chinese technology instead, while Nvidia had already suffered a concrete financial impact from similar export curbs, taking an estimated $5.5bn earnings hit from restrictions on selling AI chips to China.",
        "gold_ids": ["c61203aa-bd1a-47cd-9c14-a2e9894f37ea", "66e6abfa-2b79-407c-bda6-d04d19b3b814"],
        "hop_type": "multi",
    },
    {
        "id": "mh20",
        "question": "How did the emergence of the Chinese AI model DeepSeek affect sentiment toward established AI leaders and toward Chinese technology stocks?",
        "reference_answer": "DeepSeek's low-cost model that matched OpenAI's performance shook confidence in Western AI leaders by suggesting cheaper alternatives were viable, while at the same time it triggered a bull market in Chinese tech stocks, with the Hang Seng Tech index rising more than 20% as investors piled into Chinese internet companies.",
        "gold_ids": ["9ace44ca-18c2-498b-bb37-d376b976105b", "af0636d6-59af-453c-9d75-6f6a3d9f11ce"],
        "hop_type": "multi",
    },
    # ---------------------------------------------------------------
    # SINGLE-HOP QUESTIONS (|Rel(q)| = 1, harder / paraphrased, drawn
    # from distractor-rich topic clusters)
    # ---------------------------------------------------------------
    {
        "id": "sh01",
        "question": "Why did an open-source advocacy group take issue with how Meta labels some of its AI models?",
        "reference_answer": "The group that has championed open-source software for 25 years said Meta was confusing users and diluting the meaning of 'open-source' by applying that label to AI models that do not meet the traditional standards of openness.",
        "gold_ids": ["397c50d8-8796-4042-a814-0ac2c068361f"],
        "hop_type": "single",
    },
    {
        "id": "sh02",
        "question": "What new kind of marketing discipline has emerged as consumers increasingly get information from AI assistants instead of search engines?",
        "reference_answer": "A new form of search engine optimisation aimed at AI chatbots has emerged, with companies building tools to help brands increase how often they are mentioned in responses from services like ChatGPT, Claude and Google's AI Overviews.",
        "gold_ids": ["9cc6cc0b-759f-4b8e-9ed1-9e32ad0fe22f"],
        "hop_type": "single",
    },
    {
        "id": "sh03",
        "question": "What restriction did a US regulator propose regarding how Meta can use data collected from young users?",
        "reference_answer": "The Federal Trade Commission proposed banning Meta from monetising data collected from children and further restricting its use of facial recognition technology, citing repeated violations of the company's privacy promises.",
        "gold_ids": ["05eeb0f8-d5b4-4c8c-bd98-7d843bbd4f53"],
        "hop_type": "single",
    },
    {
        "id": "sh04",
        "question": "What did a US court conclude about Google's conduct in the online advertising business?",
        "reference_answer": "A federal judge ruled that Google illegally built and maintained a monopoly in digital advertising, finding it had 'wilfully' monopolised the markets for ad exchanges and publisher ad servers, a ruling that could force it to divest parts of its ad business.",
        "gold_ids": ["34560a41-bd6c-4264-a4b5-da4bf4b8290b"],
        "hop_type": "single",
    },
    {
        "id": "sh05",
        "question": "What new wearable device did Meta's chief executive show off at the company's annual conference?",
        "reference_answer": "Mark Zuckerberg unveiled a prototype of lightweight augmented reality glasses called Orion, which use holographic displays and AI to overlay digital content on the real world and proactively suggest information to the wearer.",
        "gold_ids": ["29dbf49b-da1d-4dc1-804e-f3ebc6d68e77"],
        "hop_type": "single",
    },
    {
        "id": "sh06",
        "question": "Why did Microsoft's stock market value fall sharply after one of its quarterly earnings reports?",
        "reference_answer": "Microsoft lost about $200bn in market value after its cloud division, its biggest revenue driver including Azure, reported slower growth than Wall Street had expected, even though overall revenue and net income beat forecasts.",
        "gold_ids": ["5d044add-d6cd-4681-9c5f-d0278f52a476"],
        "hop_type": "single",
    },
    {
        "id": "sh07",
        "question": "What drove a positive reaction in Microsoft's share price following a different quarterly report?",
        "reference_answer": "Microsoft shares jumped after the company posted better-than-expected quarterly results, with cloud revenue growing strongly on the back of AI-related demand, easing investor fears of a slowdown; revenue rose 13% to $70.1bn and net income rose 18% to $25.8bn.",
        "gold_ids": ["9443ca4b-09c1-4f21-ba71-3953b3e0a714"],
        "hop_type": "single",
    },
    {
        "id": "sh08",
        "question": "How did a UK regulator's position change regarding Microsoft's attempt to buy a major video game publisher?",
        "reference_answer": "The UK's Competition and Markets Authority reversed its earlier objection to Microsoft's $75bn acquisition of Activision Blizzard, clearing the deal after reviewing new evidence, despite having previously suggested Microsoft would need to divest the Call of Duty business.",
        "gold_ids": ["4824dae0-847d-46d7-aa85-7a37daf82156"],
        "hop_type": "single",
    },
    {
        "id": "sh09",
        "question": "What accusation did Microsoft make against Google regarding lobbying tactics?",
        "reference_answer": "Microsoft accused Google of secretly funding a lobbying group designed to discredit Microsoft with regulators and mislead the public, describing it as a 'shadow campaign' amid intensifying competition between the two companies in cloud computing.",
        "gold_ids": ["520bf847-7346-442a-8f70-5c4680ae2886"],
        "hop_type": "single",
    },
    {
        "id": "sh10",
        "question": "How have US semiconductor export restrictions affected a major South Korean memory chip maker's outlook?",
        "reference_answer": "Samsung Electronics said weak demand for its memory chips would limit earnings growth in the current quarter, a problem made worse by US restrictions on supplying advanced AI-related semiconductors, even as it expected overall demand to recover later.",
        "gold_ids": ["1d401558-17a8-4734-89d7-a7e3a293d405"],
        "hop_type": "single",
    },
    {
        "id": "sh11",
        "question": "What unusual pattern does a data-centre operator's stock market debut illustrate about venture capital returns?",
        "reference_answer": "CoreWeave's IPO offers a twist on the venture-capital 'power law' concept, whereby a small number of investments generate most of a portfolio's returns; CoreWeave itself operates by renting out large numbers of Nvidia chips to AI companies rather than being an AI developer itself.",
        "gold_ids": ["9a0c9928-a5bc-4894-aff2-27b0312b3843"],
        "hop_type": "single",
    },
    {
        "id": "sh12",
        "question": "Why did shares of a Dutch chip-equipment maker rise despite a broader market panic over a Chinese AI breakthrough?",
        "reference_answer": "ASML's shares rose after it reported a surge in orders for its most advanced chipmaking machines, suggesting AI chip producers were expanding capacity even as DeepSeek's emergence had triggered a sell-off across chipmakers including Nvidia and Broadcom.",
        "gold_ids": ["a3a34274-f924-4199-a8bc-b3aa32c97f2a"],
        "hop_type": "single",
    },
    {
        "id": "sh13",
        "question": "How did Hong Kong-listed technology stocks perform in the weeks following a Chinese AI model's breakthrough?",
        "reference_answer": "The Hang Seng Tech index rose more than 20% in the month after DeepSeek's breakthrough, entering a bull market and outperforming both the Nasdaq 100 and the 'Magnificent Seven' US tech stocks as investors piled into Chinese internet companies.",
        "gold_ids": ["af0636d6-59af-453c-9d75-6f6a3d9f11ce"],
        "hop_type": "single",
    },
    {
        "id": "sh14",
        "question": "What did Tesla argue in court about the fee sought by the lawyers who successfully challenged Elon Musk's pay package?",
        "reference_answer": "Tesla argued that a proposed $5.2bn legal fee for the lawyers who won the challenge to Musk's pay package was excessive, amounting to the highest hourly rate in history, and said the lawyers should instead receive only $13.6mn.",
        "gold_ids": ["2a9bec67-c7aa-42ff-b14b-428785a89741"],
        "hop_type": "single",
    },
    {
        "id": "sh15",
        "question": "How did Tesla's vehicle deliveries in a given quarter compare with Wall Street's already-lowered forecasts?",
        "reference_answer": "Tesla delivered 435,059 vehicles in the quarter, falling short even of analysts' reduced expectations of 440,000-455,000, although the figure was still 27% higher than the same period a year earlier.",
        "gold_ids": ["333b4586-4def-4c13-9f18-05a1f5a8631c"],
        "hop_type": "single",
    },
    {
        "id": "sh16",
        "question": "Why is a Chinese electric vehicle maker expected to lose its position as the world's top-selling EV brand to Tesla?",
        "reference_answer": "BYD reported a 42% quarter-on-quarter fall in electric vehicle deliveries, selling around 300,114 battery-only vehicles amid weaker demand and increased competition, setting the stage for Tesla to reclaim the title of the world's largest battery-electric-vehicle seller.",
        "gold_ids": ["4f1a2188-ced0-4018-998d-5148209a5f5e"],
        "hop_type": "single",
    },
    {
        "id": "sh17",
        "question": "Why did Tesla take legal action against the European Union?",
        "reference_answer": "Tesla sued the EU over anti-subsidy tariffs the bloc imposed on electric vehicles imported from China, joining similar legal challenges from BMW and Chinese carmakers, after the EU set tariffs of up to 7.8% on Tesla and up to 35.3% on other Chinese-made EVs.",
        "gold_ids": ["178adfba-f197-4f66-a9cd-f0c04ae400b4"],
        "hop_type": "single",
    },
    {
        "id": "sh18",
        "question": "What is the main reason given for the recent decline in second-hand Tesla prices in the US and UK?",
        "reference_answer": "The drop in used Tesla prices in the US and Britain was attributed mainly to a glut of formerly leased vehicles entering the resale market, rather than to any reputational effect linked to Elon Musk, with US prices falling 7% and UK prices falling 15% year-on-year.",
        "gold_ids": ["07f90b17-6348-40f0-bd45-15e48b82b827"],
        "hop_type": "single",
    },
    {
        "id": "sh19",
        "question": "Why did Elon Musk say he would spend less time on his government role and more time running Tesla?",
        "reference_answer": "Musk said he would significantly scale back his US government role and refocus on Tesla after the carmaker's profits fell sharply in the first quarter, while still saying he would likely remain involved with the Doge cost-cutting effort until the end of the presidential term.",
        "gold_ids": ["5128df45-8595-41e5-84f1-695adba053a7"],
        "hop_type": "single",
    },
    {
        "id": "sh20",
        "question": "Which chipmaker was among the investors in a recent funding round for the AI infrastructure group that emerged from Yandex's non-Russian operations?",
        "reference_answer": "Nvidia was among the investors in a $700mn funding round for Nebius, the AI infrastructure company formed from Yandex's operations outside Russia, which raised the capital to meet growing demand for AI data centres shortly after its shares resumed trading on Nasdaq.",
        "gold_ids": ["6cedfaf6-b882-44e0-b785-116130ac5b5a"],
        "hop_type": "single",
    },
]

if __name__ == "__main__":
    ids_seen = [q["id"] for q in EVAL_DATASET_V2]
    assert len(ids_seen) == len(set(ids_seen)), "duplicate question ids"
    n_single = sum(1 for q in EVAL_DATASET_V2 if q["hop_type"] == "single")
    n_multi = sum(1 for q in EVAL_DATASET_V2 if q["hop_type"] == "multi")
    print(f"Total questions: {len(EVAL_DATASET_V2)} ({n_single} single-hop, {n_multi} multi-hop)")
    for q in EVAL_DATASET_V2:
        assert isinstance(q["gold_ids"], list) and len(q["gold_ids"]) >= 1
        if q["hop_type"] == "single":
            assert len(q["gold_ids"]) == 1
        else:
            assert len(q["gold_ids"]) >= 2
    print("All checks passed.")
