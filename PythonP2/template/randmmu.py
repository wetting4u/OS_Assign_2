from mmu import MMU

class RandMMU(MMU):
    def __init__(self, frames):
        self.frames = frames
        self.frame_table = [None] * frames  # Each entry: {'page': int, 'dirty': bool}
        self.page_map = {}  # page_number -> frame index
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0
        self.debug = False

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    def read_memory(self, page_number):
        if page_number in self.page_map:
            idx = self.page_map[page_number]
            if self.debug:
                print(f"Read hit: page {page_number} in frame {idx}")
            return
        # Page fault
        self.page_faults += 1
        self.disk_reads += 1
        if self.debug:
            print(f"Read miss: page {page_number} causes page fault")
        self._replace_page(page_number, is_write=False)

    def write_memory(self, page_number):
        if page_number in self.page_map:
            idx = self.page_map[page_number]
            self.frame_table[idx]['dirty'] = True
            if self.debug:
                print(f"Write hit: page {page_number} in frame {idx}")
            return
        # Page fault
        self.page_faults += 1
        self.disk_reads += 1
        if self.debug:
            print(f"Write miss: page {page_number} causes page fault")
        self._replace_page(page_number, is_write=True)
    def _replace_page(self, page_number, is_write):
        import random
        # Find empty frame first
        for i in range(self.frames):
            if self.frame_table[i] is None:
                self.frame_table[i] = {'page': page_number, 'dirty': is_write}
                self.page_map[page_number] = i
                if self.debug:
                    print(f"Loaded page {page_number} into empty frame {i}")
                return
        # Random replacement
        victim = random.randint(0, self.frames - 1)
        old_page = self.frame_table[victim]['page']
        if self.frame_table[victim]['dirty']:
            self.disk_writes += 1
            if self.debug:
                print(f"Evict dirty page {old_page} from frame {victim}, write to disk")
        else:
            if self.debug:
                print(f"Evict clean page {old_page} from frame {victim}")
        del self.page_map[old_page]
        self.frame_table[victim] = {'page': page_number, 'dirty': is_write}
        self.page_map[page_number] = victim
        if self.debug:
            print(f"Loaded page {page_number} into frame {victim}")

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
