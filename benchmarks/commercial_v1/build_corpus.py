#!/usr/bin/env python3
"""Build the explicit truth-by-construction commercial_v1 corpus.

This generator contains no Regula detector terms copied from implementation.
Its cases derive from the public product claims and Article 50 observable
evidence categories frozen in PROTOCOL.md.
"""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).parent


def _case(identifier, candidate, language, content, transform, observable):
    return {
        "id": identifier,
        "candidate": candidate,
        "language": language,
        "relative_path": "src/case." + ("py" if language == "python" else "html"),
        "transform": transform,
        "content": content,
        "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
        "observable": observable,
    }


def build():
    corpus = []
    labels = []
    ai_modules = [
        "torch", "tensorflow", "transformers", "sklearn", "openai",
        "anthropic", "langchain", "llama_index", "ollama", "xgboost",
    ]
    transforms = ["direct_import", "alias_import", "from_import"]
    for index in range(40):
        module = ai_modules[index % len(ai_modules)]
        transform = transforms[index % len(transforms)]
        if transform == "direct_import":
            content = f"import {module}\nmodel_component = {module!r}\n"
        elif transform == "alias_import":
            content = f"import {module} as component_{index}\n"
        else:
            content = f"from {module} import client as component_{index}\n"
        identifier = f"a-positive-{index + 1:02d}"
        corpus.append(_case(identifier, "A", "python", content, transform,
                            "AI library or service import"))
        labels.append({"decision_id": identifier, "candidate": "A", "expected": True,
                       "basis": "truth-by-construction import"})

    negative_templates = [
        ("comment", "# Example documentation says: import {module}\nvalue = 1\n"),
        ("string_literal", "message = \"import {module}\"\nvalue = len(message)\n"),
        ("near_name", "import {near}\nvalue = {near}.__name__\n"),
        ("dead_comment", "# removed dependency: {module}\ndef add(a, b): return a + b\n"),
        ("documentation", "DOC = \"The team evaluated {module}, but it is not used.\"\n"),
    ]
    for index in range(40):
        module = ai_modules[index % len(ai_modules)]
        transform, template = negative_templates[index % len(negative_templates)]
        near = module.replace("_", "") + "_notes"
        content = template.format(module=module, near=near)
        identifier = f"a-negative-{index + 1:02d}"
        corpus.append(_case(identifier, "A", "python", content, transform,
                            "no implemented AI library, model, or service"))
        labels.append({"decision_id": identifier, "candidate": "A", "expected": False,
                       "basis": "truth-by-construction near miss"})

    article50_positive = [
        ("chatbot_notice", '<p id="ai-notice">You are interacting with an AI system.</p>'),
        ("synthetic_marker", '<meta name="ai-generated" content="true">'),
        ("deepfake_notice", '<figcaption>This video was artificially generated.</figcaption>'),
        ("emotion_notice", '<p>Emotion recognition is active during this session.</p>'),
        ("biometric_notice", '<p>Biometric categorisation is active for this interaction.</p>'),
    ]
    wrappers = [
        ("rendered_body", "<html><body>{}</body></html>"),
        ("nested_template", "<main><section>{}</section></main>"),
        ("language_attribute", '<div lang="en">{}</div>'),
    ]
    for index in range(40):
        category, fragment = article50_positive[index % len(article50_positive)]
        transform, wrapper = wrappers[index % len(wrappers)]
        content = wrapper.format(fragment) + "\n"
        identifier = f"b-positive-{index + 1:02d}"
        corpus.append(_case(identifier, "B", "html", content,
                            f"{category}:{transform}",
                            "rendered Article 50 implementation evidence"))
        labels.append({"decision_id": identifier, "candidate": "B", "expected": True,
                       "basis": f"truth-by-construction {category}"})

    article50_negative = [
        ("html_comment", "<!-- You are interacting with an AI system. -->"),
        ("non_rendered_template", '<template id="unused">AI-generated content</template>'),
        ("irrelevant_attribute", '<div data-doc="deepfake disclosure">ordinary content</div>'),
        ("developer_note", '<script type="text/plain">add emotion recognition notice later</script>'),
        ("negated_copy", '<p>This service does not use biometric categorisation.</p>'),
    ]
    for index in range(40):
        transform, fragment = article50_negative[index % len(article50_negative)]
        content = f"<html><body>{fragment}</body></html>\n"
        identifier = f"b-negative-{index + 1:02d}"
        corpus.append(_case(identifier, "B", "html", content, transform,
                            "no rendered affirmative Article 50 evidence"))
        labels.append({"decision_id": identifier, "candidate": "B", "expected": False,
                       "basis": "truth-by-construction near miss"})

    return corpus, labels


def main():
    corpus, labels = build()
    (ROOT / "corpus.json").write_text(json.dumps(corpus, indent=2) + "\n")
    (ROOT / "labels.json").write_text(json.dumps(labels, indent=2) + "\n")
    print(f"wrote {len(corpus)} corpus decisions and {len(labels)} blinded labels")


if __name__ == "__main__":
    main()
