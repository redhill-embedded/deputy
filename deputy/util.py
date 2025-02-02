import os
import re

# Function to search for udev rules with given VID:PID
def find_udev_rule(vid, pid):
    # Directories where udev rules are typically stored
    udev_dirs = ['/etc/udev/rules.d/', '/lib/udev/rules.d/']

    # Regular expression to match the VID:PID
    vid_pid_pattern = re.compile(rf'\b(idVendor|ATTR{{idVendor}})=="{vid}"\s*(idProduct|ATTR{{idProduct}})=="{pid}"')

    # Search for the rule in the udev rule directories
    for udev_dir in udev_dirs:
        if not os.path.isdir(udev_dir):
            continue

        for rule_file in os.listdir(udev_dir):
            rule_file_path = os.path.join(udev_dir, rule_file)
            
            # Only check .rules files
            if rule_file.endswith('.rules'):
                try:
                    with open(rule_file_path, 'r') as f:
                        content = f.read()
                        # Check if the VID:PID exists in the file
                        if re.search(vid_pid_pattern, content):
                            print(f'Found rule in: {rule_file_path}')
                            return True
                except Exception as e:
                    #print(f"Error reading {rule_file_path}: {e}")
                    pass
    
    print('No matching udev rule found.')
    return False
