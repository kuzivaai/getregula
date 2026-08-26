// Shared questionnaire flow. Question text and UI strings are locale data
// supplied by each page; the control flow below is defined once so the three
// locale pages cannot drift apart the way three inline copies did.
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.RegulaAssessFlow = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const STORAGE_KEY = "regula_assess";
  // Rough reading-and-answering rate used only for the entry-time estimate.
  const SECONDS_PER_QUESTION = 15;

  let config = null;
  let currentQuestion = 0;
  let answers = {};
  let assessmentStarted = false;
  let activeJurisdiction = "eu";

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, character => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
    })[character]);
  }

  function byId(id) { return document.getElementById(id); }

  function questionsFor(jurisdiction) {
    return config.questions[jurisdiction] || config.questions.eu;
  }

  function activeQuestions() { return questionsFor(activeJurisdiction); }

  // A question counts as decision-bearing only if the adapter maps it onto a
  // fact the kernel actually evaluates. Deriving this instead of hardcoding a
  // list means a question that later gains a mapping is promoted automatically,
  // and none can silently become dead weight.
  function isDecisionQuestion(jurisdiction, question) {
    return window.RegulaDecisionAdapters
      .factIdsForQuestion(jurisdiction, question.id).length > 0;
  }

  function partitionFor(jurisdiction) {
    const questions = questionsFor(jurisdiction);
    const decision = [];
    const readiness = [];
    questions.forEach((question, index) => {
      (isDecisionQuestion(jurisdiction, question) ? decision : readiness).push(index);
    });
    return { decision, readiness };
  }

  // Display order puts decision-bearing questions first. The underlying array
  // order is untouched because the share-link encoding is positional over it.
  function displayOrderFor(jurisdiction) {
    const parts = partitionFor(jurisdiction);
    return parts.decision.concat(parts.readiness);
  }

  function activeDisplayOrder() { return displayOrderFor(activeJurisdiction); }

  function decisionCount(jurisdiction) {
    return partitionFor(jurisdiction).decision.length;
  }

  function scopeQuestionId() {
    return config.scopeQuestionId[activeJurisdiction];
  }

  function saveProgress() {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
        currentQuestion, answers, assessmentStarted, activeJurisdiction,
      }));
    } catch (e) { /* quota or private browsing */ }
  }

  function loadProgress(jurisdictionFromUrl) {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY);
      if (!saved) return;
      const data = JSON.parse(saved);
      // An explicit ?j= in the address bar is a deliberate request for a
      // jurisdiction and outranks whatever a previous visit left in session
      // storage. Without this, a stored jurisdiction silently won and the link
      // opened the wrong regulation. When the two disagree, the stored answers
      // belong to a different question set, so the saved position is dropped
      // rather than resumed against questions it was never given for.
      if (jurisdictionFromUrl && data.activeJurisdiction &&
          data.activeJurisdiction !== activeJurisdiction) {
        return;
      }
      currentQuestion = data.currentQuestion || 0;
      answers = data.answers || {};
      assessmentStarted = data.assessmentStarted || false;
      if (data.activeJurisdiction && !jurisdictionFromUrl) {
        activeJurisdiction = data.activeJurisdiction;
        selectJurisdiction(activeJurisdiction);
      }
      if (assessmentStarted) {
        byId("heroSection").style.display = "none";
        byId("questionnaireSection").style.display = "block";
        byId("assessIntro").style.display = "block";
        renderQuestion();
      }
    } catch (e) { /* ignore */ }
  }

  function selectJurisdiction(jurisdiction) {
    activeJurisdiction = jurisdiction;
    document.querySelectorAll(".jurisdiction-btn").forEach(button => {
      button.style.border = "1px solid var(--border)";
      button.style.background = "transparent";
      button.style.color = "var(--text-dim)";
      button.classList.remove("selected");
      button.setAttribute("aria-pressed", "false");
    });
    const button = byId("jur-" + jurisdiction);
    if (button) {
      button.style.border = "1px solid var(--border-active)";
      button.style.background = "var(--accent-dim)";
      button.style.color = "var(--accent)";
      button.classList.add("selected");
      button.setAttribute("aria-pressed", "true");
    }
    renderJurisdictionMeta();
  }

  // Previously this line was written only when a jurisdiction button was
  // clicked, so a visitor arriving on the default selection was never told
  // how long the questionnaire is before committing to it.
  function renderJurisdictionMeta() {
    const target = byId("jurisdictionInfo");
    if (!target) return;
    const info = config.jurisdictionInfo[activeJurisdiction];
    if (!info) return;
    const decisions = decisionCount(activeJurisdiction);
    const minutes = Math.max(1, Math.round(decisions * SECONDS_PER_QUESTION / 60));
    target.textContent = config.copy.jurisdictionMeta(info, decisions, minutes);
  }

  function updateAssessIntro() {
    const target = byId("assessIntro");
    if (!target) return;
    const intro = config.copy.intros[activeJurisdiction] || config.copy.intros.eu;
    target.innerHTML = '<p style="margin:0 0 8px 0;">' + escapeHtml(intro) +
      '</p><p style="margin:0;font-size:0.8rem;color:var(--text-muted);">' +
      escapeHtml(config.copy.storageNotice) + "</p>";
  }

  function startAssessment() {
    assessmentStarted = true;
    byId("heroSection").style.display = "none";
    byId("questionnaireSection").style.display = "block";
    byId("resultsSection").classList.remove("active");
    byId("assessIntro").style.display = "block";
    updateAssessIntro();
    renderQuestion();
  }

  function answeredCount() { return Object.keys(answers).length; }

  // The scope question is decisive on its own: when it resolves false the
  // kernel returns outside_scope_candidate whatever the remaining answers say,
  // so continuing cannot change the outcome. Verified against the kernel for
  // all three jurisdictions before this shortcut was offered.
  function scopeResolvedOut() {
    return answers[scopeQuestionId()] === "no";
  }

  function renderQuestion() {
    const questions = activeQuestions();
    const order = activeDisplayOrder();
    const decisions = decisionCount(activeJurisdiction);
    const question = questions[order[currentQuestion]];
    const existing = answers[question.id] || null;
    const isReadiness = currentQuestion >= decisions;
    const container = byId("questionContainer");
    const qId = "q-" + question.id;
    const copy = config.copy;

    const position = isReadiness ? currentQuestion - decisions + 1 : currentQuestion + 1;
    const total = isReadiness ? order.length - decisions : decisions;
    const eyebrow = isReadiness
      ? copy.optionalEyebrow(position, total)
      : copy.questionEyebrow(position, total);

    let banner = "";
    if (isReadiness && position === 1) {
      banner = '<div class="q-banner" role="note">' +
        "<strong>" + escapeHtml(copy.readiness.title) + "</strong> " +
        escapeHtml(copy.readiness.body) + "</div>";
    }

    container.innerHTML = `
      ${banner}
      <div class="q-card" role="group" aria-labelledby="${qId}-text">
        <div class="q-number" aria-hidden="true">${escapeHtml(eyebrow)}</div>
        <div class="q-text" id="${qId}-text">${question.text}</div>
        <div class="q-help" id="${qId}-help">${question.help}</div>
        <div class="q-article">${question.article}</div>
        <div class="answers" role="group" aria-label="${escapeHtml(copy.answerGroupLabel)}" aria-describedby="${qId}-help">
          <button type="button" class="ans-btn ${existing === "yes" ? "selected" : ""}" onclick="answer('yes', this)" aria-pressed="${existing === "yes"}">${escapeHtml(copy.answers.yes)}</button>
          <button type="button" class="ans-btn ${existing === "no" ? "selected-no" : ""}" onclick="answer('no', this)" aria-pressed="${existing === "no"}">${escapeHtml(copy.answers.no)}</button>
          <button type="button" class="ans-btn ${existing === "unsure" ? "selected-unsure" : ""}" onclick="answer('unsure', this)" aria-pressed="${existing === "unsure"}">${escapeHtml(copy.answers.unsure)}</button>
          <button type="button" class="ans-btn ${existing === "not_applicable" ? "selected-na" : ""}" onclick="answer('not_applicable', this)" aria-pressed="${existing === "not_applicable"}">${escapeHtml(copy.answers.notApplicable)}</button>
        </div>
        <p class="answer-legend">${escapeHtml(copy.answerLegend)}</p>
      </div>
    `;

    if (currentQuestion > 0) {
      const intro = byId("assessIntro");
      if (intro) intro.style.display = "none";
    }

    // Progress counts the current question as in progress, so the bar starts
    // above zero and reaches full on the final question rather than showing
    // 0% to someone who has already committed to answering.
    const pct = Math.round(((position) / total) * 100);
    byId("progressBar").style.width = pct + "%";
    byId("progressPct").textContent = pct + "%";
    byId("progressText").textContent = isReadiness
      ? copy.optionalProgress(position, total)
      : copy.progress(position, total);
    byId("progressWrap").setAttribute("aria-valuenow", pct);

    byId("prevBtn").disabled = currentQuestion === 0;
    byId("nextBtn").disabled = !existing;
    byId("nextBtn").textContent = currentQuestion === order.length - 1
      ? copy.seeResults : copy.next;

    renderEarlyExit();

    const questionText = byId(qId + "-text");
    if (questionText) {
      questionText.setAttribute("tabindex", "-1");
      questionText.focus();
    }
  }

  // A persistent way out with a valid result. Someone who has answered enough
  // to get an honest answer should never have to click through questions that
  // cannot change it in order to see one.
  function renderEarlyExit() {
    const host = byId("earlyExit");
    if (!host) return;
    const copy = config.copy;
    const order = activeDisplayOrder();
    const onLastQuestion = currentQuestion === order.length - 1;

    if (!answeredCount() || onLastQuestion) {
      host.innerHTML = "";
      host.style.display = "none";
      return;
    }
    host.style.display = "block";
    if (scopeResolvedOut()) {
      host.innerHTML = '<div class="early-exit early-exit-final" role="note">' +
        "<p>" + escapeHtml(copy.earlyExit.finalBody) + "</p>" +
        '<button type="button" class="btn btn-primary" onclick="showResults()">' +
        escapeHtml(copy.earlyExit.seeResult) + "</button></div>";
      return;
    }
    host.innerHTML = '<div class="early-exit">' +
      '<button type="button" class="btn btn-secondary" onclick="showResults()">' +
      escapeHtml(copy.earlyExit.seeResult) + "</button>" +
      '<span class="early-exit-note">' + escapeHtml(copy.earlyExit.note) + "</span></div>";
  }

  function answer(value, button) {
    const questions = activeQuestions();
    const order = activeDisplayOrder();
    const question = questions[order[currentQuestion]];
    answers[question.id] = value;

    button.parentElement.querySelectorAll(".ans-btn").forEach(other => {
      other.className = "ans-btn";
      other.setAttribute("aria-pressed", "false");
    });
    button.setAttribute("aria-pressed", "true");
    if (value === "yes") button.className = "ans-btn selected";
    else if (value === "no") button.className = "ans-btn selected-no";
    else if (value === "unsure") button.className = "ans-btn selected-unsure";
    else button.className = "ans-btn selected-na";

    byId("nextBtn").disabled = false;
    renderEarlyExit();
    saveProgress();
  }

  function nextQuestion() {
    if (currentQuestion < activeDisplayOrder().length - 1) {
      currentQuestion++;
      renderQuestion();
      saveProgress();
    } else {
      showResults();
    }
  }

  function prevQuestion() {
    if (currentQuestion > 0) {
      currentQuestion--;
      renderQuestion();
      saveProgress();
    }
  }

  function calculateResults() {
    return window.RegulaDecisionAdapters
      .evaluateQuestionnaireDecision(activeJurisdiction, answers);
  }

  function showResults() {
    byId("questionnaireSection").style.display = "none";
    const results = calculateResults();
    byId("resultsSection").classList.add("active");
    window.RegulaDecisionUI.renderQuestionnaireResult(results, {
      locale: document.documentElement.lang,
      questions: activeQuestions(),
      tierElement: byId("tierResult"),
      detailsElement: byId("obligationsList"),
      nextElement: byId("nextStepsSection"),
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function encodeAnswers() {
    return window.RegulaDecisionAdapters
      .encodeAnswers(activeJurisdiction, answers, activeQuestions());
  }

  function decodeAnswers(code) {
    return window.RegulaDecisionAdapters
      .decodeAnswers(activeJurisdiction, code, activeQuestions());
  }

  function copyShareLink() {
    const code = encodeAnswers();
    const jurParam = activeJurisdiction !== "eu" ? "&j=" + activeJurisdiction : "";
    const url = window.location.origin + window.location.pathname + "?r=" + code + jurParam;
    const input = byId("shareUrl");
    input.value = url;
    byId("shareSection").style.display = "block";
    input.select();
    navigator.clipboard.writeText(url).catch(() => {});
  }

  function exportJSON() {
    window.RegulaDecisionUI.exportResult(calculateResults(), {
      locale: document.documentElement.lang,
      answers: answers,
    });
  }

  function resetAssessment() {
    currentQuestion = 0;
    answers = {};
    assessmentStarted = false;
    activeJurisdiction = "eu";
    selectJurisdiction("eu");
    byId("resultsSection").classList.remove("active");
    byId("heroSection").style.display = "block";
    byId("questionnaireSection").style.display = "none";
    window.history.replaceState(null, "", window.location.pathname);
    try { sessionStorage.removeItem(STORAGE_KEY); } catch (e) { /* ignore */ }
  }

  function handleKeydown(event) {
    if (!assessmentStarted) return;
    const section = byId("questionnaireSection");
    if (!section || section.style.display === "none") return;
    const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
    const buttons = document.querySelectorAll(".ans-btn");
    const pick = index => {
      if (buttons.length > index) { buttons[index].click(); buttons[index].focus(); }
    };
    if (key === "ArrowRight" || key === "ArrowDown") {
      event.preventDefault();
      if (!byId("nextBtn").disabled) nextQuestion();
    } else if (key === "ArrowLeft" || key === "ArrowUp") {
      event.preventDefault();
      if (!byId("prevBtn").disabled) prevQuestion();
    } else if (key === "1" || key === config.copy.keys.yes) pick(0);
    else if (key === "2" || key === config.copy.keys.no) pick(1);
    else if (key === "3" || key === config.copy.keys.unsure) pick(2);
    else if (key === "4" || key === config.copy.keys.notApplicable) pick(3);
  }

  function install(options) {
    config = options;

    window.selectJurisdiction = selectJurisdiction;
    window.startAssessment = startAssessment;
    window.renderQuestion = renderQuestion;
    window.answer = answer;
    window.nextQuestion = nextQuestion;
    window.prevQuestion = prevQuestion;
    window.showResults = showResults;
    window.calculateResults = calculateResults;
    window.copyShareLink = copyShareLink;
    window.exportJSON = exportJSON;
    window.resetAssessment = resetAssessment;
    window.updateAssessIntro = updateAssessIntro;

    // The scanner section still lives in each page and reads the active
    // jurisdiction. Expose it as a live getter rather than a copied value so
    // the two can never disagree.
    Object.defineProperty(window, "activeJurisdiction", {
      get: () => activeJurisdiction,
      configurable: true,
    });

    document.addEventListener("keydown", handleKeydown);

    const params = new URLSearchParams(window.location.search);
    const jurParam = params.get("j");
    const jurisdictionFromUrl = Boolean(jurParam && config.jurisdictionInfo[jurParam]);
    if (jurisdictionFromUrl) {
      selectJurisdiction(jurParam);
    } else {
      selectJurisdiction(activeJurisdiction);
    }

    const code = params.get("r");
    if (code) {
      // Strip encoded answers from the address bar once decoded. The payload
      // is user-derived data and should not remain in browser history.
      try { history.replaceState(null, "", location.pathname); } catch (e) { /* ignore */ }
      const decoded = decodeAnswers(code);
      if (decoded) {
        answers = decoded;
        assessmentStarted = true;
        byId("heroSection").style.display = "none";
        showResults();
        return;
      }
    }
    loadProgress(jurisdictionFromUrl);
  }

  return {
    install,
    // Exposed for contract tests: these derive from the adapter at runtime,
    // so a test can assert the split without copying any question list.
    partitionFor,
    displayOrderFor,
    decisionCount,
  };
});
