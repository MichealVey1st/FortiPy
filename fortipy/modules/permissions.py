import os
import subprocess
import subprocess
import json

# Paths to audit
SUID_PATH = "/"

# Define SUID severity levels (just examples, can be expanded)
SUID_SEVERITY = {
    "critical": [
        "/bin/passwd", "/bin/su", "/bin/chsh", "/bin/ping", "/sbin/mount", "/sbin/umount"
    ],
    "moderate": [
        "/usr/bin/chage", "/usr/bin/crontab", "/usr/bin/newgrp"
    ],
    "minimal": [
        "/usr/local/bin/some_unsafe_script"  # Example of a user-installed or less critical binary
    ]
}

# File to back up removed binaries
RESTORE_FILE = "removed_suids.json"


CAPABILITY_PATH = "/"
USER_PERMISSIONS_PATH = "/etc/sudoers"


def get_suid_files():
    """Find all files with the SUID bit set."""
    print("Finding SUID files...")
    result = subprocess.run(['find', SUID_PATH, '-type', 'f', '-perm', '-4000'], stdout=subprocess.PIPE, text=True)
    suid_files = result.stdout.splitlines()
    return suid_files

def display_and_select_severity():
    """Display severity options and allow the user to select."""
    print("\nSelect SUID severity level to audit:")
    print("1. Critical (e.g., /bin/passwd, /bin/su)")
    print("2. Moderate (e.g., /usr/bin/chage, /usr/bin/crontab)")
    print("3. Minimal (e.g., /usr/local/bin/some_unsafe_script)")
    print("4. All (All files with SUID)")

    selection = input("\nEnter the number for your selection (1-4): ").strip()
    return selection

def audit_suids():
    """Audit SUID files based on severity level."""
    suid_files = get_suid_files()

    # Categorize found files into severity levels
    critical_files = [file for file in suid_files if file in SUID_SEVERITY["critical"]]
    moderate_files = [file for file in suid_files if file in SUID_SEVERITY["moderate"]]
    minimal_files = [file for file in suid_files if file in SUID_SEVERITY["minimal"]]

    # Get user input for the severity level to act on
    selection = display_and_select_severity()

    files_to_remove = []
    if selection == "1":
        files_to_remove = critical_files
    elif selection == "2":
        files_to_remove = moderate_files
    elif selection == "3":
        files_to_remove = minimal_files
    elif selection == "4":
        files_to_remove = suid_files
    else:
        print("Invalid selection, auditing all files.")
        files_to_remove = suid_files

    # Backup and remove the selected SUID files
    remove_suids(files_to_remove)

def remove_suids(files_to_remove):
    """Remove the selected SUID files and back them up."""
    print(f"\nRemoving {len(files_to_remove)} SUID files...")

    # Backup the files to the restore file
    backup_suids(files_to_remove)

    # Remove the SUID bit from the selected files
    for file in files_to_remove:
        print(f"Removing SUID from {file}...")
        subprocess.run(['sudo', 'chmod', '-s', file])

    print(f"\nSUID bit removed from {len(files_to_remove)} files.")

def backup_suids(files_to_remove):
    """Backup removed SUID files to the restore file."""
    try:
        with open(RESTORE_FILE, "r") as f:
            restore_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        restore_data = []

    # Add files to backup
    restore_data.extend(files_to_remove)

    # Save the backup to the restore file
    with open(RESTORE_FILE, "w") as f:
        json.dump(restore_data, f, indent=4)

    print(f"\nBackup completed. Removed SUID files saved to {RESTORE_FILE}.")

if __name__ == "__main__":
    audit_suids()








def audit_capabilities():
    # audit capabilities files
    print("Auditing capabilities...")
    result = subprocess.run(['getcap', '-r', CAPABILITY_PATH], stdout=subprocess.PIPE, text=True)
    capabilities = result.stdout.splitlines()
    
    if not capabilities:
        print("No capabilities set on any files.")
    else:
        print(f"Found {len(capabilities)} files with capabilities:")
        for file in capabilities:
            print(f" - {file}")

    # Suggest minimizing unnecessary capabilities
    print("\nConsider removing capabilities from files that do not require them.")

def audit_user_permissions():
    # audit user permissions
    print("Auditing user permissions...")
    
    # Check for sudoers file and group memberships
    with open(USER_PERMISSIONS_PATH, 'r') as f:
        sudoers_content = f.readlines()

    sudo_users = [line for line in sudoers_content if line.strip().startswith('User_Alias') or line.strip().startswith('root')]
    print("Sudo users (root access):")
    for user in sudo_users:
        print(f" - {user.strip()}")
    
    # Check for users in sudo or wheel group (or other admin group)
    result = subprocess.run(['getent', 'group', 'sudo', 'wheel'], stdout=subprocess.PIPE, text=True)
    admin_groups = result.stdout.splitlines()
    print("\nUsers in sudo/wheel groups:")
    for group in admin_groups:
        print(f" - {group.strip()}")

    # Suggest minimizing root access where unnecessary
    print("\nConsider removing unnecessary sudo/root access.")

def permissions_audit():
    # run all audit subfunctions
    audit_suids()
    audit_capabilities()
    audit_user_permissions()

permissions_audit()
