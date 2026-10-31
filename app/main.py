from __future__ import annotations

import argparse
import json

from app.graph import workflow_graph


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the multi-agent software company workflow.")
    parser.add_argument(
        "task",
        nargs="?",
        default="Yeni çıkan X kütüphanesini kullanarak bir e-ticaret botu yaz",
        help="Engineering task to process.",
    )
    args = parser.parse_args()

    result = workflow_graph.run(args.task)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
