"""Main CLI entry point for System//Zero."""
import argparse
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from interface.cli.commands import (
    cmd_simulate,
    cmd_drift,
    cmd_replay,
    cmd_status,
    cmd_capture,
    cmd_dashboard,
    cmd_forensic,
    cmd_consistency,
)


def main():
    """Main CLI entry point with argparse."""
    parser = argparse.ArgumentParser(
        prog='systemzero',
        description='System//Zero - Environment Parser for Drift Detection',
        epilog='See PHASE2_PLAN.md for detailed usage'
    )
    
    parser.add_argument('--version', action='version', version='System//Zero 0.2.0 (Phase 2)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Simulate command
    sim_parser = subparsers.add_parser('simulate', help='Simulate pipeline with mock tree')
    sim_parser.add_argument('tree', nargs='?', help='Tree JSON file or fixture name (discord, doordash, login)')
    sim_parser.add_argument('--template', '-t', help='Template ID to match against')
    
    # Drift command
    drift_parser = subparsers.add_parser('drift', help='View drift events from log')
    drift_parser.add_argument('--log', '-l', help='Log file path (default: logs/systemzero.log)')
    drift_parser.add_argument('--filter', '-f', choices=['layout', 'content', 'sequence', 'manipulative'],
                             help='Filter by drift type')
    drift_parser.add_argument('--severity', '-s', choices=['info', 'warning', 'critical'],
                             help='Filter by severity')
    
    # Replay command
    replay_parser = subparsers.add_parser('replay', help='Replay log entries with timeline')
    replay_parser.add_argument('--log', '-l', help='Log file path (default: logs/systemzero.log)')
    replay_parser.add_argument('--start', type=int, default=0, help='Start index')
    replay_parser.add_argument('--end', type=int, help='End index')
    replay_parser.add_argument('--entry', '-e', type=int, help='View single entry')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Capture command (Phase 4)
    capture_parser = subparsers.add_parser('capture', help='Capture current UI tree')
    capture_parser.add_argument('--out', '-o', help='Output file path (default: captures/capture_<timestamp>.json)')
    capture_parser.add_argument('--tree', '-t', help='Existing tree JSON to record instead of live capture')

    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch live monitoring dashboard')
    dashboard_parser.add_argument('--log', '-l', help='Log file path (default: logs/systemzero.log)')

    # Forensic viewer command
    forensic_parser = subparsers.add_parser('forensic', help='Launch forensic drift viewer')
    forensic_parser.add_argument('--log', '-l', help='Log file path (default: logs/systemzero.log)')

    # Consistency monitor command
    consistency_parser = subparsers.add_parser('monitor', help='Launch cross-app consistency monitor')
    consistency_parser.add_argument('--log', '-l', help='Log file path (default: logs/systemzero.log)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'simulate':
        cmd_simulate(args.tree, args.template)
    elif args.command == 'drift':
        cmd_drift(args.log, args.filter, args.severity)
    elif args.command == 'replay':
        cmd_replay(args.log, args.start, args.end, args.entry)
    elif args.command == 'status':
        cmd_status()
    elif args.command == 'capture':
        cmd_capture(args.out, args.tree)
    elif args.command == 'dashboard':
        cmd_dashboard(args.log)
    elif args.command == 'forensic':
        cmd_forensic(args.log)
    elif args.command == 'monitor':
        cmd_consistency(args.log)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
