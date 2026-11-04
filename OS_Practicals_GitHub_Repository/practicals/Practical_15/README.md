# Practical 15

> Source content transcribed from the supplied OS practical PDF. Code and run instructions are preserved below.

```text
printf("PRODUCER-CONSUMER PROBLEM\n\n");

    // Create producer and consumer threads
    pthread_create(&p, NULL, producer, NULL);
    pthread_create(&c, NULL, consumer, NULL);

    // Wait for both threads
    pthread_join(p, NULL);
    pthread_join(c, NULL);

    // Destroy synchronization objects
    sem_destroy(&empty);
    sem_destroy(&full);
    pthread_mutex_destroy(&mutex);

    printf("\nProducer-Consumer completed successfully!\n");

    return 0;
}


2. How to run in VS Code (Ubuntu WSL)
Execute these commands in the Ubuntu terminal:

nano practical14.c

gcc practical14.c -o practical14 -pthread

./practical14



15. Develop programs using semaphores and mutex locks to solve
synchronization problems such as Readers–Writers. Evaluate the
effect of synchronization on resource allocation and system
performance.


Save the file as practical15.c.


#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

int read_count = 0;
int shared_data = 100;

sem_t write_lock;

pthread_mutex_t mutex;

void *reader(void *arg)
{
    int id = *(int *)arg;

    // Update reader count safely
    pthread_mutex_lock(&mutex);

    read_count++;

    if (read_count == 1)
    {
        sem_wait(&write_lock);
    }

    pthread_mutex_unlock(&mutex);

    // Reading shared data
    printf("Reader %d is reading data: %d\n",
           id, shared_data);

    sleep(1);

    // Decrease reader count safely
    pthread_mutex_lock(&mutex);

    read_count--;

    if (read_count == 0)
    {
        sem_post(&write_lock);
    }

    pthread_mutex_unlock(&mutex);

    printf("Reader %d completed reading.\n", id);

    return NULL;
}

void *writer(void *arg)
{
    int id = *(int *)arg;

    sem_wait(&write_lock);

    // Writing shared data
    shared_data += 10;

    printf("Writer %d is writing data: %d\n",
           id, shared_data);

    sleep(2);

    printf("Writer %d completed writing.\n", id);

    sem_post(&write_lock);

    return NULL;
}

int main()
{
    pthread_t readers[3], writers[2];

    int reader_id[3] = {1, 2, 3};
    int writer_id[2] = {1, 2};

    // Initialize synchronization variables
    sem_init(&write_lock, 0, 1);
    pthread_mutex_init(&mutex, NULL);

    printf("READERS-WRITERS PROBLEM\n\n");

    // Create reader threads
    for (int i = 0; i < 3; i++)
    {
        pthread_create(&readers[i], NULL,
                       reader, &reader_id[i]);
    }

    // Create writer threads
    for (int i = 0; i < 2; i++)
    {
        pthread_create(&writers[i], NULL,
                       writer, &writer_id[i]);
    }

    // Wait for reader threads
    for (int i = 0; i < 3; i++)
    {
        pthread_join(readers[i], NULL);
    }
```
