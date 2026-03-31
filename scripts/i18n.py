"""Internationalisation support for Regula CLI output.

Usage:
    from i18n import t, set_language
    set_language("pt-BR")
    print(t("scan_header"))  # "Verificação Regula: ..."
"""

_LANG = "en"

_STRINGS = {
    "en": {
        # Scan output
        "scan_header": "Regula Scan: {path}",
        "files_scanned": "Files scanned:",
        "prohibited": "Prohibited:",
        "credentials": "Credentials:",
        "high_risk": "High-risk:",
        "agent_autonomy": "Agent autonomy:",
        "limited_risk": "Limited-risk:",
        "suppressed": "Suppressed:",
        "block_tier": "BLOCK tier:",
        "warn_tier": "WARN tier:",
        "info_tier": "INFO tier:",
        "confidence_note": "Confidence scores: 0-100 (higher = more indicators matched)",
        "tier_note": "Tiers: BLOCK (>=80 or prohibited), WARN (50-79), INFO (<50)",
        "suppress_note": "Suppress findings: add '# regula-ignore' to file",

        # Classification tiers
        "tier_prohibited": "PROHIBITED",
        "tier_high_risk": "HIGH-RISK",
        "tier_limited_risk": "LIMITED-RISK",
        "tier_minimal_risk": "MINIMAL-RISK",

        # Gap assessment
        "gap_header": "EU AI Act Compliance Gap Assessment: {project}",
        "gap_highest_risk": "Highest risk tier: {tier}",
        "gap_date": "Assessment date:",
        "gap_score": "Overall score:",
        "gap_evidence": "Evidence:",
        "gap_finding": "Gap:",
        "gap_frameworks": "Frameworks:",
        "gap_summary": "Summary:",

        # Doctor
        "doctor_header": "Regula Doctor",

        # Metrics
        "metrics_header": "Regula Metrics (local only — never sent)",
        "metrics_total_scans": "Total scans:",
        "metrics_total_findings": "Total findings:",
        "metrics_first_scan": "First scan:",
        "metrics_last_scan": "Last scan:",
        "metrics_by_tier": "Findings by tier:",

        # General
        "error_prefix": "Error:",
        "not_legal_advice": "Findings are indicators, not legal determinations.",
    },
    "pt-BR": {
        # Scan output
        "scan_header": "Verificação Regula: {path}",
        "files_scanned": "Arquivos verificados:",
        "prohibited": "Proibidos:",
        "credentials": "Credenciais:",
        "high_risk": "Alto risco:",
        "agent_autonomy": "Autonomia de agente:",
        "limited_risk": "Risco limitado:",
        "suppressed": "Suprimidos:",
        "block_tier": "Nível BLOQUEAR:",
        "warn_tier": "Nível ALERTA:",
        "info_tier": "Nível INFO:",
        "confidence_note": "Pontuação de confiança: 0-100 (maior = mais indicadores encontrados)",
        "tier_note": "Níveis: BLOQUEAR (>=80 ou proibido), ALERTA (50-79), INFO (<50)",
        "suppress_note": "Suprimir resultados: adicione '# regula-ignore' ao arquivo",

        # Classification tiers
        "tier_prohibited": "PROIBIDO",
        "tier_high_risk": "ALTO RISCO",
        "tier_limited_risk": "RISCO LIMITADO",
        "tier_minimal_risk": "RISCO MÍNIMO",

        # Gap assessment
        "gap_header": "Avaliação de Conformidade com a Lei IA da UE: {project}",
        "gap_highest_risk": "Maior nível de risco: {tier}",
        "gap_date": "Data da avaliação:",
        "gap_score": "Pontuação geral:",
        "gap_evidence": "Evidência:",
        "gap_finding": "Lacuna:",
        "gap_frameworks": "Marcos regulatórios:",
        "gap_summary": "Resumo:",

        # Doctor
        "doctor_header": "Regula Diagnóstico",

        # Metrics
        "metrics_header": "Métricas Regula (apenas local — nunca enviadas)",
        "metrics_total_scans": "Total de verificações:",
        "metrics_total_findings": "Total de achados:",
        "metrics_first_scan": "Primeira verificação:",
        "metrics_last_scan": "Última verificação:",
        "metrics_by_tier": "Achados por nível:",

        # General
        "error_prefix": "Erro:",
        "not_legal_advice": "Os achados são indicadores, não determinações legais.",
    },
}


def set_language(lang: str) -> None:
    """Set the output language. Supported: 'en', 'pt-BR'."""
    global _LANG
    if lang in _STRINGS:
        _LANG = lang


def get_language() -> str:
    """Return the current language code."""
    return _LANG


def t(key: str, **kwargs) -> str:
    """Translate a string key. Falls back to English if key not found."""
    strings = _STRINGS.get(_LANG, _STRINGS["en"])
    template = strings.get(key, _STRINGS["en"].get(key, key))
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template
