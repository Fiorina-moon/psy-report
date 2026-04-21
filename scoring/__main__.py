from __future__ import annotations

import argparse
from pathlib import Path

from agent.loaders import load_config
from scoring.compute import run_scoring


def main() -> None:
    p = argparse.ArgumentParser(description="离线计分：生成 output/scored/scored_cohort.json")
    p.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "config.yaml",
    )
    args = p.parse_args()
    cfg = load_config(args.config.resolve())
    out = cfg.paths.scored_cohort_json
    run_scoring(cfg.paths.results_xlsx, out)
    print(f"已写入: {out}")


if __name__ == "__main__":
    main()
