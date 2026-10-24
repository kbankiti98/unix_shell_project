
import threading
import time
from collections import deque


class ProducerConsumer:
    def __init__(self, capacity=3):
        if capacity <= 0:
            raise ValueError("Buffer capacity must be positive")

        self.capacity = capacity
        self.buffer = deque()

        # Count empty spaces and available items
        self.empty = threading.Semaphore(capacity)
        self.full = threading.Semaphore(0)

        # Only one thread can modify the buffer at a time
        self.mutex = threading.Lock()

        self.produced = []
        self.consumed = []

    def produce(self, item):
        print(f"Producer: wants to add {item}")

        if not self.empty.acquire(blocking=False):
            print("Producer: buffer full, waiting for space")
            self.empty.acquire()

        with self.mutex:
            print("Producer: mutex acquired")
            self.buffer.append(item)
            self.produced.append(item)
            print(f"Producer: added {item}")
            print(f"Buffer: {list(self.buffer)}")
            print("Producer: mutex released")

        self.full.release()

    def consume(self):
        print("Consumer: wants to remove an item")

        if not self.full.acquire(blocking=False):
            print("Consumer: buffer empty, waiting for item")
            self.full.acquire()

        with self.mutex:
            print("Consumer: mutex acquired")
            item = self.buffer.popleft()
            self.consumed.append(item)
            print(f"Consumer: removed {item}")
            print(f"Buffer: {list(self.buffer)}")
            print("Consumer: mutex released")

        self.empty.release()
        return item

    def run_demo(self, delay=0.1):
        if delay < 0:
            raise ValueError("Delay cannot be negative")

        print("\nProducer-Consumer Synchronization")
        print(f"Buffer capacity: {self.capacity}")

        items = ["A", "B", "C", "D", "E"]

        def producer():
            for item in items:
                self.produce(item)
                time.sleep(delay)

        def consumer():
            for _ in items:
                time.sleep(delay * 2)
                self.consume()

        producer_thread = threading.Thread(target=producer)
        consumer_thread = threading.Thread(target=consumer)

        producer_thread.start()
        consumer_thread.start()

        producer_thread.join()
        consumer_thread.join()

        print("\nSynchronization Results")
        print(f"Produced: {self.produced}")
        print(f"Consumed: {self.consumed}")
        print(f"Final buffer: {list(self.buffer)}")
        print(f"Produced count: {len(self.produced)}")
        print(f"Consumed count: {len(self.consumed)}")


if __name__ == "__main__":
    demo = ProducerConsumer(capacity=3)
    demo.run_demo(delay=0.1)
