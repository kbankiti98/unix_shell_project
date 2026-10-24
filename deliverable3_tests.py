
import io
from contextlib import redirect_stdout

from memory_manager import MemoryManager
from page_replacement import PagingSimulator
from synchronization import ProducerConsumer


def run_quietly(function, *args, **kwargs):
    output = io.StringIO()

    with redirect_stdout(output):
        result = function(*args, **kwargs)

    return result, output.getvalue()


def check_result(name, condition):
    if condition:
        print(f"PASS: {name}")
        return 1

    print(f"FAIL: {name}")
    return 0


def main():
    passed = 0
    total = 0

    # Test 1: Page allocation and loading
    memory = MemoryManager(frame_count=3, page_size=4)

    with redirect_stdout(io.StringIO()):
        memory.allocate(1, [1, 2])
        memory.access_page(1, 1)
        memory.access_page(1, 2)

    total += 1
    passed += check_result(
        "Memory allocation",
        memory.frames == [(1, 1), (1, 2), None]
    )

    # Test 2: Deallocation releases frames
    with redirect_stdout(io.StringIO()):
        memory.deallocate(1)

    total += 1
    passed += check_result(
        "Memory deallocation",
        memory.frames == [None, None, None]
        and 1 not in memory.allocated_pages
    )

    # Test 3: Page fault and page hit
    memory = MemoryManager(frame_count=2)

    with redirect_stdout(io.StringIO()):
        memory.allocate(1, [1, 2])
        first_access = memory.access_page(1, 1)
        second_access = memory.access_page(1, 1)

    total += 1
    passed += check_result(
        "Page faults and hits",
        first_access is False
        and second_access is True
        and memory.page_faults == 1
    )

    # Test 4 and 5: FIFO and LRU comparison
    references = [1, 2, 3, 1, 4, 2, 5]

    expected = {
        "fifo": 5,
        "lru": 6
    }

    for policy, faults in expected.items():
        paging = PagingSimulator(frame_count=3, policy=policy)

        with redirect_stdout(io.StringIO()):
            paging.allocate(1, sorted(set(references)))
            paging.run_references(1, references)

        total += 1
        passed += check_result(
            f"{policy.upper()} page replacement",
            paging.page_faults == faults
        )

    # Test 6: Producer-Consumer synchronization
    demo = ProducerConsumer(capacity=1)

    _, sync_output = run_quietly(demo.run_demo, delay=0.1)

    total += 1
    passed += check_result(
        "Producer-Consumer synchronization",
        demo.produced == ["A", "B", "C", "D", "E"]
        and demo.consumed == ["A", "B", "C", "D", "E"]
        and len(demo.buffer) == 0
    )

    # Test 7: Buffer-full waiting
    total += 1
    passed += check_result(
        "Buffer-full waiting",
        "buffer full, waiting for space" in sync_output
    )

    print(f"\n{passed} of {total} Deliverable 3 tests passed")


if __name__ == "__main__":
    main()
