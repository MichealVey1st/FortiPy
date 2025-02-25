import subprocess

def update_security_patches():
    try:

        # Determine the Debian code name
        result = subprocess.run(['lsb_release', '-c'], capture_output=True, text=True, check=True)
        code_name = result.stdout.split(':')[1].strip()
        print(f"Debian code name: {code_name}")

        # Check if a specific string is in a particular file
        file_path = '/etc/apt/sources.list'
        search_string = 'deb http://security.debian.com/'+code_name+'/updates main contrib non-free'
        
        with open(file_path, 'r') as file:
            if search_string in file.read():
                print("The security repository is already in the sources list.")
            else:
                print("The security repository is not in the sources list.")
                # Add the security repository to the sources list
                with open(file_path, 'a') as file:
                    file.write('\n')
                    file.write(search_string)
                print("The security repository has been added to the sources list")

        # Update the package list
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        
        # Upgrade the packages with security patches
        subprocess.run(['sudo', 'apt-get', 'upgrade', '-y'], check=True)
        
        # Clean up
        subprocess.run(['sudo', 'apt-get', 'autoremove', '-y'], check=True)
        subprocess.run(['sudo', 'apt-get', 'clean'], check=True)
        
        print("System updated with the latest security patches.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

update_security_patches()