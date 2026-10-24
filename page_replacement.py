
from memory_manager import MemoryManager


class PagingSimulator(MemoryManager):
    def __init__(self, frame_count=3, page_size=4, policy="fifo"):
        super().__init__(frame_count, page_size)

        self.policy = policy.lower()

        if self.policy not in ("fifo", "lru"):
            raise ValueError("Policy must be fifo or lru")

        self.load_order = {}
        self.last_used = {}
        self.clock = 0

    def access_page(self, pid, page):
        if pid not in self.allocated_pages:
            raise ValueError(f"P{pid} has no allocated memory")

        if page not in self.allocated_pages[pid]:
            raise ValueError(f"Page {page} is not allocated to P{pid}")

        self.clock += 1
        entry = (pid, page)

        # Page already exists in a frame
        if entry in self.frames:
            print(f"P{pid} page {page}: HIT")
            self.last_used[entry] = self.clock
            self.show_frames()
            return True

        # Page is missing from physical memory
        self.page_faults += 1
        print(f"P{pid} page {page}: PAGE FAULT")

        if None in self.frames:
            index = self.frames.index(None)

        else:
            # Choose the page to replace
            if self.policy == "fifo":
                victim = min(
                    self.frames,
                    key=lambda item: self.load_order[item]
                )
            else:
                victim = min(
                    self.frames,
                    key=lambda item: self.last_used[item]
                )

            index = self.frames.index(victim)

            print(
                f"Memory full: replaced "
                f"P{victim[0]} page {victim[1]} "
                f"using {self.policy.upper()}"
            )

            del self.load_order[victim]
            del self.last_used[victim]

        self.frames[index] = entry
        self.load_order[entry] = self.clock
        self.last_used[entry] = self.clock

        print(f"Loaded P{pid} page {page} into frame {index}")
        self.show_frames()

        return False

    def deallocate(self, pid):
        for entry in self.frames:
            if entry is not None and entry[0] == pid:
                self.load_order.pop(entry, None)
                self.last_used.pop(entry, None)

        super().deallocate(pid)

    def show_frames(self):
        values = [
            f"P{entry[0]}:{entry[1]}" if entry else "-"
            for entry in self.frames
        ]

        print("Frames:", values)

    def run_references(self, pid, references):
        print(f"\nPage Replacement: {self.policy.upper()}")
        print(f"Frame count: {self.frame_count}")
        print("References:", " ".join(map(str, references)))

        for page in references:
            self.access_page(pid, page)

        print(f"\nTotal page faults: {self.page_faults}")
        self.show_frames()


if __name__ == "__main__":
    references = [1, 2, 3, 1, 4, 2, 5]

    for policy in ("fifo", "lru"):
        memory = PagingSimulator(
            frame_count=3,
            page_size=4,
            policy=policy
        )

        memory.allocate(1, sorted(set(references)))
        memory.run_references(1, references)
        print()
