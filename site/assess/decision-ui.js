// Shared review-record presentation. Locale copy is kept in this one renderer.
(function (root, factory) {
  const api = factory(root.RegulaDecisionAdapters);
  if (typeof module === "object" && module.exports) module.exports = api;
  root.RegulaDecisionUI = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (adapters) {
  "use strict";

  const VISIBLE_MISSING = 5;
  const COPY = {
    en: {
      eyebrow: "Review record",
      status: { insufficient_information: "More context is needed", human_review_required: "Human review required" },
      plain: {
        insufficient_information: "The answers preserve open or contradictory context. Nothing here is a completed legal decision.",
        human_review_required: "The answers name potentially relevant provisions, but an accountable person must decide what they mean for the real deployment.",
      },
      evidence: function (c) { return "Context considered: " + c.resolved_fact_count + " resolved, " + c.absent_fact_count + " absent, " + c.explicit_unknown_fact_count + " explicitly unknown, " + c.contradictory_fact_count + " contradictory."; },
      declared: "Declared context", noDeclared: "No context has been declared.",
      provisions: "Potentially relevant provisions", provisionState: "Unresolved applicability question",
      noProvisions: "No provision was selected from the supplied context. This is not a non-applicability conclusion.",
      missing: "Missing or explicitly unknown context", missingIntro: "These questions remain open and have not been counted as No.",
      contradictions: "Contradictory context", contradictionsIntro: "Conflicting declarations require manual resolution.",
      reason: "Current state", reasons: { absent: "Not answered", explicit_unknown: "You selected Not sure" }, showMore: function (n) { return "Show " + n + " more open facts"; },
      human: "Human decision", humanEmpty: "Not recorded. This field remains empty until an accountable reviewer completes it.",
      limitations: "Limits of this record",
      limitationItems: [
        "Declared answers and code observations do not determine legal applicability, risk tier, duties or compliance.",
        "A missing code indicator does not prove that legal relevance is absent.",
        "This record does not replace qualified legal, governance, security or technical review.",
      ],
      nextTitle: "What to do next",
      steps: {
        resolve: "Resolve the open facts from sources you can identify, while preserving any uncertainty or contradiction.",
        settled: "Check each declaration against a source you can identify and update it if the deployment changes.",
        scan: "Scan source code for observable indicators, then keep those observations separate from declared context.",
        review: "Ask an accountable qualified reviewer to interpret the evidence and record the human decision separately.",
      },
      scanCta: "Scan source code",
      states: { yes: "Yes", no: "No", unknown: "Not sure", not_applicable: "Not applicable" },
      exportDisclaimer: "Evidence-preparation record based on self-reported facts. No legal determination. Not legal advice.",
    },
    de: {
      eyebrow: "Prüfprotokoll",
      status: { insufficient_information: "Mehr Kontext erforderlich", human_review_required: "Menschliche Prüfung erforderlich" },
      plain: {
        insufficient_information: "Die Antworten bewahren offene oder widersprüchliche Angaben. Dies ist keine abgeschlossene rechtliche Entscheidung.",
        human_review_required: "Die Antworten benennen möglicherweise relevante Vorschriften. Eine verantwortliche Person muss ihre Bedeutung für den tatsächlichen Einsatz prüfen.",
      },
      evidence: function (c) { return "Berücksichtigter Kontext: " + c.resolved_fact_count + " geklärt, " + c.absent_fact_count + " fehlend, " + c.explicit_unknown_fact_count + " ausdrücklich unbekannt, " + c.contradictory_fact_count + " widersprüchlich."; },
      declared: "Deklarierter Kontext", noDeclared: "Es wurde kein Kontext deklariert.",
      provisions: "Möglicherweise relevante Vorschriften", provisionState: "Offene Anwendungsfrage",
      noProvisions: "Aus dem angegebenen Kontext wurde keine Vorschrift ausgewählt. Dies ist keine Feststellung der Nichtanwendbarkeit.",
      missing: "Fehlender oder ausdrücklich unbekannter Kontext", missingIntro: "Diese Fragen bleiben offen und wurden nicht als Nein gewertet.",
      contradictions: "Widersprüchlicher Kontext", contradictionsIntro: "Widersprüchliche Angaben müssen manuell geklärt werden.",
      reason: "Aktueller Stand", reasons: { absent: "Nicht beantwortet", explicit_unknown: "Sie haben Unsicher ausgewählt" }, showMore: function (n) { return n + " weitere offene Tatsachen anzeigen"; },
      human: "Menschliche Entscheidung", humanEmpty: "Nicht erfasst. Dieses Feld bleibt leer, bis eine verantwortliche prüfende Person es ausfüllt.",
      limitations: "Grenzen dieses Protokolls",
      limitationItems: [
        "Deklarierte Antworten und Code-Beobachtungen bestimmen weder rechtliche Anwendbarkeit, Risikoklasse, Pflichten noch Konformität.",
        "Ein fehlender Code-Indikator beweist nicht, dass keine rechtliche Relevanz besteht.",
        "Dieses Protokoll ersetzt keine qualifizierte rechtliche, Governance-, Sicherheits- oder technische Prüfung.",
      ],
      nextTitle: "Nächste Schritte",
      steps: {
        resolve: "Klären Sie offene Tatsachen aus benennbaren Quellen und bewahren Sie Unsicherheit oder Widersprüche.",
        settled: "Prüfen Sie jede Angabe anhand einer benennbaren Quelle und aktualisieren Sie sie bei Änderungen des Einsatzes.",
        scan: "Prüfen Sie den Quellcode auf beobachtbare Indikatoren und halten Sie diese von deklariertem Kontext getrennt.",
        review: "Lassen Sie die Nachweise qualifiziert und verantwortlich auslegen und erfassen Sie die menschliche Entscheidung separat.",
      },
      scanCta: "Quellcode prüfen",
      states: { yes: "Ja", no: "Nein", unknown: "Unsicher", not_applicable: "Nicht anwendbar" },
      exportDisclaimer: "Protokoll zur Nachweisvorbereitung auf Grundlage selbst angegebener Tatsachen. Keine rechtliche Feststellung. Keine Rechtsberatung.",
    },
    "pt-br": {
      eyebrow: "Registro para revisão",
      status: { insufficient_information: "Mais contexto é necessário", human_review_required: "Revisão humana necessária" },
      plain: {
        insufficient_information: "As respostas preservam contexto em aberto ou contraditório. Isto não é uma decisão jurídica concluída.",
        human_review_required: "As respostas indicam dispositivos possivelmente relevantes, mas uma pessoa responsável deve decidir o que significam para a implantação real.",
      },
      evidence: function (c) { return "Contexto considerado: " + c.resolved_fact_count + " resolvidos, " + c.absent_fact_count + " ausentes, " + c.explicit_unknown_fact_count + " explicitamente desconhecidos, " + c.contradictory_fact_count + " contraditórios."; },
      declared: "Contexto declarado", noDeclared: "Nenhum contexto foi declarado.",
      provisions: "Dispositivos possivelmente relevantes", provisionState: "Questão de aplicabilidade em aberto",
      noProvisions: "Nenhum dispositivo foi selecionado a partir do contexto informado. Isso não é uma conclusão de não aplicabilidade.",
      missing: "Contexto ausente ou explicitamente desconhecido", missingIntro: "Estas perguntas continuam em aberto e não foram contadas como Não.",
      contradictions: "Contexto contraditório", contradictionsIntro: "Declarações conflitantes exigem resolução manual.",
      reason: "Estado atual", reasons: { absent: "Sem resposta", explicit_unknown: "Você selecionou Não sei" }, showMore: function (n) { return "Mostrar mais " + n + " fatos em aberto"; },
      human: "Decisão humana", humanEmpty: "Não registrada. Este campo permanece vazio até ser preenchido por uma pessoa revisora responsável.",
      limitations: "Limites deste registro",
      limitationItems: [
        "Respostas declaradas e observações de código não determinam aplicabilidade jurídica, classe de risco, deveres ou conformidade.",
        "A ausência de um indicador de código não prova a ausência de relevância jurídica.",
        "Este registro não substitui revisão jurídica, de governança, de segurança ou técnica qualificada.",
      ],
      nextTitle: "Próximos passos",
      steps: {
        resolve: "Resolva os fatos em aberto a partir de fontes identificáveis, preservando incertezas ou contradições.",
        settled: "Verifique cada declaração em uma fonte identificável e atualize-a se a implantação mudar.",
        scan: "Analise o código-fonte em busca de indicadores observáveis e mantenha essas observações separadas do contexto declarado.",
        review: "Peça a uma pessoa revisora qualificada e responsável que interprete as evidências e registre a decisão humana separadamente.",
      },
      scanCta: "Analisar código-fonte",
      states: { yes: "Sim", no: "Não", unknown: "Não sei", not_applicable: "Não aplicável" },
      exportDisclaimer: "Registro de preparação de evidências baseado em fatos autodeclarados. Sem determinação jurídica. Não é aconselhamento jurídico.",
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

  function card(title, body) {
    return `<div class="obl-card"><div class="obl-title">${escapeHtml(title)}</div>` +
      `<div class="obl-desc">${escapeHtml(body)}</div></div>`;
  }

  function renderQuestionnaireResult(result, options) {
    const copy = copyFor(options.locale);
    const labels = factLabels(result.jurisdiction, options.questions);
    const completeness = result.evidence_completeness;
    const styleClass = result.review_status === "insufficient_information" ? "tier-limited" : "tier-high";
    options.tierElement.innerHTML = `
      <div class="result-tier ${styleClass}" role="status" aria-live="polite">
        <div class="tier-label">${escapeHtml(copy.eyebrow)}</div>
        <div class="tier-name">${escapeHtml(copy.status[result.review_status])}</div>
        <div class="tier-desc">${escapeHtml(copy.plain[result.review_status])}</div>
        <div style="margin-top:12px;font-size:0.8rem;opacity:0.75;">${escapeHtml(copy.evidence(completeness))}</div>
      </div>`;
    const resultTier = options.tierElement.querySelector(".result-tier");
    if (resultTier) { resultTier.tabIndex = -1; resultTier.focus(); }

    let detail = `<h2>${escapeHtml(copy.declared)}</h2><div class="obligations">`;
    if (!result.declared_context.length) detail += `<p>${escapeHtml(copy.noDeclared)}</p>`;
    for (const context of result.declared_context) {
      const title = labels[context.fact_id] || context.fact_id;
      const state = context.state === null ? context.status : (copy.states[context.state] || context.state);
      detail += card(title, state);
    }
    detail += "</div>";

    detail += `<h2 style="margin-top:20px;">${escapeHtml(copy.provisions)}</h2>`;
    if (!result.potentially_relevant_provisions.length) detail += `<p>${escapeHtml(copy.noProvisions)}</p>`;
    else {
      detail += '<div class="obligations">';
      for (const provision of result.potentially_relevant_provisions) detail += card(provision.reference, copy.provisionState);
      detail += "</div>";
    }

    const missing = result.missing_context || [];
    if (missing.length) {
      detail += `<h2 style="margin-top:20px;">${escapeHtml(copy.missing)}</h2><p>${escapeHtml(copy.missingIntro)}</p><div class="obligations">`;
      for (const item of missing.slice(0, VISIBLE_MISSING)) detail += card(labels[item.fact_id] || item.question, `${copy.reason}: ${copy.reasons[item.reason] || item.reason}`);
      detail += "</div>";
      if (missing.length > VISIBLE_MISSING) {
        detail += `<details><summary>${escapeHtml(copy.showMore(missing.length - VISIBLE_MISSING))}</summary><div class="obligations">`;
        for (const item of missing.slice(VISIBLE_MISSING)) detail += card(labels[item.fact_id] || item.question, `${copy.reason}: ${copy.reasons[item.reason] || item.reason}`);
        detail += "</div></details>";
      }
    }

    const contradictions = result.contradictory_context || [];
    if (contradictions.length) {
      detail += `<h2 style="margin-top:20px;">${escapeHtml(copy.contradictions)}</h2><p>${escapeHtml(copy.contradictionsIntro)}</p><div class="obligations">`;
      for (const item of contradictions) detail += card(labels[item.fact_id] || item.fact_id, item.status);
      detail += "</div>";
    }

    const humanDecision = result.human_decision;
    const humanText = humanDecision === null ? copy.humanEmpty : String(humanDecision);
    detail += `<h2 style="margin-top:20px;">${escapeHtml(copy.human)}</h2>` +
      `<div class="obl-card"><div class="obl-title">${escapeHtml(humanText)}</div></div>`;
    detail += `<h2 style="margin-top:20px;">${escapeHtml(copy.limitations)}</h2><ul>` +
      copy.limitationItems.map(item => `<li>${escapeHtml(item)}</li>`).join("") + "</ul>";
    options.detailsElement.innerHTML = detail;

    const steps = [missing.length ? copy.steps.resolve : copy.steps.settled, copy.steps.scan, copy.steps.review];
    let next = `<h2>${escapeHtml(copy.nextTitle)}</h2>`;
    steps.forEach((text, index) => {
      next += `<div class="step-item"><div class="step-num">${index + 1}</div><div class="step-text"><span>${escapeHtml(text)}</span></div></div>`;
    });
    next += `<div style="margin-top:16px;"><button type="button" class="btn btn-secondary" style="min-height:44px;" onclick="if(window.startScanner)window.startScanner()">${escapeHtml(copy.scanCta)}</button></div>`;
    options.nextElement.innerHTML = next;
  }

  function exportResult(result, options) {
    const copy = copyFor(options.locale);
    const data = {
      tool: "Regula Web Assessment", model_version: result.model_version,
      date: new Date().toISOString(), disclaimer: copy.exportDisclaimer,
      answers: options.answers, review_record: result,
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
