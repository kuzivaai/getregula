// scanner.js — Regula client-side EU AI Act detection pattern scanner
// regula-ignore: this file defines compliance detection rules, not prohibited AI practices
// Ported from scripts/risk_patterns.py + scripts/classify_risk.py (627 detection patterns)
// All logic runs client-side. Nothing leaves the browser.
// Licensed under the Detection Rule License (DRL) 1.1.

'use strict';

// =====================================================================
// Pattern definitions — ported from scripts/risk_patterns.py
// To regenerate after pattern changes:
//   1. Run: python3 -c "import json,sys; sys.path.insert(0,'scripts'); from risk_patterns import *; ..." > /tmp/patterns.json
//   2. Convert JSON to JS const declarations
//   3. Replace the pattern data section below
//   4. Verify: node -e "const s=require('./scanner.js'); ..." against benchmarks/synthetic/fixtures/
// See .claude/handover.md for the full regeneration process used to create this file.
// =====================================================================

// Pattern data (627 detection patterns: 398 risk + 212 indicators + 17 GPAI)

const PROHIBITED_PATTERNS = {
  "subliminal_manipulation": {
    "patterns": [
      "subliminal",
      "beyond.?consciousness",
      "subconscious.?influence"
    ],
    "article": "5(1)(a)",
    "description": "AI deploying subliminal techniques beyond a person's consciousness",
    "conditions": "Prohibited when the technique materially distorts behaviour and causes or is likely to cause significant harm.",
    "exceptions": null,
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "exploitation_vulnerabilities": {
    "patterns": [
      "target.?elderly",
      "exploit.?disabil",
      "vulnerable.?group.?target"
    ],
    "article": "5(1)(b)",
    "description": "Exploiting vulnerabilities of specific groups (age, disability, economic situation)",
    "conditions": "Prohibited when exploiting vulnerabilities to materially distort behaviour causing significant harm.",
    "exceptions": null,
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "social_scoring": {
    "patterns": [
      "\\bsocial.?scor(?:e|ing)\\b",
      "\\bsocial.?credit.?(?:scor|system|rating)",
      "\\bsocial.?credit\\b",
      "\\bcitizen.?score",
      "\\bscore.{0,5}citizen",
      "\\bbehaviour.{0,10}scor.{0,40}(?:citizen|public|authorit|government|civic|trustworth)"
    ],
    "article": "5(1)(c)",
    "description": "Social scoring by public authorities or on their behalf",
    "conditions": "Prohibited when evaluating or classifying persons based on social behaviour or personal traits, leading to detrimental treatment disproportionate to context.",
    "exceptions": null,
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "criminal_prediction": {
    "patterns": [
      "crime.?predict",
      "criminal.?risk.?assess",
      "predictive.?policing",
      "recidivism"
    ],
    "article": "5(1)(d)",
    "description": "Criminal risk prediction based solely on profiling or personality traits",
    "conditions": "Prohibited ONLY when based solely on profiling or personality traits. Systems using multiple evidence sources (case facts, prior convictions with human review) may be lawful.",
    "exceptions": "AI systems that support human assessment based on objective, verifiable facts directly linked to criminal activity are NOT prohibited.",
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "facial_recognition_scraping": {
    "patterns": [
      "\\bface.?scrap",
      "facial.?database.?untarget",
      "mass.?facial.?collect"
    ],
    "article": "5(1)(e)",
    "description": "Creating facial recognition databases through untargeted scraping",
    "conditions": "Prohibited when scraping facial images from the internet or CCTV to build or expand recognition databases.",
    "exceptions": null,
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "emotion_inference_workplace": {
    "patterns": [
      "emotion.{0,40}workplace",
      "sentiment.{0,40}employee",
      "workplace.{0,40}emotion",
      "employee.{0,40}emotion"
    ],
    "article": "5(1)(f)",
    "description": "Emotion inference in workplace settings",
    "conditions": "Prohibited in workplace and educational institutions.",
    "exceptions": "EXEMPT when used for medical or safety purposes (e.g., detecting driver fatigue, monitoring patient wellbeing in clinical settings).",
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "emotion_inference_education": {
    "patterns": [
      "emotion.{0,40}school",
      "emotion.{0,40}classroom",
      "emotion.{0,40}student",
      "student.{0,40}emotion"
    ],
    "article": "5(1)(f)",
    "description": "Emotion inference in educational settings",
    "conditions": "Prohibited in workplace and educational institutions.",
    "exceptions": "EXEMPT when used for medical or safety purposes (e.g., monitoring student wellbeing in clinical settings).",
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "biometric_categorisation_sensitive": {
    "patterns": [
      "\\brace.?detect(?!.*(?:condition|thread|concurrent))",
      "ethnicity.?infer",
      "political.?opinion.?biometric",
      "religion.?detect",
      "sexual.?orientation.?infer"
    ],
    "article": "5(1)(g)",
    "description": "Biometric categorisation inferring sensitive attributes (race, politics, religion, sexuality)",
    "conditions": "Prohibited when using biometric data to categorise persons by race, political opinions, trade union membership, religious beliefs, sex life, or sexual orientation.",
    "exceptions": "Labelling or filtering of lawfully acquired biometric datasets (e.g., photo sorting) may be exempt where no categorisation of individuals occurs.",
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "realtime_biometric_public": {
    "patterns": [
      "real.?time.?facial.?recogn",
      "live.?biometric.?public",
      "public.?space.?biometric",
      "mass.?surveillance.?biometric"
    ],
    "article": "5(1)(h)",
    "description": "Real-time remote biometric identification in publicly accessible spaces for law enforcement",
    "conditions": "Prohibited for law enforcement in publicly accessible spaces in real-time.",
    "exceptions": "Narrow exceptions exist with PRIOR judicial authorisation for: (i) targeted search for victims of abduction/trafficking/sexual exploitation, (ii) prevention of specific imminent terrorist threat, (iii) identification of suspects of serious criminal offences (as defined in Annex II).",
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "ncii_generation": {
    "patterns": [
      "\\bnudif",
      "\\bundress(?:ing)?[\\s_-]?(?:ai|model|gen)",
      "\\bdeepnude",
      "\\bcloth_off",
      "\\bstrip_ai"
    ],
    "article": "5(1)(i) [Omnibus]",
    "description": "AI systems generating non-consensual intimate imagery of identifiable persons",
    "conditions": "Added by Digital Omnibus provisional agreement 7 May 2026. Effective 2 December 2026.",
    "exceptions": null,
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "csam_generation": {
    "patterns": [
      "age_regress(?:ion)?[\\s_-]?(?:generat|synthesi|model|face)",
      "\\bdeage[\\s_-]?(?:generat|face|model|synthes)",
      "\\bchild[\\s_-]?(?:face[\\s_-]?(?:swap|generat)|body[\\s_-]?generat|image[\\s_-]?generat)",
      "\\bminor[\\s_-]?(?:face[\\s_-]?(?:swap|generat)|body[\\s_-]?generat|image[\\s_-]?generat)"
    ],
    "article": "5(1)(i) [Omnibus]",
    "description": "AI systems generating material depicting minors in sexually explicit contexts",
    "conditions": "Added by Digital Omnibus provisional agreement 7 May 2026. Effective 2 December 2026.",
    "exceptions": null,
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  }
};

const HIGH_RISK_PATTERNS = {
  "biometrics": {
    "patterns": [
      "\\bbiometric.?ident",
      "\\bfac(?:ial|e)\\s*[\\W_]?recogn",
      "\\bfingerprint\\s*[\\W_]?recogn",
      "\\bvoice\\s*[\\W_]?recogn",
      "\\biris\\s*[\\W_]?(?:recogn|scan|match|identif)",
      "\\bretina\\s*[\\W_]?(?:scan|recogn)",
      "\\bpalm\\s*[\\W_]?(?:print|recogn|scan)",
      "\\bgait\\s*[\\W_]?(?:recogn|analysis|identif)",
      "\\b(?:face|voice|fingerprint|iris)[_\\W]?(?:match|verif|compar|enrol|template)",
      "\\b(?:identify|recognise|recognize|verify|match|enrol)[_\\W]?(?:face|faces|person|people|identity)\\b",
      "\\bbiometric[_\\W]?(?:categoris|categoriz|classif|template|verif|match|enrol)",
      "\\b(?:detect|infer|classify|predict)[_\\W]?(?:age|gender|ethnicity|race)[_\\W]?from[_\\W]?(?:face|image|photo|voice)",
      "\\b(?:speaker|voice)[_\\W]?(?:identif|verif|recogn|diariz)",
      "\\bface[_\\W]?embed(?:ding)?",
      "(?:identify|match|recognise|recognize|verify)[^\\\"\\\\n]{0,30}(?:face|person|identity|suspect)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 1",
    "description": "Biometric identification and categorisation",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "critical_infrastructure": {
    "patterns": [
      "\\benergy.?grid",
      "\\bwater.?supply",
      "\\btraffic.?control",
      "\\belectricity.?manage",
      "\\b(?:power|electricity|energy|electric)[_\\W]?(?:grid|dispatch|load|demand|forecast|balanc|outage|substation|transmission|distribution)",
      "\\b(?:grid|substation|transformer|feeder)[_\\W]?(?:load|forecast|predict|balanc|fault|dispatch|stabil)",
      "\\b(?:gas|natural[_\\W]?gas)[_\\W]?(?:pressure|flow|leak|monitor|dispatch|scada|control)",
      "\\b(?:gas|oil)[_\\W]?pipeline[_\\W]?(?:pressure|flow|leak|monitor|dispatch|scada|control)",
      "\\bpipeline[_\\W]?(?:pressure|flow|leak|monitor|dispatch|scada)(?!net\\b)",
      "\\b(?:water|wastewater|sewage)[_\\W]?(?:treatment|supply|distribution|scada|leak|flow|quality|contamin)",
      "\\b(?:district[_\\W]?)?heating[_\\W]?(?:grid|supply|control|manage|dispatch)",
      "\\bscada\\b",
      "\\bplc[_\\W]?(?:control|automat)",
      "\\bics[_\\W]?(?:control|automat|security)",
      "\\b(?:nuclear|reactor)[_\\W]?(?:control|safety|monitor|scada)",
      "\\brailway[_\\W]?(?:signal|control|dispatch|interlock|track|switching)",
      "\\b(?:metro|subway|tram)[_\\W]?(?:signal|dispatch|control)",
      "\\b(?:air[_\\W]?traffic|atc|atm)[_\\W]?(?:control|manage|dispatch|safety|conflict)",
      "\\b(?:maritime|vessel|port)[_\\W]?traffic[_\\W]?(?:control|manage|dispatch)",
      "\\broad[_\\W]?traffic[_\\W]?(?:control|signal|light|management|flow|dispatch)",
      "\\btraffic[_\\W]?(?:signal|light|flow|congestion)[_\\W]?(?:control|manage|optim|predict|ai)",
      "(?:control|manage|dispatch|forecast)[^\\\"\\\\n]{0,30}(?:grid|substation|pipeline|scada|reactor|railway|air[_\\W]?traffic)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 2",
    "description": "Critical infrastructure management",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "high"
  },
  "education": {
    "patterns": [
      "\\badmission.?decision",
      "\\bstudent.?assess",
      "\\bexam.?scor",
      "\\bprocto\\w*.{0,15}(exam|test|monitor|ai|automat|student|cheat)",
      "\\b(?:grade|score|rank|classify|evaluate|assess)[_\\W]?(?:essays?|assignments?|homework|coursework|submissions?)\\b",
      "\\b(?:essays?|assignments?|homework|coursework)[_\\W]?(?:grad(?:e|ing)|scor|rank|classif|evaluat|auto)",
      "\\bauto[_\\W]?grad(?:e|ing|er)\\b",
      "\\b(?:predict|model|estimate)[_\\W]?(?:dropouts?|attrition|grades?|gpas?|graduation|completion)\\b",
      "\\b(?:dropouts?|attrition|gpa|grades?)[_\\W]?(?:predict|model|score|rank)",
      "\\b(?:score|rank|classify|filter|shortlist)[_\\W]?(?:students?|pupils?|learners?|applicants?[_\\W]?(?:to|for)[_\\W]?(?:college|university|school))\\b",
      "\\bplacement[_\\W]?(?:test|exam|score|decision)",
      "\\b(?:university|college|school|admission)[_\\W]?rank",
      "\\b(?:rank|score|filter|shortlist|classify)[_\\W]?(?:university|college|school)[_\\W]?(?:applicants?|students?|candidates?)",
      "\\badmissions?[_\\W]?(?:scor|rank|filter|model|predict|classif|decision)",
      "\\b(?:student|pupil|learner)[_\\W]?(?:scor|rank|classif|risk)",
      "(?:grade|score|rank|evaluate|assess)[^\\\"\\\\n]{0,30}(?:essay|assignment|homework|student|admission)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 3",
    "description": "Education and vocational training",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "high"
  },
  "employment": {
    "patterns": [
      "\\bcv.?screen",
      "\\bresume.?filt",
      "\\bhiring.?decision",
      "\\brecruit\\w*\\W{0,3}automat",
      "\\bautomat\\w*\\W{0,3}recruit",
      "\\bcandidate[_\\W]?rank",
      "rank[_\\W]?candidate",
      "\\bpromotion.?decision",
      "\\btermination.?decision",
      "\\bperformance.?review.{0,30}(ai|automat|model|predict)",
      "\\bscreen.?candidate",
      "\\bjob.?candidate",
      "\\bcandidate.?screen",
      "\\bresume\\s*[\\W_]?screen",
      "\\bapplicant.?scor",
      "\\bapplicant.?rank",
      "\\bemployee.?assess",
      "\\b(?:classify|score|rank|evaluate|assess|filter|shortlist)[_\\W]?resumes?\\b",
      "\\bresumes?[_\\W]?(?:classif|scor|rank|evaluat|filter|shortlist|match)",
      "\\b(?:score|rank|evaluate|shortlist)[_\\W]?(?:job[_\\W]?)?candidates?\\b",
      "\\bjob[_\\W]?applicants?[_\\W]?(?:scor|rank|filter|evaluat|shortlist)",
      "\\b(?:score|rank|shortlist)[_\\W]?job[_\\W]?applicants?\\b",
      "(?:score|rank|classify|evaluate)[^\\\"\\\\n]{0,30}resumes?\\b",
      "\\bresumes?[^\\\"\\\\n]{0,30}(?:score|rank|classif|evaluat|shortlist)",
      "(?:score|rank|classify|evaluate)[^\\\"\\\\n]{0,30}(?:job[_\\W]candidate|job[_\\W]applicant)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 4",
    "description": "Employment and workers management",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "essential_services": {
    "patterns": [
      "\\bcredit.?scor",
      "\\bcreditworth",
      "\\bloan.?decision",
      "\\binsurance.?pric",
      "\\bbenefit.?eligib",
      "\\bemergency.?dispatch",
      "credit.?risk",
      "credit.?model",
      "credit.?predict",
      "\\bloan.?approv",
      "\\blending.?decision",
      "\\b(?:score|approve|deny|reject|underwrit|automate)[_\\W]?(?:loans?|mortgages?|credit|lending|advances?)\\b",
      "\\b(?:loans?|mortgages?|credit|lending|advances?)[_\\W]?(?:scor|approv|deny|reject|underwrit|automat|decision|risk|model|predict)",
      "\\bmortgage[_\\W]?(?:decision|approv|underwrit|risk|score)",
      "\\b(?:insurance|policy|premium)[_\\W]?(?:price|quote|underwrit|risk|tier|model|score)",
      "\\bclaim[_\\W]?(?:assess|adjudicat|deni|approv|fraud|risk|score|decision)",
      "\\b(?:health|life|auto|car|vehicle|home|property)[_\\W]?insurance[_\\W]?(?:price|quote|tier|underwrit|risk|score|decision)",
      "\\b(?:welfare|benefit|disability|unemployment|housing|food[_\\W]?stamp|snap|medicaid|medicare)[_\\W]?(?:eligib|decision|approv|deni|risk|fraud|model)",
      "\\b(?:eligib|approv|deny)[_\\W]?(?:welfare|benefit|disability|housing|public[_\\W]?assistance)",
      "\\butility[_\\W]?(?:disconnect|shutoff|cut[_\\W]?off|deni|priorit)",
      "\\b(?:emergency|911|999|112)[_\\W]?(?:dispatch|priorit|triage|routing|severity)",
      "\\bambulance[_\\W]?(?:dispatch|priorit|routing|triage)",
      "(?:approve|deny|score|underwrite)[^\\\"\\\\n]{0,30}(?:loan|mortgage|credit|claim|application|benefit)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 5",
    "description": "Access to essential services",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "law_enforcement": {
    "patterns": [
      "\\bpolygraph",
      "\\blie.?detect",
      "\\bevidence.?reliab",
      "\\bcriminal.?investigat",
      "\\brecidivism\\b",
      "\\b(?:offen[cs]e|reoffend|reoffending)[_\\W]?(?:forecast|risk|hotspot|map|model|analytics)",
      "\\b(?:forecast)[_\\W]?(?:offence|offense|reoffend|arrests?)",
      "\\bpredictive[_\\W]?polic(?:e|ing)\\b",
      "\\b(?:suspect|offender|defendant|inmate|parolee|probationer)[_\\W]?(?:scor|rank|risk|profil|classif|threat)",
      "\\b(?:risk|threat)[_\\W]?(?:scor|assess|model|rank|classif)[_\\W]?(?:offender|suspect|defendant|inmate|parolee)",
      "\\bflight[_\\W]?risk[_\\W]?(?:assess|score|model|predict)",
      "\\b(?:parole|probation|bail|sentencing)[_\\W]?(?:decision|recommend|risk|score|model|predict|algorithm)",
      "\\b(?:gang|cartel)[_\\W]?(?:member(?:ship)?|affiliation|associat)[_\\W]?(?:predict|model|score|classif)",
      "\\bcrime[_\\W]?hotspot",
      "\\bthreat[_\\W]?(?:assess|score|level|model)[_\\W]?(?:individual|suspect|person)",
      "\\b(?:facial|face)[_\\W]?(?:recogn|match|identif)[_\\W]?(?:suspect|wanted|fugitive|offender)",
      "(?:predict|score|assess)[^\\\"\\\\n]{0,30}(?:reoffend|offender|suspect|parole|bail)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 6",
    "description": "Law enforcement",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "migration": {
    "patterns": [
      "\\bborder.?control",
      "\\bvisa.?application",
      "\\basylum.?application",
      "\\bimmigration.?decision",
      "\\b(?:visa|residence[_\\W]?permit|work[_\\W]?permit)[_\\W]?(?:risk|scor|approv|deni|reject|decision|classif|predict|assess)",
      "\\b(?:approve|deny|reject|score|assess|decide)[_\\W]?(?:visa|asylum|refugee|immigration|residence[_\\W]?permit|work[_\\W]?permit)",
      "\\basylum[_\\W]?(?:risk|scor|decision|classif|triage|eligib|predict|credibility)",
      "\\brefugee[_\\W]?(?:status|risk|scor|decision|classif|triage|eligib)",
      "\\b(?:migrant|asylum[_\\W]?seeker|refugee|applicant)[_\\W]?(?:risk|scor|classif|profil|threat|fraud)",
      "\\bimmigration[_\\W]?(?:risk|scor|enforce|fraud|detect|classif)",
      "\\bborder[_\\W]?(?:screen|risk|threat|profil|identif|surveillance|scor)",
      "\\b(?:frontex|e-?gate|iborder|smart[_\\W]?border)",
      "\\bentry[_\\W]?(?:risk|decision|classif|scor)[_\\W]?(?:border|immigration|frontier)",
      "\\bpassport[_\\W]?(?:verif|authent|fraud|match|recogn)",
      "(?:approve|deny|score|assess)[^\\\"\\\\n]{0,30}(?:visa|asylum|refugee|immigration|border)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 7",
    "description": "Migration, asylum, and border control",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "high"
  },
  "justice": {
    "patterns": [
      "\\bjudicial.?decision",
      "\\bcourt.?rul",
      "\\bsentenc(ing|e\\.?)\\W{0,5}(recommend|decision|guidelines|court|judge|judicial|legal|verdict|criminal|prison|convict|parole|probation)",
      "\\belection.?influence",
      "\\b(?:judge|judicial|court)[_\\W]?(?:ai|assistant|recommend|decision|predict|automat)",
      "\\b(?:verdict|ruling|judgement|judgment)[_\\W]?(?:predict|recommend|draft|score|classif)",
      "\\b(?:case|claim|dispute|lawsuit)[_\\W]?(?:outcome|predict|score|classif|triage|recommend)",
      "\\b(?:legal|statute|precedent)[_\\W]?(?:search|retriev|interpret|classif|recommend)[_\\W]?(?:ai|automat|model)",
      "\\b(?:predict|forecast|recommend)[_\\W]?(?:sentence|verdict|ruling|judgment|judgement|settlement)",
      "\\b(?:voter|electorate|constituent)[_\\W]?(?:target|profil|micro[_\\W]?target|influenc|persuad|predict)",
      "\\belection[_\\W]?(?:target|micro[_\\W]?target|influenc|manipul|profil|predict)",
      "\\b(?:campaign|political)[_\\W]?(?:micro[_\\W]?target|profil|influenc|manipul)[_\\W]?(?:voter|user|person)",
      "\\b(?:referendum|ballot|electoral)[_\\W]?(?:influenc|manipul|target|profil)",
      "(?:predict|recommend|draft|score)[^\\\"\\\\n]{0,30}(?:verdict|sentence|judgment|ruling|case[_\\W]outcome)",
      "(?:target|profile|influence)[^\\\"\\\\n]{0,30}(?:voter|election|electorate|referendum)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 8",
    "description": "Justice and democratic processes",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "high"
  },
  "medical_devices": {
    "patterns": [
      "\\bmedical.?diagnos",
      "\\bclinical.?decision",
      "\\btreatment.?recommend",
      "\\bpatient.?triage",
      "\\b(?:detect|classify|segment|diagnose|predict)[_\\W]?(?:tumor|tumour|lesion|cancer|malignan|nodule|polyp|stroke|aneurysm|fracture)",
      "\\b(?:radiology|radiograph|ct[_\\W]?scan|mri|x[_\\W]?ray|ultrasound|mammogram|ecg|ekg|eeg|pathology|histolog|dermatology|retinal|fundus)[_\\W]?(?:ai|classif|detect|diagnos|segment|scor|interpret|automat)",
      "\\b(?:ai|model|neural|deep)[_\\W]?(?:radiology|pathology|dermatology|cardiology|ophthalmology)",
      "\\b(?:sepsis|deterioration|readmission|mortality|icu|length[_\\W]?of[_\\W]?stay)[_\\W]?(?:predict|scor|risk|model|classif|early[_\\W]?warning)",
      "\\b(?:patient|clinical)[_\\W]?(?:risk|scor|deterior|outcome|mortality|readmission)[_\\W]?(?:predict|model|classif|scor)",
      "\\b(?:drug|dose|dosage|insulin|anticoagulant|chemotherapy)[_\\W]?(?:dos|titrat|recommend|adjust)[_\\W]?(?:ai|model|automat|predict)",
      "\\b(?:clinical|diagnostic)[_\\W]?(?:support|assist|recommend|decision)[_\\W]?(?:system|ai|model|tool)",
      "\\bcdss\\b",
      "\\b(?:prior[_\\W]?authori[sz]ation|utilisation[_\\W]?review|claim[_\\W]?medical)[_\\W]?(?:predict|automat|deny|approv)",
      "\\b(?:symptom|diagnosis|disease)[_\\W]?(?:predict|classif|recommend|scor|check)[_\\W]?(?:ai|model|chatbot)",
      "\\b(?:medical|health)[_\\W]?(?:chatbot|triage[_\\W]?bot|symptom[_\\W]?checker)",
      "(?:diagnose|detect|classify|predict)[^\\\"\\\\n]{0,30}(?:tumor|tumour|cancer|stroke|sepsis|patient|disease)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Medical Devices",
    "description": "AI components of medical devices",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "high"
  },
  "high_risk__insurance": {
    "patterns": [
      "\\binsurance[_\\W]?scor",
      "\\binsurance[_\\W]?risk",
      "\\bunderwriting[_\\W]?model",
      "\\bclaim[_\\W]?predict",
      "\\bactuarial[_\\W]?model",
      "\\binsurance[_\\W]?pricing",
      "\\bpolicy[_\\W]?risk[_\\W]?scor",
      "\\b(?:life|health)[_\\W]?insurance[_\\W]?(?:scor|model|predict|assess|classif)",
      "\\b(?:actuarial|underwriting)[_\\W]?(?:ai|automat|model|predict|classif|scor)",
      "(?:score|assess|predict|price)[^\\\"\\\\n]{0,30}(?:insurance|underwriting|actuarial|policy[_\\W]risk)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 5(c)",
    "description": "Insurance access and pricing",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "high_risk__credit_scoring": {
    "patterns": [
      "\\bcredit[_\\W]?scor",
      "\\bcredit[_\\W]?risk",
      "\\bcreditworth",
      "\\bloan[_\\W]?decision",
      "\\blending[_\\W]?model",
      "\\bcredit[_\\W]?assess",
      "\\bfico\\b",
      "\\bcredit[_\\W]?rating",
      "\\b(?:credit|lending)[_\\W]?(?:model|predict|classif|algorithm|automat)",
      "\\b(?:score|assess|evaluate|rate)[_\\W]?(?:creditworth|borrower|applicant[_\\W]?credit)",
      "(?:score|assess|evaluate|predict)[^\\\"\\\\n]{0,30}(?:credit|creditworth|borrower|lending|fico)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 5(b)",
    "description": "Creditworthiness assessment",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "high_risk__worker_management": {
    "patterns": [
      "\\bemployee[_\\W]?monitor",
      "\\bproductivity[_\\W]?track",
      "\\bworker[_\\W]?surveillance",
      "\\btask[_\\W]?allocation",
      "\\b(?:employee|worker|staff)[_\\W]?performance[_\\W]?scor",
      "\\bworkforce[_\\W]?management",
      "\\bemployee[_\\W]?ranking",
      "\\bworker[_\\W]?efficiency",
      "\\b(?:employee|worker|staff)[_\\W]?(?:monitor|surveil|track|rank|scor|evaluat|profil)",
      "\\b(?:task|shift|workload)[_\\W]?(?:allocat|assign|distribut|optimis|optimiz)[_\\W]?(?:ai|model|automat|algorithm)",
      "\\b(?:productivity|efficiency)[_\\W]?(?:monitor|track|scor|rank|dashboard)",
      "(?:monitor|track|score|rank|evaluate)[^\\\"\\\\n]{0,30}(?:employee|worker|staff|productivity|performance)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 4(b)",
    "description": "Worker monitoring and task allocation",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "high_risk__democratic_processes": {
    "patterns": [
      "\\bvoter[_\\W]?target",
      "\\belection[_\\W]?predict",
      "\\bpolitical[_\\W]?ad",
      "\\bcampaign[_\\W]?target",
      "\\bvoter[_\\W]?profil",
      "\\bballot\\b",
      "\\belectoral\\b",
      "\\bvote[_\\W]?predict",
      "\\b(?:voter|electorate)[_\\W]?(?:micro[_\\W]?target|segment|influenc|persuad|manipul)",
      "\\b(?:election|electoral|referendum|ballot)[_\\W]?(?:predict|forecast|model|manipul|influenc|interfere)",
      "\\b(?:political|campaign)[_\\W]?(?:ad|advertis|target|micro[_\\W]?target|profil)[_\\W]?(?:ai|model|automat|algorithm)",
      "(?:target|profile|influence|predict)[^\\\"\\\\n]{0,30}(?:voter|election|electoral|referendum|ballot|campaign)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 8",
    "description": "Democratic processes and elections",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "high"
  },
  "high_risk__emergency_services": {
    "patterns": [
      "\\bemergency[_\\W]?dispatch",
      "\\btriage[_\\W]?model",
      "\\bfirst[_\\W]?responder",
      "\\bemergency[_\\W]?priority",
      "\\bincident[_\\W]?priority",
      "\\bambulance[_\\W]?dispatch",
      "\\bfire[_\\W]?dispatch",
      "\\b(?:emergency|911|999|112)[_\\W]?(?:call|dispatch|priorit|triage|routing|severity|queue)",
      "\\b(?:ambulance|fire|police|paramedic)[_\\W]?(?:dispatch|routing|priorit|triage|allocat)",
      "\\b(?:incident|emergency)[_\\W]?(?:triage|severity|priorit|classif|scor)[_\\W]?(?:ai|model|automat|algorithm)",
      "(?:dispatch|triage|prioritise|prioritize)[^\\\"\\\\n]{0,30}(?:emergency|ambulance|fire|incident|first[_\\W]responder)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Annex III, Category 5(d)",
    "description": "Emergency services dispatch and triage",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "high"
  },
  "safety_components": {
    "patterns": [
      "\\bautonomous.?vehicle",
      "\\bself[\\s_-]driv(?:ing|en|erless)\\b",
      "\\bdriverless",
      "\\bautomat\\w*\\W{0,3}driv",
      "\\bvehicle.?control.?system",
      "\\baviation.?safety",
      "\\bmachinery.?safety",
      "\\badas\\b",
      "\\b(?:level[_\\W]?[2-5]|l[2-5])[_\\W]?(?:autonomy|automat|driv)",
      "\\b(?:lane[_\\W]?keep|lane[_\\W]?assist|lane[_\\W]?departure|automatic[_\\W]?emergency[_\\W]?brak|aeb|collision[_\\W]?avoid|adaptive[_\\W]?cruise|autopilot)",
      "\\b(?:pedestrian|cyclist)[_\\W]?detect(?:ion|or)?\\b",
      "\\b(?:obstacle|vehicle|object)[_\\W]?detect(?:ion|or)?[_\\W]?(?:ai|model|classif|lidar|radar|camera|adas|autonom)",
      "\\b(?:perception|planning|prediction|control)[_\\W]?stack[_\\W]?(?:av|autonomous|self[_\\W]?driv)",
      "\\b(?:drone|uav|uas)[_\\W]?(?:autonomous|obstacle|collision|flight[_\\W]?control|safety)",
      "\\b(?:robot|cobot|industrial[_\\W]?robot|manipulator)[_\\W]?(?:safety|collision|safe[_\\W]?stop|force[_\\W]?limit)",
      "\\b(?:machine|machinery|equipment)[_\\W]?(?:safety|interlock|safe[_\\W]?stop|e[_\\W]?stop|guard)[_\\W]?(?:ai|predict|classif|monitor)",
      "\\b(?:aviation|aircraft|avionics|flight)[_\\W]?(?:control|safety|autopilot|tcas|stall|collision|anti[_\\W]?icing)[_\\W]?(?:ai|automat|predict)",
      "\\b(?:train|rail|metro)[_\\W]?(?:automat|ato|atp|autonomous|collision|brake|emergency)[_\\W]?(?:ai|model|predict)",
      "\\b(?:marine|maritime|vessel|ship)[_\\W]?(?:autonomous|collision|anti[_\\W]?collision|autopilot|dynamic[_\\W]?position)",
      "\\b(?:lift|elevator|escalator|cableway)[_\\W]?(?:safety|emergency|brake|fault)[_\\W]?(?:ai|predict|classif)",
      "\\b(?:tire|tyre|brake|airbag|esp|abs|stability[_\\W]?control)[_\\W]?(?:ai|predict|model|classif)",
      "(?:detect|classify|predict|avoid)[^\\\"\\\\n]{0,30}(?:pedestrian|cyclist|obstacle|collision|lane)"
    ],
    "articles": [
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15"
    ],
    "category": "Safety Components",
    "description": "Safety components under Union harmonisation legislation",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "high"
  },
  "transportation": {
    "patterns": [
      "autonomous[_\\W]?(?:vehicle|driving|car|bus|truck|shuttle)",
      "self[_\\W]?driv(?:ing|en|erless)",
      "driverless",
      "railway[_\\W]?(?:signal|control|dispatch|automat)",
      "(?:metro|subway|tram)[_\\W]?(?:signal|dispatch|control|automat)",
      "(?:air[_\\W]?traffic|atc)[_\\W]?(?:control|manage|dispatch)",
      "(?:maritime|vessel|port)[_\\W]?(?:traffic|autonom|navigation)",
      "adas",
      "(?:autopilot|auto[_\\W]?pilot)"
    ],
    "articles": [],
    "category": "Transportation (Korea AI Basic Act Art 33)",
    "description": "AI in operation of transport conveyances",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "high"
  },
  "housing": {
    "patterns": [
      "tenant[_\\W]?(?:screen|scor|risk|background|check|reject|approv|rank|select)",
      "(?:screen|score|rank|approve|deny|reject)[_\\W]?tenants?",
      "rental[_\\W]?(?:applic|decision|screen|approv|deny|eligib|risk|scor)",
      "(?:housing|apartment|rental)[_\\W]?(?:allocat|assign|decision|eligib|waitlist|priorit)",
      "(?:fair[_\\W]?housing|housing[_\\W]?discriminat)",
      "(?:eviction|evict)[_\\W]?(?:predict|risk|scor|model|decision)",
      "property[_\\W]?(?:valuat|apprais)[_\\W]?(?:ai|model|automat|predict|algorithm)",
      "(?:mortgage|home[_\\W]?loan)[_\\W]?(?:approv|deny|decision|risk|scor|automat|algorithm)",
      "(?:screen|score|approve|deny|rank)[^\"\\n]{0,30}(?:tenant|rental|housing|eviction)"
    ],
    "articles": [],
    "category": "Housing (Colorado SB 26-189)",
    "description": "Housing and residential real estate decisions",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "high"
  }
};

const LIMITED_RISK_PATTERNS = {
  "chatbots": {
    "patterns": [
      "\\bchatbot",
      "conversational.?ai",
      "conversational.?model",
      "virtual.?assist",
      "dialogue.?system",
      "support.?bot\\b"
    ],
    "article": "50",
    "description": "Chatbots and conversational AI",
    "confidence": "high",
    "likelihood": "high",
    "impact": "medium"
  },
  "emotion_recognition": {
    "patterns": [
      "emotion.?recogn",
      "sentiment.?analy",
      "affect.?detect",
      "mood.?analy"
    ],
    "article": "50",
    "description": "Emotion recognition systems",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "medium"
  },
  "biometric_categorisation": {
    "patterns": [
      "\\bage.?estimat",
      "\\bgender.?detect",
      "\\bdemographic.?analy"
    ],
    "article": "50",
    "description": "Biometric categorisation (non-sensitive)",
    "confidence": "high",
    "likelihood": "high",
    "impact": "medium"
  },
  "synthetic_content": {
    "patterns": [
      "deepfake",
      "synthetic.?media",
      "face.?swap",
      "voice.?clon",
      "ai[\\s_-]generated[\\s_-]image",
      "text[\\s_-]to[\\s_-]image",
      "generate_(?:deepfake|synthetic)",
      "image_generat(?:or|ion)",
      "\\.Image\\.create\\b",
      "generate.?image\\b"
    ],
    "article": "50",
    "description": "Synthetic content generation",
    "confidence": "high",
    "likelihood": "high",
    "impact": "medium"
  }
};

const AI_SECURITY_PATTERNS = {
  "unsafe_deserialization": {
    "patterns": [
      "pickle\\.load\\b(?!s)",
      "pickle\\.loads",
      "torch\\.load\\s*\\((?![^)]*weights_only\\s*=\\s*True)[^)]*\\)",
      "joblib\\.load",
      "dill\\.load"
    ],
    "owasp": "LLM05",
    "articles": [
      "15"
    ],
    "description": "Unsafe model deserialization \u2014 arbitrary code execution risk",
    "severity": "high",
    "remediation": "Use safetensors format or torch.load(path, weights_only=True). Never unpickle untrusted model files.",
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "prompt_injection_vulnerable": {
    "patterns": [
      "f['\\\"][^'\\\"]{0,500}\\{[^}]{0,200}user[^}]{0,200}\\}[^'\\\"]{0,500}['\\\"][^\\n]{0,500}(?:messages|prompt|system)",
      "\\.format\\([^)]{0,500}user[^)]{0,500}\\)[^\\n]{0,500}(?:messages|prompt|content)",
      "\\+\\s*(?:user_input|user_message|user_query|request\\.body|req\\.body|request\\.json|req\\.json)[^\\n]{0,500}(?:messages|prompt)",
      "request\\.(?:form|args|json|values)\\[?['\\\"]?[a-z_]+['\\\"]?\\]?[^\\n]{0,300}(?:messages|prompt|completion|invoke)",
      "messages\\s*=\\s*\\[\\s*\\{[^}]*['\\\"]content['\\\"]\\s*:\\s*(?:request\\.|req\\.|user_input|user_message)"
    ],
    "owasp": "LLM01",
    "articles": [
      "15"
    ],
    "description": "User input directly concatenated into LLM prompt \u2014 prompt injection risk (direct)",
    "severity": "high",
    "remediation": "Use structured prompt templates with input sanitisation. Use a guardrails library (NeMo Guardrails, Lakera Guard, LLM Guard, Rebuff, Guardrails AI). Never concatenate raw user input into system prompts. OWASP LLM01:2025.",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "prompt_injection_indirect": {
    "patterns": [
      "['\\\"]content['\\\"]\\s*:\\s*(?:requests\\.get|httpx\\.get|urlopen)\\([^)]*\\)\\.(?:text|content|json\\(\\))",
      "['\\\"]content['\\\"]\\s*:\\s*(?:open\\([^)]+\\)\\.read\\(\\)|Path\\([^)]+\\)\\.read_text\\(\\))",
      "(?:chain|llm|model|llm_chain|qa_chain)\\.invoke\\s*\\(\\s*\\{[^}]*['\\\"]context['\\\"]\\s*:\\s*(?:retriever|vectorstore|loader)",
      "messages\\.append\\s*\\(\\s*\\{[^}]*['\\\"]content['\\\"]\\s*:\\s*(?:requests\\.get|httpx\\.get|urlopen|open\\(|Path\\()",
      "(?:llm|client|model)\\.(?:invoke|chat\\.completions\\.create)\\([^)]*(?:requests\\.get|httpx\\.get|urlopen)\\([^)]*\\)\\.(?:text|content)",
      "f['\\\"][^'\\\"]{0,500}\\{(?:retrieved|context|page_content|doc_text|web_content|fetched|scraped)[^}]{0,200}\\}[^'\\\"]{0,500}['\\\"][^\\n]{0,300}(?:messages|prompt|invoke)"
    ],
    "owasp": "LLM01",
    "articles": [
      "15"
    ],
    "description": "Untrusted external content flows into LLM prompt without sanitisation \u2014 indirect prompt injection risk (OWASP LLM01:2025 emphasises this vector)",
    "severity": "high",
    "remediation": "Treat all external content (web pages, documents, retrieval results, emails) as untrusted. Apply a guardrails layer (NeMo Guardrails, LLM Guard, Lakera Guard, Rebuff, Guardrails AI). Use spotlighting or context delimiters that the model is trained to respect. OWASP LLM01:2025.",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "prompt_injection_tool_output": {
    "patterns": [
      "(?:messages\\.append|messages\\s*\\+=|prompt\\s*=)[^\\n]{0,200}subprocess\\.(?:run|check_output|Popen)",
      "(?:llm|chain|client)\\.invoke\\s*\\([^)]*subprocess\\.(?:run|check_output|Popen)",
      "messages\\.append\\s*\\(\\s*\\{[^}]*['\\\"]content['\\\"]\\s*:\\s*(?:tool_result|tool_output|function_result|action_result|observation)",
      "(?:AgentExecutor|create_react_agent|create_tool_calling_agent)\\([^)]*verbose\\s*=\\s*True[^)]*\\)[^\\n]{0,300}invoke\\("
    ],
    "owasp": "LLM01",
    "articles": [
      "15"
    ],
    "description": "Tool / agent / shell output passed to LLM without validation \u2014 agentic prompt injection risk",
    "severity": "high",
    "remediation": "Treat tool outputs as untrusted user input. Validate structure (JSON schema), strip control tokens, apply a guardrails layer. Maps to OWASP Agentic ASI04 (control-flow hijacking). OWASP LLM01:2025.",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "no_output_validation": {
    "patterns": [
      "\\beval\\s*\\([^\\n]{0,500}(?:response|result|output|completion)",
      "\\bexec\\s*\\([^\\n]{0,500}(?:response|result|output|completion)"
    ],
    "owasp": "LLM02",
    "articles": [
      "15"
    ],
    "description": "AI output used without validation \u2014 code injection risk",
    "severity": "critical",
    "remediation": "Never eval/exec AI model output. Validate and sanitise all AI-generated content before use.",
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "hardcoded_model_path": {
    "patterns": [
      "(?:from_pretrained|load_model|torch\\.load)\\s*\\(\\s*['\\\"]https?://",
      "(?:from_pretrained|load_model|torch\\.load)\\s*\\(\\s*['\\\"](?:/tmp|/var|C:\\\\)"
    ],
    "owasp": "LLM03",
    "articles": [
      "15"
    ],
    "description": "Model loaded from untrusted or hardcoded path \u2014 supply chain risk",
    "severity": "medium",
    "remediation": "Use model registries (HuggingFace Hub, MLflow) with integrity verification. Pin model revisions.",
    "confidence": "high",
    "likelihood": "medium",
    "impact": "medium"
  },
  "unbounded_token_generation": {
    "patterns": [
      "max_tokens\\s*[:=]\\s*(?:None|0|-1|999999|1000000)"
    ],
    "owasp": "LLM10",
    "articles": [
      "15"
    ],
    "description": "Unbounded token generation \u2014 cost and resource exhaustion risk",
    "severity": "medium",
    "remediation": "Set explicit max_tokens limit. Add cost monitoring and rate limiting.",
    "confidence": "high",
    "likelihood": "medium",
    "impact": "medium"
  },
  "missing_temperature_control": {
    "patterns": [
      "(?<!room_)(?<!water_)(?<!cpu_)(?<!body_)(?<!core_)(?<!ambient_)temperature\\s*[:=]\\s*(?:[1-9]\\.\\d|[2-9]\\.0|[1-9]\\d+\\.)"
    ],
    "owasp": "LLM09",
    "articles": [
      "15"
    ],
    "description": "High temperature setting (>=1.0) \u2014 review whether hallucination risk is acceptable for this use case",
    "severity": "low",
    "remediation": "Use temperature=0 or 0.1 for factual/production tasks. Reserve high temperature for creative tasks.",
    "confidence": "high",
    "likelihood": "low",
    "impact": "low"
  },
  "no_error_handling_ai_call": {
    "patterns": [
      "(?:chat\\.completions\\.create|messages\\.create|llm\\.invoke)\\s*\\("
    ],
    "owasp": "LLM06",
    "articles": [
      "15"
    ],
    "description": "AI API call detected \u2014 verify error handling is in place",
    "severity": "low",
    "remediation": "Ensure AI API calls are wrapped in try/except. Handle rate limits, timeouts, and malformed responses. Required by CRA Annex I secure-by-design.",
    "confidence": "low",
    "likelihood": "low",
    "impact": "medium"
  },
  "exposed_api_key_env": {
    "patterns": [
      "(?:OPENAI_API_KEY|ANTHROPIC_API_KEY)\\s*[:=]\\s*['\\\"]sk-[a-zA-Z0-9]"
    ],
    "owasp": "LLM06",
    "articles": [
      "15"
    ],
    "description": "AI API key appears hardcoded \u2014 credential exposure risk",
    "severity": "critical",
    "remediation": "Use environment variables or a secrets manager. Never commit API keys to source code. CRA Annex I (2)(c) requires access control.",
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "sensitive_info_disclosure": {
    "patterns": [
      "(?:messages|prompt|content)\\s*[:=][^\\n]{0,300}(?:ssn|social_security|date_of_birth|passport|credit_card|phone_number|email_address)",
      "(?:chat\\.completions|messages\\.create|llm\\.invoke)\\s*\\([^\\n]{0,500}(?:personal_data|pii|user_email|user_phone|patient_record|medical_record)",
      "(?:return|response|send|render)\\s[^\\n]{0,80}(?<![A-Z])(?:completion|ai_response|llm_output|model_output)[^\\n]{0,80}(?:pii|personal|ssn|email|phone|patient|medical|credit_card|sensitive)"
    ],
    "owasp": "LLM02",
    "articles": [
      "15"
    ],
    "description": "PII or sensitive data flows into or out of LLM without redaction \u2014 information disclosure risk",
    "severity": "high",
    "remediation": "Scrub PII before sending to model APIs and filter model output before returning to users. Use libraries like presidio, scrubadub, or pii-catcher. OWASP LLM02:2025.",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "supply_chain_model": {
    "patterns": [
      "from_pretrained\\s*\\([^)]*trust_remote_code\\s*=\\s*True",
      "(?:from_pretrained|load_model|torch\\.load)\\s*\\(\\s*(?:user_input|request\\.|args\\.|sys\\.argv)",
      "subprocess[^\\n]{0,200}pip\\s+install[^\\n]{0,200}(?:--index-url|--extra-index-url|git\\+https?://)"
    ],
    "owasp": "LLM03",
    "articles": [
      "15"
    ],
    "description": "Model loaded from untrusted source or with unsafe deserialisation \u2014 supply chain attack risk",
    "severity": "high",
    "remediation": "Pin model revisions and verify checksums. Never use trust_remote_code=True in production. Use safetensors format. Audit third-party model sources. OWASP LLM03:2025.",
    "confidence": "high",
    "likelihood": "medium",
    "impact": "high"
  },
  "data_poisoning": {
    "patterns": [
      "(?:\\.fit|\\.train|fine_tune|fine_tuning)\\s*\\([^\\n]{0,300}(?:user_input|request\\.|upload|user_data|submitted)",
      "(?:training_data|train_dataset|dataset)\\s*[:=][^\\n]{0,200}(?:request\\.|upload|user_submit|crowd_sourc)",
      "(?:rlhf|dpo|human_feedback|reward_model)\\s*[:=][^\\n]{0,200}(?:request\\.|user_|crowd|unvalidat)"
    ],
    "owasp": "LLM04",
    "articles": [
      "15"
    ],
    "description": "Model trained or fine-tuned on unvalidated user-submitted data \u2014 data poisoning risk",
    "severity": "high",
    "remediation": "Validate and sanitise all training data. Implement data provenance tracking, statistical anomaly detection, and human review for training corpora. OWASP LLM04:2025.",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "high"
  },
  "excessive_agency": {
    "patterns": [
      "(?:exec|eval)\\s*\\(\\s*(?:ai_response|llm_output|completion|model_output|agent_output|result\\[?['\\\"]?(?:code|command|action))",
      "(?:subprocess\\.(?:run|call|Popen)|os\\.system|os\\.popen)\\s*\\([^\\n]{0,200}(?:ai_response|llm_output|completion|model_output|agent_output)",
      "(?:auto_execute|auto_approve|auto_confirm|allow_dangerous)\\s*[:=]\\s*True",
      "(?:open\\([^)]*,\\s*['\\\"]w|write_file|save_file)\\s*[^\\n]{0,200}(?:ai_response|llm_output|completion|model_output|agent_output)"
    ],
    "owasp": "LLM06",
    "articles": [
      "15"
    ],
    "description": "AI agent executes actions (code, shell, filesystem) without human confirmation \u2014 excessive agency risk",
    "severity": "critical",
    "remediation": "Require human-in-the-loop approval for all destructive or privileged actions. Implement least-privilege tool permissions and action allowlists. OWASP LLM06:2025.",
    "confidence": "high",
    "likelihood": "high",
    "impact": "high"
  },
  "system_prompt_leakage": {
    "patterns": [
      "(?:const|let|var)\\s+(?:system_prompt|systemPrompt|SYSTEM_PROMPT|system_message|systemMessage)\\s*=\\s*['\\\"`]",
      "(?:response|res|jsonify|json\\.dumps)\\s*\\([^\\n]{0,200}(?:system_prompt|system_message|instructions)",
      "(?:data-prompt|data-system|data-instructions)\\s*=\\s*['\\\"]",
      "(?:print|console\\.log|logger\\.(?:info|debug))\\s*\\([^\\n]{0,200}(?:system_prompt|system_message|system_instructions)"
    ],
    "owasp": "LLM07",
    "articles": [
      "15"
    ],
    "description": "System prompt exposed in client code, API response, or logs \u2014 prompt leakage risk",
    "severity": "medium",
    "remediation": "Keep system prompts server-side only. Never return them in API responses or log them. Use prompt references/IDs instead of inline prompt text. OWASP LLM07:2025.",
    "confidence": "high",
    "likelihood": "medium",
    "impact": "medium"
  },
  "rag_poisoning": {
    "patterns": [
      "(?:add_documents|add_texts|upsert|insert)\\s*\\([^\\n]{0,300}(?:user_upload|request\\.files|uploaded_file|user_document|request\\.body)",
      "(?:embed|embed_documents|embed_query|get_embedding)\\s*\\([^\\n]{0,200}(?:user_input|request\\.|upload|untrusted)",
      "@(?:app|router)\\.(?:post|put)\\s*\\((?![^\\n]{0,500}(?:auth|login_required|Depends|require_auth|verify_token|api_key))[^\\n]{0,200}(?:embed|ingest|index|vector)[^\\n]{10,300}$"
    ],
    "owasp": "LLM08",
    "articles": [
      "15"
    ],
    "description": "Untrusted content ingested into vector store without validation \u2014 RAG poisoning risk",
    "severity": "high",
    "remediation": "Validate and sanitise all documents before embedding. Implement access controls on vector store write endpoints. Use content filtering and metadata provenance tracking. OWASP LLM08:2025.",
    "confidence": "medium",
    "likelihood": "high",
    "impact": "high"
  },
  "no_grounding": {
    "patterns": [
      "(?:fact|answer|knowledge|information)\\s*[:=]\\s*(?:completion|ai_response|llm_output|model_output|response\\.choices)",
      "(?:diagnosis|legal_advice|financial_advice|medical_recommendation|treatment_plan)\\s*[:=][^\\n]{0,200}(?:completion|ai_response|llm_output|chat\\.completions|messages\\.create)",
      "(?:messages|prompt)\\s*[:=](?![^\\n]{0,500}(?:cite|source|reference|ground|retriev|verify|fact.?check))[^\\n]{0,500}(?:provide facts|answer accurately|give information|tell me about)"
    ],
    "owasp": "LLM09",
    "articles": [
      "15"
    ],
    "description": "LLM output used as factual information without grounding or verification \u2014 misinformation risk",
    "severity": "medium",
    "remediation": "Implement retrieval-augmented generation (RAG) for factual tasks. Require citations and source attribution. Add fact-checking or grounding verification before presenting LLM output as fact. OWASP LLM09:2025.",
    "confidence": "medium",
    "likelihood": "medium",
    "impact": "medium"
  }
};

const AI_INDICATORS = {
  "libraries": [
    "tensorflow",
    "torch",
    "pytorch",
    "transformers",
    "langchain",
    "openai",
    "anthropic",
    "sklearn",
    "scikit.?learn",
    "keras",
    "xgboost",
    "lightgbm",
    "huggingface",
    "spacy",
    "nltk",
    "onnx",
    "onnxruntime",
    "brain\\.js",
    "@tensorflow/tfjs",
    "@anthropic-ai/sdk",
    "@langchain",
    "transformers\\.js",
    "litellm",
    "crewai",
    "autogen",
    "pyautogen",
    "haystack",
    "smolagents",
    "ollama",
    "google\\.generativeai",
    "mistralai",
    "groq",
    "dspy",
    "vertexai",
    "semantic_kernel",
    "instructor",
    "pydantic_ai",
    "together\\b",
    "replicate",
    "google\\.adk",
    "claude_agent_sdk",
    "openai\\.agents",
    "langgraph",
    "@ai-sdk",
    "ai-sdk",
    "@mastra",
    "cohere",
    "vllm",
    "fireworks",
    "autogpt",
    "babygpt",
    "baby.?agi",
    "metagpt",
    "memgpt",
    "letta",
    "guidance",
    "import\\s+guidance",
    "marvin",
    "import\\s+marvin",
    "semantic.?router",
    "portkey.?ai",
    "portkey",
    "org\\.springframework\\.ai",
    "import\\s+jax\\b",
    "from\\s+jax\\b",
    "import\\s+flax\\b",
    "llama.?index",
    "from\\s+llama_index",
    "import\\s+gradio\\b",
    "gr\\.Interface",
    "import\\s+fastai\\b",
    "from\\s+fastai\\b",
    "sentence.?transformers",
    "import\\s+deepspeed\\b",
    "from\\s+accelerate\\b",
    "import\\s+accelerate\\b",
    "from\\s+datasets\\b",
    "import\\s+evaluate\\b",
    "import\\s+catboost\\b",
    "from\\s+ultralytics\\b",
    "import\\s+ultralytics\\b",
    "import\\s+openvino\\b",
    "import\\s+tensorrt\\b",
    "from\\s+detectron2\\b",
    "import\\s+chromadb\\b",
    "from\\s+chromadb\\b",
    "pinecone",
    "import\\s+weaviate\\b",
    "import\\s+qdrant",
    "from\\s+qdrant",
    "import\\s+milvus\\b",
    "pymilvus",
    "import\\s+faiss\\b",
    "tflite",
    "tf\\.lite",
    "tensorflow.?lite",
    "coremltools",
    "\\.mlmodel",
    "mediapipe",
    "com\\.google\\.mlkit",
    "mlkit",
    "executorch",
    "mlflow",
    "wandb",
    "weights.?and.?biases",
    "dvc\\.yaml",
    "import\\s+ray",
    "ray\\.serve",
    "bentoml",
    "from\\s+diffusers\\s+import",
    "diffusers",
    "elevenlabs",
    "ELEVEN_API_KEY",
    "import\\s+whisper",
    "openai\\.audio",
    "from\\s+bark\\s+import",
    "from\\s+TTS\\s+import",
    "coqui"
  ],
  "model_files": [
    "\\.onnx",
    "\\.pt\\b",
    "\\.pth\\b",
    "\\.pkl\\b",
    "\\.joblib\\b",
    "\\.h5\\b",
    "\\.hdf5\\b",
    "\\.safetensors",
    "\\.gguf\\b",
    "\\.ggml\\b"
  ],
  "api_endpoints": [
    "api\\.openai\\.com",
    "api\\.anthropic\\.com",
    "generativelanguage\\.googleapis\\.com",
    "api\\.cohere\\.ai",
    "api\\.mistral\\.ai",
    "openrouter\\.ai",
    "OPENROUTER_API_KEY"
  ],
  "ml_patterns": [
    "model\\.fit",
    "model\\.train",
    "model\\.predict",
    "embedding",
    "vectorstore",
    "llm\\.invoke",
    "chat\\.completions",
    "messages\\.create",
    "from_pretrained",
    "fine.?tune",
    "neural.?network",
    "deep.?learning",
    "machine.?learning"
  ],
  "domain_keywords": [
    "\\bfacial\\s+recognition\\b",
    "\\bface\\s+recognition\\b",
    "\\bface\\s+detection\\b",
    "\\bfingerprint\\s+recognition\\b",
    "\\bvoice\\s+recognition\\b",
    "\\bvoice\\s+identification\\b",
    "\\bbiometric\\s+identification\\b",
    "\\bbiometric\\s+authentication\\b",
    "\\bbiometric\\s+scanning\\b",
    "\\benergy\\s+grid\\b",
    "\\bwater\\s+supply\\b",
    "\\btraffic\\s+control\\b",
    "\\belectricity\\s+manage",
    "\\bstudent\\s+assess",
    "\\badmission\\s+decision\\b",
    "\\bexam\\s+scor",
    "\\bcv\\s+screen",
    "\\bresume\\s+screen",
    "\\bresume\\s+filt",
    "\\bhiring\\s+decision\\b",
    "\\brecruitment\\s+ai\\b",
    "\\bcandidate\\s+rank",
    "\\bcandidate\\s+screen",
    "\\bapplicant\\s+scor",
    "\\bcredit\\s+scor",
    "\\bcreditworth",
    "\\bloan\\s+decision\\b",
    "\\bloan\\s+approv",
    "\\binsurance\\s+pric",
    "\\bbenefit\\s+eligib",
    "\\bemergency\\s+dispatch",
    "\\bpolygraph\\b",
    "\\blie\\s+detect",
    "\\bborder\\s+control\\b",
    "\\bvisa\\s+application\\b",
    "\\basylum\\s+application\\b",
    "\\bimmigration\\s+decision\\b",
    "\\bjudicial\\s+decision\\b",
    "\\bcourt\\s+rul",
    "\\bsentenc(?:ing|e)\\b",
    "\\bmedical\\s+diagnosis\\b",
    "\\bclinical\\s+decision\\b",
    "\\bpatient\\s+triage\\b",
    "\\btreatment\\s+recommend",
    "\\bautonomous\\s+vehicle\\b",
    "\\bself[\\s-]driving\\s+car\\b",
    "\\bdriverless\\s+car\\b",
    "\\bautonomous\\s+driv",
    "\\baviation\\s+safety\\b",
    "\\bemotion\\s+detection\\b",
    "\\bemotion\\s+recognition\\b",
    "\\bchatbot\\b",
    "\\bvirtual\\s+assistant\\b",
    "\\bconversational\\s+ai\\b",
    "\\bdeepfake\\b",
    "\\bface\\s+swap\\b",
    "\\bsynthetic\\s+media\\b",
    "\\bpredictive\\s+policing\\b",
    "\\bautomated\\s+decision\\b",
    "\\bautomated\\s+assessment\\b",
    "\\bai\\s+system\\b",
    "\\bai\\s+model\\b",
    "\\bai[\\s-]powered\\b",
    "\\bai\\b"
  ]
};

const GOVERNANCE_OBSERVATIONS = {
  "training_data": {
    "patterns": [
      "\\.fit\\(",
      "\\.train\\(",
      "training_data",
      "train_test_split",
      "\\.csv",
      "read_csv",
      "load_data"
    ],
    "article": "10",
    "observation": "Training data detected \u2014 Article 10 requires data to be relevant, representative, and examined for biases."
  },
  "prediction_without_review": {
    "patterns": [
      "\\.predict\\(",
      "\\.predict_proba\\("
    ],
    "article": "14",
    "observation": "Model predictions detected \u2014 Article 14 requires human oversight with ability to override or reverse AI outputs."
  },
  "automated_decision_function": {
    "patterns": [
      "def\\s+\\w*(screen|filter|rank|score|decide|reject|accept|approve|deny)\\w*\\s*\\(",
      "function\\s+\\w*(?:screen|filter|rank|score|decide|reject|accept|approve|deny)\\w*\\s*\\(",
      "(?:const|let|var)\\s+\\w*(?:screen|filter|rank|score|decide|reject|accept|approve|deny)\\w*\\s*=\\s*(?:async\\s+)?(?:\\([^)]*\\)|\\w+)\\s*=>"
    ],
    "article": "13",
    "observation": "Automated decision function detected \u2014 Article 13 requires transparency to deployers about capabilities and limitations."
  },
  "no_logging": {
    "patterns": [
      "logging",
      "\\.log\\(",
      "audit",
      "logger"
    ],
    "article": "12",
    "observation": null,
    "absence_observation": "No logging detected \u2014 Article 12 requires automatic recording of events for traceability."
  },
  "rag_pipeline": {
    "patterns": [
      "(?:chromadb|pinecone|weaviate|qdrant|pgvector|faiss|milvus)",
      "(?:VectorStore|vectorStore|vector_store|vector_db)",
      "(?:similaritySearch|similarity_search|from_documents|from_texts|addDocuments|add_documents)",
      "(?:asRetriever|as_retriever|getRelevantDocuments|get_relevant_documents)",
      "(?:createEmbedding|create_embedding|embedDocuments|embed_documents|embedQuery|embed_query)",
      "(?:text.embedding|embedding.model|embedding.dimension|OpenAIEmbeddings)"
    ],
    "article": "10",
    "observation": "RAG (retrieval-augmented generation) pipeline detected \u2014 external data is injected at inference time. Article 10 data governance requirements apply to retrieved data, not only training data. Consider: data source provenance, freshness, access controls, and bias in the retrieval corpus."
  },
  "local_inference": {
    "patterns": [
      "localhost:11434",
      "ollama\\.generate\\(|ollama\\.chat\\(",
      "(?:onnxruntime|onnx\\.load|InferenceSession)",
      "llama\\.cpp|llama_cpp|llamacpp",
      "ctransformers",
      "\\.gguf\\b|\\.ggml\\b"
    ],
    "article": "15",
    "observation": "Local model inference detected (Ollama, ONNX, llama.cpp, or GGUF model files). Article 15 accuracy and robustness obligations still apply to locally deployed models. Local deployment does not exempt from conformity requirements \u2014 it changes the deployment context."
  }
};

const BIAS_RISK_PATTERNS = {
  "protected_class_as_feature": {
    "patterns": [
      "(?:df|X|features|X_train|X_test|train_data|dataset|data)\\s*\\[\\s*['\"](?:race|ethnicity|gender|sex\\b|religion|nationality|disability|marital.status|national.origin)",
      "['\"]\\s*(?:race|ethnicity|religion|nationality|disability|marital.status|national.origin)\\s*['\"]\\s*,",
      ",\\s*['\"]\\s*(?:race|ethnicity|religion|nationality|disability|marital.status|national.origin)\\s*['\"]\\s*[\\]\\)]",
      "\\b(?:race|ethnicity|nationality|disability)(?:_col|_column|_feature|_var|_field)\\b"
    ],
    "article": "10",
    "article_clause": "10(5)",
    "description": "Protected class attribute detected as potential model feature",
    "observation": "Protected class attribute (race, ethnicity, religion, nationality, disability) detected in a data or ML context. Article 10(5) requires training data to be examined for biases for high-risk AI systems. This flag does not mean your model is biased \u2014 it means: (1) document why this attribute is included, (2) perform disparate impact analysis before deploying in employment, credit, or essential services, (3) check whether the system falls under Annex III obligations.",
    "eu_ai_act_basis": "Article 10(5): training data must be examined for possible biases that could cause prohibited discrimination. Recital 44: particular attention to elimination of discriminatory effects."
  },
  "missing_fairness_evaluation": {
    "patterns": [
      "fairlearn",
      "aif360",
      "themis[_\\-]ml",
      "fairness[_\\-]indicator",
      "equalized[_\\.]odds",
      "demographic[_\\.]parity",
      "disparate[_\\.]impact",
      "audit[_\\-]ai"
    ],
    "article": "10",
    "article_clause": "10(5)",
    "description": "No fairness evaluation detected",
    "observation": null,
    "absence_observation": "No fairness evaluation library detected alongside protected class attributes. Article 10(5) requires training data to be examined for biases. Consider: fairlearn, AIF360, or manual disparate impact analysis before deploying in employment, credit, or essential services contexts."
  }
};

const GPAI_TRAINING_PATTERNS = [
  "model\\.fit\\b",
  "model\\.train\\b",
  "\\.train\\(\\)",
  "trainer\\.train",
  "fine.?tun",
  "from_pretrained.{0,30}train",
  "training_args",
  "TrainingArguments",
  "Trainer\\(",
  "SFTTrainer",
  "\\.compile\\(.{0,30}optimizer",
  "backpropagat",
  "torch\\.optim",
  "tf\\.keras\\.optimizers",
  "\\blora\\b",
  "\\bqlora\\b",
  "\\bpeft\\b"
];

// =====================================================================
// Pattern compilation — pre-compile all patterns at load time
// =====================================================================

function _compilePatterns(patternsObj) {
  const compiled = {};
  for (const [name, cfg] of Object.entries(patternsObj)) {
    compiled[name] = cfg.patterns.map(p => {
      try { return new RegExp(p); }
      catch(e) { return null; }
    }).filter(Boolean);
  }
  return compiled;
}

function _compilePatternsIC(patternsObj) {
  const compiled = {};
  for (const [name, cfg] of Object.entries(patternsObj)) {
    compiled[name] = cfg.patterns.map(p => {
      try { return new RegExp(p, 'i'); }
      catch(e) { return null; }
    }).filter(Boolean);
  }
  return compiled;
}

function _compileList(patterns) {
  return patterns.map(p => {
    try { return new RegExp(p, 'i'); }
    catch(e) { return null; }
  }).filter(Boolean);
}

function _compileIndicators(indicatorsObj) {
  const compiled = {};
  for (const [cat, patterns] of Object.entries(indicatorsObj)) {
    compiled[cat] = patterns.map(p => {
      try { return new RegExp(p); }
      catch(e) { return null; }
    }).filter(Boolean);
  }
  return compiled;
}

const _PROHIBITED_C = _compilePatterns(PROHIBITED_PATTERNS);
const _HIGH_RISK_C = _compilePatterns(HIGH_RISK_PATTERNS);
const _LIMITED_RISK_C = _compilePatterns(LIMITED_RISK_PATTERNS);
const _AI_SECURITY_C = _compilePatternsIC(AI_SECURITY_PATTERNS);
const _AI_INDICATORS_C = _compileIndicators(AI_INDICATORS);
const _GOVERNANCE_C = _compilePatterns(GOVERNANCE_OBSERVATIONS);
const _BIAS_RISK_C = _compilePatternsIC(BIAS_RISK_PATTERNS);
const _GPAI_TRAINING_C = _compileList(GPAI_TRAINING_PATTERNS);


// =====================================================================
// Confidence scoring — ported from classify_risk.py
// =====================================================================

const _CONF_BASE = { prohibited: 75, high_risk: 55, limited_risk: 40, minimal_risk: 15 };

function _confScore(tier, n, hasAi) {
  const base = _CONF_BASE[tier] || 10;
  const matchBonus = Math.min(n * 8, 15);
  const aiBonus = hasAi ? 10 : 0;
  return Math.min(base + matchBonus + aiBonus, 100);
}


// =====================================================================
// Comment stripping — ported from classify_risk.py
// =====================================================================

function detectLanguage(text, filename) {
  if (filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const map = {
      py: 'python', pyw: 'python',
      js: 'javascript', jsx: 'javascript', mjs: 'javascript', cjs: 'javascript',
      ts: 'typescript', tsx: 'typescript',
      java: 'java', kt: 'java', kts: 'java', scala: 'java',
      go: 'go', rs: 'rust',
      c: 'c', h: 'c', cpp: 'cpp', cc: 'cpp', cxx: 'cpp', hpp: 'cpp',
      rb: 'python', r: 'python',
      yml: 'python', yaml: 'python',
      sh: 'python', bash: 'python', zsh: 'python',
    };
    if (map[ext]) return map[ext];
  }
  if (/^#!.*python/m.test(text)) return 'python';
  if (/^#!.*node/m.test(text)) return 'javascript';
  if (/^package\s+\w+/m.test(text)) return 'go';
  if (/^import\s+\w+|^from\s+\w+\s+import/m.test(text)) return 'python';
  if (/\bfunction\s+\w+|const\s+\w+\s*=|=>\s*\{/m.test(text)) return 'javascript';
  if (/\bfn\s+\w+|let\s+mut\s+/m.test(text)) return 'rust';
  if (/public\s+class\s+|private\s+void\s+/m.test(text)) return 'java';
  return 'python';
}

function stripComments(text, language) {
  const lines = text.split('\n');
  const result = [];
  let inBlock = false;

  for (const line of lines) {
    const s = line.trim();

    if (language === 'python') {
      if (s.startsWith('#')) { result.push(''); continue; }
      // Simple inline # strip (outside quotes)
      if (s.includes('#')) {
        let inStr = false, strCh = null, cut = -1;
        for (let i = 0; i < line.length; i++) {
          const c = line[i];
          if ((c === '"' || c === "'") && !inStr) { inStr = true; strCh = c; }
          else if (c === strCh && inStr) {
            let bs = 0, j = i - 1;
            while (j >= 0 && line[j] === '\\') { bs++; j--; }
            if (bs % 2 === 0) inStr = false;
          } else if (c === '#' && !inStr) { cut = i; break; }
        }
        if (cut >= 0) { result.push(line.substring(0, cut)); continue; }
      }
    } else if (['javascript','typescript','java','go','rust','c','cpp'].includes(language)) {
      if (s.startsWith('//')) { result.push(''); continue; }
      if (s.startsWith('/*')) { inBlock = true; result.push(''); continue; }
      if (inBlock) {
        if (s.includes('*/')) inBlock = false;
        result.push('');
        continue;
      }
    }
    result.push(line);
  }
  return result.join('\n');
}


// =====================================================================
// AI indicator detection
// =====================================================================

function isAiRelated(text) {
  const check = text.toLowerCase();
  for (const rxList of Object.values(_AI_INDICATORS_C)) {
    for (const rx of rxList) {
      if (rx.test(check)) return true;
    }
  }
  return false;
}


// =====================================================================
// Core pattern matching — _check_patterns()
// =====================================================================

function _checkPatterns(compiledDict, patternsDict, text, strippedText) {
  const textLo = text.toLowerCase();
  const stripLo = strippedText ? strippedText.toLowerCase() : null;
  const matches = [];

  for (const [name, rxList] of Object.entries(compiledDict)) {
    let first = null;
    const allLines = [];

    for (const rx of rxList) {
      // Reset lastIndex for non-global regexes (safety)
      rx.lastIndex = 0;
      const m = rx.exec(textLo);
      if (m) {
        const lineNum = textLo.substring(0, m.index).split('\n').length;
        allLines.push(lineNum);
        if (first === null) {
          first = Object.assign({}, patternsDict[name], {
            indicator: name,
            match_line: lineNum,
          });
        }
      }
    }
    if (first !== null) {
      first.match_lines_all = allLines;
      matches.push(first);
    }
  }

  // Filter: keep only matches also in stripped (non-comment) text
  if (matches.length > 0 && stripLo !== null) {
    const confirmed = [];
    for (const m of matches) {
      const pats = m.patterns || (patternsDict[m.indicator] || {}).patterns || [];
      for (const p of pats) {
        try {
          if (new RegExp(p).test(stripLo)) { confirmed.push(m); break; }
        } catch(e) { /* skip */ }
      }
    }
    return confirmed;
  }
  return matches;
}


// =====================================================================
// Tier-specific checks
// =====================================================================

function _sortArticles(articles) {
  return [...articles].sort((a, b) => {
    const ai = parseInt(a, 10), bi = parseInt(b, 10);
    if (!isNaN(ai) && !isNaN(bi)) return ai - bi;
    if (!isNaN(ai)) return -1;
    if (!isNaN(bi)) return 1;
    return a.localeCompare(b);
  });
}

function _collectLines(matches) {
  const lines = [];
  for (const m of matches) {
    if (m.match_lines_all) lines.push(...m.match_lines_all);
    else if (m.match_line != null) lines.push(m.match_line);
  }
  return lines;
}

function checkProhibited(text, stripped) {
  const matches = _checkPatterns(_PROHIBITED_C, PROHIBITED_PATTERNS, text, stripped);
  if (matches.length === 0) return null;
  const primary = matches[0];
  return {
    tier: 'prohibited',
    confidence: matches.length >= 2 ? 'high' : 'medium',
    indicators_matched: matches.map(m => m.indicator),
    applicable_articles: [primary.article],
    category: 'Prohibited (Article 5)',
    description: primary.description,
    action: 'block',
    message: 'PROHIBITED: ' + primary.description,
    exceptions: primary.exceptions || null,
    confidence_score: _confScore('prohibited', matches.length, isAiRelated(text)),
    match_lines: _collectLines(matches),
  };
}

function checkHighRisk(text, stripped) {
  const matches = _checkPatterns(_HIGH_RISK_C, HIGH_RISK_PATTERNS, text, stripped);
  if (matches.length === 0) return null;
  const arts = new Set();
  for (const m of matches) { if (m.articles) m.articles.forEach(a => arts.add(a)); }
  const primary = matches[0];
  return {
    tier: 'high_risk',
    confidence: matches.length >= 2 ? 'high' : 'medium',
    indicators_matched: matches.map(m => m.indicator),
    applicable_articles: _sortArticles(arts),
    category: primary.category,
    description: primary.description,
    action: 'allow_with_requirements',
    message: 'HIGH-RISK: ' + primary.description + ' - Articles ' + _sortArticles(arts).join(', '),
    confidence_score: _confScore('high_risk', matches.length, true),
    match_lines: _collectLines(matches),
  };
}

function checkLimitedRisk(text, stripped) {
  const matches = _checkPatterns(_LIMITED_RISK_C, LIMITED_RISK_PATTERNS, text, stripped);
  if (matches.length === 0) return null;
  const primary = matches[0];
  return {
    tier: 'limited_risk',
    confidence: matches.length >= 2 ? 'high' : 'medium',
    indicators_matched: matches.map(m => m.indicator),
    applicable_articles: ['50'],
    category: 'Limited Risk (Article 50)',
    description: primary.description,
    action: 'allow_with_transparency',
    message: 'LIMITED-RISK: ' + primary.description,
    confidence_score: _confScore('limited_risk', matches.length, true),
    match_lines: _collectLines(matches),
  };
}


// =====================================================================
// AI security check
// =====================================================================

function checkAiSecurity(text) {
  const findings = [];
  const lines = text.split('\n');

  for (const [name, rxList] of Object.entries(_AI_SECURITY_C)) {
    const cfg = AI_SECURITY_PATTERNS[name];
    let found = false;

    for (const rx of rxList) {
      if (found) break;
      let inDoc = false;
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (line.length > 2000) continue;
        const s = line.trim();
        if (s.startsWith('#') || s.startsWith('//')) continue;
        if (s.includes('"""') || s.includes("'''")) {
          const cnt = (s.match(/\"\"\"/g) || []).length + (s.match(/'''/g) || []).length;
          if (cnt === 1) inDoc = !inDoc;
          continue;
        }
        if (inDoc) continue;
        if (s.startsWith('Args:') || s.startsWith('Returns:') ||
            s.startsWith('Example:') || s.startsWith('>>>') || s.startsWith('.. ')) continue;

        rx.lastIndex = 0;
        if (rx.test(line)) {
          findings.push({
            pattern_name: name,
            owasp: cfg.owasp,
            description: cfg.description,
            severity: cfg.severity,
            remediation: cfg.remediation,
            confidence: cfg.confidence,
            likelihood: cfg.likelihood,
            impact: cfg.impact,
            line: i + 1,
            matched_line: s.substring(0, 100),
          });
          found = true;
          break;
        }
      }
    }
  }
  return findings;
}


// =====================================================================
// Governance observations and bias risk
// =====================================================================

function generateObservations(text) {
  const obs = [];
  const lo = text.toLowerCase();
  for (const [name, rxList] of Object.entries(_GOVERNANCE_C)) {
    const cfg = GOVERNANCE_OBSERVATIONS[name];
    const found = rxList.some(rx => { rx.lastIndex = 0; return rx.test(lo); });
    if (name === 'no_logging') {
      if (!found && cfg.absence_observation) {
        obs.push({ article: cfg.article, observation: cfg.absence_observation });
      }
    } else if (found && cfg.observation) {
      obs.push({ article: cfg.article, observation: cfg.observation });
    }
  }
  return obs;
}

function checkBiasRisk(text) {
  const obs = [];
  const lo = text.toLowerCase();
  const featRx = _BIAS_RISK_C.protected_class_as_feature || [];
  if (featRx.some(rx => { rx.lastIndex = 0; return rx.test(lo); })) {
    obs.push({
      article: BIAS_RISK_PATTERNS.protected_class_as_feature.article,
      observation: BIAS_RISK_PATTERNS.protected_class_as_feature.observation,
    });
    const fairRx = _BIAS_RISK_C.missing_fairness_evaluation || [];
    if (!fairRx.some(rx => { rx.lastIndex = 0; return rx.test(lo); })) {
      obs.push({
        article: BIAS_RISK_PATTERNS.missing_fairness_evaluation.article,
        observation: BIAS_RISK_PATTERNS.missing_fairness_evaluation.absence_observation,
      });
    }
  }
  return obs;
}

function isTrainingActivity(text) {
  return _GPAI_TRAINING_C.some(rx => { rx.lastIndex = 0; return rx.test(text); });
}


// =====================================================================
// Main classify function
// =====================================================================

function classifyCode(text, language) {
  if (!language) language = detectLanguage(text);
  const stripped = stripComments(text, language);

  // 1. Prohibited (Article 5) — always first, cannot be overridden
  const prohibited = checkProhibited(text, stripped);
  if (prohibited) return prohibited;

  // 2. AI check
  if (!isAiRelated(text)) {
    return {
      tier: 'not_ai', confidence: 'high',
      indicators_matched: [], applicable_articles: [],
      action: 'allow', message: 'No AI indicators detected.',
      confidence_score: 0, match_lines: [],
    };
  }

  // 3. High-risk
  const hr = checkHighRisk(text, stripped);
  if (hr) return hr;

  // 4. Limited-risk
  const lr = checkLimitedRisk(text, stripped);
  if (lr) return lr;

  // 5. Minimal-risk
  return {
    tier: 'minimal_risk', confidence: 'medium',
    indicators_matched: [], applicable_articles: [],
    action: 'allow',
    message: 'Minimal-risk AI system. No specific EU AI Act requirements.',
    confidence_score: _confScore('minimal_risk', 0, true),
    match_lines: [],
  };
}


// =====================================================================
// Public API
// =====================================================================

function scanCode(text, filename) {
  const language = detectLanguage(text, filename);
  const classification = classifyCode(text, language);
  const security = checkAiSecurity(text);
  const observations = (classification.tier === 'high_risk')
    ? generateObservations(text) : [];
  const bias = (classification.tier !== 'not_ai')
    ? checkBiasRisk(text) : [];
  const training = isTrainingActivity(text);

  return { classification, security, observations, bias, is_training: training, language };
}

// Export for Node.js testing; browser uses globals
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { classifyCode, scanCode, isAiRelated, detectLanguage, stripComments };
}
