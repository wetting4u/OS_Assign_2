import random

class RandMMU:
    def __init__(self, frames):
        self.frames = frames
        self.memory = {}   # page_number -> {frame, dirty}
        self.frame_table = [None] * frames
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0
        self.debug = False

    def set_debug(self): self.debug = True
    def reset_debug(self): self.debug = False

    def _evict(self):
        victim_frame = random.randint(0, self.frames - 1)
        victim_page = self.frame_table[victim_frame]
        if self.memory[victim_page]["dirty"]:
            self.disk_writes += 1
            if self.debug: print(f"Disk write {victim_page}")
        else:
            if self.debug: print(f"Discard {victim_page}")
        del self.memory[victim_page]
        return victim_frame

    def _load_page(self, page_number, dirty):
        if len(self.memory) < self.frames:
            frame = self.frame_table.index(None)
        else:
            frame = self._evict()
        self.disk_reads += 1
        self.page_faults += 1
        self.frame_table[frame] = page_number
        self.memory[page_number] = {"frame": frame, "dirty": dirty}
        return frame

    def read_memory(self, page_number):
        if page_number in self.memory:
            if self.debug: print(f"Reading {page_number}")
        else:
            self._load_page(page_number, False)
            if self.debug: print(f"Page fault {page_number}")

    def write_memory(self, page_number):
        if page_number in self.memory:
            self.memory[page_number]["dirty"] = True
            if self.debug: print(f"Writing {page_number}")
        else:
            self._load_page(page_number, True)
            if self.debug: print(f"Page fault {page_number}")

    def get_total_disk_reads(self): return self.disk_reads
    def get_total_disk_writes(self): return self.disk_writes
    def get_total_page_faults(self): return self.page_faults
