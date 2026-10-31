# Practical 10

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
avgWT += wt[i];
           avgTAT += tat[i];

           printf("P%d\t%d\t%d\t%d\n",
                  i + 1, bt[i], wt[i], tat[i]);
       }

       printf("Average Waiting Time = %.2f\n", avgWT / n);
       printf("Average Turnaround Time = %.2f\n", avgTAT / n);

       return 0;
}

2. Compile and run

Compile the program: gcc practical9.c -o practical9

Run:

./practical9

Practical 10:
Practical 10
10. Implement Inter-Process Communication using pipes and shared
memory. Analyze communication efficiency, resource sharing, and memory
utilization.


Create a file named practical10.c:

nano practical10.c

Paste the following code:


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/ipc.h>
#include <sys/shm.h>

int main()
{
    int fd[2];
    pid_t pid;
    char message[] = "Hello from Parent Process!";
    char buffer[100];

    // IPC USING PIPE
    printf("\n--- IPC USING PIPE ---\n");

    if (pipe(fd) == -1)
    {
        perror("Pipe failed");
        return 1;
    }

    pid = fork();

    if (pid < 0)
    {
        perror("Fork failed");
        return 1;
    }

    if (pid == 0)
    {
        // Child process reads data
        close(fd[1]);

         read(fd[0], buffer, sizeof(buffer));
         printf("Child received through pipe: %s\n", buffer);

         close(fd[0]);

       exit(0);
}
else
{
       // Parent process writes data
       close(fd[0]);

       write(fd[1], message, strlen(message) + 1);
       close(fd[1]);

       wait(NULL);
       printf("Parent sent message through pipe.\n");
}

// IPC USING SHARED MEMORY
printf("\n--- IPC USING SHARED MEMORY ---\n");

int shmid;
char *shared_memory;

// Create shared memory
shmid = shmget(IPC_PRIVATE, 1024, IPC_CREAT | 0666);

if (shmid < 0)
{
    perror("Shared memory creation failed");
    return 1;
}

// Attach shared memory
shared_memory = (char *)shmat(shmid, NULL, 0);

if (shared_memory == (char *)-1)
{
    perror("Shared memory attachment failed");
    shmctl(shmid, IPC_RMID, NULL);
    return 1;
}

// Parent writes data into shared memory
strcpy(shared_memory, "Hello from Shared Memory!");

pid = fork();

if (pid < 0)
{
    perror("Fork failed");
    shmdt(shared_memory);
    shmctl(shmid, IPC_RMID, NULL);
    return 1;
}

if (pid == 0)
{
    // Child reads shared memory
    printf("Child received through shared memory: %s\n",
           shared_memory);

            shmdt(shared_memory);
            exit(0);
     }
     else
     {
            wait(NULL);

            printf("Parent shared data successfully.\n");

            // Detach and remove shared memory
            shmdt(shared_memory);
            shmctl(shmid, IPC_RMID, NULL);
     }
```
