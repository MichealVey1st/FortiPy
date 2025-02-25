import subprocess

def get_users_never_logged_in():
    # Get users who have never logged in
    output = subprocess.getoutput("lastlog | grep 'Never logged in' | awk '{print $1}'")
    return output.splitlines()

def get_users_without_home():
    # Get users without a home directory
    output = subprocess.getoutput("awk -F: '($3 >= 1000 && $6 == \"/\") {print $1}' /etc/passwd")
    return output.splitlines()

def get_users_without_password():
    # Get users without a password
    output = subprocess.getoutput("awk -F: '($2 == \"\" ) {print $1}' /etc/shadow")
    return output.splitlines()

def remove_users(users):
    for user in users:
        print(f"Removing user: {user}")
        try:
            subprocess.run(["sudo", "deluser", "--remove-home", user])
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")

unnecessary_users = set(get_users_never_logged_in() + get_users_without_home() + get_users_without_password())

if unnecessary_users:
    print("Users to be removed:", unnecessary_users)
    confirm = input("Proceed with removal? (yes/no): ")
    # Ask for confirmation before removing users
    if confirm.lower() == "yes" or "y":
        # Remove unnecessary users
        remove_users(unnecessary_users)
    elif confirm.lower() == "no" or "n":
        # do nothing
        print("Operation canceled.")
    else:
        # do nothing
        print("Invalid input. Operation canceled.")
else:
    # no users found so do nothing
    print("No unnecessary users found.")
