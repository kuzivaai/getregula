# SBOM Standards for AI Systems: Research Findings

**Date:** 2026-03-27
**Purpose:** Determine what format Regula should generate for AI-specific SBOMs and what fields to populate.

---

## 1. CycloneDX ML-BOM (Recommended Primary Format)

### Overview
CycloneDX added ML-BOM support in **v1.5** (June 2023) and refined it in **v1.6** (April 2024). It is the most mature, widely-tooled standard for AI/ML bill of materials.

### Component Type Enum Values (v1.6)
```
application | container | cryptographic-asset | data | device | device-driver |
file | firmware | framework | library | machine-learning-model | operating-system | platform
```

**AI-relevant types:**
- `machine-learning-model` -- triggers modelCard support
- `data` -- for datasets
- `framework` -- for ML frameworks (PyTorch, TensorFlow, etc.)
- `library` -- for AI libraries (LangChain, transformers, etc.)

### modelCard Object (on components of type `machine-learning-model`)

```json
{
  "type": "machine-learning-model",
  "name": "gpt-4o",
  "version": "2024-08-06",
  "modelCard": {
    "bom-ref": "mc-gpt4o",
    "modelParameters": {
      "approach": {
        "type": "supervised"  // supervised | unsupervised | reinforcement-learning | semi-supervised | self-supervised
      },
      "task": "text-generation",
      "architectureFamily": "transformer",
      "modelArchitecture": "GPT-4",
      "datasets": [
        {
          "type": "dataset",
          "ref": "dataset-bom-ref",
          "name": "training-data-v3",
          "contents": {
            "type": "text",   // text | image | audio | video | structured | other
            "url": "https://...",
            "properties": []
          },
          "classification": "confidential",
          "governance": {
            "custodians": [],     // responsible for safe custody/transport/storage
            "stewards": [],       // responsible for content/context/business rules
            "owners": []          // responsible for risk and access
          }
        }
      ],
      "inputs": [
        {
          "format": "text/plain"
        }
      ],
      "outputs": [
        {
          "format": "text/plain"
        }
      ]
    },
    "quantitativeAnalysis": {
      "performanceMetrics": [
        {
          "type": "accuracy",
          "value": "0.92",
          "slice": "english-language",
          "confidenceInterval": {
            "lowerBound": "0.90",
            "upperBound": "0.94"
          }
        }
      ],
      "graphics": {
        "description": "Performance charts",
        "collection": [
          {
            "name": "ROC Curve",
            "image": "base64-or-url"
          }
        ]
      }
    },
    "considerations": {
      "users": ["deployers", "end-users"],
      "useCases": ["customer-support-automation"],
      "technicalLimitations": ["hallucination risk on niche domains"],
      "performanceTradeoffs": ["speed vs accuracy at different quantization levels"],
      "ethicalConsiderations": [
        {
          "name": "bias",
          "mitigationStrategy": "Red-team testing on demographic subgroups"
        }
      ],
      "fairnessAssessments": [
        {
          "groupAtRisk": "non-English speakers",
          "benefits": "...",
          "harms": "..."
        }
      ],
      "environmentalConsiderations": {
        "energyConsumptions": [
          {
            "activity": "training",
            "energyProviders": ["AWS eu-west-1"],
            "activityEnergyCost": {
              "value": 1200,
              "unit": "kWh"
            }
          }
        ],
        "properties": []
      }
    },
    "properties": []
  }
}
```

### Key modelParameters Fields

| Field | Type | Description |
|-------|------|-------------|
| `approach.type` | enum | supervised, unsupervised, reinforcement-learning, semi-supervised, self-supervised |
| `task` | string | ML task (text-generation, classification, object-detection, etc.) |
| `architectureFamily` | string | transformer, CNN, RNN, LSTM, etc. |
| `modelArchitecture` | string | Specific arch (GPT-4, ResNet-50, YOLOv3) |
| `datasets` | array | Training/eval datasets with governance metadata |
| `inputs` | array | Input data type/format |
| `outputs` | array | Output data type/format |

