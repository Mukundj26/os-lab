# Practical 20

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
else
    {
         printf("Segmentation Fault!\n");
    }
}

int main()
{
    int pages[] = {7, 0, 1, 2, 0, 3, 0,
                   4, 2, 3, 0, 3, 2};

    int n = sizeof(pages) / sizeof(pages[0]);

    printf("OPERATING SYSTEM - PRACTICAL 19\n");

    paging();

    segmentation();

    LRU(pages, n);

    Optimal(pages, n);

    printf("\n===== PERFORMANCE COMPARISON =====\n");
    printf("Compare LRU and Optimal results above.\n");

    return 0;
}

2. Run in Ubuntu WSL (Without VS Code)
Open Ubuntu from the Windows Start Menu.

Step 1: Create the file

nano practical19.c

Step 2: Paste the complete C program.

Save using:

       Ctrl + O
       Press Enter.
       Ctrl + X

Step 3: Compile

gcc practical19.c -o practical19

Step 4: Run

./practical19



20. Implement file allocation and disk scheduling algorithms (FCFS, SSTF).
Analyze storage utilization, access time, and system throughput.


Save the file as practical20.c.


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

       printf("Enter file length (number of blocks): ");
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

// SSTF Disk Scheduling
void SSTF(int request[], int n, int head)
{
    int visited[MAX] = {0};
    int movement = 0;
    int current = head;

    printf("\n===== SSTF DISK SCHEDULING =====\n");

    printf("Head movement: %d", head);

    for (int i = 0; i < n; i++)
    {
        int min = 100000;
        int index = -1;

        for (int j = 0; j < n; j++)
        {
            if (!visited[j])
            {
                int distance = abs(request[j] - current);

                if (distance < min)
                {
                    min = distance;
                    index = j;
                }
            }

          }

          visited[index] = 1;
          movement += min;
          current = request[index];

          printf(" -> %d", current);
     }

     printf("\nTotal Head Movement = %d\n", movement);
     printf("Average Seek Distance = %.2f\n",
            (float)movement / n);
}

int main()
```
