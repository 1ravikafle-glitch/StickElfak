"""
AICOS entrypoint — CLI only. Do not add a web server, dashboard, or GUI here
in v1 (see ARCHITECTURE.md > Scope Lock).

Usage:
    python -m src.main run --topic "Why cookies exist" --script path/to/script.txt
    python -m src.main run --topic "Why cookies exist" --script path/to/script.txt --publish yes
    python -m src.main status --job-id <id>

Contract:
    `run` MUST do nothing but call job_runner.run_job(topic, script_path, publish)
    and print the returned JobResult. All actual logic lives in src/pipeline
    and src/publishing. This file stays a thin CLI wrapper — if it grows
    past ~120 lines, that's drift; move logic out.
"""

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aicos")
    sub = parser.add_subparsers(dest="command", required=True)

    run_cmd = sub.add_parser("run", help="Generate (and optionally publish) one video")
    run_cmd.add_argument("--topic", required=True, help="Short topic string, e.g. 'Why cookies exist'")
    run_cmd.add_argument("--script", required=True, help="Path to a .txt file with the full narration script")
    run_cmd.add_argument("--publish", choices=["yes", "no"], default="no")
    run_cmd.add_argument("--platforms", nargs="*", default=["youtube", "facebook", "tiktok"],
                          help="Subset of platforms to publish to, if --publish yes")

    status_cmd = sub.add_parser("status", help="Check a past job's status")
    status_cmd.add_argument("--job-id", required=True)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        # from src.pipeline.job_runner import run_job
        # result = run_job(topic=args.topic, script_path=args.script,
        #                   publish=args.publish == "yes", platforms=args.platforms)
        # print(result)
        raise NotImplementedError("Wire up job_runner.run_job here — see contract above.")
    elif args.command == "status":
        raise NotImplementedError("Wire up utils.job_state lookup here.")


if __name__ == "__main__":
    main()
