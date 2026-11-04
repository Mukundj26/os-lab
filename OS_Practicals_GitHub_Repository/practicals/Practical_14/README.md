# Practical 14

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
cpu_utilization);
              printf("Maximum Resident Memory: %ld KB\n",
                     memory_kb);
        }

        printf("\nAll thread tests completed successfully!\n");

        return 0;
}


2. How to run in VS Code (Ubuntu WSL)
Open the Ubuntu terminal in VS Code and execute these commands:

# Create practical file
nano practical13.c

# Compile the program
gcc practical13.c -o practical13 -pthread

# Run the program
./practical13

Save the file in Nano:

           Press Ctrl + O, then Enter.
           Press Ctrl + X to exit




14. Develop programs using semaphores and mutex locks to solve
synchronization problems such as Producer–Consumer. Evaluate the
effect of synchronization on resource allocation and system
performance.



Save the file as practical14.c.


#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

#define SIZE 5
#define ITEMS 10

int buffer[SIZE];

int in = 0, out = 0;

sem_t empty, full;
pthread_mutex_t mutex;

void *producer(void *arg)
{
    for (int i = 1; i <= ITEMS; i++)
    {
        sem_wait(&empty);
        pthread_mutex_lock(&mutex);

        buffer[in] = i;

        printf("Producer produced: %d\n", i);

        in = (in + 1) % SIZE;

        pthread_mutex_unlock(&mutex);
        sem_post(&full);

        sleep(1);
    }

    return NULL;
}

void *consumer(void *arg)
{
    for (int i = 1; i <= ITEMS; i++)
    {
        sem_wait(&full);
        pthread_mutex_lock(&mutex);

        int item = buffer[out];

        printf("Consumer consumed: %d\n", item);

        out = (out + 1) % SIZE;

        pthread_mutex_unlock(&mutex);
        sem_post(&empty);

        sleep(2);
    }

    return NULL;
}

int main()
{
    pthread_t p, c;

    // Initialize semaphores
    sem_init(&empty, 0, SIZE);
    sem_init(&full, 0, 0);

    // Initialize mutex
    pthread_mutex_init(&mutex, NULL);
```
