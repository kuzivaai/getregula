// Shared tagged-result presentation. All presentation strings are locale data.
(function (root, factory) {
  const api = factory(root.RegulaDecisionAdapters);
  if (typeof module === "object" && module.exports) module.exports = api;
  root.RegulaDecisionUI = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (adapters) {
  "use strict";

  // How many unresolved-fact cards are shown before the rest are collapsed.
  // The full list stays in the DOM inside a <details>, so nothing is hidden
  // from export, print or assistive technology; it is only folded away.
  const UNRESOLVED_VISIBLE = 5;

  const COPY = {
    en: {
      eyebrow: "Assessment result",
      labels: {
        indication: "Regulatory indication",
        insufficient_information: "More facts required",
        outside_scope_candidate: "Outside-scope candidate",
      },
      plain: {
        indication: "Based on the answers you gave, at least one named rule in this regulation appears to apply to your system. The provisions to review are listed below.",
        insufficient_information: "This cannot be settled yet. Your answers do not resolve the question either way. The facts still needed are listed below, and anything you marked “Not sure” was left open rather than counted as a no.",
        outside_scope_candidate: "Based on the answers you gave, this regulation does not appear to be triggered. Check the evidence path below, and run this again if any of those answers change.",
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
      evidencePlain: function (c) {
        const parts = [
          c.resolved_fact_count + " settled by your answers",
          c.absent_fact_count + " not supplied",
          c.explicit_unknown_fact_count + " marked not sure",
        ];
        if (c.contradictory_fact_count) {
          parts.push(c.contradictory_fact_count + " contradictory");
        }
        return "Facts considered: " + parts.join(", ") + ".";
      },
      indications: "Indications",
      obligations: "Obligations supported by resolved predicate paths",
      unresolved: "Facts that would resolve more of the decision",
      unresolvedIntro: "Each one names the provision it would settle. None of these has been counted for or against you.",
      showMore: function (n) {
        return "Show " + n + " more open " + (n === 1 ? "fact" : "facts");
      },
      applies: "Applicable from",
      provision: "Provision",
      reason: "Current state",
      resolves: "Would resolve",
      noObligations: "No obligation was emitted from the supplied facts.",
      nextTitle: "What to do next",
      steps: {
        resolve: "Resolve the open facts listed above. Answer each one from a source you can point to, then run this assessment again.",
        settled: "Your answers settled every fact this model considered. Run this again if your system, its purpose or where it is used changes.",
        scan: "Scan your source code. The questionnaire records what you know; the scanner reads what the code actually does. Together they are stronger evidence than either alone.",
        review: "Save or print this result and have a qualified reviewer confirm the legal interpretation. Regula indicates possible relevance; it does not determine compliance.",
      },
      scanCta: "Scan source code",
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
      eyebrow: "Bewertungsergebnis",
      labels: { indication: "Regulatorischer Hinweis", insufficient_information: "Weitere Tatsachen erforderlich", outside_scope_candidate: "Möglicherweise außerhalb des Geltungsbereichs" },
      plain: {
        indication: "Nach Ihren Angaben scheint mindestens eine benannte Regel dieser Verordnung für Ihr System zu gelten. Die zu prüfenden Vorschriften stehen unten.",
        insufficient_information: "Das lässt sich noch nicht klären. Ihre Angaben beantworten die Frage in keine Richtung. Die noch fehlenden Tatsachen stehen unten; alles, was Sie mit „Unsicher“ beantwortet haben, bleibt offen und wurde nicht als Nein gewertet.",
        outside_scope_candidate: "Nach Ihren Angaben scheint diese Verordnung nicht einschlägig zu sein. Prüfen Sie den Nachweispfad unten und führen Sie die Bewertung erneut durch, wenn sich eine dieser Antworten ändert.",
      },
      descriptions: {
        indication: "Mindestens ein benanntes rechtliches Prädikat wird durch die vorgelegten Nachweise erfüllt. Prüfen Sie offene Prädikate vor einer Verwendung des Ergebnisses.",
        insufficient_information: "Die vorgelegten Tatsachen tragen keine Feststellung. Klären Sie die folgenden Fragen; fehlende und unsichere Antworten wurden nicht als Nein behandelt.",
        outside_scope_candidate: "Ein benanntes Geltungsbereichsprädikat ist als falsch geklärt oder alle geprüften Regeln sind als falsch geklärt. Der verwendete Nachweispfad ist enthalten.",
      },
      evidence: "Nachweisstand", resolved: "geklärt", absent: "fehlend", unknown: "ausdrücklich unbekannt", contradictory: "widersprüchlich",
      evidencePlain: function (c) {
        const parts = [
          c.resolved_fact_count + " durch Ihre Antworten geklärt",
          c.absent_fact_count + " nicht angegeben",
          c.explicit_unknown_fact_count + " als unsicher markiert",
        ];
        if (c.contradictory_fact_count) {
          parts.push(c.contradictory_fact_count + " widersprüchlich");
        }
        return "Berücksichtigte Tatsachen: " + parts.join(", ") + ".";
      },
      indications: "Hinweise", obligations: "Durch geklärte Prädikatpfade gestützte Pflichten", unresolved: "Tatsachen, die weitere Teile der Entscheidung klären",
      unresolvedIntro: "Zu jeder ist die Vorschrift benannt, die sie klären würde. Keine davon wurde zu Ihren Gunsten oder Lasten gewertet.",
      showMore: function (n) {
        return n + " weitere offene " + (n === 1 ? "Tatsache" : "Tatsachen") + " anzeigen";
      },
      applies: "Anwendbar ab", provision: "Vorschrift", reason: "Aktueller Stand", resolves: "Würde klären", noObligations: "Aus den vorgelegten Tatsachen wurde keine Pflicht ausgegeben.", nextTitle: "Nächste Schritte",
      steps: {
        resolve: "Klären Sie die oben aufgeführten offenen Tatsachen. Beantworten Sie jede aus einer benennbaren Quelle und führen Sie die Bewertung erneut durch.",
        settled: "Ihre Antworten haben jede von diesem Modell berücksichtigte Tatsache geklärt. Führen Sie die Bewertung erneut durch, wenn sich Ihr System, sein Zweck oder sein Einsatzort ändert.",
        scan: "Prüfen Sie Ihren Quellcode. Der Fragebogen erfasst, was Sie wissen; der Scanner liest, was der Code tatsächlich tut. Zusammen sind sie ein stärkerer Nachweis als jedes für sich.",
        review: "Speichern oder drucken Sie dieses Ergebnis und lassen Sie die Rechtsauslegung qualifiziert prüfen. Regula weist auf mögliche Relevanz hin; es stellt keine Konformität fest.",
      },
      scanCta: "Quellcode prüfen",
      exportDisclaimer: "Markiertes Entscheidungsergebnis auf Grundlage selbst angegebener Tatsachen. Keine Rechtsberatung.",
      classifications: { high_risk_candidate: "Hochrisiko-Kandidat", prohibited_practice_candidate: "Kandidat für eine verbotene Praktik", transparency_duty_candidate: "Kandidat für eine Transparenzpflicht", high_impact_candidate: "Kandidat für KI mit hoher Auswirkung", advance_review_duty_candidate: "Kandidat für die Vorabprüfung", article_32_safety_duty_candidate: "Kandidat für die Sicherheitspflicht nach Artikel 32", domestic_agent_duty_candidate: "Kandidat für die Pflicht zu einem inländischen Vertreter", covered_admt_candidate: "Kandidat für abgedeckte ADMT" },
    },
    "pt-br": {
      eyebrow: "Resultado da avaliação",
      labels: { indication: "Indicação regulatória", insufficient_information: "Mais fatos necessários", outside_scope_candidate: "Candidato a fora do escopo" },
      plain: {
        indication: "Com base nas respostas que você deu, pelo menos uma regra nomeada desta regulamentação parece se aplicar ao seu sistema. Os dispositivos a revisar estão listados abaixo.",
        insufficient_information: "Ainda não é possível resolver. Suas respostas não decidem a questão em nenhuma direção. Os fatos que ainda faltam estão listados abaixo, e tudo que você marcou como “Não sei” permaneceu em aberto, sem ser contado como não.",
        outside_scope_candidate: "Com base nas respostas que você deu, esta regulamentação não parece ser acionada. Verifique o caminho de evidência abaixo e refaça a avaliação se alguma dessas respostas mudar.",
      },
      descriptions: {
        indication: "Um ou mais predicados jurídicos nomeados são satisfeitos pelas evidências fornecidas. Revise os predicados não resolvidos antes de confiar no resultado.",
        insufficient_information: "Os fatos fornecidos não sustentam uma determinação. Resolva as perguntas abaixo; respostas ausentes e incertas não foram tratadas como não.",
        outside_scope_candidate: "Um predicado de escopo nomeado foi resolvido como falso ou todas as regras rastreadas foram resolvidas como falsas. O caminho de evidência usado está incluído.",
      },
      evidence: "Resolução da evidência", resolved: "resolvidos", absent: "ausentes", unknown: "explicitamente desconhecidos", contradictory: "contraditórios",
      evidencePlain: function (c) {
        const parts = [
          c.resolved_fact_count + " resolvidos pelas suas respostas",
          c.absent_fact_count + " não informados",
          c.explicit_unknown_fact_count + " marcados como não sei",
        ];
        if (c.contradictory_fact_count) {
          parts.push(c.contradictory_fact_count + " contraditórios");
        }
        return "Fatos considerados: " + parts.join(", ") + ".";
      },
      indications: "Indicações", obligations: "Obrigações sustentadas por caminhos de predicados resolvidos", unresolved: "Fatos que resolveriam mais da decisão",
      unresolvedIntro: "Cada um indica o dispositivo que resolveria. Nenhum deles foi contado a seu favor ou contra você.",
      showMore: function (n) {
        return "Mostrar mais " + n + " " + (n === 1 ? "fato em aberto" : "fatos em aberto");
      },
      applies: "Aplicável a partir de", provision: "Dispositivo", reason: "Estado atual", resolves: "Resolveria", noObligations: "Nenhuma obrigação foi emitida a partir dos fatos fornecidos.", nextTitle: "Próximos passos",
      steps: {
        resolve: "Resolva os fatos em aberto listados acima. Responda cada um a partir de uma fonte identificável e execute a avaliação novamente.",
        settled: "Suas respostas resolveram todos os fatos considerados por este modelo. Execute novamente se o seu sistema, sua finalidade ou onde ele é usado mudar.",
        scan: "Analise o seu código-fonte. O questionário registra o que você sabe; o analisador lê o que o código realmente faz. Juntos são uma evidência mais forte do que cada um isoladamente.",
        review: "Salve ou imprima este resultado e obtenha revisão qualificada da interpretação jurídica. O Regula indica possível relevância; ele não determina conformidade.",
      },
      scanCta: "Analisar código-fonte",
      exportDisclaimer: "Resultado de decisão marcado com base em fatos autodeclarados. Não é aconselhamento jurídico.",
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

  function unresolvedCard(unresolved, labels, copy) {
    const question = labels[unresolved.fact_id] || unresolved.question;
    const provisions = unresolved.would_resolve.map(item => item.provision).join("; ");
    return `<div class="obl-card"><div class="obl-title">${escapeHtml(question)}</div>` +
      `<div class="obl-desc"><strong>${escapeHtml(copy.reason)}:</strong> ${escapeHtml(unresolved.reason)}` +
      `<br><strong>${escapeHtml(copy.resolves)}:</strong> ${escapeHtml(provisions)}</div></div>`;
  }

  function renderQuestionnaireResult(result, options) {
    const copy = copyFor(options.locale);
    const completeness = result.evidence_completeness;
    const labels = factLabels(result.jurisdiction, options.questions);
    const styleClass = result.result_type === "indication" ? "tier-high" :
      result.result_type === "outside_scope_candidate" ? "tier-minimal" : "tier-limited";
    // The eyebrow is a generic section label. Repeating the specific result
    // name in both slots read as a rendering fault, so the name appears once.
    options.tierElement.innerHTML = `
      <div class="result-tier ${styleClass}" role="status" aria-live="polite">
        <div class="tier-label">${escapeHtml(copy.eyebrow)}</div>
        <div class="tier-name">${escapeHtml(copy.labels[result.result_type])}</div>
        <div class="tier-desc">${escapeHtml(copy.plain[result.result_type])}</div>
        <div class="tier-desc" style="margin-top:10px;font-size:0.85rem;opacity:0.75;">${escapeHtml(copy.descriptions[result.result_type])}</div>
        <div style="margin-top:12px;font-size:0.8rem;opacity:0.75;">
          ${escapeHtml(copy.evidencePlain(completeness))}
        </div>
      </div>`;
    // The question card previously held focus when it was hidden, leaving
    // keyboard and screen-reader users at <body> after completion. Move focus
    // to the newly rendered status without adding it to the normal tab order.
    const resultTier = options.tierElement.querySelector(".result-tier");
    if (resultTier) {
      resultTier.tabIndex = -1;
      resultTier.focus();
    }

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
    const unresolvedList = result.unresolved_predicates || [];
    if (unresolvedList.length) {
      // A long unresolved list buried the obligations above it. The first few
      // stay visible; the remainder are folded but still present in the DOM.
      const visible = unresolvedList.slice(0, UNRESOLVED_VISIBLE);
      const hidden = unresolvedList.slice(UNRESOLVED_VISIBLE);
      detail += `<h2 style="margin-top:20px;">${escapeHtml(copy.unresolved)}</h2>`;
      detail += `<p style="font-size:0.85rem;color:var(--text-dim);margin:0 0 12px 0;">${escapeHtml(copy.unresolvedIntro)}</p>`;
      detail += `<div class="obligations">`;
      for (const unresolved of visible) {
        detail += unresolvedCard(unresolved, labels, copy);
      }
      detail += "</div>";
      if (hidden.length) {
        detail += `<details style="margin-top:4px;"><summary style="cursor:pointer;padding:10px 4px;min-height:44px;box-sizing:border-box;color:var(--accent);font-size:0.9rem;">${escapeHtml(copy.showMore(hidden.length))}</summary><div class="obligations">`;
        for (const unresolved of hidden) {
          detail += unresolvedCard(unresolved, labels, copy);
        }
        detail += "</div></details>";
      }
    }
    options.detailsElement.innerHTML = detail;

    // Next steps are adaptive: telling someone to resolve open facts when
    // none are open is a dead end, so that step is swapped for a re-run cue.
    const steps = [
      unresolvedList.length ? copy.steps.resolve : copy.steps.settled,
      copy.steps.scan,
      copy.steps.review,
    ];
    let next = `<h2>${escapeHtml(copy.nextTitle)}</h2>`;
    steps.forEach((text, index) => {
      next += `<div class="step-item"><div class="step-num">${index + 1}</div>` +
        `<div class="step-text"><span>${escapeHtml(text)}</span></div></div>`;
    });
    next += `<div style="margin-top:16px;"><button type="button" class="btn btn-secondary" style="min-height:44px;" onclick="if(window.startScanner)window.startScanner()">${escapeHtml(copy.scanCta)}</button></div>`;
    options.nextElement.innerHTML = next;
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
