"""Mycelium CLI entry point — python -m core <command>"""

import argparse
import sys
import json
from core.mycelium import Mycelium, Scout, ArmyAnt, DynamicAnt
from core.providers import MockAgentProvider


def main():
    parser = argparse.ArgumentParser(prog="core", description="Mycelium AI Framework CLI")
    sub = parser.add_subparsers(dest="cmd")

    # mission
    m = sub.add_parser("mission", help="Execute a mission")
    m.add_argument("mission", help="Mission description")
    m.add_argument("--provider", default="mock", choices=["mock"], help="Agent provider")
    m.add_argument("--capabilities", nargs="+", default=["frontend", "design"], help="Required capabilities")

    # health
    sub.add_parser("health", help="Check colony health")

    # scout
    s = sub.add_parser("scout", help="Scout research")
    s.add_argument("query", help="Research query")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    provider = MockAgentProvider()
    brain = Mycelium(provider=provider)

    if args.cmd == "mission":
        result = brain.execute_mission(args.mission, capabilities=args.capabilities)
        print(json.dumps(result, indent=2, default=str))

    elif args.cmd == "health":
        result = brain.check_colony_health()
        print(json.dumps(result, indent=2))

    elif args.cmd == "scout":
        sc = Scout(brain)
        result = sc.research_models(args.query)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
