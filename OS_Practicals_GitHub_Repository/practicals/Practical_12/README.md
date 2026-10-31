# Practical 12

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
// Remove message queue
        msgctl(qid, IPC_RMID, NULL);
    }

    printf("\nIPC Communication Completed Successfully!\n");

    return 0;
}

2. Compile and run the program
Step 1: Save your file

Press Ctrl + S in VS Code.

Step 2: Compile

gcc practical11.c -o practical11

Step 3: Run

./practical11




12. Implement Inter-Process Communication using shared
memory and message queues. Analyze communication
efficiency, resource sharing, and memory utilization.


Create a file named practical12.c:

nano practical12.c

Paste this complete code:


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/msg.h>

// Message Queue Structure
struct message {
    long type;
    char text[100];
};

int main()
{

pid_t pid;
int shmid;
char *shared_memory;

// IPC USING SHARED MEMORY
printf("\n--- IPC USING SHARED MEMORY ---\n");

// Create shared memory
shmid = shmget(IPC_PRIVATE, 1024, IPC_CREAT | 0666);

if (shmid == -1) {
    perror("Shared memory creation failed");
    return 1;
}

// Attach shared memory
shared_memory = (char *)shmat(shmid, NULL, 0);

if (shared_memory == (char *)-1) {
    perror("Shared memory attachment failed");
    shmctl(shmid, IPC_RMID, NULL);
    return 1;
}

// Parent writes message
strcpy(shared_memory, "Hello from Shared Memory!");

pid = fork();

if (pid < 0) {
    perror("Fork failed");
    shmdt(shared_memory);
    shmctl(shmid, IPC_RMID, NULL);
    return 1;
}

if (pid == 0) {
    // Child reads shared memory
    printf("Child received: %s\n", shared_memory);

    shmdt(shared_memory);
    exit(0);
}
else {
    wait(NULL);

    printf("Parent shared data successfully.\n");

    // Detach and remove shared memory
    shmdt(shared_memory);
    shmctl(shmid, IPC_RMID, NULL);
}

// IPC USING MESSAGE QUEUE
printf("\n--- IPC USING MESSAGE QUEUE ---\n");

int qid;

    struct message m;

    // Create message queue
    qid = msgget(IPC_PRIVATE, IPC_CREAT | 0666);

    if (qid == -1) {
        perror("Message queue creation failed");
        return 1;
    }

    pid = fork();

    if (pid < 0) {
        perror("Fork failed");
        msgctl(qid, IPC_RMID, NULL);
        return 1;
    }

    if (pid == 0) {
        // Child receives message
        if (msgrcv(qid, &m, sizeof(m.text), 1, 0) == -1) {
            perror("Message receive failed");
            exit(1);
        }

        printf("Child received: %s\n", m.text);
        exit(0);
    }
    else {
        // Parent sends message
        m.type = 1;
        strcpy(m.text, "Hello from Message Queue!");

        if (msgsnd(qid, &m, sizeof(m.text), 0) == -1) {
            perror("Message send failed");
            wait(NULL);
            msgctl(qid, IPC_RMID, NULL);
            return 1;
        }

        wait(NULL);
```
