# Practical 19

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
}

int main()
{
    int pages[] = {7, 0, 1, 2, 0, 3, 0,
                   4, 2, 3, 0, 3, 2};

    int n = sizeof(pages) / sizeof(pages[0]);

    printf("OPERATING SYSTEM - PRACTICAL 18\n");

    paging();

    segmentation();

    FIFO(pages, n);

    Optimal(pages, n);

    printf("\n===== PERFORMANCE COMPARISON =====\n");
    printf("Compare FIFO and Optimal results above.\n");

    return 0;
}

2. Run in Ubuntu WSL (Without VS Code)
Open Ubuntu from the Windows Start Menu.

Step 1: Create file

nano practical18.c

Step 2: Paste the complete C program.

Save using:

       Ctrl + O
       Press Enter.
       Ctrl + X

Step 3: Compile

gcc practical18.c -o practical18

Step 4: Run

./practical18


19. Simulate paging, segmentation, and virtual memory management. Implement
LRU and Optimal page replacement algorithms and compare their effectiveness
using performance metrics.


Save the file as practical19.c.


#include <stdio.h>

#define FRAMES 3

// LRU Page Replacement
void LRU(int pages[], int n)
{
    int frames[FRAMES];
    int lastUsed[FRAMES];
    int faults = 0, hits = 0;

       for (int i = 0; i < FRAMES; i++)
       {
           frames[i] = -1;
           lastUsed[i] = -1;
       }

       printf("\n===== LRU PAGE REPLACEMENT =====\n");

for (int i = 0; i < n; i++)
{
    int found = -1;

   for (int j = 0; j < FRAMES; j++)
   {
       if (frames[j] == pages[i])
           found = j;
   }

   if (found != -1)
   {
       hits++;
       lastUsed[found] = i;

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

          // Find least recently used page
          if (replace == -1)
          {
              replace = 0;

              for (int j = 1; j < FRAMES; j++)
              {
                  if (lastUsed[j] < lastUsed[replace])
                      replace = j;
              }
          }

          frames[replace] = pages[i];
          lastUsed[replace] = i;
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

    printf("\nLRU Results:\n");
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

            // Find page used farthest in future
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
```
