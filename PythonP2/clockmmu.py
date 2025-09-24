from mmu import MMU

class ClockMMU(MMU):
    def __init__(self, frames):
        self.frames = frames
        self.frame_table = [None] * frames  # Each entry: {'page': int, 'ref': bool, 'dirty': bool}
        self.page_map = {}  # page_number -> frame index
        self.pointer = 0
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
            self.frame_table[idx]['ref'] = True
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
            self.frame_table[idx]['ref'] = True
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
        # Find empty frame first
        for i in range(self.frames):
            if self.frame_table[i] is None:
                self.frame_table[i] = {'page': page_number, 'ref': True, 'dirty': is_write}
                self.page_map[page_number] = i
                if self.debug:
                    print(f"Loaded page {page_number} into empty frame {i}")
                return
        # Clock replacement
        while True:
            entry = self.frame_table[self.pointer]
            if not entry['ref']:
                # Victim found
                old_page = entry['page']
                if entry['dirty']:
                    self.disk_writes += 1
                    if self.debug:
                        print(f"Evict dirty page {old_page} from frame {self.pointer}, write to disk")
                else:
                    if self.debug:
                        print(f"Evict clean page {old_page} from frame {self.pointer}")
                del self.page_map[old_page]
                self.frame_table[self.pointer] = {'page': page_number, 'ref': True, 'dirty': is_write}
                self.page_map[page_number] = self.pointer
                if self.debug:
                    print(f"Loaded page {page_number} into frame {self.pointer}")
                self.pointer = (self.pointer + 1) % self.frames
                return
            else:
                # Give second chance
                self.frame_table[self.pointer]['ref'] = False
                self.pointer = (self.pointer + 1) % self.frames

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
