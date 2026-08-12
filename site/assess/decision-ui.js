// Shared tagged-result presentation. All presentation strings are locale data.
(function (root, factory) {
  const api = factory(root.RegulaDecisionAdapters);
  if (typeof module === "object" && module.exports) module.exports = api;
  root.RegulaDecisionUI = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (adapters) {
  "use strict";

  const COPY = {
    en: {
      labels: {
        indication: "Regulatory indication",
        insufficient_information: "More facts required",
        outside_scope_candidate: "Outside-scope candidate",
      },
      descriptions: {
        indication: "One or more named legal predicates are satisfied by the supplied evidence. Review unresolved predicates before relying on the result.",
        insufficient_information: "The supplied facts do not support a determination. Resolve the questions below; missing and unsure answers have not been treated as no.",
        outside_scope_candidate: "A named scope predicate is resolved false, or all traced rules are resolved false. This result includes the evidence path used.",
      },
      evidence: "Evidence resolution",
      resolved: "resolved",
      absent: "absent",
      unknown: "explicitly unknown",
      contradictory: "contradictory",
      indications: "Indications",
      obligations: "Obligations supported by resolved predicate paths",
      unresolved: "Facts that would resolve more of the decision",
      applies: "Applicable from",
      provision: "Provision",
      reason: "Current state",
      resolves: "Would resolve",
      noObligations: "No obligation was emitted from the supplied facts.",
      nextTitle: "What to do next",
      next: "Collect or verify the unresolved facts from a source you can identify, then rerun the assessment. Have a qualified reviewer confirm legal interpretation before reliance.",
      exportDisclaimer: "Tagged decision result based on self-reported facts. Not legal advice.",
      classifications: {
        high_risk_candidate: "High-risk candidate",
        prohibited_practice_candidate: "Prohibited-practice candidate",
        transparency_duty_candidate: "Transparency-duty candidate",
        high_impact_candidate: "High-impact candidate",
        advance_review_duty_candidate: "Advance-review duty candidate",
        article_32_safety_duty_candidate: "Article 32 safety-duty candidate",
        domestic_agent_duty_candidate: "Domestic-agent duty candidate",
        covered_admt_candidate: "Covered-ADMT candidate",
      },
    },
    de: {
      labels: { indication: "Regulatorischer Hinweis", insufficient_information: "Weitere Tatsachen erforderlich", outside_scope_candidate: "Möglicherweise außerhalb des Geltungsbereichs" },
      descriptions: {
        indication: "Mindestens ein benanntes rechtliches Prädikat wird durch die vorgelegten Nachweise erfüllt. Prüfen Sie offene Prädikate vor einer Verwendung des Ergebnisses.",
        insufficient_information: "Die vorgelegten Tatsachen tragen keine Feststellung. Klären Sie die folgenden Fragen; fehlende und unsichere Antworten wurden nicht als Nein behandelt.",
        outside_scope_candidate: "Ein benanntes Geltungsbereichsprädikat ist als falsch geklärt oder alle geprüften Regeln sind als falsch geklärt. Der verwendete Nachweispfad ist enthalten.",
      },
      evidence: "Nachweisstand", resolved: "geklärt", absent: "fehlend", unknown: "ausdrücklich unbekannt", contradictory: "widersprüchlich",
      indications: "Hinweise", obligations: "Durch geklärte Prädikatpfade gestützte Pflichten", unresolved: "Tatsachen, die weitere Teile der Entscheidung klären", applies: "Anwendbar ab", provision: "Vorschrift", reason: "Aktueller Stand", resolves: "Würde klären", noObligations: "Aus den vorgelegten Tatsachen wurde keine Pflicht ausgegeben.", nextTitle: "Nächste Schritte", next: "Erheben oder prüfen Sie die offenen Tatsachen aus einer benennbaren Quelle und führen Sie die Bewertung erneut durch. Lassen Sie die Rechtsauslegung vor einer Verwendung qualifiziert prüfen.", exportDisclaimer: "Markiertes Entscheidungsergebnis auf Grundlage selbst angegebener Tatsachen. Keine Rechtsberatung.",
      classifications: { high_risk_candidate: "Hochrisiko-Kandidat", prohibited_practice_candidate: "Kandidat für eine verbotene Praktik", transparency_duty_candidate: "Kandidat für eine Transparenzpflicht", high_impact_candidate: "Kandidat für KI mit hoher Auswirkung", advance_review_duty_candidate: "Kandidat für die Vorabprüfung", article_32_safety_duty_candidate: "Kandidat für die Sicherheitspflicht nach Artikel 32", domestic_agent_duty_candidate: "Kandidat für die Pflicht zu einem inländischen Vertreter", covered_admt_candidate: "Kandidat für abgedeckte ADMT" },
    },
    "pt-br": {
      labels: { indication: "Indicação regulatória", insufficient_information: "Mais fatos necessários", outside_scope_candidate: "Candidato a fora do escopo" },
      descriptions: {
        indication: "Um ou mais predicados jurídicos nomeados são satisfeitos pelas evidências fornecidas. Revise os predicados não resolvidos antes de confiar no resultado.",
        insufficient_information: "Os fatos fornecidos não sustentam uma determinação. Resolva as perguntas abaixo; respostas ausentes e incertas não foram tratadas como não.",
        outside_scope_candidate: "Um predicado de escopo nomeado foi resolvido como falso ou todas as regras rastreadas foram resolvidas como falsas. O caminho de evidência usado está incluído.",
      },
      evidence: "Resolução da evidência", resolved: "resolvidos", absent: "ausentes", unknown: "explicitamente desconhecidos", contradictory: "contraditórios",
      indications: "Indicações", obligations: "Obrigações sustentadas por caminhos de predicados resolvidos", unresolved: "Fatos que resolveriam mais da decisão", applies: "Aplicável a partir de", provision: "Dispositivo", reason: "Estado atual", resolves: "Resolveria", noObligations: "Nenhuma obrigação foi emitida a partir dos fatos fornecidos.", nextTitle: "Próximos passos", next: "Colete ou verifique os fatos não resolvidos em uma fonte identificável e execute a avaliação novamente. Obtenha revisão qualificada da interpretação jurídica antes de confiar no resultado.", exportDisclaimer: "Resultado de decisão marcado com base em fatos autodeclarados. Não é aconselhamento jurídico.",
      classifications: { high_risk_candidate: "Candidato a alto risco", prohibited_practice_candidate: "Candidato a prática proibida", transparency_duty_candidate: "Candidato a dever de transparência", high_impact_candidate: "Candidato a alto impacto", advance_review_duty_candidate: "Candidato a revisão prévia", article_32_safety_duty_candidate: "Candidato a dever de segurança do Artigo 32", domestic_agent_duty_candidate: "Candidato a dever de representante doméstico", covered_admt_candidate: "Candidato a TATD abrangida" },
    },
  };

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, character => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
    })[character]);
  }

  function copyFor(locale) {
    const key = String(locale || "en").toLowerCase();
    return COPY[key] || COPY[key.split("-")[0]] || COPY.en;
  }

  function factLabels(jurisdiction, questions) {
    const labels = {};
    for (const question of questions || []) {
      for (const factId of adapters.factIdsForQuestion(jurisdiction, question.id)) {
        labels[factId] = question.text;
      }
    }
    return labels;
  }

  function renderQuestionnaireResult(result, options) {
    const copy = copyFor(options.locale);
    const completeness = result.evidence_completeness;
    const labels = factLabels(result.jurisdiction, options.questions);
    const styleClass = result.result_type === "indication" ? "tier-high" :
      result.result_type === "outside_scope_candidate" ? "tier-minimal" : "tier-limited";
    options.tierElement.innerHTML = `
      <div class="result-tier ${styleClass}" role="status" aria-live="polite">
        <div class="tier-label">${escapeHtml(copy.labels[result.result_type])}</div>
        <div class="tier-name">${escapeHtml(copy.labels[result.result_type])}</div>
        <div class="tier-desc">${escapeHtml(copy.descriptions[result.result_type])}</div>
        <div style="margin-top:12px;font-size:0.8rem;opacity:0.75;">
          ${escapeHtml(copy.evidence)}: ${completeness.resolved_fact_count} ${escapeHtml(copy.resolved)},
          ${completeness.absent_fact_count} ${escapeHtml(copy.absent)},
          ${completeness.explicit_unknown_fact_count} ${escapeHtml(copy.unknown)},
          ${completeness.contradictory_fact_count} ${escapeHtml(copy.contradictory)}
        </div>
      </div>`;

    let detail = "";
    if (result.indications && result.indications.length) {
      detail += `<h2>${escapeHtml(copy.indications)}</h2><div class="obligations">`;
      for (const indication of result.indications) {
        detail += `<div class="obl-card"><div class="obl-title">${escapeHtml(copy.classifications[indication.classification] || indication.classification)}</div><div class="obl-desc"><strong>${escapeHtml(copy.provision)}:</strong> ${escapeHtml(indication.provision)}</div>${indication.applicable_from ? `<div class="obl-deadline">${escapeHtml(copy.applies)}: ${escapeHtml(indication.applicable_from)}</div>` : ""}</div>`;
      }
      detail += "</div>";
    }
    if (result.obligations && result.obligations.length) {
      detail += `<h2 style="margin-top:20px;">${escapeHtml(copy.obligations)}</h2><div class="obligations">`;
      for (const obligation of result.obligations) {
        const dates = Object.values(obligation.applicability_by_rule || {});
        const date = obligation.applicable_from || (dates.length ? [...new Set(dates)].join(", ") : null);
        detail += `<div class="obl-card"><div class="obl-title">${escapeHtml(obligation.name)}</div><div class="obl-desc"><strong>${escapeHtml(copy.provision)}:</strong> ${escapeHtml(obligation.provision)}</div>${date ? `<div class="obl-deadline">${escapeHtml(copy.applies)}: ${escapeHtml(date)}</div>` : ""}</div>`;
      }
      detail += "</div>";
    } else {
      detail += `<p>${escapeHtml(copy.noObligations)}</p>`;
    }
    if (result.unresolved_predicates && result.unresolved_predicates.length) {
      detail += `<h2 style="margin-top:20px;">${escapeHtml(copy.unresolved)}</h2><div class="obligations">`;
      for (const unresolved of result.unresolved_predicates) {
        const question = labels[unresolved.fact_id] || unresolved.question;
        detail += `<div class="obl-card"><div class="obl-title">${escapeHtml(question)}</div><div class="obl-desc"><strong>${escapeHtml(copy.reason)}:</strong> ${escapeHtml(unresolved.reason)}<br><strong>${escapeHtml(copy.resolves)}:</strong> ${escapeHtml(unresolved.would_resolve.map(item => item.provision).join("; "))}</div></div>`;
      }
      detail += "</div>";
    }
    options.detailsElement.innerHTML = detail;
    options.nextElement.innerHTML = `<div class="next-steps"><h2>${escapeHtml(copy.nextTitle)}</h2><div class="step-item"><div class="step-num">1</div><div class="step-text"><span>${escapeHtml(copy.next)}</span></div></div></div>`;
  }

  function exportResult(result, options) {
    const copy = copyFor(options.locale);
    const data = {
      tool: "Regula Web Assessment",
      model_version: result.model_version,
      date: new Date().toISOString(),
      disclaimer: copy.exportDisclaimer,
      answers: options.answers,
      decision: result,
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const anchor = document.createElement("a");
    anchor.href = URL.createObjectURL(blob);
    anchor.download = `regula-assessment-${new Date().toISOString().slice(0, 10)}.json`;
    anchor.click();
    URL.revokeObjectURL(anchor.href);
  }

  return { exportResult, renderQuestionnaireResult };
});