### Key quantitativeAnalysis.performanceMetrics Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Metric name (accuracy, precision, recall, F1, BLEU, etc.) |
| `value` | string | Measured value |
| `slice` | string | Data subset this metric applies to |
| `confidenceInterval.lowerBound` | string | Lower CI bound |
| `confidenceInterval.upperBound` | string | Upper CI bound |

### Key considerations Fields

| Field | Type | Description |
|-------|------|-------------|
| `users` | array[string] | Intended users |
| `useCases` | array[string] | Intended use cases |
| `technicalLimitations` | array[string] | Known limitations |
| `performanceTradeoffs` | array[string] | Documented tradeoffs |
| `ethicalConsiderations` | array[object] | Bias and ethics notes |
| `fairnessAssessments` | array[object] | Demographic fairness evaluations |
| `environmentalConsiderations` | object | Energy consumption data (added in v1.6) |

### CycloneDX 1.6 Declarations (for compliance attestation)

CycloneDX 1.6 added `declarations` at the BOM root level, supporting:
- **assessors** -- who evaluated (third-party boolean, organization)
- **attestations** -- maps requirements to claims with conformance levels
- **claims** -- specific compliance claims with evidence
- **evidence** -- supporting data for claims
- **targets** -- what the claims apply to
- **standards** -- referenced standards (EU AI Act, ISO 42001, etc.)

This is directly usable for Regula's framework crosswalk attestation output.

### Tools That Generate CycloneDX

| Tool | Focus | Formats |
|------|-------|---------|
| **cdxgen** | General SBOM + ML support | CycloneDX (primary) |
| **syft** (Anchore) | Container/package scanning | CycloneDX, SPDX |
| **trivy** (Aqua) | Vulnerability + SBOM | CycloneDX, SPDX |
| **aisbom** (Lab700x) | ML model binary inspection | CycloneDX 1.6 (default), SPDX 2.3 |
| **agent-bom** | AI agent supply chain | CycloneDX 1.6, SPDX 3.0, SARIF + 14 more |

---

## 2. SPDX 3.0 AI Profile

### Overview
SPDX 3.0 (published March 2025) uses a profile-based architecture. The **AI Profile** defines the `AIPackage` class in the `ai` namespace.

### AIPackage Fields (all optional)

| Field | Type | Description |
|-------|------|-------------|
| `autonomyType` | PresenceType | Level of decision-making autonomy; whether human-in-the-loop |
| `domain` | string | Application area (healthcare, finance, automotive) |
| `energyConsumption` | EnergyConsumption | Overall energy used |
| `energyQuantity` | decimal | Numeric energy value |
| `energyUnit` | EnergyUnitType | Unit of energy measurement |
| `hyperparameter` | DictionaryEntry[] | Key-value pairs of hyperparameters |
| `informationAboutApplication` | string | How model is used in software (pre-processing, APIs) |
| `informationAboutTraining` | string | Training methodology (supervised fine-tuning, RLHF, etc.) |
| `limitation` | string | Known limitations of the AI model |
| `metric` | DictionaryEntry[] | Evaluation metrics (accuracy, fairness, robustness) |
| `metricDecisionThreshold` | DictionaryEntry[] | Thresholds per metric (e.g., probability > 0.5) |
| `modelDataPreprocessing` | string | Data preprocessing techniques used |
| `modelExplainability` | string | How model decisions can be explained |
| `safetyRiskAssessment` | SafetyRiskAssessmentType | Risk level per EU AI Act Article 20 / EC Reg 765/2008 |
| `standardCompliance` | string | Standards/regulations the system adheres to |
| `trainingEnergyConsumption` | EnergyConsumption | Energy for training specifically |
| `finetuningEnergyConsumption` | EnergyConsumption | Energy for fine-tuning |
| `inferenceEnergyConsumption` | EnergyConsumption | Energy for inference |
| `typeOfModel` | string | Model type (neural network, decision tree, etc.) |
| `useSensitivePersonalInformation` | PresenceType | Whether PII/biometric data used for training/inference |

