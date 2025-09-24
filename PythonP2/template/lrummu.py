from mmu import MMU

class LruMMU(MMU):
    def __init__(self, frames):
        self.frames = frames
        self.frame_table = {}  # page_number -> [frame index, last_used, dirty]
        self.frame_list = []   # [page_number]
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0
        self.debug = False
        self.time = 0

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    def read_memory(self, page_number):
        self.time += 1
        if page_number in self.frame_table:
            self.frame_table[page_number][1] = self.time
            if self.debug:
                print(f"Read hit: page {page_number}")
            return
        # Page fault
        self.page_faults += 1
        self.disk_reads += 1
        if self.debug:
            print(f"Read miss: page {page_number} causes page fault")
        self._replace_page(page_number, is_write=False)

    def write_memory(self, page_number):
        self.time += 1
        if page_number in self.frame_table:
            self.frame_table[page_number][1] = self.time
            self.frame_table[page_number][2] = True
            if self.debug:
                print(f"Write hit: page {page_number}")
            return
        # Page fault
        self.page_faults += 1
        self.disk_reads += 1
        if self.debug:
            print(f"Write miss: page {page_number} causes page fault")
        self._replace_page(page_number, is_write=True)
    def _replace_page(self, page_number, is_write):
        if len(self.frame_table) < self.frames:
            self.frame_table[page_number] = [len(self.frame_table), self.time, is_write]
            self.frame_list.append(page_number)
            if self.debug:
                print(f"Loaded page {page_number} into frame {len(self.frame_table)-1}")
            return
        # Find LRU page
        lru_page = min(self.frame_table.items(), key=lambda x: x[1][1])[0]
        lru_info = self.frame_table[lru_page]
        idx = lru_info[0]
        if lru_info[2]:
            self.disk_writes += 1
            if self.debug:
                print(f"Evict dirty page {lru_page} from frame {idx}, write to disk")
        else:
            if self.debug:
                print(f"Evict clean page {lru_page} from frame {idx}")
        del self.frame_table[lru_page]
        self.frame_list.remove(lru_page)
        self.frame_table[page_number] = [idx, self.time, is_write]
        self.frame_list.append(page_number)
        if self.debug:
            print(f"Loaded page {page_number} into frame {idx}")

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
