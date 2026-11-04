# Practical 13

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
printf("Parent sent message successfully.\n");

        // Remove message queue
        msgctl(qid, IPC_RMID, NULL);
    }

    printf("\nIPC Demonstration Completed Successfully!\n");

    return 0;
}


2. Compile and run the program

Step 1: Save the file

Press Ctrl + S in VS Code.

Step 2: Compile

gcc practical12.c -o practical12

Step 3: Execute

./practical12




13. Create a multithreaded application using POSIX threads to
execute concurrent tasks. Measure CPU utilization, memory
consumption, and execution time under different thread



Save the file as practical13.c.


#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <sys/resource.h>
#include <unistd.h>

#define TOTAL_WORK 50000000

void *calculate(void *arg)
{
    long thread_id = *(long *)arg;
    long long sum = 0;

     for (long i = 1; i <= TOTAL_WORK; i++)
     {
         sum += i % 100;
     }

     printf("Thread %ld completed. Result = %lld\n",
            thread_id, sum);

     return NULL;
}

int main()
{

int thread_counts[] = {1, 2, 4, 8};
int tests = 4;

printf("MULTITHREADING PERFORMANCE ANALYSIS\n");

for (int t = 0; t < tests; t++)
{
    int n = thread_counts[t];

   pthread_t threads[n];
   long ids[n];

   struct timespec start, end;
   struct rusage usage;

   printf("\n----------------------------------\n");
   printf("Number of Threads: %d\n", n);

   clock_gettime(CLOCK_MONOTONIC, &start);

   for (int i = 0; i < n; i++)
   {
       ids[i] = i + 1;

        if (pthread_create(&threads[i], NULL,
                           calculate, &ids[i]) != 0)
        {
            perror("Thread creation failed");
            exit(1);
        }
   }

   for (int i = 0; i < n; i++)
   {
       pthread_join(threads[i], NULL);
   }

   clock_gettime(CLOCK_MONOTONIC, &end);

   double elapsed =
       (end.tv_sec - start.tv_sec) +
       (end.tv_nsec - start.tv_nsec) / 1000000000.0;

   getrusage(RUSAGE_SELF, &usage);

   double cpu_time =
       usage.ru_utime.tv_sec +
       usage.ru_utime.tv_usec / 1000000.0 +
       usage.ru_stime.tv_sec +
       usage.ru_stime.tv_usec / 1000000.0;

   double cpu_utilization =
       (cpu_time / elapsed) * 100.0;

   long memory_kb = usage.ru_maxrss;

   printf("\nPerformance Results:\n");

              printf("Execution Time: %.3f seconds\n", elapsed);
              printf("CPU Utilization: %.2f%% (approx.)\n",
```
