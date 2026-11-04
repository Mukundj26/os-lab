# Practical 03

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
Practical 3
    3. Create a directory named Student_Records. Perform the following operations: i. Create separate
        directories for FY, SY, TE and BE students. ii. Create text files containing student names and roll
        numbers. iii. Copy selected files into another directory. iv. Rename and delete specified files. v.
        Display the complete directory structure.



# Step 1: Create main directory
mkdir -p Student_Records
cd Student_Records

# Step 2: Create separate directories
mkdir -p FY SY TE BE

# Step 3: Create student text files
echo -e "Name: Rahul\nRoll No: 101\nName: Amit\nRoll No: 102" > FY/FY_Students.txt

echo -e "Name: Soham\nRoll No: 201\nName: Mukund\nRoll No: 202" > SY/SY_Students.txt

echo -e "Name: Guru\nRoll No: 301\nName: Akash\nRoll No: 302" > TE/TE_Students.txt

echo -e "Name: Priya\nRoll No: 401\nName: Sneha\nRoll No: 402" > BE/BE_Students.txt

# Step 4: Create directory and copy selected files
mkdir -p Selected_Students

cp FY/FY_Students.txt Selected_Students/
cp TE/TE_Students.txt Selected_Students/

# Step 5: Rename FY file
mv FY/FY_Students.txt FY/FY_Records.txt

# Step 6: Delete BE student file
rm BE/BE_Students.txt

# Step 7: Install tree command
sudo apt install tree -y

# Step 8: Display complete directory structure
cd ..
tree Student_Records
```
