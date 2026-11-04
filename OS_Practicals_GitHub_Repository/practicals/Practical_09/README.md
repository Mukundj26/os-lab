# Practical 09

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
printf("Average Turnaround Time = %.2f\n", avgTAT / n);

    return 0;
}




Compile:

gcc practical8.c -o practical8

Run:

./practical8

PRACTICAL-9

9. Develop programs to create and manage processes using system calls.
Implement CPU scheduling algorithms (FCFS, Round Robin) and analyze their
impact on process execution, memory utilization, and overall system
performance.

Create a file named practical9.c in VS Code.

nano practical9.c

Paste this code:

#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdlib.h>

int main()
{
    int n, i, tq, time = 0;
    int bt[20], wt[20], tat[20], rem[20];
    float avgWT, avgTAT;

     // Process Management using fork()
     printf("PROCESS MANAGEMENT\n");

     pid_t pid = fork();

     if (pid < 0)
     {
          printf("Process creation failed\n");
          return 1;
     }
     else if (pid == 0)
     {
          printf("\nChild Process\n");
          printf("Child PID: %d\n", getpid());
          printf("Parent PID: %d\n", getppid());
          exit(0);
     }
     else
     {
          wait(NULL);
          printf("\nParent Process\n");
          printf("Parent PID: %d\n", getpid());
          printf("Child PID: %d\n", pid);
     }

     // Input number of processes
     printf("\nEnter number of processes: ");
     scanf("%d", &n);

     if (n < 1 || n > 20)
     {

    printf("Invalid number of processes\n");
    return 1;
}

for (i = 0; i < n; i++)
{
    printf("Enter burst time for P%d: ", i + 1);
    scanf("%d", &bt[i]);

    if (bt[i] <= 0)
    {
        printf("Burst time must be positive\n");
        return 1;
    }

    rem[i] = bt[i];
}

// FCFS Scheduling
printf("\nFCFS SCHEDULING\n");

wt[0] = 0;

for (i = 1; i < n; i++)
{
    wt[i] = wt[i - 1] + bt[i - 1];
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
           i + 1, bt[i], wt[i], tat[i]);
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

       time = 0;
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
```
