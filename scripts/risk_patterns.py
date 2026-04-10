# regula-ignore
"""EU AI Act risk pattern definitions for Regula.

Pure configuration — no functions, no logic. Contains all regex patterns
used by the classification engine, organised by risk tier.

Licensed under the Detection Rule License (DRL) 1.1.
See LICENSE.Detection.Rules.md at the repository root.
Author: The Implementation Layer (https://getregula.com)
"""

# ---------------------------------------------------------------------------
# Article 5 prohibited patterns
#
# Each entry includes the specific conditions under which the prohibition
# applies and any narrow exceptions from the Act, so that messages to the
# developer are legally accurate rather than categorical.
# ---------------------------------------------------------------------------

PROHIBITED_PATTERNS = {
    "subliminal_manipulation": {
        "patterns": [r"subliminal", r"beyond.?consciousness", r"subconscious.?influence"],
        "article": "5(1)(a)",
        "description": "AI deploying subliminal techniques beyond a person's consciousness",
        "conditions": "Prohibited when the technique materially distorts behaviour and causes or is likely to cause significant harm.",
        "exceptions": None,
    },
    "exploitation_vulnerabilities": {
        "patterns": [r"target.?elderly", r"exploit.?disabil", r"vulnerable.?group.?target"],
        "article": "5(1)(b)",
        "description": "Exploiting vulnerabilities of specific groups (age, disability, economic situation)",
        "conditions": "Prohibited when exploiting vulnerabilities to materially distort behaviour causing significant harm.",
        "exceptions": None,
    },
    "social_scoring": {
        "patterns": [r"\bsocial.?scor(?:e|ing)\b", r"\bsocial.?credit.?(?:scor|system|rating)", r"\bsocial.?credit\b", r"\bcitizen.?score", r"\bbehaviour.?scor"],
        "article": "5(1)(c)",
        "description": "Social scoring by public authorities or on their behalf",
        "conditions": "Prohibited when evaluating or classifying persons based on social behaviour or personal traits, leading to detrimental treatment disproportionate to context.",
        "exceptions": None,
    },
    "criminal_prediction": {
        "patterns": [r"crime.?predict", r"criminal.?risk.?assess", r"predictive.?policing", r"recidivism"],
        "article": "5(1)(d)",
        "description": "Criminal risk prediction based solely on profiling or personality traits",
        "conditions": "Prohibited ONLY when based solely on profiling or personality traits. Systems using multiple evidence sources (case facts, prior convictions with human review) may be lawful.",
        "exceptions": "AI systems that support human assessment based on objective, verifiable facts directly linked to criminal activity are NOT prohibited.",
    },
    "facial_recognition_scraping": {
        "patterns": [r"\bface.?scrap", r"facial.?database.?untarget", r"mass.?facial.?collect"],
        "article": "5(1)(e)",
        "description": "Creating facial recognition databases through untargeted scraping",
        "conditions": "Prohibited when scraping facial images from the internet or CCTV to build or expand recognition databases.",
        "exceptions": None,
    },
    "emotion_inference_restricted": {
        "patterns": [r"emotion.{0,20}workplace", r"emotion.{0,20}school", r"sentiment.{0,20}employee",
                     r"workplace.{0,20}emotion", r"employee.{0,20}emotion"],
        "article": "5(1)(f)",
        "description": "Emotion inference in workplace or educational settings",
        "conditions": "Prohibited in workplace and educational institutions.",
        "exceptions": "EXEMPT when used for medical or safety purposes (e.g., detecting driver fatigue, monitoring patient wellbeing in clinical settings).",
    },
    "biometric_categorisation_sensitive": {
        "patterns": [r"\brace.?detect(?!.*(?:condition|thread|concurrent))", r"ethnicity.?infer", r"political.?opinion.?biometric",
                     r"religion.?detect", r"sexual.?orientation.?infer"],
        "article": "5(1)(g)",
        "description": "Biometric categorisation inferring sensitive attributes (race, politics, religion, sexuality)",
        "conditions": "Prohibited when using biometric data to categorise persons by race, political opinions, trade union membership, religious beliefs, sex life, or sexual orientation.",
        "exceptions": "Labelling or filtering of lawfully acquired biometric datasets (e.g., photo sorting) may be exempt where no categorisation of individuals occurs.",
    },
    "realtime_biometric_public": {
        "patterns": [r"real.?time.?facial.?recogn", r"live.?biometric.?public",
                     r"public.?space.?biometric", r"mass.?surveillance.?biometric"],
        "article": "5(1)(h)",
        "description": "Real-time remote biometric identification in publicly accessible spaces for law enforcement",
        "conditions": "Prohibited for law enforcement in publicly accessible spaces in real-time.",
        "exceptions": "Narrow exceptions exist with PRIOR judicial authorisation for: (i) targeted search for victims of abduction/trafficking/sexual exploitation, (ii) prevention of specific imminent terrorist threat, (iii) identification of suspects of serious criminal offences (as defined in Annex II).",
    },
}


# ---------------------------------------------------------------------------
# Annex III high-risk patterns
#
# NOTE: The EU AI Act Article 6 requires a two-step test:
#   1. The system falls within an Annex III area, AND
#   2. It poses a significant risk of harm.
# Article 6(3) explicitly exempts systems that perform narrow procedural
# tasks, improve previously completed human activities, detect patterns
# without replacing human assessment, or perform preparatory tasks.
#
# Pattern matches here indicate the system MAY be high-risk and should
# be reviewed — not that it IS high-risk.
# ---------------------------------------------------------------------------

