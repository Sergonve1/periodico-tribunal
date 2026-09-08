# app/kafka/eval_dataset.py
"""
Conjunto de evaluacion (gold) para el experimento RAG del TFG.

50 preguntas en ingles sobre articulos de la carpeta
"Artificial intelligence" del corpus. Cada pregunta tiene:
  - id: identificador de la pregunta
  - question: pregunta en ingles
  - reference_answer: respuesta de referencia (gold) en ingles,
    usada para calcular la similitud respuesta-referencia
  - gold_article_id: id del articulo (_id/id del JSON) que contiene
    la informacion necesaria para responder. Se asume |Rel(q)| = 1
    (un unico pasaje relevante por pregunta), por lo que:
      Recall@k(q) = 1 si gold_article_id esta en el top-k, si no 0
      Precision@k(q) = Recall@k(q) / k
      RR(q) = 1 / rank si esta en el top-k, si no 0
"""

EVAL_QUESTIONS = [
    {
        "id": "q01",
        "question": "How much did the Musk-led consortium offer for OpenAI's non-profit entity?",
        "reference_answer": "The Musk-led consortium offered $97.4 billion for OpenAI's non-profit entity.",
        "gold_article_id": "0491811a-4884-48f0-bd1e-255aaf5e9332",
    },
    {
        "id": "q02",
        "question": "Which carmaker has Wayve signed its first deal with, and from what year will it install its software?",
        "reference_answer": "Wayve signed its first carmaker deal with Nissan, and will install its software starting in 2027.",
        "gold_article_id": "14d012e3-6a47-455f-b533-57c8e2f08a16",
    },
    {
        "id": "q03",
        "question": "How much did Isomorphic Labs raise in its first external funding round?",
        "reference_answer": "Isomorphic Labs raised $600 million in its first external funding round.",
        "gold_article_id": "14d93672-dce7-482d-9b32-fa3553b37273",
    },
    {
        "id": "q04",
        "question": "For how much did SoftBank agree to acquire chip start-up Ampere Computing?",
        "reference_answer": "SoftBank agreed to acquire Ampere Computing for $6.5 billion.",
        "gold_article_id": "235a02b0-bbb1-4f2e-a181-57a3907f36e3",
    },
    {
        "id": "q05",
        "question": "Which organization warned UK ministers about AI content-scraping rules?",
        "reference_answer": "The Copyright Alliance warned UK ministers about AI content-scraping rules.",
        "gold_article_id": "25650c27-7723-4aa8-8c29-6bc5af47cf3b",
    },
    {
        "id": "q06",
        "question": "What valuation is OpenAI targeting in the SoftBank-led funding round?",
        "reference_answer": "OpenAI is targeting a valuation of $300 billion in the SoftBank-led funding round.",
        "gold_article_id": "2c697ff8-dfe9-4c42-a328-d21216293aa3",
    },
    {
        "id": "q07",
        "question": "What system does the UK propose to let AI companies use copyrighted material without prior permission?",
        "reference_answer": "The UK proposes a 'rights reservation' system, where rights holders must explicitly opt out.",
        "gold_article_id": "2ced1e1f-7d14-44d7-b188-464ddd69890d",
    },
    {
        "id": "q08",
        "question": "According to the CISAC study cited by Bjorn Ulvaeus, what share of musicians' revenues could be lost to generative AI by 2028?",
        "reference_answer": "About a fifth (20%) of musicians' revenues could be lost to generative AI by 2028.",
        "gold_article_id": "40b28a25-eddc-4ac5-82f3-dac0128a187f",
    },
    {
        "id": "q09",
        "question": "According to Demis Hassabis, when will Isomorphic Labs have an AI-designed drug in clinical trials?",
        "reference_answer": "Demis Hassabis said Isomorphic Labs will have an AI-designed drug in clinical trials by the end of this year.",
        "gold_article_id": "41b51d07-0754-4ffd-a8f9-737e1b1f0c2e",
    },
    {
        "id": "q10",
        "question": "What is the value of the deal between OpenAI and CoreWeave?",
        "reference_answer": "OpenAI struck a near-$12 billion, five-year deal with CoreWeave.",
        "gold_article_id": "4b52fdbb-ca8e-4208-bb99-f1e7f9313863",
    },
    {
        "id": "q11",
        "question": "How much have Lumen Technologies' shares gained amid the AI frenzy?",
        "reference_answer": "Lumen Technologies' shares have gained more than 700% amid the AI frenzy.",
        "gold_article_id": "4ba4b1d1-15f9-4a7e-bff2-e6277832fd74",
    },
    {
        "id": "q12",
        "question": "Which model did DeepSeek release, and which company released a new Qwen model at the same time?",
        "reference_answer": "DeepSeek released its improved V3 model, while Alibaba released a new model in its Qwen series.",
        "gold_article_id": "5192a8b1-a71e-409c-8edf-1fcccb9539ec",
    },
    {
        "id": "q13",
        "question": "Which DeepMind scientists did Mustafa Suleyman hire, and what feature were they responsible for?",
        "reference_answer": "Mustafa Suleyman hired Marco Tagliasacchi and Zalan Borsos, who were responsible for the 'Audio Overviews' feature in NotebookLM.",
        "gold_article_id": "51bb0496-59ab-4a75-a410-14c097104594",
    },
    {
        "id": "q14",
        "question": "What did the US federal court decide on Musk's request to immediately block OpenAI's conversion to a for-profit entity?",
        "reference_answer": "The US federal court denied Musk's request to immediately block OpenAI's conversion, though it expedited the broader trial to autumn.",
        "gold_article_id": "532931dd-e1c0-4f18-a8af-5777dd70a52d",
    },
    {
        "id": "q15",
        "question": "Which companies are joining xAI and Nvidia in the $30 billion AI infrastructure fund?",
        "reference_answer": "BlackRock, Microsoft and Abu Dhabi are joining xAI and Nvidia in the $30 billion AI infrastructure fund.",
        "gold_article_id": "53eeadd8-8fec-4f1b-991e-642e24959e02",
    },
    {
        "id": "q16",
        "question": "Which seven companies make up the 'Magnificent Seven' in BlackRock's AI investment chart?",
        "reference_answer": "The 'Magnificent Seven' are Alphabet, Amazon, Apple, Meta, Microsoft, Nvidia and Tesla.",
        "gold_article_id": "573cb3d1-219a-4ff4-9d67-524914e0e323",
    },
    {
        "id": "q17",
        "question": "How much does CoreWeave aim to raise in its IPO, and at what valuation?",
        "reference_answer": "CoreWeave aims to raise $4 billion in its IPO, at a valuation of more than $35 billion.",
        "gold_article_id": "579176c5-a769-4102-8010-3965c4b717a7",
    },
    {
        "id": "q18",
        "question": "What did Nvidia founder Jensen Huang call the next stage of AI unveiled at CES?",
        "reference_answer": "Jensen Huang called the next stage of AI unveiled at CES 'physical AI'.",
        "gold_article_id": "5b5b72ce-0236-4eba-9c51-480f6a6ed8c3",
    },
    {
        "id": "q19",
        "question": "How much did AI medical-scribe start-ups raise in 2024 compared with 2023?",
        "reference_answer": "AI medical-scribe start-ups raised $800 million in 2024, compared with $390 million in 2023.",
        "gold_article_id": "5c356658-6db4-47c1-940b-b2e3cf3a51f3",
    },
    {
        "id": "q20",
        "question": "What did the UK decide regarding the global AI safety accord?",
        "reference_answer": "The UK declined to sign the global AI safety accord.",
        "gold_article_id": "5cb480f1-caeb-4fcf-b598-bc9e6518ebb5",
    },
    {
        "id": "q21",
        "question": "How much per month did the care UnitedHealth stopped reimbursing cost Gene Lokken's family?",
        "reference_answer": "The care UnitedHealth stopped reimbursing cost Gene Lokken's family more than $12,000 a month.",
        "gold_article_id": "600e53b6-963b-4c62-9548-b2b98788a950",
    },
    {
        "id": "q22",
        "question": "Which past technology bet by Masayoshi Son is cited as a costly flop?",
        "reference_answer": "WeWork is cited as a costly flop among Masayoshi Son's past technology bets.",
        "gold_article_id": "6112eabc-ae2c-486c-8934-a5bdf665f61c",
    },
    {
        "id": "q23",
        "question": "What tasks did Google DeepMind's robot demonstrate in its recent videos?",
        "reference_answer": "Google DeepMind's robot demonstrated folding an origami fox, organising a desk and slam-dunking a small basketball.",
        "gold_article_id": "62b89c94-e5be-4093-97a5-d934c153662b",
    },
    {
        "id": "q24",
        "question": "Which survey ranked AI disinformation as the second most pressing risk of 2024?",
        "reference_answer": "A World Economic Forum survey of experts ranked AI disinformation as the second most pressing risk of 2024.",
        "gold_article_id": "62d81e6c-eec0-4d09-a71f-6aba579912dd",
    },
    {
        "id": "q25",
        "question": "Who is the UK National Audit Office head calling on the public sector to embrace risk-taking with AI?",
        "reference_answer": "Gareth Davies, the UK National Audit Office head, is calling on the public sector to embrace risk-taking with AI.",
        "gold_article_id": "5299582a-4a27-44ea-aec7-be2b3124e7b8",
    },
    {
        "id": "q26",
        "question": "Who did Nvidia CEO Jensen Huang meet for the first time at the White House?",
        "reference_answer": "Nvidia CEO Jensen Huang met US President Donald Trump for the first time at the White House.",
        "gold_article_id": "65e9c766-9ff7-4ff8-bff1-2c1c05c9d802",
    },
    {
        "id": "q27",
        "question": "Which US state's legislators advanced a bill to address data centres' water use?",
        "reference_answer": "Virginia state legislators advanced a bill to address data centres' water use.",
        "gold_article_id": "65fff689-bd47-4c15-bdb8-083e5ccd84dc",
    },
    {
        "id": "q28",
        "question": "Which book won the FT and Schroders Business Book of the Year Award, and how much was the prize?",
        "reference_answer": "'Supremacy' by Parmy Olson won the FT and Schroders Business Book of the Year Award, with a prize of £30,000.",
        "gold_article_id": "66753879-fcb9-4baf-a1d7-7790439255f2",
    },
    {
        "id": "q29",
        "question": "Which company's AI chatbot reprimanded a customer for using the word 'virgin'?",
        "reference_answer": "Virgin Money's AI-powered chatbot reprimanded a customer for using the word 'virgin'.",
        "gold_article_id": "670f5896-1fe5-4a31-b41f-ad4f5b91202f",
    },
    {
        "id": "q30",
        "question": "What is Meta's new internal AI tool called, and what large language model is it built on?",
        "reference_answer": "Meta's new internal AI tool is called Metamate, and it is built on Meta's large language model, Llama.",
        "gold_article_id": "68828793-2978-4fc7-9f00-df2ca4e8b2b0",
    },
    {
        "id": "q31",
        "question": "How much has TSMC pledged to spend on advanced manufacturing plants in the US?",
        "reference_answer": "TSMC has pledged to spend an extra $100 billion on advanced manufacturing plants in the US.",
        "gold_article_id": "68a0da9b-ffc7-4c67-8249-d7c452efa864",
    },
    {
        "id": "q32",
        "question": "Which three leading academics joined former OpenAI staff in urging authorities to block OpenAI's for-profit restructuring?",
        "reference_answer": "Geoffrey Hinton, Margaret Mitchell and Stuart Russell joined former OpenAI staff in urging authorities to block the restructuring.",
        "gold_article_id": "6b8e7eb5-d300-4c1f-8915-686d7449cae4",
    },
    {
        "id": "q33",
        "question": "How much does Norway's oil fund expect to save annually in trading costs by using AI?",
        "reference_answer": "Norway's oil fund expects to save $400 million a year in trading costs by using AI.",
        "gold_article_id": "6cda7685-40f7-493a-9d24-8355083c8ecd",
    },
    {
        "id": "q34",
        "question": "How much did Nebius raise from investors including Nvidia?",
        "reference_answer": "Nebius raised $700 million from investors including Nvidia.",
        "gold_article_id": "6cedfaf6-b882-44e0-b785-116130ac5b5a",
    },
    {
        "id": "q35",
        "question": "Which California governor vetoed the state's AI safety bill?",
        "reference_answer": "California governor Gavin Newsom vetoed the state's AI safety bill.",
        "gold_article_id": "6e460960-9530-40ac-8346-cd25b94f8f32",
    },
    {
        "id": "q36",
        "question": "What is the name of Google's AI tool designed to help scientists accelerate biomedical research?",
        "reference_answer": "Google's AI tool for accelerating biomedical research is called the 'co-scientist' tool.",
        "gold_article_id": "6e53cc55-9031-4ba4-9e7c-e5e9c02b3203",
    },
    {
        "id": "q37",
        "question": "What is the name of the AI weather prediction model that aims to democratise forecasting via desktop computers?",
        "reference_answer": "The model is called Aardvark, and the project is led by the UK's Alan Turing Institute.",
        "gold_article_id": "73492128-5822-4bb2-b953-64217eb303e4",
    },
    {
        "id": "q38",
        "question": "Who is the UK technology secretary urging critics of the AI copyright proposal not to 'resist change'?",
        "reference_answer": "UK technology secretary Peter Kyle urged critics of the AI copyright proposal not to 'resist change'.",
        "gold_article_id": "7366eef2-8ae4-4d8f-8c4e-9adbd641c183",
    },
    {
        "id": "q39",
        "question": "For how much did Elon Musk's xAI buy the social media platform X?",
        "reference_answer": "Elon Musk's xAI bought X for $45 billion, in an all-stock deal valuing xAI at $80 billion.",
        "gold_article_id": "74194702-29f0-407b-89a1-c5a4058d934e",
    },
    {
        "id": "q40",
        "question": "How much did Ilya Sutskever raise for his start-up Safe Superintelligence, and at what valuation?",
        "reference_answer": "Ilya Sutskever raised $2 billion for Safe Superintelligence, valuing the company at $32 billion.",
        "gold_article_id": "792e09b2-f63b-41ac-8be8-e10e75ead2d1",
    },
    {
        "id": "q41",
        "question": "How much of a charge did Nvidia reveal related to new US export controls on chip sales to China?",
        "reference_answer": "Nvidia revealed a $5.5 billion charge related to the new US export controls on chip sales to China.",
        "gold_article_id": "7935826a-ba3b-4f6b-a64d-b8167d5dc38e",
    },
    {
        "id": "q42",
        "question": "Who pledged that the UK will legislate against AI risks in the next year?",
        "reference_answer": "UK technology secretary Peter Kyle pledged that the UK will legislate against AI risks in the next year.",
        "gold_article_id": "79fedc1c-579d-4b23-8404-e4cb9e7bbae3",
    },
    {
        "id": "q43",
        "question": "Which organisation is pushing a shareholder motion against Apple's diversity policies?",
        "reference_answer": "The National Center for Public Policy Research is pushing the shareholder motion against Apple's diversity policies.",
        "gold_article_id": "7fa6081c-98da-4103-bc23-0597bea2acda",
    },
    {
        "id": "q44",
        "question": "Which new coding-focused models did OpenAI release, according to the article?",
        "reference_answer": "OpenAI released the GPT-4.1, o3 and o4-mini models, aimed at computer programming.",
        "gold_article_id": "8069b127-8589-4f06-9c38-8e0216c6fd9c",
    },
    {
        "id": "q45",
        "question": "How many years in prison was Hugh Nelson sentenced to for using AI to create child sexual abuse imagery?",
        "reference_answer": "Hugh Nelson was sentenced to 18 years in prison.",
        "gold_article_id": "81060e76-994d-4635-af02-637504c69532",
    },
    {
        "id": "q46",
        "question": "According to the Higher Education Policy Institute survey, what percentage of UK undergraduates used generative AI this year, compared with last year?",
        "reference_answer": "92% of UK undergraduates used generative AI this year, up from 66% last year.",
        "gold_article_id": "82d59679-0985-4c07-9416-06a0bec6e16a",
    },
    {
        "id": "q47",
        "question": "Which venues did MSG Entertainment use facial recognition technology to bar lawyers from?",
        "reference_answer": "MSG Entertainment used facial recognition to bar lawyers from Madison Square Garden and Radio City Music Hall.",
        "gold_article_id": "733f040e-3e44-4cd7-b719-bf6f1f4cc27b",
    },
    {
        "id": "q48",
        "question": "What is the ticker symbol of Tuttle Capital's 'alien tech' AI-powered ETF?",
        "reference_answer": "The ticker symbol of Tuttle Capital's AI-powered UFO Disclosure ETF is UFOD.",
        "gold_article_id": "7b83f0f5-4d03-40c4-b79d-36cc4e247d54",
    },
    {
        "id": "q49",
        "question": "According to the letter about AI and power consumption, how many watts does the human brain consume, and how much power would simulating an entire 86-billion-neuron brain require?",
        "reference_answer": "The human brain consumes about 20 watts, while simulating an entire 86-billion-neuron brain would require on the order of 10 megawatts.",
        "gold_article_id": "00c035fc-2b74-41ee-ad41-8b04c08b3b22",
    },
    {
        "id": "q50",
        "question": "According to John Thornhill's column, what loss and revenue did OpenAI report for last year?",
        "reference_answer": "OpenAI reported a loss of about $5 billion on revenue of $3.7 billion last year.",
        "gold_article_id": "557479b5-2513-441d-85c4-8acbc398e4b4",
    },
]
