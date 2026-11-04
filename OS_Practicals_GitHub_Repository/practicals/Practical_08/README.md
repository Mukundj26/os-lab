# Practical 08

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
gcc practical.c -o practical


Step 2: Run

./practical




PRACTICAL -8


    7. Develop programs to create and manage processes using system calls. Implement CPU
       scheduling algorithms (SJF, Round Robin) and analyze their impact on process execution,
       memory utilization, and overall system performance.


#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

#include <stdlib.h>

int main()
{
  int n, i, j, tq;
  int bt[20], wt[20], tat[20];
  int rem[20], p[20], temp;
  float avgWT, avgTAT;

  // Process creation using fork()
  printf("PROCESS MANAGEMENT\n");

  pid_t pid = fork();

  if (pid == 0)
  {
      printf("\nChild Process\n");
      printf("Child PID: %d\n", getpid());
      printf("Parent PID: %d\n", getppid());
     exit(0);
  }
  else if (pid > 0)
  {
     wait(NULL);
      printf("\nParent Process\n");
      printf("Parent PID: %d\n", getpid());
      printf("Child PID: %d\n", pid);
  }
  else
  {
      printf("Fork failed\n");
      return 1;
  }

  // Input processes
  printf("\nEnter number of processes: ");
  scanf("%d", &n);

  if (n < 1 || n > 20)
  {
      printf("Invalid number of processes\n");
      return 1;
  }

  for (i = 0; i < n; i++)
  {
    p[i] = i + 1;
    printf("Enter burst time for P%d: ", i + 1);

    scanf("%d", &bt[i]);

    if (bt[i] <= 0)
    {
        printf("Burst time must be positive\n");
        return 1;
    }
}

// SJF Scheduling
printf("\nSJF SCHEDULING\n");

int sjfBT[20], sjfP[20];

for (i = 0; i < n; i++)
{
  sjfBT[i] = bt[i];
  sjfP[i] = p[i];
}

// Sort according to burst time
for (i = 0; i < n - 1; i++)
{
   for (j = i + 1; j < n; j++)
   {
     if (sjfBT[i] > sjfBT[j])
     {
        temp = sjfBT[i];
        sjfBT[i] = sjfBT[j];
        sjfBT[j] = temp;

            temp = sjfP[i];
            sjfP[i] = sjfP[j];
            sjfP[j] = temp;
        }
    }
}

wt[0] = 0;

for (i = 1; i < n; i++)
  wt[i] = wt[i - 1] + sjfBT[i - 1];

avgWT = 0;
avgTAT = 0;

printf("\nPID\tBT\tWT\tTAT\n");

for (i = 0; i < n; i++)
{
  tat[i] = wt[i] + sjfBT[i];
  avgWT += wt[i];
  avgTAT += tat[i];

    printf("P%d\t%d\t%d\t%d\n",
        sjfP[i], sjfBT[i], wt[i], tat[i]);
}

printf("Average Waiting Time = %.2f\n", avgWT / n);
printf("Average Turnaround Time = %.2f\n", avgTAT / n);

// Round Robin Scheduling
printf("\nROUND ROBIN SCHEDULING\n");

printf("Enter Time Quantum: ");
scanf("%d", &tq);

if (tq <= 0)
{
    printf("Time quantum must be positive\n");
    return 1;
}

for (i = 0; i < n; i++)
  rem[i] = bt[i];

int time = 0;
int completed = 0;

while (completed < n)
{
  for (i = 0; i < n; i++)
  {
    if (rem[i] > 0)
    {
        if (rem[i] > tq)
       {
           time += tq;
           rem[i] -= tq;
       }
       else
       {
           time += rem[i];
           wt[i] = time - bt[i];
           rem[i] = 0;
           completed++;

                }
            }
        }
    }

    avgWT = 0;
    avgTAT = 0;

    printf("\nPID\tBT\tWT\tTAT\n");

    for (i = 0; i < n; i++)
    {
      tat[i] = wt[i] + bt[i];
      avgWT += wt[i];
      avgTAT += tat[i];

        printf("P%d\t%d\t%d\t%d\n",
            p[i], bt[i], wt[i], tat[i]);
    }

    printf("Average Waiting Time = %.2f\n", avgWT / n);
```
