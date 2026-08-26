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
    return kernel.evaluateDecision(
      model,
      buildQuestionnaireRequest(jurisdiction, answers, timestamp),
    );
  }

  function factIdsForQuestion(jurisdiction, questionId) {
    if (jurisdiction === "co" && questionId === "co_role") {
      return ["role_provider", "role_deployer"];
    }
    const factId = SIMPLE_MAPPINGS[jurisdiction] &&
      SIMPLE_MAPPINGS[jurisdiction][questionId];
    return factId ? [factId] : [];
  }

  function encodeAnswers(jurisdiction, answers, questions) {
    const payload = questions.map(question => {
      const answer = answers[question.id];
      return answer === "yes" ? "y" : answer === "no" ? "n" :
        answer === "not_applicable" ? "a" : "u";
    }).join("");
    return `3${payload}`;
  }

  function decodeAnswers(jurisdiction, code, questions) {
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
      return null;
    }
    raw = raw.padEnd(questionIds.length, "u");
    const decoded = {};
    questionIds.forEach((questionId, index) => {
      let encoded = raw[index];
      if (euLegacyVersion === 1 && questionId === "public_facing") {
        encoded = encoded === "y" ? "n" : encoded === "n" ? "y" : encoded;
      }
      decoded[questionId] = encoded === "y" ? "yes" :
        encoded === "n" ? "no" : encoded === "a" ? "not_applicable" : "unsure";
    });
    return decoded;
  }

  return {
    buildQuestionnaireRequest,
    decodeAnswers,
    encodeAnswers,
    evaluateQuestionnaireDecision,
    factIdsForQuestion,
  };
});
