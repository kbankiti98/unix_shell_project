
class MemoryManager:
    def __init__(self, frame_count=3, page_size=4):
        if frame_count <= 0:
            raise ValueError("Frame count must be positive")
        if page_size <= 0:
            raise ValueError("Page size must be positive")

        self.frame_count = frame_count
        self.page_size = page_size
        self.frames = [None] * frame_count
        self.allocated_pages = {}
        self.page_faults = 0

    def allocate(self, pid, pages):
        if pid in self.allocated_pages:
            raise ValueError(f"P{pid} already has allocated pages")

        if not pages:
            raise ValueError("At least one page is required")

        if len(pages) != len(set(pages)):
            raise ValueError("Page numbers must be unique")

        self.allocated_pages[pid] = set(pages)

        print(f"P{pid}: allocated pages {list(pages)}")
        print("Pages are assigned but not loaded into frames yet.")

    def access_page(self, pid, page):
        if pid not in self.allocated_pages:
            raise ValueError(f"P{pid} has no allocated memory")

        if page not in self.allocated_pages[pid]:
            raise ValueError(f"Page {page} is not allocated to P{pid}")

        entry = (pid, page)

        if entry in self.frames:
            print(f"P{pid} page {page}: HIT")
            return True

        self.page_faults += 1
        print(f"P{pid} page {page}: PAGE FAULT")

        if None in self.frames:
            index = self.frames.index(None)
            self.frames[index] = entry
            print(f"Loaded into frame {index}")
        else:
            print("Memory full. Page replacement is required.")

        return False

    def deallocate(self, pid):
        if pid not in self.allocated_pages:
            raise ValueError(f"P{pid} has no allocated memory")

        for index, entry in enumerate(self.frames):
            if entry is not None and entry[0] == pid:
                self.frames[index] = None

        del self.allocated_pages[pid]
        print(f"P{pid}: memory deallocated")

    def show_memory(self):
        print("\nMemory Frames")

        for index, entry in enumerate(self.frames):
            if entry is None:
                print(f"Frame {index}: Empty")
            else:
                pid, page = entry
                print(f"Frame {index}: P{pid} Page {page}")

        print("\nProcess Memory Usage")

        for pid in sorted(self.allocated_pages):
            resident = sum(
                1 for entry in self.frames
                if entry is not None and entry[0] == pid
            )
            print(
                f"P{pid}: {resident} resident frame(s), "
                f"{resident * self.page_size} KB used"
            )

        used = sum(entry is not None for entry in self.frames)
        print(f"\nFrames used: {used}/{self.frame_count}")
        print(f"Page faults: {self.page_faults}")


if __name__ == "__main__":
    memory = MemoryManager(frame_count=3, page_size=4)

    memory.allocate(1, [1, 2])
    memory.allocate(2, [1, 2])

    memory.access_page(1, 1)
    memory.access_page(1, 2)
    memory.access_page(2, 1)

    memory.show_memory()

    memory.deallocate(1)
    memory.show_memory()
