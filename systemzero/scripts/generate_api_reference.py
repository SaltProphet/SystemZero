from typing import Any, Dict, List
from pathlib import Path
import argparse
import yaml

from interface.api.server import app


def md(s: str) -> str:
    return s.replace("_", "\\_")


def render_parameters(params: List[Dict[str, Any]]) -> str:
    if not params:
        return "- None\n"
    lines = []
    for p in params:
        name = p.get("name", "")
        required = p.get("required", False)
        loc = p.get("in", "")
        schema = p.get("schema", {})
        typ = schema.get("type", schema.get("$ref", "object"))
        desc = (p.get("description") or "").strip().replace("\n", " ")
        lines.append(f"- {name} ({loc}, {typ}, {'required' if required else 'optional'}): {desc}")
    return "\n".join(lines) + "\n"


def render_request_body(body: Dict[str, Any]) -> str:
    if not body:
        return "- None\n"
    required = body.get("required", False)
    content = body.get("content", {})
    media_types = ", ".join(content.keys()) or "application/json"
    return f"- media: {media_types} ({'required' if required else 'optional'})\n"


def render_responses(resp: Dict[str, Any]) -> str:
    if not resp:
        return "- None\n"
    lines = []
    for code, spec in resp.items():
        desc = (spec.get("description") or "").strip().replace("\n", " ")
        lines.append(f"- {code}: {desc}")
    return "\n".join(lines) + "\n"


def generate_markdown(schema: Dict[str, Any]) -> str:
    out: List[str] = []
    info = schema.get("info", {})
    title = info.get("title", "API")
    version = info.get("version", "")
    out.append(f"# {md(title)} Reference\n\n")
    out.append(f"Version: {version}\n\n")
    servers = schema.get("servers", [])
    if servers:
        out.append("## Servers\n")
        for s in servers:
            out.append(f"- {s.get('url')}\n")
        out.append("\n")

    paths = schema.get("paths", {})
    if not paths:
        out.append("No paths defined.\n")
        return "".join(out)

    out.append("## Endpoints\n\n")
    for path, methods in sorted(paths.items()):
        out.append(f"### {path}\n\n")
        for method, spec in methods.items():
            method_up = method.upper()
            summary = spec.get("summary") or spec.get("operationId") or ""
            out.append(f"- **{method_up}**: {md(summary)}\n")
            params = spec.get("parameters", [])
            if params:
                out.append("  - Parameters:\n")
                out.append(render_parameters(params))
            req_body = spec.get("requestBody")
            if req_body:
                out.append("  - Request Body:\n")
                out.append(render_request_body(req_body))
            responses = spec.get("responses", {})
            out.append("  - Responses:\n")
            out.append(render_responses(responses))
        out.append("\n")
    return "".join(out)


def main():
    parser = argparse.ArgumentParser(description="Generate Markdown API reference from OpenAPI schema")
    parser.add_argument("--out", type=Path, default=Path("docs/API_REFERENCE.md"))
    args = parser.parse_args()

    schema = app.openapi()
    md_text = generate_markdown(schema)

    out_path: Path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md_text, encoding="utf-8")
    print(f"✓ API reference generated at {out_path}")


if __name__ == "__main__":
    main()
