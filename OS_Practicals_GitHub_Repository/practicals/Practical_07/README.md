# Practical 07

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
echo ""
echo "Enter a number to display:"
read value

display_number "$value"




PRACTICAL – 7
7. Develop programs to create and manage processes using system calls. Implement CPU scheduling
algorithms (FCFS, SJF) and analyze their impact on process execution, memory utilization, and overall
system performance.


1)Create a file named:

nano practical.c



#include <stdio.h>
#include <stdlib.h>

#include <unistd.h>
#include <sys/wait.h>

struct Process {
    int pid, bt, wt, tat;
};

int main() {
    int n, i, j;
    struct Process p[20], temp;
    float avgWT = 0, avgTAT = 0;

    // Process creation using fork()
    printf("PROCESS MANAGEMENT\n");

    pid_t pid = fork();

    if (pid < 0) {
        printf("Process creation failed\n");
        return 1;
    }
    else if (pid == 0) {
        printf("\nChild Process\n");
        printf("Child PID: %d\n", getpid());
        printf("Parent PID: %d\n", getppid());
        exit(0);
    }
    else {
        wait(NULL);
        printf("\nParent Process\n");
        printf("Parent PID: %d\n", getpid());
        printf("Child PID: %d\n", pid);
    }

    // Input processes
    printf("\nCPU SCHEDULING\n");
    printf("Enter number of processes: ");
    scanf("%d", &n);

    if (n < 1 || n > 20) {
        printf("Enter processes between 1 and 20\n");
        return 1;
    }

    for (i = 0; i < n; i++) {
        p[i].pid = i + 1;
        printf("Enter Burst Time for P%d: ", i + 1);
        scanf("%d", &p[i].bt);
        if (p[i].bt <= 0) {
            printf("Burst time must be positive\n");
            return 1;
        }
    }

    // FCFS Scheduling
    printf("\nFCFS SCHEDULING\n");

p[0].wt = 0;

for (i = 1; i < n; i++) {
    p[i].wt = p[i-1].wt + p[i-1].bt;
}

avgWT = 0;
avgTAT = 0;

printf("\nPID\tBT\tWT\tTAT\n");

for (i = 0; i < n; i++) {
    p[i].tat = p[i].wt + p[i].bt;
    avgWT += p[i].wt;
    avgTAT += p[i].tat;

    printf("P%d\t%d\t%d\t%d\n",
           p[i].pid, p[i].bt, p[i].wt, p[i].tat);
}

printf("Average Waiting Time = %.2f\n", avgWT/n);
printf("Average Turnaround Time = %.2f\n", avgTAT/n);

// SJF Scheduling (Non-preemptive)
printf("\nSJF SCHEDULING\n");

// Sort processes by burst time
for (i = 0; i < n-1; i++) {
    for (j = i+1; j < n; j++) {
        if (p[i].bt > p[j].bt) {
            temp = p[i];
            p[i] = p[j];
            p[j] = temp;
        }
    }
}

p[0].wt = 0;

for (i = 1; i < n; i++) {
    p[i].wt = p[i-1].wt + p[i-1].bt;
}

avgWT = 0;
avgTAT = 0;

printf("\nPID\tBT\tWT\tTAT\n");

for (i = 0; i < n; i++) {
    p[i].tat = p[i].wt + p[i].bt;
    avgWT += p[i].wt;
    avgTAT += p[i].tat;

    printf("P%d\t%d\t%d\t%d\n",
           p[i].pid, p[i].bt, p[i].wt, p[i].tat);
}

     printf("Average Waiting Time = %.2f\n", avgWT/n);
     printf("Average Turnaround Time = %.2f\n", avgTAT/n);

     return 0;
}




Step 1: Compile
```
