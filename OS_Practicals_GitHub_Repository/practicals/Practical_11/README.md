# Practical 11

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
printf("\nIPC Demonstration Completed Successfully!\n");

     return 0;
}

2. Compile and run the program

Step 1: Save the file

- Press Ctrl + S in VS Code.

Step 2: Compile

gcc practical10.c -o practical10

Step 3: Execute

./practical10




Practical 11
11. Implement Inter-Process Communication using pipes and message
queues. Analyze communication efficiency, resource sharing, and memory
utilization.




Create a file named practical11.c:

nano practical11.c

Paste this complete code:

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/ipc.h>
#include <sys/msg.h>

struct message {
    long type;
    char text[100];
};

int main()
{
    int fd[2];
    pid_t pid;
    char msg[] = "Hello from Parent using Pipe!";
    char buffer[100];

    // IPC USING PIPE
    printf("\n--- IPC USING PIPE ---\n");

    if (pipe(fd) == -1) {
        perror("Pipe creation failed");
        return 1;
    }

    pid = fork();

    if (pid < 0) {
        perror("Fork failed");
        return 1;
    }

    if (pid == 0) {
        // Child reads message
        close(fd[1]);

        if (read(fd[0], buffer, sizeof(buffer)) > 0) {
            printf("Child received: %s\n", buffer);
        }

        close(fd[0]);
        exit(0);
    }
    else {
        // Parent writes message
        close(fd[0]);

        write(fd[1], msg, strlen(msg) + 1);
        close(fd[1]);

        wait(NULL);
        printf("Parent sent message using Pipe.\n");
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
        strcpy(m.text, "Hello from Parent using Message Queue!");

        if (msgsnd(qid, &m, sizeof(m.text), 0) == -1) {
            perror("Message send failed");
            wait(NULL);
            msgctl(qid, IPC_RMID, NULL);
            return 1;
        }

        wait(NULL);
        printf("Parent sent message using Message Queue.\n");
```
