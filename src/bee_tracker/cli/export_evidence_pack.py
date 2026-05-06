from __future__ import annotations
import argparse
import logging
from pathlib import Path
from ..evidence_pack import build_evidence_pack


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bee-export-evidence-pack")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--entity", required=True)
    parser.add_argument("--output", type=Path, required=True,
                        help="Output zip path")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    build_evidence_pack(
        root=args.root, entity_name=args.entity, output_zip=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
