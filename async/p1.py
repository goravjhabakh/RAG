import asyncio
import time

async def task(name, delay):
    print(f"[{name}] delay: {delay}")
    await asyncio.sleep(delay)
    print(f"[{name}] Finished.")

async def main():
    start = time.time()
    await asyncio.gather(
        task("Task 1", 2),
        task("Task 2", 3),
        task("Task 3", 1)
    )
    end = time.time()
    print(f"Total time taken: {end - start:.2f}s")

asyncio.run(main())