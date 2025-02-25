import argparse
import subprocess

def run_command(cmd):
    """Runs a shell command and handles errors."""
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def clear_firewall():
    """Flush all iptables rules and set default deny policy."""
    print("[+] Flushing all iptables rules...")
    run_command("iptables -F")  # Flush rules
    run_command("iptables -X")  # Delete custom chains
    run_command("iptables -Z")  # Zero counters
    run_command("iptables -P INPUT DROP")  # Default deny
    run_command("iptables -P FORWARD DROP")
    run_command("iptables -P OUTPUT DROP")
    print("[+] Firewall cleared. Default deny all traffic.")

def apply_exceptions(allow_rules):
    # Get the allow rules and apply them to the firewall in contrast to the total deny policy
    for rule in allow_rules:
        direction, ports = rule.split(":")
        ports = [int(port) for port in ports.split(",")]

        for port in ports:
            if direction.lower() == "in":
                print(f"[+] Allowing incoming traffic on port {port}")
                run_command(f"iptables -A INPUT -p tcp --dport {port} -j ACCEPT")

            elif direction.lower() == "out":
                print(f"[+] Allowing outgoing traffic on port {port}")
                run_command(f"iptables -A OUTPUT -p tcp --sport {port} -j ACCEPT")

def save_firewall():
    # Save the firewall rules for persistence
    print("[+] Saving firewall rules...")
    run_command("iptables-save > /etc/iptables/rules.v4")

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="FortiPy Firewall - Flush and Apply Rules")
    parser.add_argument("--allow", nargs="+", help='Allow traffic with format "in:443 out:80"')

    args = parser.parse_args()

    # Clear the firewall rules
    clear_firewall()

    if args.allow:
        apply_exceptions(args.allow)

    save_firewall()

    print("[+] Firewall rules applied successfully.")

main()