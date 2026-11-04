# Practical 17

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
{
    printf("OPERATING SYSTEM - PRACTICAL 16\n");

    bankers();

        deadlockDetection();

        return 0;
}


2. Run in Ubuntu WSL (without VS Code)
Open Ubuntu from the Windows Start Menu.

Step 1: Create the file

nano practical16.c

Step 2: Paste the complete C program and save it.

         Press Ctrl + O
         Press Enter
         Press Ctrl + X

Step 3: Compile

gcc practical16.c -o practical16

Step 4: Run

./practical16

If GCC is not installed:

sudo apt update
sudo apt install gcc -y




17. Simulate paging, segmentation, and virtual memory
management. Implement FIFO and LRU page replacement algorithms
and compare their effectiveness using performance metrics.


Save the file as practical17.c.


#include <stdio.h>

#define MAX 30
#define FRAMES 3

// FIFO Page Replacement
void FIFO(int pages[], int n)

{
    int frames[FRAMES];
    int index = 0, faults = 0, hits = 0;

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
    printf("Hit Ratio = %.2f%%\n", (hits * 100.0) / n);
    printf("Fault Ratio = %.2f%%\n", (faults * 100.0) / n);
}

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

          for (int j = 0; j < FRAMES; j++)
          {
              if (frames[j] == -1)
              {
                  replace = j;
                  break;
              }
          }

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
    printf("Hit Ratio = %.2f%%\n", (hits * 100.0) / n);
    printf("Fault Ratio = %.2f%%\n", (faults * 100.0) / n);
}

// Paging Demonstration
void paging()
{
    int pageSize = 100;
    int logicalAddress = 250;

    int pageNumber = logicalAddress / pageSize;
    int offset = logicalAddress % pageSize;

    printf("\n===== PAGING =====\n");
    printf("Logical Address: %d\n", logicalAddress);
    printf("Page Size: %d\n", pageSize);
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
        int physicalAddress = base[segment] + offset;

        printf("Physical Address: %d\n", physicalAddress);

        }
        else
        {
               printf("Segmentation Fault!\n");
        }
}

int main()
{
```
