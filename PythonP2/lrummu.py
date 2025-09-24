from collections import OrderedDict
from mmu import MMU

class LruMMU(MMU):
    #initialize some variables here

    def __init__(self, frames):
        # TODO: Constructor logic for LruMMU
        self.frames = frames
        self.debug = False
        self.memory = OrderedDict()
        
        self.disk_reads = 0
        self.disk_writes = 0
        
        self.page_faults = 0

    def set_debug(self):
        # TODO: Implement the method to set debug mode
        self.debug = True

    def reset_debug(self):
        # TODO: Implement the method to reset debug mode
        self.debug = False

    def read_memory(self, page_number):
        if page_number in self.memory:
            # HIT: move to MRU
            dirty = self.memory.pop(page_number)
            self.memory[page_number] = dirty
            if self.debug:
                print(f"Read page {page_number}: HIT")
        else:
            # MISS
            self.page_faults += 1
            self.disk_reads += 1
            if len(self.memory) >= self.frames:
                evicted_page, dirty = self.memory.popitem(last=False)
                if dirty:
                    self.disk_writes += 1
                if self.debug:
                    print(f"Evict: {evicted_page} (dirty={dirty})")
            self.memory[page_number] = False  # clean on read
            if self.debug:
                print(f"Read miss: {page_number}")

    def write_memory(self, page_number):
        if page_number in self.memory:
            # HIT: move to MRU and mark dirty
            self.memory.pop(page_number)
            self.memory[page_number] = True
            if self.debug:
                print(f"Write hit: {page_number}")
        else:
            # MISS
            self.page_faults += 1
            self.disk_reads += 1
            if len(self.memory) >= self.frames:
                evicted_page, dirty = self.memory.popitem(last=False)
                if dirty:
                    self.disk_writes += 1
                if self.debug:
                    print(f"Evict: {evicted_page} (dirty={dirty})")
            self.memory[page_number] = True  # dirty on write
            if self.debug:
                print(f"Write miss: {page_number}")

    def get_total_disk_reads(self):
        # TODO: Implement the method to get total disk reads
        return self.disk_reads

    def get_total_disk_writes(self):
        # TODO: Implement the method to get total disk writes
        return self.disk_writes

    def get_total_page_faults(self):
        # TODO: Implement the method to get total page faults
        return self.page_faults
