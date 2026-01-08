from pathlib import Path
import argparse
import yaml

from interface.api.server import app


def main():
    parser = argparse.ArgumentParser(description="Export OpenAPI schema to YAML/JSON")
    parser.add_argument("--out", type=Path, default=Path("openapi.yaml"), help="Output file path")
    parser.add_argument("--format", choices=["yaml", "json"], default="yaml", help="Output format")
    args = parser.parse_args()

    schema = app.openapi()

    out_path: Path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "yaml":
        out_path.write_text(yaml.safe_dump(schema, sort_keys=False), encoding="utf-8")
    else:
        import json
        out_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    print(f"✓ OpenAPI schema exported to {out_path}")


if __name__ == "__main__":
    main()
