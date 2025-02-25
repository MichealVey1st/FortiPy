import argparse
from fortipy import config, patcher, audit

def main():
    parser = argparse.ArgumentParser(description="FortiPy - Debian Hardening CLI Tool")
    parser.add_argument("--apply-config", action="store_true", help="Apply security configurations")
    parser.add_argument("--patch", action="store_true", help="Apply security patches")
    parser.add_argument("--audit", action="store_true", help="Check system security status")

    args = parser.parse_args()

    if args.apply_config:
        config.apply()
    if args.patch:
        patcher.apply()
    if args.audit:
        audit.check()

if __name__ == "__main__":
    main()
