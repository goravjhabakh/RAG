import time
from threading import Thread
from multiprocessing import Process

def task():
    print('Starting Task')
    count = 0
    for _ in range(10**8):
        count += 1
    print('Finished Task')

if __name__ == '__main__':
    # Multi-Threading
    start_time = time.time()
    t1 = Thread(target=task)
    t2 = Thread(target=task)

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f'Multi-Threading time taken - {time.time() - start_time}s')

    # Multi-Processing
    start_time = time.time()
    p1 = Process(target=task)
    p2 = Process(target=task)

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print(f'Multi-Processing time taken - {time.time() - start_time}s')