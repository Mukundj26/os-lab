# Practical 01

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
Practical 1

     1. Perform basic file and directory operations using Linux command-line utilities. Tasks: i. Display
        the current working directory and list files, including hidden files. ii. Create a directory named
        OS_Lab and three subdirectories inside it. iii. Create text files, write content into them, and
        display their contents. iv. Copy, rename, move, and delete files using appropriate commands. v.
        Search for a specified file and display its size and other file information.

# i. Display current working directory and list all files including hidden files

pwd
ls -la

# ii. Create OS_Lab directory and three subdirectories

mkdir -p OS_Lab
cd OS_Lab
mkdir -p FY SY TE

# iii. Create text files and write content into them

echo "Operating System Lab - FY Students" > FY/fy.txt
echo "Operating System Lab - SY Students" > SY/sy.txt
echo "Operating System Lab - TE Students" > TE/te.txt

# Display file contents

cat FY/fy.txt
cat SY/sy.txt
cat TE/te.txt

# iv. Copy, rename, move and delete files

# Copy file
cp FY/fy.txt SY/

# Rename file
mv SY/fy.txt SY/fy_records.txt

# Move file
mv TE/te.txt OS_Lab_te.txt

# Delete file
rm SY/fy_records.txt

# v. Search for a specified file

find . -name "sy.txt"

# Display file size and other information

stat SY/sy.txt



# Display final directory structure

ls -R
```
