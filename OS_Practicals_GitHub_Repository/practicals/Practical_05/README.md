# Practical 05

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
ls -l




PRACTICAL-5
   5. Write a shell script to- i. to generate a multiplication table using loops (for, while, until) ii. to
       check whether a number is positive, negative or zero, using if-elif-else. iii. Develop a script to
       check whether a file exists, display its size and basic information.




1)CREATE FILE
nano practical.sh

#!/bin/bash

# i. Multiplication table using FOR loop

echo "Enter a number for FOR loop:"
read num

echo "Multiplication table using FOR loop:"
for ((i=1; i<=10; i++))

do
  echo "$num x $i = $((num*i))"
done

# Multiplication table using WHILE loop

echo " "
echo "Multiplication table using WHILE loop:"
i=1

while [ $i -le 10 ]
do
  echo "$num x $i = $((num*i))"
  i=$((i+1))
done

# Multiplication table using UNTIL loop

echo ""
echo "Multiplication table using UNTIL loop:"
i=1

until [ $i -gt 10 ]
do
  echo "$num x $i = $((num*i))"
  i=$((i+1))
done

# ii. Check positive, negative or zero using if-elif-else

echo ""
echo "Enter a number to check:"
read n

if [ $n -gt 0 ]
then
   echo "Number is Positive"
elif [ $n -lt 0 ]
then
   echo "Number is Negative"
else
   echo "Number is Zero"

fi

# iii. Check whether a file exists

echo ""
echo "Enter file name:"
read filename

if [ -e "$filename" ]
then
   echo "File exists"
   echo "File information:"
   ls -l "$filename"
   echo "File size:"
   du -h "$filename"
else
   echo "File does not exist"
fi
```
