# Practical 02

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
practical 2
    2. Manage file permissions and ownership, monitor running processes, and inspect system
        resource usage in Linux. Tasks: i. Create files with different permissions and display their
        permission details. ii. Modify read, write, and execute permissions using symbolic and numeric
        modes. iii. Identify the current user and group, and demonstrate ownership changes where
        administrator privileges are available. iv. Display running processes and identify their process
        IDs. v. Monitor CPU and memory usage and display disk-space information.

# i. Create files with different permissions and display permission details

mkdir -p OS_Permissions
cd OS_Permissions

touch file1.txt file2.txt file3.txt

# Set different permissions
chmod 644 file1.txt
chmod 600 file2.txt
chmod 755 file3.txt

# Display permission details
ls -l

# ii. Modify read, write and execute permissions

# Symbolic mode
chmod u+x file1.txt
chmod g+w file1.txt
chmod o-r file1.txt

# Numeric mode
chmod 755 file2.txt
chmod 644 file3.txt

# Display updated permissions
ls -l

# iii. Identify current user and group

whoami
id
groups

# Demonstrate ownership information
ls -l file1.txt

# Change ownership (administrator privileges required)
# Replace mukund with your Ubuntu username if different
sudo chown mukund file1.txt

# Change group ownership
sudo chgrp mukund file1.txt

# Display updated ownership
ls -l file1.txt

# iv. Display running processes and identify their PIDs

ps
ps -ef
ps -u "$USER"

# Display process IDs
pgrep -a bash

# v. Monitor CPU and memory usage

# Display CPU and memory information
top -b -n 1 | head -15

# Display memory usage
free -h

# Display disk-space information
df -h

# Display directory size
du -sh .

# Display final file permissions
ls -l
```
