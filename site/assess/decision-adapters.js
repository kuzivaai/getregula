// regula-ignore: * -- questionnaire mapping data names regulated practices but does not implement them
// Shared questionnaire-to-fact adapter. Presentation strings remain in locale pages.
(function (root, factory) {
  const api = factory(root.RegulaDecisionModel, root.RegulaDecisionKernel);
  if (typeof module === "object" && module.exports) module.exports = api;
  root.RegulaDecisionAdapters = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (model, kernel) {
  "use strict";

  const SIMPLE_MAPPINGS = {
    eu: {
      deployment_eu: "jurisdiction_in_scope",
      is_ai_system: "is_ai_system",
      role_provider: "role_provider",
      role_deployer: "role_deployer",
      affected_domain: "eu_annex_iii_use",
      significant_harm: "eu_significant_risk",
      profiling: "eu_profiling",
      narrow_procedural: "eu_narrow_procedural_task",
      improves_human_activity: "eu_improves_completed_human_activity",
      pattern_detection: "eu_pattern_detection_without_replacement",
      preparatory_task: "eu_preparatory_task",
      social_scoring: "eu_social_evaluation",
      emotion_recognition: "eu_emotion_inference_work_or_school",
    },
    kr: {
      kr_scope: "jurisdiction_in_scope",
      kr_is_ai_system: "is_ai_system",
      kr_operator: "kr_ai_business_operator",
      kr_provides: "kr_provides_ai_product_or_service",
      kr_high_impact_domain: "kr_high_impact_area",
      kr_significant_impact: "kr_significant_impact_or_risk",
      kr_training_compute: "kr_training_compute_threshold_met",
      kr_frontier_technology: "kr_frontier_technology_configuration",
      kr_widespread_impact: "kr_widespread_significant_impact_risk",
      kr_generative: "kr_generative_ai",
      kr_virtual_media: "kr_virtual_realistic_media",
      kr_foreign_operator: "kr_foreign_operator",
      kr_total_revenue: "kr_total_revenue_at_least_1trn_krw",
      kr_ai_services_revenue: "kr_ai_services_revenue_at_least_10bn_krw",
      kr_domestic_users: "kr_average_daily_domestic_users_at_least_1m",
      kr_admin_fine: "kr_article_43_1_3_administrative_fine",
    },
    co: {
      co_scope: "jurisdiction_in_scope",
      co_is_ai_system: "is_ai_system",
      co_doing_business: "co_doing_business",
      co_personal_data: "co_processes_personal_data",
      co_decisions: "co_computational_output",
      co_material: "co_substantial_factor",
      co_domain: "co_consequential_domain",
      co_excluded: "co_excluded_technology",
      co_other_law_exemption: "co_other_law_exemption",
      co_adverse_outcome: "co_adverse_outcome",
    },
  };
  const LEGACY_QUESTION_ORDER = {
    eu: ["deployment_eu", "affected_domain", "autonomous_decisions",
      "significant_harm", "biometric_data", "social_scoring",
      "emotion_recognition", "public_facing", "narrow_procedural",
      "improves_human_activity", "risk_documentation", "logging_active",
      "profiling", "pattern_detection", "preparatory_task"],
    kr: ["kr_scope", "kr_high_impact_domain", "kr_high_performance",
      "kr_transparency", "kr_generative", "kr_explanation",
      "kr_risk_management", "kr_human_oversight", "kr_representative"],
    co: ["co_scope", "co_decisions", "co_domain", "co_material", "co_role",
      "co_pre_notice", "co_adverse", "co_consumer_rights"],
  };
  const SHARE_SCHEMA = "regula-assessment-share";
  const SHARE_VERSION = 4;
  const SHARE_STATES = new Set([
    "unanswered", "yes", "no", "unsure", "not_applicable", "contradictory",
  ]);

  function normaliseAnswer(answer) {
    if (answer === "unsure") return "unknown";
    if (["yes", "no", "not_applicable"].includes(answer)) return answer;
    throw new kernel.DecisionInputError(`invalid questionnaire answer: ${answer}`);
  }

  function addFact(facts, factId, answer, jurisdiction, answerId, now) {
    facts[factId] = kernel.makeFact(
      normaliseAnswer(answer),
      `browser-questionnaire:${answerId}`,
      jurisdiction,
      now,
      "user_attestation",
    );
  }

  function mapRoleAnswers(facts, jurisdiction, answers, now) {
    if (jurisdiction !== "co" || answers.co_role === undefined) return;
    const answer = answers.co_role;
    if (answer === "yes") {
      addFact(facts, "role_provider", "yes", jurisdiction, "co_role", now);
      addFact(facts, "role_deployer", "no", jurisdiction, "co_role", now);
    } else if (answer === "no") {
      addFact(facts, "role_provider", "no", jurisdiction, "co_role", now);
      addFact(facts, "role_deployer", "yes", jurisdiction, "co_role", now);
    } else {
      addFact(facts, "role_provider", answer, jurisdiction, "co_role", now);
      addFact(facts, "role_deployer", answer, jurisdiction, "co_role", now);
    }
  }

  function buildQuestionnaireRequest(jurisdiction, answers, timestamp) {
    if (!model || !kernel) throw new Error("decision model and kernel must load first");
    if (!Object.prototype.hasOwnProperty.call(SIMPLE_MAPPINGS, jurisdiction)) {
      throw new kernel.DecisionInputError("unsupported questionnaire jurisdiction");
    }
    const now = timestamp || new Date().toISOString();
    const facts = {};
    for (const [answerId, factId] of Object.entries(SIMPLE_MAPPINGS[jurisdiction])) {
      if (answers[answerId] !== undefined) {
        addFact(facts, factId, answers[answerId], jurisdiction, answerId, now);
      }
    }
    mapRoleAnswers(facts, jurisdiction, answers, now);
    return {
      model_version: model.model_version,
      jurisdiction,
      facts,
    };
  }

  function evaluateQuestionnaireDecision(jurisdiction, answers, timestamp) {
    const request = buildQuestionnaireRequest(jurisdiction, answers, timestamp);
    const internal = kernel.evaluateDecision(model, request);
    return toReviewRecord(internal, request);
  }

  function factResolution(factId, record) {
    const values = record && Array.isArray(record.values) ? record.values : [];
    const decisive = [...new Set(values
      .filter(value => value.state !== "unknown")
      .map(value => value.state))];
    const status = decisive.length > 1 ? "contradictory" :
      decisive.length === 0 ? "explicit_unknown" : "resolved";
    return {
      fact_id: factId,
      status,
      state: decisive.length === 1 ? decisive[0] : null,
      values: JSON.parse(JSON.stringify(values)),
    };
  }

  function relevantProvisions(internal) {
    const references = new Set();
    for (const indication of internal.indications || []) {
      if (indication.provision) references.add(indication.provision);
    }
    for (const obligation of internal.obligations || []) {
      if (obligation.provision) references.add(obligation.provision);
    }
    for (const unresolved of internal.unresolved_predicates || []) {
      for (const affected of unresolved.would_resolve || []) {
        if (affected.provision) references.add(affected.provision);
      }
    }
    if (internal.outside_scope_basis && internal.outside_scope_basis.provision) {
      references.add(internal.outside_scope_basis.provision);
    }
    return [...references].sort().map(reference => ({
      reference,
      status: "unresolved_question",
      source_version: null,
      source_date: null,
    }));
  }

  function toReviewRecord(internal, request) {
    const declared = Object.entries(request.facts || {})
      .map(([factId, record]) => factResolution(factId, record));
    const contradictory = declared.filter(item => item.status === "contradictory");
    const missing = (internal.unresolved_predicates || []).map(item => ({
      fact_id: item.fact_id,
      reason: item.reason,
      question: item.question,
      observed_values: JSON.parse(JSON.stringify(item.observed_values || [])),
    }));
    return {
      schema_version: "2.0",
      record_type: "declared_context_review",
      review_status: internal.result_type === "insufficient_information" ||
        contradictory.length ? "insufficient_information" : "human_review_required",
      model_version: internal.model_version,
      jurisdiction: internal.jurisdiction,
      evidence_completeness: JSON.parse(JSON.stringify(internal.evidence_completeness)),
      declared_context: declared,
      missing_context: missing,
      contradictory_context: contradictory,
      potentially_relevant_provisions: relevantProvisions(internal),
      reviewer_questions: missing.map(item => item.question),
      suggested_human_review_steps: [
        "Confirm each declared fact from an accountable source",
        "Preserve unknown and contradictory context instead of treating it as no",
        "Review potentially relevant provisions with an appropriately qualified reviewer",
        "Record the accountable human decision and its evidence separately",
      ],
      explicit_limitations: [
        "Declared answers and code observations do not determine legal applicability or legal risk tier",
        "Absence of a configured indicator does not prove absence of legal relevance",
        "The human decision field is intentionally empty until accountable review",
      ],
      probability_calibration: JSON.parse(JSON.stringify(internal.probability_calibration)),
      human_decision: null,
    };
  }

  function factIdsForQuestion(jurisdiction, questionId) {
    if (jurisdiction === "co" && questionId === "co_role") {
      return ["role_provider", "role_deployer"];
    }
    const factId = SIMPLE_MAPPINGS[jurisdiction] &&
      SIMPLE_MAPPINGS[jurisdiction][questionId];
    return factId ? [factId] : [];
  }

  function toBase64Url(text) {
    if (typeof Buffer !== "undefined") {
      return Buffer.from(text, "utf8").toString("base64url");
    }
    const bytes = new TextEncoder().encode(text);
    let binary = "";
    for (const byte of bytes) binary += String.fromCharCode(byte);
    return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
  }

  function fromBase64Url(encoded) {
    if (!encoded || !/^[A-Za-z0-9_-]+$/.test(encoded)) {
      throw new Error("invalid base64url payload");
    }
    if (typeof Buffer !== "undefined") {
      return Buffer.from(encoded, "base64url").toString("utf8");
    }
    const padded = encoded.replace(/-/g, "+").replace(/_/g, "/") +
      "=".repeat((4 - encoded.length % 4) % 4);
    const binary = atob(padded);
    const bytes = Uint8Array.from(binary, character => character.charCodeAt(0));
    return new TextDecoder().decode(bytes);
  }

  function questionIdsFrom(questions) {
    if (!Array.isArray(questions)) throw new Error("questions must be an array");
    const ids = questions.map(question => question && question.id);
    if (ids.some(id => typeof id !== "string" || !id) ||
        new Set(ids).size !== ids.length) {
      throw new Error("questions must have unique string ids");
    }
    return ids;
  }

  function encodeAnswers(jurisdiction, answers, questions) {
    const questionIds = questionIdsFrom(questions);
    if (!answers || typeof answers !== "object" || Array.isArray(answers)) {
      throw new Error("answers must be an object");
    }
    const unknownAnswerIds = Object.keys(answers)
      .filter(answerId => !questionIds.includes(answerId));
    if (unknownAnswerIds.length) {
      throw new Error(`unknown shared answer ids: ${unknownAnswerIds.join(", ")}`);
    }
    const states = {};
    for (const questionId of questionIds) {
      const state = Object.prototype.hasOwnProperty.call(answers, questionId)
        ? answers[questionId] : "unanswered";
      if (!SHARE_STATES.has(state)) {
        throw new Error(`invalid shared evidence state: ${state}`);
      }
      states[questionId] = state;
    }
    const payload = {
      schema: SHARE_SCHEMA,
      version: SHARE_VERSION,
      jurisdiction,
      question_ids: questionIds,
      states,
      provenance: {
        jurisdiction,
        decision_model_version: model && model.model_version || null,
      },
    };
    return `${SHARE_VERSION}.${toBase64Url(JSON.stringify(payload))}`;
  }

  function decodeLegacyShare(jurisdiction, code, questions) {
    let questionIds;
    let raw;
    let euLegacyVersion = null;
    if (code.startsWith("3")) {
      questionIds = questions.map(question => question.id);
      raw = code.slice(1);
    } else {
      questionIds = LEGACY_QUESTION_ORDER[jurisdiction];
      if (jurisdiction === "eu" && code.startsWith("2")) {
        euLegacyVersion = 2;
        raw = code.slice(1);
      } else {
        euLegacyVersion = jurisdiction === "eu" ? 1 : null;
        raw = code;
      }
    }
    if (!questionIds || raw.length > questionIds.length || !/^[ynua]*$/.test(raw)) {
      return { ok: false, error: "malformed_payload" };
    }
    raw = raw.padEnd(questionIds.length, "u");
    const decoded = {};
    const states = {};
    questionIds.forEach((questionId, index) => {
      let encoded = raw[index];
      if (euLegacyVersion === 1 && questionId === "public_facing") {
        encoded = encoded === "y" ? "n" : encoded === "n" ? "y" : encoded;
      }
      const state = encoded === "y" ? "yes" :
        encoded === "n" ? "no" : encoded === "a" ? "not_applicable" : "unsure";
      decoded[questionId] = state;
      states[questionId] = state;
    });
    return {
      ok: true,
      schema_version: code.startsWith("3") ? 3 : euLegacyVersion,
      legacy: true,
      legacy_lossy: true,
      answers: decoded,
      states,
      provenance: {
        jurisdiction,
        legacy_share_schema: code.startsWith("3") ? 3 : euLegacyVersion,
      },
      requires_manual_recovery: false,
    };
  }

  function decodeShare(jurisdiction, code, questions) {
    if (typeof code !== "string" || !code) {
      return { ok: false, error: "malformed_payload" };
    }
    if (!code.startsWith(`${SHARE_VERSION}.`)) {
      if (code.startsWith("3") ||
          (jurisdiction === "eu" && code.startsWith("2")) ||
          /^[ynua]*$/.test(code)) {
        return decodeLegacyShare(jurisdiction, code, questions);
      }
      if (/^\d/.test(code)) {
        return { ok: false, error: "unsupported_version" };
      }
      return { ok: false, error: "malformed_payload" };
    }

    let payload;
    try {
      payload = JSON.parse(fromBase64Url(code.slice(2)));
    } catch (error) {
      return { ok: false, error: "malformed_payload" };
    }
    if (!payload || typeof payload !== "object" || Array.isArray(payload) ||
        payload.schema !== SHARE_SCHEMA || payload.version !== SHARE_VERSION) {
      return { ok: false, error: "malformed_payload" };
    }
    if (payload.jurisdiction !== jurisdiction) {
      return { ok: false, error: "jurisdiction_mismatch" };
    }

    let currentQuestionIds;
    try {
      currentQuestionIds = questionIdsFrom(questions);
    } catch (error) {
      return { ok: false, error: "question_set_mismatch" };
    }
    if (!Array.isArray(payload.question_ids) ||
        JSON.stringify(payload.question_ids) !== JSON.stringify(currentQuestionIds)) {
      return { ok: false, error: "question_set_mismatch" };
    }
    if (!payload.states || typeof payload.states !== "object" ||
        Array.isArray(payload.states) ||
        Object.keys(payload.states).length !== currentQuestionIds.length) {
      return { ok: false, error: "malformed_payload" };
    }

    const answers = {};
    const states = {};
    const contradictory = [];
    for (const questionId of currentQuestionIds) {
      if (!Object.prototype.hasOwnProperty.call(payload.states, questionId)) {
        return { ok: false, error: "malformed_payload" };
      }
      const state = payload.states[questionId];
      if (!SHARE_STATES.has(state)) {
        return { ok: false, error: "malformed_payload" };
      }
      states[questionId] = state;
      if (state !== "unanswered") answers[questionId] = state;
      if (state === "contradictory") contradictory.push(questionId);
    }
    return {
      ok: true,
      schema_version: SHARE_VERSION,
      legacy: false,
      legacy_lossy: false,
      answers,
      states,
      provenance: {
        jurisdiction,
        decision_model_version: payload.provenance &&
          payload.provenance.decision_model_version || null,
      },
      contradictory_question_ids: contradictory,
      requires_manual_recovery: contradictory.length > 0,
    };
  }

  function decodeAnswers(jurisdiction, code, questions) {
    const decoded = decodeShare(jurisdiction, code, questions);
    return decoded.ok ? decoded.answers : null;
  }

  return {
    buildQuestionnaireRequest,
    decodeAnswers,
    decodeShare,
    encodeAnswers,
    evaluateQuestionnaireDecision,
    factIdsForQuestion,
  };
});
