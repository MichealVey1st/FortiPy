import subprocess
import json
import os
import curses

# Path to store stopped services
BACKUP_FILE = "/var/log/fortipy_stopped_services.json"

# Define critical services for each server type
CRITICAL_SERVICES = {
    "Web Server": ["apache2", "nginx", "caddy"],
    "Database Server": ["mysql", "postgresql", "mongod"],
    "File Server": ["smbd", "nmbd", "nfs-server"],
    "DNS Server": ["bind9", "named"],
    "Mail Server": ["postfix", "dovecot"],
    "NTP Server": ["chronyd", "ntpd"],
    "Logging Server": ["rsyslog", "systemd-journald"],
    "Security Services": ["fail2ban", "ufw"]
}

# Always-enabled critical services
ALWAYS_ENABLED_SERVICES = ["ufw", "fail2ban", "rsyslog", "systemd-journald"]

def get_running_services():
    # Get currently running services using systemctl 
    result = subprocess.run(['systemctl', 'list-units', '--type=service', '--state=running', '--no-pager', '--no-legend'],
                            stdout=subprocess.PIPE, text=True)
    services = [line.split()[0] for line in result.stdout.splitlines()]
    return services

def prompt_user_roles(stdscr):
    # Initialize curses selection UI
    curses.curs_set(0)
    stdscr.clear()
    
    options = list(CRITICAL_SERVICES.keys())
    selected = [False] * len(options)
    
    index = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select the server roles (SPACE to toggle, ENTER to confirm):", curses.A_BOLD)

        for i, option in enumerate(options):
            if selected[i]:
                stdscr.addstr(i + 2, 0, f"[X] {option}")
            else:
                stdscr.addstr(i + 2, 0, f"[ ] {option}")

        key = stdscr.getch()
        
        if key == curses.KEY_UP and index > 0:
            index -= 1
        elif key == curses.KEY_DOWN and index < len(options) - 1:
            index += 1
        elif key == ord(' '):  # Toggle selection
            selected[index] = not selected[index]
        elif key == 10:  # Enter key to confirm
            break

    return [options[i] for i, selected in enumerate(selected) if selected]

def stop_unnecessary_services(selected_roles):
    # Get currently running services
    running_services = get_running_services()
    
    # Gather allowed services from selected roles
    allowed_services = {svc for role in selected_roles for svc in CRITICAL_SERVICES.get(role, [])}
    
    # Add always-enabled services to the allowed list
    allowed_services.update(ALWAYS_ENABLED_SERVICES)
    
    # Find services that need to be stopped
    services_to_stop = [svc for svc in running_services if svc not in allowed_services]
    
    if not services_to_stop:
        print("No unnecessary services found.")
        return

    # Backup before stopping
    with open(BACKUP_FILE, "w") as f:
        json.dump(services_to_stop, f)

    # Stop services
    for service in services_to_stop:
        print(f"Stopping {service}...")
        subprocess.run(["sudo", "systemctl", "stop", service])

    print(f"Stopped {len(services_to_stop)} services. Backup saved at {BACKUP_FILE}.")

def revert_services():
    # Revert stopped services
    if not os.path.exists(BACKUP_FILE):
        print("No backup found. Nothing to revert.")
        return
    
    with open(BACKUP_FILE, "r") as f:
        services_to_start = json.load(f)

    for service in services_to_start:
        print(f"Restarting {service}...")
        subprocess.run(["sudo", "systemctl", "start", service])

    os.remove(BACKUP_FILE)
    print("Services reverted successfully.")

def main():
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description="FortiPy Services Audit Module")
    parser.add_argument("--revert", action="store_true", help="Revert stopped services")
    args = parser.parse_args()

    if args.revert:
        revert_services()
        return

    # Run the curses UI for selection
    selected_roles = curses.wrapper(prompt_user_roles)

    if not selected_roles:
        print("No roles selected. Exiting...")
        return

    print(f"Selected roles: {', '.join(selected_roles)}")
    stop_unnecessary_services(selected_roles)

main()
