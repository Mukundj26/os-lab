# Practical 18

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
int pages[] = {7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2};
    int n = sizeof(pages) / sizeof(pages[0]);

        printf("OPERATING SYSTEM - PRACTICAL 17\n");

        paging();

        segmentation();

        FIFO(pages, n);

        LRU(pages, n);

        printf("\n===== PERFORMANCE COMPARISON =====\n");
        printf("FIFO and LRU results are shown above.\n");
        printf("Compare page faults and hit ratios.\n");

        return 0;
}


2. Run in Ubuntu WSL (Without VS Code)
Open your Ubuntu terminal.

Step 1: Create file

nano practical17.c

Step 2: Paste the complete program.

Save using:

           Ctrl + O
           Enter
           Ctrl + X

Step 3: Compile

gcc practical17.c -o practical17

Step 4: Execute

./practical17


 18. Simulate paging, segmentation, and virtual memory management. Implement
FIFO, and Optimal page replacement algorithms and compare their effectiveness
using performance metrics.


Save the file as practical18.c.


#include <stdio.h>

#define FRAMES 3

// FIFO Page Replacement
void FIFO(int pages[], int n)
{
    int frames[FRAMES];
    int faults = 0, hits = 0;
    int index = 0;

    for (int i = 0; i < FRAMES; i++)
        frames[i] = -1;

    printf("\n===== FIFO PAGE REPLACEMENT =====\n");

    for (int i = 0; i < n; i++)
    {
        int found = 0;

         for (int j = 0; j < FRAMES; j++)
         {
             if (frames[j] == pages[i])
                 found = 1;
         }

         if (found)
         {
              hits++;
              printf("Page %d: HIT\n", pages[i]);
         }
         else
         {
              frames[index] = pages[i];
              index = (index + 1) % FRAMES;
              faults++;

              printf("Page %d: PAGE FAULT\n", pages[i]);
         }

         printf("Frames: ");

         for (int j = 0; j < FRAMES; j++)
         {
             if (frames[j] == -1)

                   printf("- ");
            else
                   printf("%d ", frames[j]);
        }

        printf("\n");
    }

    printf("\nFIFO Results:\n");
    printf("Page Faults = %d\n", faults);
    printf("Page Hits = %d\n", hits);
    printf("Hit Ratio = %.2f%%\n", hits * 100.0 / n);
    printf("Fault Ratio = %.2f%%\n", faults * 100.0 / n);
}

// Optimal Page Replacement
void Optimal(int pages[], int n)
{
    int frames[FRAMES];
    int faults = 0, hits = 0;

    for (int i = 0; i < FRAMES; i++)
        frames[i] = -1;

    printf("\n===== OPTIMAL PAGE REPLACEMENT =====\n");

    for (int i = 0; i < n; i++)
    {
        int found = 0;

        for (int j = 0; j < FRAMES; j++)
        {
            if (frames[j] == pages[i])
                found = 1;
        }

        if (found)
        {
             hits++;
             printf("Page %d: HIT\n", pages[i]);
        }
        else
        {
             int replace = -1;

            // Find an empty frame
            for (int j = 0; j < FRAMES; j++)
            {
                if (frames[j] == -1)
                {
                    replace = j;
                    break;
                }
            }

            // Find the page used farthest in the future
            if (replace == -1)

            {
                int farthest = -1;

                for (int j = 0; j < FRAMES; j++)
                {
                    int k;

                    for (k = i + 1; k < n; k++)
                    {
                        if (frames[j] == pages[k])
                            break;
                    }

                    if (k == n)
                    {
                        replace = j;
                        break;
                    }

                    if (k > farthest)
                    {
                        farthest = k;
                        replace = j;
                    }
                }
            }

            frames[replace] = pages[i];
            faults++;

            printf("Page %d: PAGE FAULT\n", pages[i]);
        }

        printf("Frames: ");

        for (int j = 0; j < FRAMES; j++)
        {
            if (frames[j] == -1)
                 printf("- ");
            else
                 printf("%d ", frames[j]);
        }

        printf("\n");
    }

    printf("\nOptimal Results:\n");
    printf("Page Faults = %d\n", faults);
    printf("Page Hits = %d\n", hits);
    printf("Hit Ratio = %.2f%%\n", hits * 100.0 / n);
    printf("Fault Ratio = %.2f%%\n", faults * 100.0 / n);
}

// Paging Demonstration
void paging()
{
    int logicalAddress = 250;

    int pageSize = 100;

    int pageNumber = logicalAddress / pageSize;
    int offset = logicalAddress % pageSize;

    printf("\n===== PAGING =====\n");
    printf("Logical Address: %d\n", logicalAddress);
    printf("Page Number: %d\n", pageNumber);
    printf("Offset: %d\n", offset);
}

// Segmentation Demonstration
void segmentation()
{
    int base[] = {1000, 2000, 3000};
    int limit[] = {500, 600, 400};

    int segment = 1;
    int offset = 200;

    printf("\n===== SEGMENTATION =====\n");
    printf("Segment Number: %d\n", segment);
    printf("Offset: %d\n", offset);

    if (offset < limit[segment])
    {
         printf("Physical Address: %d\n",
                base[segment] + offset);
    }
    else
    {
         printf("Segmentation Fault!\n");
    }
```
