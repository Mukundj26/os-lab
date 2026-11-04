# Practical 16

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
// Wait for writer threads
    for (int i = 0; i < 2; i++)
    {
        pthread_join(writers[i], NULL);
    }

    printf("\nFinal Shared Data: %d\n", shared_data);
    printf("Readers-Writers completed successfully!\n");

    // Destroy synchronization variables
    sem_destroy(&write_lock);
    pthread_mutex_destroy(&mutex);

    return 0;
}


2. How to run in VS Code (Ubuntu WSL)

Execute these commands in the Ubuntu terminal:

nano practical15.c

gcc practical15.c -o practical15 -pthread

./practical15

To save the file in Nano:

   1. Press Ctrl + O.
   2. Press Enter.
   3. Press Ctrl + X.



 16. Implement Banker's Algorithm and deadlock detection
techniques. Analyze resource allocation patterns and evaluate
system performance under different deadlock scenarios.


Save the file as practical16.c.


#include <stdio.h>

#define P 5
#define R 3

// Banker's Algorithm
void bankers()
{
    int allocation[P][R] = {
        {0, 1, 0},
        {2, 0, 0},
        {3, 0, 2},
        {2, 1, 1},
        {0, 0, 2}
    };

     int maximum[P][R] = {
         {7, 5, 3},
         {3, 2, 2},
         {9, 0, 2},
         {2, 2, 2},
         {4, 3, 3}
     };

     int available[R] = {3, 3, 2};

     int need[P][R];
     int finish[P] = {0};
     int safeSequence[P];

int count = 0;

printf("\n===== BANKER'S ALGORITHM =====\n");

// Calculate Need Matrix
printf("\nNeed Matrix:\n");

for (int i = 0; i < P; i++)
{
    for (int j = 0; j < R; j++)
    {
        need[i][j] =
            maximum[i][j] - allocation[i][j];

        printf("%d ", need[i][j]);
    }
    printf("\n");
}

// Find safe sequence
int work[R];

for (int i = 0; i < R; i++)
    work[i] = available[i];

while (count < P)
{
    int found = 0;

    for (int i = 0; i < P; i++)
    {
        if (finish[i] == 0)
        {
            int j;

            for (j = 0; j < R; j++)
            {
                if (need[i][j] > work[j])
                    break;
            }

            if (j == R)
            {
                for (int k = 0; k < R; k++)
                    work[k] += allocation[i][k];

                 safeSequence[count++] = i;
                 finish[i] = 1;
                 found = 1;
            }
        }
    }

    if (found == 0)
        break;
}

    if (count == P)
    {
        printf("\nSystem is in SAFE state.\n");
        printf("Safe Sequence: ");

           for (int i = 0; i < P; i++)
               printf("P%d ", safeSequence[i]);

           printf("\n");
    }
    else
    {
           printf("\nSystem is in UNSAFE state.\n");
    }
}

// Deadlock Detection Algorithm
void deadlockDetection()
{
    int allocation[P][R] = {
        {0, 1, 0},
        {2, 0, 0},
        {3, 0, 2},
        {2, 1, 1},
        {0, 0, 2}
    };

    int request[P][R] = {
        {0, 0, 0},
        {2, 0, 2},
        {0, 0, 0},
        {1, 0, 0},
        {0, 0, 2}
    };

    int available[R] = {0, 0, 0};

    int work[R];
    int finish[P] = {0};

    printf("\n===== DEADLOCK DETECTION =====\n");

    for (int i = 0; i < R; i++)
        work[i] = available[i];

    // Processes holding no resources can finish
    for (int i = 0; i < P; i++)
    {
        int hasResource = 0;

           for (int j = 0; j < R; j++)
           {
               if (allocation[i][j] != 0)
                   hasResource = 1;
           }

         if (hasResource == 0)
             finish[i] = 1;
    }

    // Check whether processes can complete
    int found;

    do
    {
         found = 0;

         for (int i = 0; i < P; i++)
         {
             if (finish[i] == 0)
             {
                 int j;

                 for (j = 0; j < R; j++)
                 {
                     if (request[i][j] > work[j])
                         break;
                 }

                 if (j == R)
                 {
                     for (int k = 0; k < R; k++)
                         work[k] += allocation[i][k];

                       finish[i] = 1;
                       found = 1;
                 }
             }
         }

    } while (found);

    int deadlock = 0;

    for (int i = 0; i < P; i++)
    {
        if (finish[i] == 0)
        {
            printf("Deadlock detected: P%d\n", i);
            deadlock = 1;
        }
    }

    if (deadlock == 0)
        printf("No deadlock detected.\n");
}

int main()
```
