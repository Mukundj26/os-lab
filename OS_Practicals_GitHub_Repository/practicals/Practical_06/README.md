# Practical 06

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
Step 2: Give execute permission
chmod +x practical.sh

Step 3: Run the script
./practical.sh


PRACTICAL -6
   6. Write a shell script to- i. to generate calculate the factorial of a
      number using loops (for, while, until). ii. to check whether a number
      is even or odd. using if –else. iii. display a number entered by user
      using function




#!/bin/bash

# i. Calculate factorial using FOR loop

echo "Enter a number for factorial:"
read num

fact=1

for ((i=1; i<=num; i++))

do
  fact=$((fact*i))
done

echo "Factorial using FOR loop = $fact"


# Calculate factorial using WHILE loop

fact=1
i=1

while [ $i -le $num ]
do
  fact=$((fact*i))
  i=$((i+1))
done

echo "Factorial using WHILE loop = $fact"


# Calculate factorial using UNTIL loop

fact=1
i=1

until [ $i -gt $num ]
do
  fact=$((fact*i))
  i=$((i+1))
done

echo "Factorial using UNTIL loop = $fact"


# ii. Check whether number is even or odd

echo ""
echo "Enter a number to check even or odd:"
read n

if [ $((n%2)) -eq 0 ]
then
   echo "$n is Even"
else
   echo "$n is Odd"
fi

# iii. Display number using function

display_number()
{
  echo "The entered number is: $1"
}
```
