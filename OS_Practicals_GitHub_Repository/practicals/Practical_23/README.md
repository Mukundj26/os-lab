# Practical 23

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
printf("\nTotal Head Movement = %d\n", movement);
    printf("Average Seek Distance = %.2f\n",
           (float)movement / n);
}

int main()
{
    int request[] = {98, 183, 37, 122, 14, 124, 65, 67};

    int n = 8;
    int head = 53;

        int diskSize = 200;

        printf("OPERATING SYSTEM - PRACTICAL 22\n");

        // File Allocation
        contiguous();
        linked();
        indexed();

        // Disk Scheduling
        printf("\nInitial Head Position: %d\n", head);
        printf("Disk Size: %d cylinders\n", diskSize);

        printf("Disk Requests: ");

        for (int i = 0; i < n; i++)
            printf("%d ", request[i]);

        printf("\n");

        FCFS(request, n, head);

        CSCAN(request, n, head, diskSize);

        printf("\n===== PERFORMANCE COMPARISON =====\n");
        printf("FCFS and C-SCAN results displayed above.\n");

        return 0;
}


2. Run in Ubuntu WSL (Without VS Code)
Open Ubuntu from the Windows Start Menu.

Step 1: Create the file

nano practical22.c

Step 2: Paste the complete C program.

Save using:

         Ctrl + O
         Press Enter.
         Ctrl + X

Step 3: Compile

gcc practical22.c -o practical22

Step 4: Run

./practical22


23. Deploy a simple AI/ML application inside a Docker container. Monitor CPU,
memory, storage, and process utilization using Linux tools and evaluate the
benefits of container-based deployment.
```