### SafetyRiskAssessmentType Enum
```
serious | high | medium | low
```
Aligns with EU AI Act risk tiers. There is an open issue (#650) to add `unacceptable` and `minimal` to match the full EU AI Act risk classification.

### SPDX 3.0 Dataset Profile Fields

| Field | Description |
|-------|-------------|
| `dataCollectionProcess` | How data was collected |
| `intendedUse` | Intended use of the dataset |
| `datasetSize` | Size of the dataset |
| `sensor` | Sensors producing the data |
| `knownBias` | Known biases in the data |
| `sensitivePersonalInformation` | Whether PII is present |
| `anonymizationMethodUsed` | Anonymization methods applied |
| `confidentialityLevel` | Data confidentiality classification |
| `datasetNoise` | Known noise characteristics |

### CycloneDX vs SPDX for AI: Comparison

| Criterion | CycloneDX 1.6 | SPDX 3.0 |
|-----------|---------------|----------|
| **Maturity for AI** | ML-BOM since v1.5 (2023) | AI Profile in v3.0 (2025) |
| **Tooling ecosystem** | Larger (cdxgen, syft, trivy, aisbom) | Growing (spdx-tools, NTIA tools) |
| **Model card support** | Native `modelCard` object | Flat fields on `AIPackage` |
| **Dataset governance** | Custodian/steward/owner roles | Collection process/bias/noise fields |
| **Compliance attestation** | `declarations` object (v1.6) | `standardCompliance` string field |
| **Energy/environmental** | `environmentalConsiderations` (v1.6) | Granular energy fields (training/fine-tuning/inference) |
| **Government adoption** | CISA recommends both | NTIA minimum elements reference SPDX |
| **Industry consumption** | More widely consumed by security tools | More common in open-source licensing |

**Recommendation for Regula:** Generate **CycloneDX 1.6 as primary** format (wider tool consumption, richer attestation model via `declarations`). Offer **SPDX 3.0 as secondary** export.

---

## 3. AIsbom (Lab700xOrg/aisbom)

### What It Does
- Deep binary introspection on ML model files (.pt, .pkl, .safetensors, .gguf)
- Detects malware risks via bytecode decompilation (unsafe imports: `os`, `subprocess`, `socket`)
- Identifies license violations hidden in serialized weights
- Generates CycloneDX v1.6 SBOM with SHA256 hashes and license data

### Output Formats
- **CycloneDX v1.6** (default) -- `sbom.json`
- **SPDX 2.3** -- via `--format spdx`
- **Markdown** -- GitHub-flavored reports
- **Terminal tables** -- interactive CLI

### Fields Populated
- SHA256 hashes for integrity verification
- Framework identification (PyTorch, SafeTensors, GGUF)
- Security risk level (LOW, CRITICAL with specific threats like "RCE Found")
- Legal risk classification (restricted licenses like cc-by-nc-4.0)

### Relevance to Regula
AIsbom focuses on **model artifact security** (Layer 1 pre-execution scanning). Regula focuses on **governance and compliance**. They are complementary. Regula could consume AIsbom output as an input signal.

---

## 4. Agent-BOM (msaad02/agent-bom)

### What It Does
- AI supply chain security scanner for MCP servers and AI agents
- CVE scanning with NVD CVSS and EPSS enrichment
- Blast radius analysis (vulnerability -> package -> server -> agent -> credentials -> tools)
- Registry of 427+ known MCP servers with risk levels

### Output Formats (17 total)
- **CycloneDX 1.6** with native ML extensions (modelCard, datasets, training metadata)
- **SPDX 3.0**
- **SARIF**
- JSON, HTML, GraphML, Neo4j Cypher, JUnit XML, CSV, Markdown, Mermaid, SVG, Prometheus metrics, badge formats

### AI-Specific Fields in Generated SBOMs
- AI framework dependencies (LangChain, CrewAI, OpenAI Agents SDK)
- System prompts and guardrails from instruction files
- MCP server connections with verification status
- Tool signatures and capabilities
- Exposed credentials mapped through supply chain
- Vulnerability chain mappings

### Relevance to Regula
Agent-BOM demonstrates the market expectation for AI SBOMs to include **agent-specific metadata** (tools, prompts, MCP connections). Regula's SBOM should similarly capture agent architecture details.

---

## 5. What Regula Should Generate

### Recommended Format: CycloneDX 1.6 JSON

**Rationale:**
1. Widest consumption by security and compliance tools (Dependency-Track, OWASP, Snyk, FOSSA)
2. Native `modelCard` object maps directly to EU AI Act Annex IV documentation requirements
3. `declarations` object supports framework crosswalk attestations
4. Energy/environmental tracking for sustainability reporting
5. All major AI SBOM tools (aisbom, agent-bom, cdxgen) already use CycloneDX

### Fields Regula Should Populate

#### BOM-Level
```yaml
bomFormat: "CycloneDX"
specVersion: "1.6"
serialNumber: "urn:uuid:{generated}"
version: 1
metadata:
  timestamp: ISO-8601
  tools:
    - vendor: "Regula"
      name: "regula"
      version: "{version}"
  component:
    type: "application"
    name: "{system-name}"
    description: "AI system under governance"
```

#### Components (what Regula discovers)
```yaml
components:
  # 1. The AI system itself
  - type: "application"
    name: "my-ai-system"

  # 2. ML models used
  - type: "machine-learning-model"
    name: "gpt-4o"
    version: "2024-08-06"
    supplier:
      name: "OpenAI"
    modelCard:
      modelParameters:
        approach:
          type: "supervised"
        task: "text-generation"
        architectureFamily: "transformer"
        modelArchitecture: "GPT-4"
      considerations:
        useCases: [...]
        technicalLimitations: [...]
        ethicalConsiderations: [...]

  # 3. AI frameworks/libraries
  - type: "framework"
    name: "langchain"
    version: "0.2.x"

  - type: "library"
    name: "openai"
    version: "1.x"

  # 4. Datasets (if discoverable)
  - type: "data"
    name: "training-dataset-v1"
    classification: "confidential"
```

#### Declarations (Regula's compliance attestations)
```yaml
declarations:
  standards:
    - bom-ref: "std-eu-ai-act"
      name: "EU AI Act"
      version: "Regulation 2024/1689"
      requirements:
        - bom-ref: "req-art-9"
          identifier: "Article 9"
          title: "Risk Management System"
        - bom-ref: "req-art-10"
          identifier: "Article 10"
          title: "Data and Data Governance"
        # ... articles 11-15

  claims:
    - bom-ref: "claim-risk-mgmt"
      target: "component-bom-ref"
      predicate: "compliant"
      description: "Risk management system established per Article 9"
      evidence:
        - bom-ref: "evidence-risk-assessment"
          description: "Automated risk assessment output"
          data:
            - name: "risk-score"
              value: "medium"

  attestations:
    - summary: "Regula automated compliance assessment"
      assessor: "assessor-regula"
      map:
        - requirement: "req-art-9"
          claims: ["claim-risk-mgmt"]
          conformance:
            score: 0.85
            rationale: "7 of 8 sub-requirements satisfied"
```

### What a DPO / Compliance Auditor Wants to See

1. **Risk classification** -- What EU AI Act risk tier (unacceptable/high/limited/minimal)?
2. **Model provenance** -- Who supplied each model? What version? What training methodology?
3. **Data governance** -- What data was used? Who is the data controller/processor? PII present?
4. **Framework compliance scores** -- Per-article compliance status against EU AI Act, mapped to ISO 42001/NIST AI RMF
5. **Human oversight design** -- What human-in-the-loop mechanisms exist?
6. **Transparency measures** -- Is the system explainable? Are users informed it is AI?
7. **Security posture** -- Known vulnerabilities in the AI supply chain
8. **Energy/environmental impact** -- Training and inference energy consumption
9. **Audit trail** -- When was this assessment generated? By what tool version? What inputs?
10. **Gap analysis** -- Which requirements are NOT met, with remediation guidance

---

## 6. Framework Mappings for Regula's Crosswalk

### NIST CSF 2.0 -- All 6 Functions, 22 Categories

```
GOVERN (GV) -- 6 categories
  GV.OC  Organizational Context
  GV.RM  Risk Management Strategy
  GV.RR  Roles, Responsibilities, and Authorities
  GV.PO  Policy
  GV.OV  Oversight
  GV.SC  Cybersecurity Supply Chain Risk Management

IDENTIFY (ID) -- 3 categories
  ID.AM  Asset Management
  ID.RA  Risk Assessment
  ID.IM  Improvement

PROTECT (PR) -- 5 categories
  PR.AA  Identity Management, Authentication, and Access Control
  PR.AT  Awareness and Training
  PR.DS  Data Security
  PR.PS  Platform Security
  PR.IR  Technology Infrastructure Resilience

DETECT (DE) -- 2 categories
  DE.AE  Adverse Event Analysis
  DE.CM  Continuous Monitoring

RESPOND (RS) -- 5 categories
  RS.MA  Incident Management
  RS.AN  Incident Analysis
  RS.CO  Incident Response Reporting and Communication
  RS.MI  Incident Mitigation
  RS.RP  Incident Response Plan Execution  (note: this is now under RS, not a separate category)

RECOVER (RC) -- 2 categories  (note: some sources list RC.CO under RS)
  RC.RP  Incident Recovery Plan Execution
  RC.CO  Incident Recovery Communication
```

**Total: 6 functions, 22 categories, 106 subcategories**

### NIST CSF 2.0 Cyber AI Profile (NIST IR 8596, Draft Dec 2025)

Overlays three **AI Focus Areas** on CSF 2.0 outcomes:
- **Secure** -- Protect AI systems from cybersecurity threats
- **Detect** -- Identify AI-specific attack patterns
- **Thwart** -- Prevent adversarial manipulation of AI

This is the authoritative NIST mapping for AI cybersecurity to CSF 2.0.

### NIST CSF 2.0 to EU AI Act Mapping (AI-Relevant Subcategories)

| CSF 2.0 Subcategory | EU AI Act Article | AI Relevance |
|---------------------|-------------------|--------------|
| GV.OC-01 | Art. 9 | Organizational mission informs AI risk management |
| GV.RM-01 | Art. 9 | Risk management objectives established |
| GV.RM-02 | Art. 9 | Risk appetite/tolerance for AI systems |
| GV.RR-01 | Art. 14 | Leadership takes responsibility for AI decisions |
| GV.PO-01 | Art. 11 | Policy for managing AI cybersecurity risks |
| GV.PO-02 | Art. 13 | Transparency policy communicated/enforced |
| GV.SC-03 | Art. 13, 15 | Supply chain risk for AI components |
| ID.AM-01 | Art. 11 | Hardware inventory (GPU/TPU for AI) |
| ID.AM-02 | Art. 11 | Software/model inventory |
| ID.AM-07 | Art. 10 | Data inventory with metadata |
| ID.AM-08 | Art. 10 | Lifecycle management of AI data/models |
| ID.RA-01 | Art. 9, 15 | Vulnerability identification in AI assets |
| PR.AA-* | Art. 15 | Access control for models and APIs |
| PR.DS-01 | Art. 10 | Data-at-rest protection (training data) |
| PR.DS-02 | Art. 10 | Data-in-transit protection |
| PR.PS-01 | Art. 15 | Configuration management for AI infra |
| PR.PS-06 | Art. 15 | Secure AI development practices |
| PR.IR-01 | Art. 15 | Network protection for AI environments |
| DE.CM-01 | Art. 12 | Network monitoring for AI services |
| DE.CM-06 | Art. 12 | External AI service provider monitoring |
| DE.CM-09 | Art. 12 | Runtime monitoring of AI systems |
| DE.AE-02 | Art. 15 | Adverse event analysis for AI |
| RS.MA-01 | Art. 14 | Incident response with human oversight |
| RC.RP-01 | Art. 15 | Recovery plan for AI system failures |

### SOC 2 Trust Services Criteria -- AI-Relevant Mappings

**5 Trust Services Principles:** Security, Availability, Processing Integrity, Confidentiality, Privacy

| SOC 2 Criteria | Code | AI Application |
|---------------|------|----------------|
| **Security -- Control Environment** | CC1.1 | Commitment to integrity/ethics in AI decisions |
| **Security -- Board Oversight** | CC1.2 | Board oversight of AI risk |
| **Security -- Org Structure** | CC1.3 | AI governance structure, reporting lines |
| **Security -- Communication** | CC2.1 | AI system design/controls communicated to users |
| **Security -- External Comms** | CC2.3 | External transparency about AI capabilities/limitations |
| **Risk Assessment** | CC3.1 | AI-specific risk identification and assessment |
| **Risk Assessment -- Fraud** | CC3.2 | Consideration of AI-generated fraud/deepfakes |
| **Risk Assessment -- Changes** | CC3.4 | Impact assessment for model updates/retraining |
| **Monitoring** | CC4.1 | Ongoing monitoring of AI system performance |
| **Control Activities** | CC5.1 | Controls to mitigate AI-specific risks |
| **Access Controls** | CC6.1 | Logical access controls for models, APIs, training data |
| **Access Controls -- Auth** | CC6.2 | Authentication for AI system access |
| **Access Controls -- Restrict** | CC6.3 | Restrict access to AI inference endpoints |
| **System Operations** | CC7.1 | Detection/monitoring of AI system anomalies |
| **System Operations -- Anomaly** | CC7.2 | Monitor AI outputs for anomalous behaviour |
| **Change Management** | CC8.1 | Change management for model deployments |
| **Processing Integrity** | PI1.1 | AI output validation and accuracy monitoring |
| **Confidentiality** | C1.1 | Confidential training data identification |
| **Privacy** | P1.1-P8.1 | Personal data in training sets, inference data |
| **Availability** | A1.1-A1.2 | AI service availability and resilience |

### ISO 27001:2022 Annex A -- AI-Relevant Controls

| Control | Title | AI Relevance |
|---------|-------|--------------|
| **A.5.1** | Policies for information security | Must cover AI system policies |
| **A.5.7** | Threat intelligence | AI-specific threats (adversarial, poisoning) |
| **A.5.8** | Info security in project management | AI development projects |
| **A.5.10** | Acceptable use of information | Training data usage policies |
| **A.5.12** | Classification of information | Training data and model classification |
| **A.5.13** | Labelling of information | Dataset labelling and provenance |
| **A.5.14** | Information transfer | Model and data transfer security |
| **A.5.19** | Info security in supplier relationships | AI model/API supplier management |
| **A.5.21** | Managing info security in ICT supply chain | AI supply chain (models, data, compute) |
| **A.5.23** | Info security for cloud services | Cloud AI service governance |
| **A.5.29** | Info security during disruption | AI system continuity |
| **A.5.30** | ICT readiness for business continuity | AI service resilience |
| **A.5.31** | Legal/regulatory requirements | EU AI Act, GDPR for AI |
| **A.5.34** | Privacy and PII protection | PII in training data |
| **A.5.37** | Documented operating procedures | AI system documentation |
| **A.6.3** | Info security awareness/training | AI-specific security training |
| **A.8.2** | Privileged access rights | Admin access to models/training infra |
| **A.8.3** | Information access restriction | Model API access controls |
| **A.8.8** | Management of technical vulnerabilities | AI library/framework vulnerabilities |
| **A.8.9** | Configuration management | AI infrastructure configuration |
| **A.8.10** | Information deletion | Training data deletion/right to be forgotten |
| **A.8.11** | Data masking | PII masking in training data |
| **A.8.12** | Data leakage prevention | Prevent model memorization leaks |
| **A.8.15** | Logging | AI system event logging |
| **A.8.16** | Monitoring activities | AI runtime monitoring |
| **A.8.24** | Use of cryptography | Model encryption, secure inference |
| **A.8.25** | Secure development lifecycle | ML development lifecycle security |
| **A.8.26** | Application security requirements | AI application security |
| **A.8.28** | Secure coding | Secure ML pipeline code |

---

## Sources

- [CycloneDX ML-BOM Capabilities](https://cyclonedx.org/capabilities/mlbom/)
- [CycloneDX 1.6 JSON Reference](https://cyclonedx.org/docs/1.6/json/)
- [CycloneDX 1.6 JSON Schema](https://github.com/CycloneDX/specification/blob/master/schema/bom-1.6.schema.json)
- [CycloneDX AI Models and Model Cards Use Case](https://cyclonedx.org/use-cases/ai-models-and-model-cards/)
- [SPDX 3.0.1 AI Profile - AIPackage](https://spdx.github.io/spdx-spec/v3.0.1/model/AI/AI/)
- [SPDX 3.0.1 AIPackage Class](https://spdx.github.io/spdx-spec/v3.0.1/model/AI/Classes/AIPackage/)
- [Implementing AI BOM with SPDX 3.0 (Linux Foundation)](https://www.linuxfoundation.org/hubfs/LF%20Research/lfr_spdx_aibom_102524a.pdf)
- [Understanding SPDX 3.0 AI BOM Support](https://becomingahacker.org/understanding-the-spdx-3-0-ai-bom-support-7f3dbdd28345)
- [SBOM Analysis - SPDX 3.0 AI Package](https://nd-crane.github.io/sbom-analysis/ai_specifications/spdx3_aipackage.html)
- [Lab700xOrg/aisbom](https://github.com/Lab700xOrg/aisbom)
- [msaad02/agent-bom](https://github.com/msaad00/agent-bom)
- [NIST CSF 2.0](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf)
- [NIST IR 8596 - Cyber AI Profile (Draft)](https://csrc.nist.gov/pubs/ir/8596/iprd)
- [NIST AI RMF to ISO 42001 Crosswalk](https://airc.nist.gov/docs/NIST_AI_RMF_to_ISO_IEC_42001_Crosswalk.pdf)
- [NIST AI Resource Center - Crosswalk Documents](https://airc.nist.gov/airmf-resources/crosswalks/)
- [How to Incorporate AI Controls into SOC 2 (Schellman)](https://www.schellman.com/blog/soc-examinations/how-to-incorporate-ai-into-your-soc-2-examination)
- [Representing AI Controls in SOC 2 Reports (Moss Adams)](https://www.mossadams.com/articles/2025/12/ai-controls-for-soc-2-reports)
- [ISO 27001:2022 Annex A Controls](https://www.dataguard.com/iso-27001/annex-a/)
- [ISO 27001 for AI Companies](https://hightable.io/iso-27001-for-ai-companies/)
- [EU AI Act vs NIST AI RMF vs ISO 42001 (EC-Council)](https://www.eccouncil.org/cybersecurity-exchange/responsible-ai-governance/eu-ai-act-nist-ai-rmf-and-iso-iec-42001-a-plain-english-comparison/)
- [CSA: Use ISO 42001 & NIST AI RMF for EU AI Act](https://cloudsecurityalliance.org/blog/2025/01/29/how-can-iso-iec-42001-nist-ai-rmf-help-comply-with-the-eu-ai-act)
- [CSF Tools - NIST CSF 2.0 Reference](https://csf.tools/reference/nist-cybersecurity-framework/v2-0/)
