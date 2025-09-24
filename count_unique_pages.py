#!/usr/bin/env python3
"""
計算各trace檔中的unique page數量
"""

def analyze_unique_pages(trace_file):
    """分析trace檔中的unique page數量"""
    unique_pages = set()
    total_accesses = 0
    
    with open(trace_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                addr = parts[0]
                page_num = int(addr, 16) >> 12  # PAGE_OFFSET = 12
                unique_pages.add(page_num)
                total_accesses += 1
    
    return len(unique_pages), total_accesses

def main():
    trace_files = [
        'trace/bzip.trace',
        'trace/swim.trace', 
        'trace/gcc.trace',
        'trace/sixpack.trace'
    ]
    
    print("=== Trace檔案 Unique Pages 分析 ===")
    print(f"{'程式':<10} {'Unique Pages':<12} {'總存取次數':<12} {'記憶體需求':<12}")
    print("-" * 50)
    
    for trace_file in trace_files:
        try:
            unique_count, total_count = analyze_unique_pages(trace_file)
            memory_mb = unique_count * 4 / 1024  # 4KB per page -> MB
            
            trace_name = trace_file.split('/')[-1].replace('.trace', '')
            print(f"{trace_name.upper():<10} {unique_count:<12} {total_count:<12} {memory_mb:.1f}MB")
            
        except FileNotFoundError:
            print(f"找不到檔案: {trace_file}")

if __name__ == "__main__":
    main()