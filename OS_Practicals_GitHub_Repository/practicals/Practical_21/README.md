# Practical 21

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
{
    int request[] = {98, 183, 37, 122, 14, 124, 65, 67};
    int n = 8;
    int head = 53;

     printf("OPERATING SYSTEM - PRACTICAL 20\n");

     // File Allocation
     contiguous();

     linked();

     indexed();

     // Disk Scheduling
     printf("\nInitial Disk Head Position: %d\n", head);

     printf("Disk Requests: ");
     for (int i = 0; i < n; i++)
         printf("%d ", request[i]);

     printf("\n");

     FCFS(request, n, head);

     SSTF(request, n, head);

     printf("\n===== PERFORMANCE COMPARISON =====\n");
     printf("FCFS and SSTF results displayed above.\n");

     return 0;
}


2. Run in Ubuntu WSL (Without VS Code)
Open Ubuntu from the Windows Start Menu.

Step 1: Create file

nano practical20.c

Step 2: Paste the complete program.

Save using:

         Ctrl + O
         Press Enter.
         Ctrl + X

Step 3: Compile

gcc practical20.c -o practical20

Step 4: Run

./practical20


 21. Implement file allocation and disk scheduling algorithms (FCFS, SCAN).
Analyze storage utilization, access time, and system throughput.


Save the file as practical21.c.


#include <stdio.h>
#include <stdlib.h>

#define MAX 50

// Contiguous File Allocation
void contiguous()
{
    int start, length;

        printf("\n===== CONTIGUOUS FILE ALLOCATION =====\n");

        printf("Enter starting block: ");
        scanf("%d", &start);

        printf("Enter file length: ");
        scanf("%d", &length);

        printf("Allocated blocks: ");

        for (int i = 0; i < length; i++)
            printf("%d ", start + i);

        printf("\n");
}

// Linked File Allocation

void linked()
{
    int n, blocks[MAX];

    printf("\n===== LINKED FILE ALLOCATION =====\n");

    printf("Enter number of blocks: ");
    scanf("%d", &n);

    printf("Enter block numbers:\n");

    for (int i = 0; i < n; i++)
        scanf("%d", &blocks[i]);

    printf("Linked allocation: ");

    for (int i = 0; i < n; i++)
    {
        printf("%d", blocks[i]);

        if (i < n - 1)
            printf(" -> ");
    }

    printf(" -> NULL\n");
}

// Indexed File Allocation
void indexed()
{
    int n, indexBlock, blocks[MAX];

    printf("\n===== INDEXED FILE ALLOCATION =====\n");

    printf("Enter index block: ");
    scanf("%d", &indexBlock);

    printf("Enter number of data blocks: ");
    scanf("%d", &n);

    printf("Enter data block numbers:\n");

    for (int i = 0; i < n; i++)
        scanf("%d", &blocks[i]);

    printf("Index Block: %d\n", indexBlock);
    printf("Data blocks: ");

    for (int i = 0; i < n; i++)
        printf("%d ", blocks[i]);

    printf("\n");
}

// FCFS Disk Scheduling
void FCFS(int request[], int n, int head)
{

    int movement = 0;
    int current = head;

    printf("\n===== FCFS DISK SCHEDULING =====\n");

    printf("Head movement: %d", head);

    for (int i = 0; i < n; i++)
    {
        movement += abs(request[i] - current);
        current = request[i];

        printf(" -> %d", request[i]);
    }

    printf("\nTotal Head Movement = %d\n", movement);
    printf("Average Seek Distance = %.2f\n",
           (float)movement / n);
}

// SCAN Disk Scheduling
void SCAN(int request[], int n, int head, int diskSize)
{
    int sorted[MAX];
    int movement = 0;
    int current = head;

    // Copy requests
    for (int i = 0; i < n; i++)
        sorted[i] = request[i];

    // Sort requests in ascending order
    for (int i = 0; i < n - 1; i++)
    {
        for (int j = 0; j < n - i - 1; j++)
        {
            if (sorted[j] > sorted[j + 1])
            {
                int temp = sorted[j];
                sorted[j] = sorted[j + 1];
                sorted[j + 1] = temp;
            }
        }
    }

    printf("\n===== SCAN DISK SCHEDULING =====\n");
    printf("Head movement: %d", head);

    // Move towards higher cylinder numbers
    int i;

    for (i = 0; i < n; i++)
    {
        if (sorted[i] >= head)
            break;
    }

    for (int j = i; j < n; j++)
    {
        movement += abs(sorted[j] - current);
        current = sorted[j];

        printf(" -> %d", current);
    }

    // Reach the end of the disk
    movement += abs((diskSize - 1) - current);
    current = diskSize - 1;

    printf(" -> %d", current);

    // Reverse direction
    for (int j = i - 1; j >= 0; j--)
    {
        movement += abs(sorted[j] - current);
        current = sorted[j];

        printf(" -> %d", current);
    }

    printf("\nTotal Head Movement = %d\n", movement);
    printf("Average Seek Distance = %.2f\n",
           (float)movement / n);
}
```
