from mmu import MMU
import random

class RandMMU(MMU):
    def __init__(self, frames):
        self.page_fault_count = 0
        self.write_disk_count = 0
        self.read_disk_count = 0
        self.is_debug_mode = False
        self.table_size = frames
        self.table = []
        random.seed(999)

    def set_debug(self):
        self.is_debug_mode = True

    def reset_debug(self):
        self.is_debug_mode = False

    def read_memory(self, page_number):
        if page_number in self.table:
            if self.is_debug_mode:
                print(f"{page_number} already in table, current table is:")
                print(self.table)
        else:
            #self.page_fault_count += 1
            #self.read_disk_count += 1
            if self.is_debug_mode:
                print(f"{page_number} is not in table, current table is:")
                print(self.table)
                print("reading from disk..")

            self.write_memory(page_number)
            if self.is_debug_mode:
                print(f"{page_number} after read from disk, current table is:")
                print(self.table)


    def write_memory(self, page_number):

        if page_number not in self.table:
            self.page_fault_count += 1
            self.read_disk_count += 1
            if self.is_debug_mode:
                print("table before writing:")
                print(self.table)
                print(f"writing {page_number} to table")
            if len(self.table) == self.table_size:
                random_index = random.randint(0, self.table_size-1)
                self.table[random_index] = page_number
                self.write_disk_count += 1
            else:
                self.table.append(page_number)
            if self.is_debug_mode:
                print("table after writing:")
                print(self.table)
        else:
            
            if self.is_debug_mode:
                print(f"{page_number} already in table, no need write")



    def get_total_disk_reads(self):
        return self.read_disk_count

    def get_total_disk_writes(self):
        return self.write_disk_count

    def get_total_page_faults(self):
        return self.page_fault_count
