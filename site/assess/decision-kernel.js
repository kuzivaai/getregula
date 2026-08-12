// Dependency-free browser evaluator for references/decision_model.v1.json.
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.RegulaDecisionKernel = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const FACT_STATES = new Set(["yes", "no", "unknown", "not_applicable"]);

  class DecisionInputError extends Error {}

  function validateModel(model) {
    if (!model || model.schema_version !== "1.0") {
      throw new DecisionInputError("unsupported decision model schema_version");
    }
    if (typeof model.model_version !== "string") {
      throw new DecisionInputError("decision model has no model_version");
    }
    for (const [jurisdiction, config] of Object.entries(model.jurisdictions || {})) {
      const ruleIds = new Set((config.rules || []).map(rule => rule.id));
      if (ruleIds.size !== (config.rules || []).length) {
        throw new DecisionInputError(`jurisdiction ${jurisdiction} has duplicate rule ids`);
      }
      for (const expression of [config.scope, ...config.rules, ...config.obligations]) {
        validateExpression(expression, model.fact_definitions, ruleIds);
      }
    }
  }

  function validateExpression(expression, factDefinitions, ruleIds) {
    if (!expression || typeof expression !== "object" || Array.isArray(expression)) {
      throw new DecisionInputError("predicate expression must be an object");
    }
    if (Object.prototype.hasOwnProperty.call(expression, "fact")) {
      if (!Object.prototype.hasOwnProperty.call(factDefinitions, expression.fact)) {
        throw new DecisionInputError(`unknown model fact ${expression.fact}`);
      }
      if (!FACT_STATES.has(expression.is)) {
        throw new DecisionInputError(`invalid expected state for ${expression.fact}`);
      }
    }
    for (const operator of ["all", "any"]) {
      if (Object.prototype.hasOwnProperty.call(expression, operator)) {
        if (!Array.isArray(expression[operator]) || expression[operator].length === 0) {
          throw new DecisionInputError(`predicate operator ${operator} must be non-empty`);
        }
        expression[operator].forEach(child =>
          validateExpression(child, factDefinitions, ruleIds));
      }
    }
    for (const key of ["rule_any", "when_rule_any"]) {
      if (Object.prototype.hasOwnProperty.call(expression, key)) {
        if (!Array.isArray(expression[key]) || expression[key].length === 0) {
          throw new DecisionInputError(`${key} must be a non-empty array`);
        }
        const unknown = expression[key].filter(ruleId => !ruleIds.has(ruleId));
        if (unknown.length) throw new DecisionInputError(`unknown rule references: ${unknown}`);
      }
    }
  }

  function validateTimestamp(value, factId) {
    if (typeof value !== "string" || !/(Z|[+-]\d\d:\d\d)$/.test(value) ||
        Number.isNaN(Date.parse(value))) {
      throw new DecisionInputError(`fact ${factId} timestamp must include a timezone`);
    }
  }

  function parseRequest(model, request) {
    if (!request || typeof request !== "object" || Array.isArray(request)) {
      throw new DecisionInputError("decision request must be an object");
    }
    if (request.model_version !== model.model_version) {
      throw new DecisionInputError(`model_version must be ${model.model_version}`);
    }
    const jurisdiction = request.jurisdiction;
    if (!Object.prototype.hasOwnProperty.call(model.jurisdictions, jurisdiction)) {
      throw new DecisionInputError("unsupported jurisdiction");
    }
    if (!request.facts || typeof request.facts !== "object" || Array.isArray(request.facts)) {
      throw new DecisionInputError("facts must be an object keyed by fact id");
    }
    const unknown = Object.keys(request.facts).filter(
      factId => !Object.prototype.hasOwnProperty.call(model.fact_definitions, factId));
    if (unknown.length) throw new DecisionInputError(`unknown fact ids: ${unknown.sort()}`);

    const resolutions = {};
    for (const [factId, definition] of Object.entries(model.fact_definitions)) {
      const raw = request.facts[factId];
      if (raw === undefined) {
        resolutions[factId] = { fact_id: factId, status: "absent", state: null, values: [] };
        continue;
      }
      if (!raw || typeof raw !== "object" || !Array.isArray(raw.values) || !raw.values.length) {
        throw new DecisionInputError(`fact ${factId} must have a non-empty values array`);
      }
      if (!["common", jurisdiction].includes(definition.jurisdiction)) {
        throw new DecisionInputError(`fact ${factId} does not belong to ${jurisdiction}`);
      }
      const values = raw.values.map(value => {
        if (!value || typeof value !== "object" || !FACT_STATES.has(value.state)) {
          throw new DecisionInputError(`fact ${factId} has invalid state`);
        }
        if (!value.provenance || typeof value.provenance !== "object" ||
            typeof value.provenance.source_type !== "string" ||
            typeof value.provenance.source_ref !== "string") {
          throw new DecisionInputError(`fact ${factId} provenance is required`);
        }
        if (!["common", jurisdiction].includes(value.jurisdiction)) {
          throw new DecisionInputError(`fact ${factId} value has wrong jurisdiction`);
        }
        validateTimestamp(value.timestamp, factId);
        return JSON.parse(JSON.stringify(value));
      });
      const decisive = [...new Set(values
        .filter(value => value.state !== "unknown")
        .map(value => value.state))];
      let status;
      let state;
      if (decisive.length > 1) {
        status = "contradictory";
        state = null;
      } else if (decisive.length === 0) {
        status = "explicit_unknown";
        state = null;
      } else {
        status = "resolved";
        state = decisive[0];
      }
      resolutions[factId] = { fact_id: factId, status, state, values };
    }
    return { jurisdiction, resolutions };
  }

  function combine(operator, children) {
    let state;
    if (operator === "all") {
      state = children.some(child => child.state === "false") ? "false" :
        children.some(child => child.state === "unresolved") ? "unresolved" : "true";
    } else {
      state = children.some(child => child.state === "true") ? "true" :
        children.some(child => child.state === "unresolved") ? "unresolved" : "false";
    }
    const factIds = new Set(children.flatMap(child => [...child.fact_ids]));
    const unresolved = state === "unresolved" ?
      new Set(children.flatMap(child => [...child.unresolved])) : new Set();
    return {
      state,
      trace: { operator, state, children: children.map(child => child.trace) },
      fact_ids: factIds,
      unresolved,
    };
  }

  function evaluateExpression(expression, resolutions, ruleResults) {
    if (Object.prototype.hasOwnProperty.call(expression, "fact")) {
      const resolution = resolutions[expression.fact];
      const state = resolution.state === null ? "unresolved" :
        resolution.state === expression.is ? "true" : "false";
      return {
        state,
        trace: {
          fact: expression.fact,
          expected: expression.is,
          actual: resolution.state,
          fact_status: resolution.status,
          state,
        },
        fact_ids: new Set([expression.fact]),
        unresolved: state === "unresolved" ? new Set([expression.fact]) : new Set(),
      };
    }
    for (const key of ["rule_any", "when_rule_any"]) {
      if (Object.prototype.hasOwnProperty.call(expression, key)) {
        return combine("any", expression[key].map(ruleId => {
          const result = ruleResults[ruleId];
          return {
            state: result.state,
            trace: { rule: ruleId, state: result.state },
            fact_ids: result.fact_ids,
            unresolved: result.unresolved,
          };
        }));
      }
    }
    for (const operator of ["all", "any"]) {
      if (Object.prototype.hasOwnProperty.call(expression, operator)) {
        return combine(operator, expression[operator].map(child =>
          evaluateExpression(child, resolutions, ruleResults)));
      }
    }
    throw new DecisionInputError("predicate expression has no supported operator");
  }

  function namedTrace(config, result) {
    return {
      predicate_id: config.id,
      provision: config.provision,
      state: result.state,
      trace: result.trace,
    };
  }

  function traceFactIds(value, target = new Set()) {
    if (Array.isArray(value)) value.forEach(child => traceFactIds(child, target));
    else if (value && typeof value === "object") {
      if (typeof value.fact === "string") target.add(value.fact);
      Object.values(value).forEach(child => traceFactIds(child, target));
    }
    return target;
  }

  function matchedEvidence(factIds, resolutions) {
    return [...new Set(factIds)].sort()
      .map(factId => resolutions[factId])
      .filter(resolution => resolution.state !== null)
      .map(resolution => JSON.parse(JSON.stringify(resolution)));
  }

  function rankUnresolved(model, unresolved, resolutions) {
    const impacts = new Map();
    for (const [factId, predicateId, provision] of unresolved) {
      if (!impacts.has(factId)) impacts.set(factId, new Map());
      impacts.get(factId).set(`${predicateId}\u0000${provision}`,
        { predicate_id: predicateId, provision });
    }
    return [...impacts.entries()].map(([factId, affected]) => ({
      fact_id: factId,
      reason: resolutions[factId].status,
      question: model.fact_definitions[factId].question,
      would_resolve: [...affected.values()].sort((a, b) =>
        a.predicate_id.localeCompare(b.predicate_id) || a.provision.localeCompare(b.provision)),
      resolution_count: affected.size,
      observed_values: JSON.parse(JSON.stringify(resolutions[factId].values)),
    })).sort((a, b) => b.resolution_count - a.resolution_count ||
      a.fact_id.localeCompare(b.fact_id));
  }

  function baseResult(model, resultType, jurisdiction, resolutions,
      ruleResolution, decisionTrace, evidence, payload) {
    const consideredIds = new Set();
    decisionTrace.forEach(trace => traceFactIds(trace, consideredIds));
    const considered = [...consideredIds].map(factId => resolutions[factId]);
    return Object.assign({
      result_type: resultType,
      schema_version: "1.0",
      model_version: model.model_version,
      jurisdiction,
      evidence_completeness: {
        considered_fact_count: considered.length,
        resolved_fact_count: considered.filter(item => item.state !== null).length,
        explicit_unknown_fact_count: considered.filter(item => item.status === "explicit_unknown").length,
        contradictory_fact_count: considered.filter(item => item.status === "contradictory").length,
        absent_fact_count: considered.filter(item => item.status === "absent").length,
      },
      rule_resolution: ruleResolution,
      matched_evidence: evidence,
      decision_trace: decisionTrace,
      probability_calibration: {
        available: false,
        condition: "Representative labelled outcomes are required before a correctness probability can be calibrated.",
      },
    }, payload || {});
  }

  function insufficientResult(model, jurisdiction, resolutions, traces, unresolved) {
    const factIds = new Set();
    traces.forEach(trace => traceFactIds(trace, factIds));
    return baseResult(model, "insufficient_information", jurisdiction, resolutions,
      "unresolved", traces, matchedEvidence(factIds, resolutions), {
        unresolved_predicates: rankUnresolved(model, unresolved, resolutions),
      });
  }

  function evaluateDecision(model, request) {
    validateModel(model);
    const { jurisdiction, resolutions } = parseRequest(model, request);
    const config = model.jurisdictions[jurisdiction];
    const scope = evaluateExpression(config.scope, resolutions, {});
    const scopeTrace = namedTrace(config.scope, scope);
    if (scope.state === "false") {
      return baseResult(model, "outside_scope_candidate", jurisdiction, resolutions,
        "resolved", [scopeTrace], matchedEvidence(scope.fact_ids, resolutions), {
          outside_scope_basis: {
            predicate_id: config.scope.id,
            provision: config.scope.provision,
            satisfied_false_path: scope.trace,
          },
        });
    }
    if (scope.state === "unresolved") {
      return insufficientResult(model, jurisdiction, resolutions, [scopeTrace],
        [...scope.unresolved].map(factId =>
          [factId, config.scope.id, config.scope.provision]));
    }

    const ruleResults = {};
    const ruleTraces = [];
    for (const rule of config.rules) {
      const result = evaluateExpression(rule, resolutions, ruleResults);
      ruleResults[rule.id] = result;
      ruleTraces.push(namedTrace(rule, result));
    }
    const matchedRules = config.rules.filter(rule => ruleResults[rule.id].state === "true");
    if (!matchedRules.length) {
      const unresolved = [];
      for (const rule of config.rules) {
        for (const factId of ruleResults[rule.id].unresolved) {
          unresolved.push([factId, rule.id, rule.provision]);
        }
      }
      if (unresolved.length) {
        return insufficientResult(model, jurisdiction, resolutions,
          [scopeTrace, ...ruleTraces], unresolved);
      }
      const allFactIds = new Set(scope.fact_ids);
      Object.values(ruleResults).forEach(result =>
        result.fact_ids.forEach(factId => allFactIds.add(factId)));
      return baseResult(model, "outside_scope_candidate", jurisdiction, resolutions,
        "resolved", [scopeTrace, ...ruleTraces],
        matchedEvidence(allFactIds, resolutions), {
          outside_scope_basis: {
            predicate_id: "no_traced_rule_matched",
            provision: "All named predicates for the selected jurisdiction",
            satisfied_false_path: ruleTraces.filter(trace => trace.state === "false"),
          },
        });
    }

    const obligationTraces = [];
    const obligations = [];
    const unresolved = [];
    for (const rule of config.rules) {
      if (ruleResults[rule.id].state === "unresolved") {
        for (const factId of ruleResults[rule.id].unresolved) {
          unresolved.push([factId, rule.id, rule.provision]);
        }
      }
    }
    for (const obligation of config.obligations) {
      const result = evaluateExpression(obligation, resolutions, ruleResults);
      obligationTraces.push(namedTrace(obligation, result));
      if (result.state === "true") {
        const applicabilityByRule = Object.fromEntries(Object.entries(
          obligation.applicability_by_rule || {}).filter(
          ([ruleId]) => ruleResults[ruleId].state === "true"));
        const matchedDates = [...new Set(Object.values(applicabilityByRule))].sort();
        let applicableFrom = obligation.applicable_from || null;
        if (applicableFrom === null && matchedDates.length === 1) {
          applicableFrom = matchedDates[0];
        }
        if (applicableFrom === null && Object.keys(applicabilityByRule).length === 0) {
          applicableFrom = config.default_applicable_from || null;
        }
        obligations.push({
          obligation_id: obligation.id,
          name: obligation.name,
          provision: obligation.provision,
          applicable_from: applicableFrom,
          applicability_by_rule: applicabilityByRule,
          applicability_note: obligation.applicability_note || null,
          satisfied_predicate_path: result.trace,
          evidence_path: matchedEvidence(result.fact_ids, resolutions),
        });
      } else if (result.state === "unresolved") {
        for (const factId of result.unresolved) {
          unresolved.push([factId, obligation.id, obligation.provision]);
        }
      }
    }
    const matchedFactIds = new Set(scope.fact_ids);
    matchedRules.forEach(rule => ruleResults[rule.id].fact_ids.forEach(
      factId => matchedFactIds.add(factId)));
    const indications = matchedRules.map(rule => ({
      predicate_id: rule.id,
      classification: rule.classification,
      provision: rule.provision,
      applicable_from: rule.applicable_from || config.default_applicable_from || null,
      applicability_note: rule.applicability_note || null,
      satisfied_predicate_path: ruleResults[rule.id].trace,
    }));
    return baseResult(model, "indication", jurisdiction, resolutions,
      unresolved.length ? "partial" : "resolved",
      [scopeTrace, ...ruleTraces, ...obligationTraces],
      matchedEvidence(matchedFactIds, resolutions), {
        indications,
        obligations,
        unresolved_predicates: rankUnresolved(model, unresolved, resolutions),
      });
  }

  function makeFact(state, sourceRef, jurisdiction, timestamp, sourceType = "user_attestation") {
    return { values: [{
      state,
      provenance: { source_type: sourceType, source_ref: sourceRef },
      jurisdiction,
      timestamp,
    }] };
  }

  return { DecisionInputError, evaluateDecision, makeFact, validateModel };
});
