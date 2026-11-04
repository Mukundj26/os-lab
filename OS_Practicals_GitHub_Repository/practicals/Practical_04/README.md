# Practical 04

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
PRACTICAL -4
   4. Create a directory named Student_Records. Perform the following operations: i. Create separate
       directories for FY, SY, TE and BE students. ii. Create text files containing student names and roll
       numbers. iii. Copy selected files into another directory. iv. Rename and delete specified files. v.
       Display the complete directory structure.

# Create project directory
mkdir -p AIML_Project
cd AIML_Project

# i. Create files for students, faculty and administrators
touch students.txt faculty.txt administrators.txt

# Write content into files
echo "Student Name: Mukund, Roll No: 101" > students.txt
echo "Faculty Name: Professor Renuka" > faculty.txt
echo "Administrator: System Admin" > administrators.txt

# ii. Assign different permissions to files
chmod 644 students.txt
chmod 640 faculty.txt
chmod 600 administrators.txt

# iii. Display file ownership and permission details

ls -l

# Display current user and group
whoami
id

# iv. Change permissions using symbolic notation
chmod u+x students.txt
chmod g+w faculty.txt
chmod o-r faculty.txt

# Display updated permissions
ls -l

# Change permissions using numeric notation
chmod 755 students.txt
chmod 644 faculty.txt
chmod 600 administrators.txt

# Display final permissions
ls -l



# v. Demonstrate read permission
echo "Reading student file:"
cat students.txt

# Demonstrate write permission
echo "New Student: Rahul, Roll No: 102" >> students.txt
echo "Updated student file:"
cat students.txt

# Demonstrate execute permission
echo '#!/bin/bash' > script.sh
echo 'echo "AIML Project Script Executed Successfully!"' >> script.sh

# Assign execute permission
chmod 755 script.sh

# Execute the script
./script.sh

# Demonstrate removal of read permission
chmod 000 students.txt

# Try reading the file (expected: Permission denied)
cat students.txt

# Restore normal permissions
chmod 644 students.txt

# Display final ownership and permission details
```