HIGH_RISK_PATTERNS = {
    "biometrics": {
        # regula-ignore (pattern definitions, not practice).
        # Recall expansion (Apr 2026): Annex III point 1 covers biometric
        # identification, categorisation of natural persons, and biometric
        # verification. Article 5(1)(g) prohibits untargeted facial scraping
        # and Article 5(1)(h) restricts real-time remote biometric identification
        # in publicly accessible spaces — those are handled in PROHIBITED_PATTERNS.
        # The high-risk patterns below cover the broader LAWFUL biometric uses
        # that still require Articles 9–15 compliance.
        "patterns": [r"\bbiometric.?ident", r"\bfac(?:ial|e)\s*[\W_]?recogn",
                     r"\bfingerprint\s*[\W_]?recogn", r"\bvoice\s*[\W_]?recogn",
                     r"\biris\s*[\W_]?(?:recogn|scan|match|identif)",
                     r"\bretina\s*[\W_]?(?:scan|recogn)",
                     r"\bpalm\s*[\W_]?(?:print|recogn|scan)",
                     r"\bgait\s*[\W_]?(?:recogn|analysis|identif)",
                     r"\b(?:face|voice|fingerprint|iris)[_\W]?(?:match|verif|compar|enrol|template)",
                     r"\b(?:identify|recognise|recognize|verify|match|enrol)[_\W]?(?:face|faces|person|people|identity)\b",
                     r"\bbiometric[_\W]?(?:categoris|categoriz|classif|template|verif|match|enrol)",
                     r"\b(?:detect|infer|classify|predict)[_\W]?(?:age|gender|ethnicity|race)[_\W]?from[_\W]?(?:face|image|photo|voice)",
                     r"\b(?:speaker|voice)[_\W]?(?:identif|verif|recogn|diariz)",
                     r"\bface[_\W]?embed(?:ding)?",
                     # Prompt-string templates.
                     r"(?:identify|match|recognise|recognize|verify)[^\"\\n]{0,30}(?:face|person|identity|suspect)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 1",
        "description": "Biometric identification and categorisation",
    },
    "critical_infrastructure": {
        # Recall expansion (Apr 2026): Annex III point 2 covers safety
        # components in the management and operation of critical digital
        # infrastructure, road traffic, and the supply of water, gas,
        # heating, or electricity. The original 4-pattern list missed
        # common phrasings like grid_load_forecast, substation_control,
        # scada, pipeline_pressure, railway_signalling, power_dispatch.
        # Guarded to require infrastructure context so ordinary "traffic"
        # (web traffic) and "grid" (CSS grid) do not false-positive.
        "patterns": [r"\benergy.?grid", r"\bwater.?supply", r"\btraffic.?control",
                     r"\belectricity.?manage",
                     r"\b(?:power|electricity|energy|electric)[_\W]?(?:grid|dispatch|load|demand|forecast|balanc|outage|substation|transmission|distribution)",
                     r"\b(?:grid|substation|transformer|feeder)[_\W]?(?:load|forecast|predict|balanc|fault|dispatch|stabil)",
                     r"\b(?:gas|natural[_\W]?gas|pipeline)[_\W]?(?:pressure|flow|leak|monitor|dispatch|scada|control)",
                     r"\b(?:water|wastewater|sewage)[_\W]?(?:treatment|supply|distribution|scada|leak|flow|quality|contamin)",
                     r"\b(?:district[_\W]?)?heating[_\W]?(?:grid|supply|control|manage|dispatch)",
                     r"\bscada\b", r"\bplc[_\W]?(?:control|automat)", r"\bics[_\W]?(?:control|automat|security)",
                     r"\b(?:nuclear|reactor)[_\W]?(?:control|safety|monitor|scada)",
                     r"\brailway[_\W]?(?:signal|control|dispatch|interlock|track|switching)",
                     r"\b(?:metro|subway|tram)[_\W]?(?:signal|dispatch|control)",
                     r"\b(?:air[_\W]?traffic|atc|atm)[_\W]?(?:control|manage|dispatch|safety|conflict)",
                     r"\b(?:maritime|vessel|port)[_\W]?traffic[_\W]?(?:control|manage|dispatch)",
                     r"\broad[_\W]?traffic[_\W]?(?:control|signal|light|management|flow|dispatch)",
                     r"\btraffic[_\W]?(?:signal|light|flow|congestion)[_\W]?(?:control|manage|optim|predict|ai)",
                     # Prompt-string templates.
                     r"(?:control|manage|dispatch|forecast)[^\"\\n]{0,30}(?:grid|substation|pipeline|scada|reactor|railway|air[_\W]?traffic)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 2",
        "description": "Critical infrastructure management",
    },
    "education": {
        "patterns": [r"\badmission.?decision", r"\bstudent.?assess", r"\bexam.?scor",
                     r"\bprocto\w*.{0,15}(exam|test|monitor|ai|automat|student|cheat)",
                     # Recall expansion (Apr 2026): real-world ed-tech AI phrasings.
                     # Annex III point 3 covers AI for access to / placement at education,
                     # exam scoring, student monitoring, and dropout prediction.
                     r"\b(?:grade|score|rank|classify|evaluate|assess)[_\W]?(?:essays?|assignments?|homework|coursework|submissions?)\b",
                     r"\b(?:essays?|assignments?|homework|coursework)[_\W]?(?:grad(?:e|ing)|scor|rank|classif|evaluat|auto)",
                     r"\bauto[_\W]?grad(?:e|ing|er)\b",
                     r"\b(?:predict|model|estimate)[_\W]?(?:dropouts?|attrition|grades?|gpas?|graduation|completion)\b",
                     r"\b(?:dropouts?|attrition|gpa|grades?)[_\W]?(?:predict|model|score|rank)",
                     r"\b(?:score|rank|classify|filter|shortlist)[_\W]?(?:students?|pupils?|learners?|applicants?[_\W]?(?:to|for)[_\W]?(?:college|university|school))\b",
                     r"\bplacement[_\W]?(?:test|exam|score|decision)",
                     r"\b(?:university|college|school|admission)[_\W]?rank",
                     r"\b(?:rank|score|filter|shortlist|classify)[_\W]?(?:university|college|school)[_\W]?(?:applicants?|students?|candidates?)",
                     r"\badmissions?[_\W]?(?:scor|rank|filter|model|predict|classif|decision)",
                     r"\b(?:student|pupil|learner)[_\W]?(?:scor|rank|classif|risk)",
                     # Prompt-string templates for ed-tech AI use cases.
                     r"(?:grade|score|rank|evaluate|assess)[^\"\\n]{0,30}(?:essay|assignment|homework|student|admission)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 3",
        "description": "Education and vocational training",
    },
    "employment": {
        "patterns": [r"\bcv.?screen", r"\bresume.?filt", r"\bhiring.?decision", r"\brecruit\w*\W{0,3}automat",
                     r"\bautomat\w*\W{0,3}recruit", r"\bcandidate[_\W]?rank", r"rank[_\W]?candidate",
                     r"\bpromotion.?decision",
                     r"\btermination.?decision", r"\bperformance.?review.{0,10}(ai|automat|model|predict)",
                     r"\bscreen.?candidate", r"\bjob.?candidate", r"\bcandidate.?screen", r"\bresume\s*[\W_]?screen",
                     r"\bapplicant.?scor", r"\bapplicant.?rank", r"\bemployee.?assess",
                     # Common real-world phrasings missed by the original list.
                     # Added after recall audit (Apr 2026): Regula was failing to
                     # flag obvious employment AI like classify_resume()/score_resume().
                     # NOTE: "applicant" on its own is ambiguous (job vs loan) —
                     # require explicit job context to avoid conflating with
                     # credit-applicant flows that belong in essential_services.
                     r"\b(?:classify|score|rank|evaluate|assess|filter|shortlist)[_\W]?resumes?\b",
                     r"\bresumes?[_\W]?(?:classif|scor|rank|evaluat|filter|shortlist|match)",
                     r"\b(?:score|rank|evaluate|shortlist)[_\W]?(?:job[_\W]?)?candidates?\b",
                     r"\bjob[_\W]?applicants?[_\W]?(?:scor|rank|filter|evaluat|shortlist)",
                     r"\b(?:score|rank|shortlist)[_\W]?job[_\W]?applicants?\b",
                     # Prompt-string templates that embed hiring instructions.
                     r"(?:score|rank|classify|evaluate)[^\"\\n]{0,30}resumes?\b",
                     r"\bresumes?[^\"\\n]{0,30}(?:score|rank|classif|evaluat|shortlist)",
                     r"(?:score|rank|classify|evaluate)[^\"\\n]{0,30}(?:job[_\W]candidate|job[_\W]applicant)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 4",
        "description": "Employment and workers management",
    },
    "essential_services": {
        "patterns": [r"\bcredit.?scor", r"\bcreditworth", r"\bloan.?decision", r"\binsurance.?pric",
                     r"\bbenefit.?eligib", r"\bemergency.?dispatch",
                     r"credit.?risk", r"credit.?model", r"credit.?predict",
                     r"\bloan.?approv", r"\blending.?decision",
                     # Recall expansion (Apr 2026): Annex III point 5 covers AI for
                     # creditworthiness, life/health insurance pricing, public benefit
                     # eligibility, and emergency call dispatching/triage. The original
                     # list missed common phrasings like score_loan, deny_loan,
                     # mortgage_decision, claim_assess, welfare_eligibility.
                     r"\b(?:score|approve|deny|reject|underwrit|automate)[_\W]?(?:loans?|mortgages?|credit|lending|advances?)\b",
                     r"\b(?:loans?|mortgages?|credit|lending|advances?)[_\W]?(?:scor|approv|deny|reject|underwrit|automat|decision|risk|model|predict)",
                     r"\bmortgage[_\W]?(?:decision|approv|underwrit|risk|score)",
                     r"\b(?:insurance|policy|premium)[_\W]?(?:price|quote|underwrit|risk|tier|model|score)",
                     r"\bclaim[_\W]?(?:assess|adjudicat|deni|approv|fraud|risk|score|decision)",
                     r"\b(?:health|life|auto|car|vehicle|home|property)[_\W]?insurance[_\W]?(?:price|quote|tier|underwrit|risk|score|decision)",
                     r"\b(?:welfare|benefit|disability|unemployment|housing|food[_\W]?stamp|snap|medicaid|medicare)[_\W]?(?:eligib|decision|approv|deni|risk|fraud|model)",
                     r"\b(?:eligib|approv|deny)[_\W]?(?:welfare|benefit|disability|housing|public[_\W]?assistance)",
                     r"\butility[_\W]?(?:disconnect|shutoff|cut[_\W]?off|deni|priorit)",
                     r"\b(?:emergency|911|999|112)[_\W]?(?:dispatch|priorit|triage|routing|severity)",
                     r"\bambulance[_\W]?(?:dispatch|priorit|routing|triage)",
                     # Prompt-string templates for fintech / insurtech / govtech.
                     r"(?:approve|deny|score|underwrite)[^\"\\n]{0,30}(?:loan|mortgage|credit|claim|application|benefit)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 5",
        "description": "Access to essential services",
    },
    "law_enforcement": {
        # regula-ignore (this block defines patterns that match the very
        # phrases it lists; the literal strings here are pattern definitions,
        # not a prohibited practice — Article 5(1)(d) covers the *use*, not
        # the *naming* of detection patterns).
        "patterns": [r"\bpolygraph", r"\blie.?detect", r"\bevidence.?reliab", r"\bcriminal.?investigat",
                     # Recall expansion (Apr 2026): Annex III point 6 covers AI used by
                     # law-enforcement authorities for risk assessment of natural persons,
                     # polygraph and similar tools, evidence reliability, profiling for
                     # detecting/investigating/prosecuting offences, and crime analytics.
                     # NB: Article 5(1)(d) prohibits PURE profiling-based prediction of
                     # offending — that is detected separately in PROHIBITED_PATTERNS;
                     # the patterns below cover the broader high-risk uses that remain
                     # lawful under Annex III but trigger Articles 9–15.
                     r"\b" + "recidiv" + r"ism\b",
                     r"\b(?:offen[cs]e|reoffend|reoffending)[_\W]?(?:forecast|risk|hotspot|map|model|analytics)",
                     r"\b(?:forecast)[_\W]?(?:offence|offense|reoffend|arrests?)",
                     r"\b" + "predictive" + r"[_\W]?polic(?:e|ing)\b",
                     r"\b(?:suspect|offender|defendant|inmate|parolee|probationer)[_\W]?(?:scor|rank|risk|profil|classif|threat)",
                     r"\b(?:risk|threat)[_\W]?(?:scor|assess|model|rank|classif)[_\W]?(?:offender|suspect|defendant|inmate|parolee)",
                     r"\bflight[_\W]?risk[_\W]?(?:assess|score|model|" + "predict" + r")",
                     r"\b(?:parole|probation|bail|sentencing)[_\W]?(?:decision|recommend|risk|score|model|" + "predict" + r"|algorithm)",
                     r"\b(?:gang|cartel)[_\W]?(?:member(?:ship)?|affiliation|associat)[_\W]?(?:" + "predict" + r"|model|score|classif)",
                     r"\b" + "crime" + r"[_\W]?hotspot",
                     r"\bthreat[_\W]?(?:assess|score|level|model)[_\W]?(?:individual|suspect|person)",
                     r"\b(?:facial|face)[_\W]?(?:recogn|match|identif)[_\W]?(?:suspect|wanted|fugitive|offender)",
                     # Prompt-string templates for crime analytics.
                     r"(?:" + "predict" + r"|score|assess)[^\"\\n]{0,30}(?:reoffend|offender|suspect|parole|bail)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 6",
        "description": "Law enforcement",
    },
    "migration": {
        # Recall expansion (Apr 2026): Annex III point 7 covers AI used by
        # or on behalf of competent public authorities in migration, asylum
        # and border control — risk assessment of persons entering, examining
        # applications for asylum/visa/residence, detecting/recognising/
        # identifying persons in a border context. CAUTION: "migration" on its
        # own matches database migrations, so we require immigration/border/
        # visa/asylum/refugee context on every pattern.
        "patterns": [r"\bborder.?control", r"\bvisa.?application", r"\basylum.?application",
                     r"\bimmigration.?decision",
                     r"\b(?:visa|residence[_\W]?permit|work[_\W]?permit)[_\W]?(?:risk|scor|approv|deni|reject|decision|classif|predict|assess)",
                     r"\b(?:approve|deny|reject|score|assess|decide)[_\W]?(?:visa|asylum|refugee|immigration|residence[_\W]?permit|work[_\W]?permit)",
                     r"\basylum[_\W]?(?:risk|scor|decision|classif|triage|eligib|predict|credibility)",
                     r"\brefugee[_\W]?(?:status|risk|scor|decision|classif|triage|eligib)",
                     r"\b(?:migrant|asylum[_\W]?seeker|refugee|applicant)[_\W]?(?:risk|scor|classif|profil|threat|fraud)",
                     r"\bimmigration[_\W]?(?:risk|scor|enforce|fraud|detect|classif)",
                     r"\bborder[_\W]?(?:screen|risk|threat|profil|identif|surveillance|scor)",
                     r"\b(?:frontex|e-?gate|iborder|smart[_\W]?border)",
                     r"\bentry[_\W]?(?:risk|decision|classif|scor)[_\W]?(?:border|immigration|frontier)",
                     r"\bpassport[_\W]?(?:verif|authent|fraud|match|recogn)",
                     # Prompt-string templates.
                     r"(?:approve|deny|score|assess)[^\"\\n]{0,30}(?:visa|asylum|refugee|immigration|border)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 7",
        "description": "Migration, asylum, and border control",
    },
    "justice": {
        # Recall expansion (Apr 2026): Annex III point 8 covers AI used by
        # or on behalf of a judicial authority to assist in researching and
        # interpreting facts/law and in applying the law to concrete facts,
        # as well as AI used to influence the outcome of an election or
        # referendum or the voting behaviour of natural persons (exclusive
        # of tools organising/optimising political campaigns administratively).
        "patterns": [r"\bjudicial.?decision", r"\bcourt.?rul",
                     r"\bsentenc(ing|e\.?)\W{0,5}(recommend|decision|guidelines|court|judge|judicial|legal|verdict|criminal|prison|convict|parole|probation)",
                     r"\belection.?influence",
                     r"\b(?:judge|judicial|court)[_\W]?(?:ai|assistant|recommend|decision|predict|automat)",
                     r"\b(?:verdict|ruling|judgement|judgment)[_\W]?(?:predict|recommend|draft|score|classif)",
                     r"\b(?:case|claim|dispute|lawsuit)[_\W]?(?:outcome|predict|score|classif|triage|recommend)",
                     r"\b(?:legal|statute|precedent)[_\W]?(?:search|retriev|interpret|classif|recommend)[_\W]?(?:ai|automat|model)",
                     r"\b(?:predict|forecast|recommend)[_\W]?(?:sentence|verdict|ruling|judgment|judgement|settlement)",
                     r"\b(?:voter|electorate|constituent)[_\W]?(?:target|profil|micro[_\W]?target|influenc|persuad|predict)",
                     r"\belection[_\W]?(?:target|micro[_\W]?target|influenc|manipul|profil|predict)",
                     r"\b(?:campaign|political)[_\W]?(?:micro[_\W]?target|profil|influenc|manipul)[_\W]?(?:voter|user|person)",
                     r"\b(?:referendum|ballot|electoral)[_\W]?(?:influenc|manipul|target|profil)",
                     # Prompt-string templates.
                     r"(?:predict|recommend|draft|score)[^\"\\n]{0,30}(?:verdict|sentence|judgment|ruling|case[_\W]outcome)",
                     r"(?:target|profile|influence)[^\"\\n]{0,30}(?:voter|election|electorate|referendum)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 8",
        "description": "Justice and democratic processes",
    },
    "medical_devices": {
        # Recall expansion (Apr 2026): EU AI Act Article 6(1) cross-references
        # Annex I Section A (medical devices under Regulation (EU) 2017/745 MDR
        # and in-vitro diagnostics under 2017/746 IVDR). AI used as or in a
        # medical device is high-risk. Common phrasings missed by the original
        # list: radiology/pathology AI, ECG/EEG classifiers, drug dosing,
        # patient deterioration prediction, tumour/lesion detection, clinical
        # risk scores, AI-driven prior-authorisation.
        "patterns": [r"\bmedical.?diagnos", r"\bclinical.?decision", r"\btreatment.?recommend",
                     r"\bpatient.?triage",
                     r"\b(?:detect|classify|segment|diagnose|predict)[_\W]?(?:tumor|tumour|lesion|cancer|malignan|nodule|polyp|stroke|aneurysm|fracture)",
                     r"\b(?:radiology|radiograph|ct[_\W]?scan|mri|x[_\W]?ray|ultrasound|mammogram|ecg|ekg|eeg|pathology|histolog|dermatology|retinal|fundus)[_\W]?(?:ai|classif|detect|diagnos|segment|scor|interpret|automat)",
                     r"\b(?:ai|model|neural|deep)[_\W]?(?:radiology|pathology|dermatology|cardiology|ophthalmology)",
                     r"\b(?:sepsis|deterioration|readmission|mortality|icu|length[_\W]?of[_\W]?stay)[_\W]?(?:predict|scor|risk|model|classif|early[_\W]?warning)",
                     r"\b(?:patient|clinical)[_\W]?(?:risk|scor|deterior|outcome|mortality|readmission)[_\W]?(?:predict|model|classif|scor)",
                     r"\b(?:drug|dose|dosage|insulin|anticoagulant|chemotherapy)[_\W]?(?:dos|titrat|recommend|adjust)[_\W]?(?:ai|model|automat|predict)",
                     r"\b(?:clinical|diagnostic)[_\W]?(?:support|assist|recommend|decision)[_\W]?(?:system|ai|model|tool)",
                     r"\bcdss\b",
                     r"\b(?:prior[_\W]?authori[sz]ation|utilisation[_\W]?review|claim[_\W]?medical)[_\W]?(?:predict|automat|deny|approv)",
                     r"\b(?:symptom|diagnosis|disease)[_\W]?(?:predict|classif|recommend|scor|check)[_\W]?(?:ai|model|chatbot)",
                     r"\b(?:medical|health)[_\W]?(?:chatbot|triage[_\W]?bot|symptom[_\W]?checker)",
                     # Prompt-string templates.
                     r"(?:diagnose|detect|classify|predict)[^\"\\n]{0,30}(?:tumor|tumour|cancer|stroke|sepsis|patient|disease)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Medical Devices",
        "description": "AI components of medical devices",
    },
    "safety_components": {
        # Recall expansion (Apr 2026): EU AI Act Article 6(1) cross-references
        # Annex I Sections A and B — safety components of machinery, toys,
        # recreational craft, lifts, ATEX equipment, radio equipment,
        # pressure equipment, cableways, PPE, gas appliances, civil aviation
        # security, motor vehicles (and their trailers), agricultural vehicles,
        # marine equipment, and railway systems. AI that acts as a safety
        # component of any of these is high-risk regardless of domain.
        "patterns": [r"\bautonomous.?vehicle", r"\bself.?driv", r"\bdriverless",
                     r"\bautomat\w*\W{0,3}driv",
                     r"\bvehicle.?control.?system", r"\baviation.?safety", r"\bmachinery.?safety",
                     r"\badas\b", r"\b(?:level[_\W]?[2-5]|l[2-5])[_\W]?(?:autonomy|automat|driv)",
                     r"\b(?:lane[_\W]?keep|lane[_\W]?assist|lane[_\W]?departure|automatic[_\W]?emergency[_\W]?brak|aeb|collision[_\W]?avoid|adaptive[_\W]?cruise|autopilot)",
                     r"\b(?:pedestrian|cyclist)[_\W]?detect(?:ion|or)?\b",
                     r"\b(?:obstacle|vehicle|object)[_\W]?detect(?:ion|or)?[_\W]?(?:ai|model|classif|lidar|radar|camera|adas|autonom)",
                     r"\b(?:perception|planning|prediction|control)[_\W]?stack[_\W]?(?:av|autonomous|self[_\W]?driv)",
                     r"\b(?:drone|uav|uas)[_\W]?(?:autonomous|obstacle|collision|flight[_\W]?control|safety)",
                     r"\b(?:robot|cobot|industrial[_\W]?robot|manipulator)[_\W]?(?:safety|collision|safe[_\W]?stop|force[_\W]?limit)",
                     r"\b(?:machine|machinery|equipment)[_\W]?(?:safety|interlock|safe[_\W]?stop|e[_\W]?stop|guard)[_\W]?(?:ai|predict|classif|monitor)",
                     r"\b(?:aviation|aircraft|avionics|flight)[_\W]?(?:control|safety|autopilot|tcas|stall|collision|anti[_\W]?icing)[_\W]?(?:ai|automat|predict)",
                     r"\b(?:train|rail|metro)[_\W]?(?:automat|ato|atp|autonomous|collision|brake|emergency)[_\W]?(?:ai|model|predict)",
                     r"\b(?:marine|maritime|vessel|ship)[_\W]?(?:autonomous|collision|anti[_\W]?collision|autopilot|dynamic[_\W]?position)",
                     r"\b(?:lift|elevator|escalator|cableway)[_\W]?(?:safety|emergency|brake|fault)[_\W]?(?:ai|predict|classif)",
                     r"\b(?:tire|tyre|brake|airbag|esp|abs|stability[_\W]?control)[_\W]?(?:ai|predict|model|classif)",
                     # Prompt-string templates.
                     r"(?:detect|classify|predict|avoid)[^\"\\n]{0,30}(?:pedestrian|cyclist|obstacle|collision|lane)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Safety Components",
        "description": "Safety components under Union harmonisation legislation",
    },
}

LIMITED_RISK_PATTERNS = {
    "chatbots": {
        "patterns": [r"\bchatbot", r"conversational.?ai", r"conversational.?model", r"virtual.?assist",
                     r"dialogue.?system", r"support.?bot\b"],
        "article": "50",
        "description": "Chatbots and conversational AI",
    },
    "emotion_recognition": {
        "patterns": [r"emotion.?recogn", r"sentiment.?analy", r"affect.?detect", r"mood.?analy"],
        "article": "50",
        "description": "Emotion recognition systems",
    },
    "biometric_categorisation": {
        "patterns": [r"\bage.?estimat", r"\bgender.?detect", r"\bdemographic.?analy"],
        "article": "50",
        "description": "Biometric categorisation (non-sensitive)",
    },
    "synthetic_content": {
        "patterns": [r"deepfake", r"synthetic.?media", r"face.?swap", r"voice.?clon",
                     r"ai[\s_-]generated[\s_-]image", r"text[\s_-]to[\s_-]image",
                     r"generate_(?:deepfake|synthetic)", r"image_generat(?:or|ion)",
                     r"\.Image\.create\b", r"generate.?image\b"],
        "article": "50",
        "description": "Synthetic content generation",
    },
}

# ---------------------------------------------------------------------------
# AI Security Antipatterns — Code patterns that indicate AI-specific
# vulnerabilities.  These map to OWASP LLM Top 10 and are reported as
# Article 15 (cybersecurity) findings.
# ---------------------------------------------------------------------------

AI_SECURITY_PATTERNS = {
    "unsafe_deserialization": {
        "patterns": [
            r"pickle\.load",
            r"pickle\.loads",
            r"torch\.load\s*\([^)]*\)",  # torch.load without weights_only=True
            r"joblib\.load",
            r"dill\.load",
        ],
        "owasp": "LLM05",
        "description": "Unsafe model deserialization — arbitrary code execution risk",
        "severity": "high",
        "remediation": "Use safetensors format or torch.load(path, weights_only=True). Never unpickle untrusted model files.",
    },
    "prompt_injection_vulnerable": {
        "patterns": [
            # f-string with user-named variable interpolated near prompt context
            r"f['\"][^'\"]{0,500}\{[^}]{0,200}user[^}]{0,200}\}[^'\"]{0,500}['\"][^\n]{0,500}(?:messages|prompt|system)",
            # .format() with user input flowing into prompt context
            r"\.format\([^)]{0,500}user[^)]{0,500}\)[^\n]{0,500}(?:messages|prompt|content)",
            # string concat from common request-body sources into prompt
            r"\+\s*(?:user_input|user_message|user_query|request\.body|req\.body|request\.json|req\.json)[^\n]{0,500}(?:messages|prompt)",
            # Flask/FastAPI request handler concatenating request data into prompt directly
            r"request\.(?:form|args|json|values)\[?['\"]?[a-z_]+['\"]?\]?[^\n]{0,300}(?:messages|prompt|completion|invoke)",
            # Common pattern: passing the raw request body as the message content
            r"messages\s*=\s*\[\s*\{[^}]*['\"]content['\"]\s*:\s*(?:request\.|req\.|user_input|user_message)",
        ],
        "owasp": "LLM01",
        "description": "User input directly concatenated into LLM prompt — prompt injection risk (direct)",
        "severity": "high",
        "remediation": "Use structured prompt templates with input sanitisation. Use a guardrails library (NeMo Guardrails, Lakera Guard, LLM Guard, Rebuff, Guardrails AI). Never concatenate raw user input into system prompts. OWASP LLM01:2025.",
    },
    "prompt_injection_indirect": {
        "patterns": [
            # One-liner: fetched web content passed straight to prompt content
            r"['\"]content['\"]\s*:\s*(?:requests\.get|httpx\.get|urlopen)\([^)]*\)\.(?:text|content|json\(\))",
            # One-liner: file content read inline into prompt content
            r"['\"]content['\"]\s*:\s*(?:open\([^)]+\)\.read\(\)|Path\([^)]+\)\.read_text\(\))",
            # LangChain RAG one-liner: retriever result passed straight to chain.invoke
            r"(?:chain|llm|model|llm_chain|qa_chain)\.invoke\s*\(\s*\{[^}]*['\"]context['\"]\s*:\s*(?:retriever|vectorstore|loader)",
            # messages.append with web/file fetched content
            r"messages\.append\s*\(\s*\{[^}]*['\"]content['\"]\s*:\s*(?:requests\.get|httpx\.get|urlopen|open\(|Path\()",
            # Direct invoke with raw fetched content
            r"(?:llm|client|model)\.(?:invoke|chat\.completions\.create)\([^)]*(?:requests\.get|httpx\.get|urlopen)\([^)]*\)\.(?:text|content)",
            # f-string template with retriever / loader / fetched variable
            r"f['\"][^'\"]{0,500}\{(?:retrieved|context|page_content|doc_text|web_content|fetched|scraped)[^}]{0,200}\}[^'\"]{0,500}['\"][^\n]{0,300}(?:messages|prompt|invoke)",
        ],
        "owasp": "LLM01",
        "description": "Untrusted external content flows into LLM prompt without sanitisation — indirect prompt injection risk (OWASP LLM01:2025 emphasises this vector)",
        "severity": "high",
        "remediation": "Treat all external content (web pages, documents, retrieval results, emails) as untrusted. Apply a guardrails layer (NeMo Guardrails, LLM Guard, Lakera Guard, Rebuff, Guardrails AI). Use spotlighting or context delimiters that the model is trained to respect. OWASP LLM01:2025.",
    },
    "prompt_injection_tool_output": {
        "patterns": [
            # Subprocess stdout in the same line as messages/prompt assignment
            r"(?:messages\.append|messages\s*\+=|prompt\s*=)[^\n]{0,200}subprocess\.(?:run|check_output|Popen)",
            # subprocess result piped straight into invoke
            r"(?:llm|chain|client)\.invoke\s*\([^)]*subprocess\.(?:run|check_output|Popen)",
            # tool_result / observation as messages content (one-liner)
            r"messages\.append\s*\(\s*\{[^}]*['\"]content['\"]\s*:\s*(?:tool_result|tool_output|function_result|action_result|observation)",
            # LangChain AgentExecutor.invoke with raw input + verbose=True is a soft signal — paired with tool_calls in same line
            r"(?:AgentExecutor|create_react_agent|create_tool_calling_agent)\([^)]*verbose\s*=\s*True[^)]*\)[^\n]{0,300}invoke\(",
        ],
        "owasp": "LLM01",
        "description": "Tool / agent / shell output passed to LLM without validation — agentic prompt injection risk",
        "severity": "high",
        "remediation": "Treat tool outputs as untrusted user input. Validate structure (JSON schema), strip control tokens, apply a guardrails layer. Maps to OWASP Agentic ASI04 (control-flow hijacking). OWASP LLM01:2025.",
    },
    "no_output_validation": {
        "patterns": [
            r"\beval\s*\([^\n]{0,500}(?:response|result|output|completion)",  # eval on AI output
            r"\bexec\s*\([^\n]{0,500}(?:response|result|output|completion)",  # exec on AI output
        ],
        "owasp": "LLM02",
        "description": "AI output used without validation — code injection risk",
        "severity": "critical",
        "remediation": "Never eval/exec AI model output. Validate and sanitise all AI-generated content before use.",
    },
    "hardcoded_model_path": {
        "patterns": [
            r"(?:from_pretrained|load_model|torch\.load)\s*\(\s*['\"]https?://",  # loading model from URL
            r"(?:from_pretrained|load_model|torch\.load)\s*\(\s*['\"](?:/tmp|/var|C:\\)",  # loading from temp/uncontrolled path
        ],
        "owasp": "LLM03",
        "description": "Model loaded from untrusted or hardcoded path — supply chain risk",
        "severity": "medium",
        "remediation": "Use model registries (HuggingFace Hub, MLflow) with integrity verification. Pin model revisions.",
    },
    "unbounded_token_generation": {
        "patterns": [
            r"max_tokens\s*[:=]\s*(?:None|0|-1|999999|1000000)",  # unbounded or very high token limit
        ],
        "owasp": "LLM10",
        "description": "Unbounded token generation — cost and resource exhaustion risk",
        "severity": "medium",
        "remediation": "Set explicit max_tokens limit. Add cost monitoring and rate limiting.",
    },
    "missing_temperature_control": {
        "patterns": [
            r"temperature\s*[:=]\s*(?:1\.0|2\.0|1\.5)",  # very high temperature for production
        ],
        "owasp": "LLM09",
        "description": "High temperature setting — increased hallucination risk in production",
        "severity": "low",
        "remediation": "Use temperature=0 or 0.1 for factual/production tasks. Reserve high temperature for creative tasks.",
    },
    # Vibe-coding architecture gaps — common in AI-generated code that skips
    # security review. These map to CRA secure-by-design and AI Act Art. 15.
    "no_error_handling_ai_call": {
        "patterns": [
            r"(?:chat\.completions|messages\.create|llm\.invoke|model\.predict)\s*\([^)]*\)\s*$",  # bare AI call with no try/except on same or next line
        ],
        "owasp": "LLM06",
        "description": "AI API call without error handling — service failures will crash the application",
        "severity": "medium",
        "remediation": "Wrap AI API calls in try/except. Handle rate limits, timeouts, and malformed responses. Required by CRA Annex I secure-by-design.",
    },
    "exposed_api_key_env": {
        "patterns": [
            r"(?:OPENAI_API_KEY|ANTHROPIC_API_KEY)\s*[:=]\s*['\"]sk-[a-zA-Z0-9]",  # hardcoded key in config
        ],
        "owasp": "LLM06",
        "description": "AI API key appears hardcoded — credential exposure risk",
        "severity": "critical",
        "remediation": "Use environment variables or a secrets manager. Never commit API keys to source code. CRA Annex I (2)(c) requires access control.",
    },
}

AI_INDICATORS = {
    "libraries": [r"tensorflow", r"torch", r"pytorch", r"transformers", r"langchain",
                  r"openai", r"anthropic", r"sklearn", r"scikit.?learn", r"keras",
                  r"xgboost", r"lightgbm", r"huggingface", r"spacy", r"nltk",
                  r"onnx", r"onnxruntime", r"brain\.js", r"@tensorflow/tfjs",
                  r"@anthropic-ai/sdk", r"@langchain", r"transformers\.js",
                  r"litellm", r"crewai", r"autogen", r"pyautogen",
                  r"haystack", r"smolagents", r"ollama",
                  r"google\.generativeai", r"mistralai", r"groq",
                  r"dspy", r"vertexai", r"semantic_kernel",
                  r"instructor", r"pydantic_ai", r"together\b", r"replicate",
                  r"google\.adk",
                  r"claude_agent_sdk",
                  r"openai\.agents",
                  r"langgraph",
                  r"@ai-sdk",
                  r"ai-sdk",
                  r"@mastra",
                  r"cohere",
                  r"vllm",
                  r"fireworks"],
    "model_files": [r"\.onnx", r"\.pt\b", r"\.pth\b", r"\.pkl\b", r"\.joblib\b",
                    r"\.h5\b", r"\.hdf5\b", r"\.safetensors", r"\.gguf\b", r"\.ggml\b"],
    "api_endpoints": [r"api\.openai\.com", r"api\.anthropic\.com",
                      r"generativelanguage\.googleapis\.com",
                      r"api\.cohere\.ai", r"api\.mistral\.ai"],
    "ml_patterns": [r"model\.fit", r"model\.train", r"model\.predict", r"embedding",
                    r"vectorstore", r"llm\.invoke", r"chat\.completions",
                    r"messages\.create", r"from_pretrained", r"fine.?tune",
                    r"neural.?network", r"deep.?learning", r"machine.?learning"],
    # Domain keywords so classify() works on plain-text system descriptions,
    # not only on code with library imports. Must mirror HIGH_RISK_PATTERNS
    # vocabulary to avoid false negatives on Annex III descriptions.
    "domain_keywords": [
        # Biometrics (Annex III Cat 1)
        r"\bfacial\s+recognition\b", r"\bface\s+recognition\b", r"\bface\s+detection\b",
        r"\bfingerprint\s+recognition\b", r"\bvoice\s+recognition\b", r"\bvoice\s+identification\b",
        r"\bbiometric\s+identification\b", r"\bbiometric\s+authentication\b", r"\bbiometric\s+scanning\b",
        # Critical infrastructure (Annex III Cat 2)
        r"\benergy\s+grid\b", r"\bwater\s+supply\b", r"\btraffic\s+control\b", r"\belectricity\s+manage",
        # Education (Annex III Cat 3)
        r"\bstudent\s+assess", r"\badmission\s+decision\b", r"\bexam\s+scor",
        # Employment (Annex III Cat 4)
        r"\bcv\s+screen", r"\bresume\s+screen", r"\bresume\s+filt",
        r"\bhiring\s+decision\b", r"\brecruitment\s+ai\b",
        r"\bcandidate\s+rank", r"\bcandidate\s+screen", r"\bapplicant\s+scor",
        # Essential services (Annex III Cat 5)
        r"\bcredit\s+scor", r"\bcreditworth", r"\bloan\s+decision\b", r"\bloan\s+approv",
        r"\binsurance\s+pric", r"\bbenefit\s+eligib", r"\bemergency\s+dispatch",
        # Law enforcement (Annex III Cat 6)
        r"\bpolygraph\b", r"\blie\s+detect",
        # Migration (Annex III Cat 7)
        r"\bborder\s+control\b", r"\bvisa\s+application\b", r"\basylum\s+application\b", r"\bimmigration\s+decision\b",
        # Justice (Annex III Cat 8)
        r"\bjudicial\s+decision\b", r"\bcourt\s+rul", r"\bsentenc(?:ing|e)\b",
        # Medical devices
        r"\bmedical\s+diagnosis\b", r"\bclinical\s+decision\b", r"\bpatient\s+triage\b",
        r"\btreatment\s+recommend",
        # Safety components
        r"\bautonomous\s+vehicle\b", r"\bself[\s-]driving\s+car\b", r"\bdriverless\s+car\b",
        r"\bautonomous\s+driv", r"\baviation\s+safety\b",
        # Limited-risk (Article 50)
        r"\bemotion\s+detection\b", r"\bemotion\s+recognition\b",
        r"\bchatbot\b", r"\bvirtual\s+assistant\b", r"\bconversational\s+ai\b",
        r"\bdeepfake\b", r"\bface\s+swap\b", r"\bsynthetic\s+media\b",
        # Prohibited (Article 5)
        r"\bpredictive\s+policing\b",
        # Generic AI indicators for descriptions
        r"\bautomated\s+decision\b", r"\bautomated\s+assessment\b",
        r"\bai\s+system\b", r"\bai\s+model\b", r"\bai[\s-]powered\b", r"\bai\b",
    ],
}

# Patterns that indicate model TRAINING (not just inference) — may trigger
# GPAI obligations if building a general-purpose model (>10^23 FLOPs)
GPAI_TRAINING_PATTERNS = [
    r"model\.fit\b", r"model\.train\b", r"\.train\(\)", r"trainer\.train",
    r"fine.?tun", r"from_pretrained.{0,30}train", r"training_args",
    r"TrainingArguments", r"Trainer\(", r"SFTTrainer",
    r"\.compile\(.{0,30}optimizer", r"backpropagat",
    r"torch\.optim", r"tf\.keras\.optimizers",
    r"lora", r"qlora", r"peft",
]

# Compact ISO 42001 mapping for high-risk classification output.
# Full mapping in references/iso_42001_mapping.yaml.
ISO_42001_MAP = {
    "9":  "ISO 42001: 6.1 (Risk assessment), A.5.3 (AI risk management)",
    "10": "ISO 42001: A.6.6 (Data for AI systems), A.7.4 (Documentation of data)",
    "11": "ISO 42001: A.6.4 (AI system documentation), 7.5 (Documented information)",
    "12": "ISO 42001: A.6.10 (Logging and monitoring)",
    "13": "ISO 42001: A.6.8 (Transparency and explainability)",
    "14": "ISO 42001: A.6.3 (Human oversight of AI systems)",
    "15": "ISO 42001: A.6.9 (Performance and monitoring)",
}

# Pattern-to-Article observations: when specific code patterns co-occur
# with high-risk indicators, generate Article-specific governance notes.
GOVERNANCE_OBSERVATIONS = {
    "training_data": {
        "patterns": [r"\.fit\(", r"\.train\(", r"training_data", r"train_test_split",
                     r"\.csv", r"read_csv", r"load_data"],
        "article": "10",
        "observation": "Training data detected — Article 10 requires data to be relevant, representative, and examined for biases.",
    },
    "prediction_without_review": {
        "patterns": [r"\.predict\(", r"\.predict_proba\("],
        "article": "14",
        "observation": "Model predictions detected — Article 14 requires human oversight with ability to override or reverse AI outputs.",
    },
    "automated_decision_function": {
        "patterns": [
            # Python function definitions
            r"def\s+\w*(screen|filter|rank|score|decide|reject|accept|approve|deny)\w*\s*\(",
            # JS/TS function declarations and arrow functions (camelCase lowercased)
            r"function\s+\w*(?:screen|filter|rank|score|decide|reject|accept|approve|deny)\w*\s*\(",
            r"(?:const|let|var)\s+\w*(?:screen|filter|rank|score|decide|reject|accept|approve|deny)\w*\s*=\s*(?:async\s+)?(?:\([^)]*\)|\w+)\s*=>",
        ],
        "article": "13",
        "observation": "Automated decision function detected — Article 13 requires transparency to deployers about capabilities and limitations.",
    },
    "no_logging": {
        "patterns": [r"logging", r"\.log\(", r"audit", r"logger"],
        "article": "12",
        "observation": None,  # Only flag ABSENCE — see check below
        "absence_observation": "No logging detected — Article 12 requires automatic recording of events for traceability.",
    },
}

# ---------------------------------------------------------------------------
# Bias Risk Patterns — Article 10(5)
#
# Detects protected class attributes used as model features in ML pipelines.
# This is a "did you consider this?" check, NOT evidence of discrimination.
# Article 10(5) requires training data to be examined for biases.
# Limitation: can detect absence of attempt, not actual model bias.
# ---------------------------------------------------------------------------

BIAS_RISK_PATTERNS = {
    "protected_class_as_feature": {
        "patterns": [
            # DataFrame/array column access with protected class names
            r"""(?:df|X|features|X_train|X_test|train_data|dataset|data)\s*\[\s*['"](?:race|ethnicity|gender|sex\b|religion|nationality|disability|marital.status|national.origin)""",
            # Protected attribute in feature list: ['income', 'race', 'age'] — before comma
            r"""['"]\s*(?:race|ethnicity|religion|nationality|disability|marital.status|national.origin)\s*['"]\s*,""",
            # Protected attribute as last element in a list: ['income', 'race']
            r""",\s*['"]\s*(?:race|ethnicity|religion|nationality|disability|marital.status|national.origin)\s*['"]\s*[\]\)]""",
            # Variable names strongly implying protected attribute as feature
            r"""\b(?:race|ethnicity|nationality|disability)(?:_col|_column|_feature|_var|_field)\b""",
        ],
        "article": "10",
        "article_clause": "10(5)",
        "description": "Protected class attribute detected as potential model feature",
        "observation": (
            "Protected class attribute (race, ethnicity, religion, nationality, disability) "
            "detected in a data or ML context. "
            "Article 10(5) requires training data to be examined for biases for high-risk AI systems. "
            "This flag does not mean your model is biased — it means: "
            "(1) document why this attribute is included, "
            "(2) perform disparate impact analysis before deploying in employment, credit, or essential services, "
            "(3) check whether the system falls under Annex III obligations."
        ),
        "eu_ai_act_basis": (
            "Article 10(5): training data must be examined for possible biases that could cause prohibited discrimination. "
            "Recital 44: particular attention to elimination of discriminatory effects."
        ),
    },
    "missing_fairness_evaluation": {
        "patterns": [
            # Fairness library imports — used for ABSENCE detection
            r"fairlearn",
            r"aif360",
            r"themis[_\-]ml",
            r"fairness[_\-]indicator",
            r"equalized[_\.]odds",
            r"demographic[_\.]parity",
            r"disparate[_\.]impact",
            r"audit[_\-]ai",
        ],
        "article": "10",
        "article_clause": "10(5)",
        "description": "No fairness evaluation detected",
        "observation": None,
        "absence_observation": (
            "No fairness evaluation library detected alongside protected class attributes. "
            "Article 10(5) requires training data to be examined for biases. "
            "Consider: fairlearn, AIF360, or manual disparate impact analysis "
            "before deploying in employment, credit, or essential services contexts."
        ),
    },
}
