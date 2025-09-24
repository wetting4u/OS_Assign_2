#!/usr/bin/env python3
"""
實驗腳本：批量執行page replacement算法測試
自動收集所有trace檔在不同frame數下的性能數據
"""

import subprocess
import csv
import os

def run_simulation(trace_file, frames, algorithm):
    """執行單次模擬並返回結果"""
    cmd = f"python PythonP2/memsim.py {trace_file} {frames} {algorithm} quiet"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=r"c:\Users\user\Documents\Adelaide University\Semester 2\Operating System\Assignment 2")
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            
            # 解析輸出
            total_frames = int(lines[0].split(': ')[1])
            events = int(lines[1].split(': ')[1])
            disk_reads = int(lines[2].split(': ')[1])
            disk_writes = int(lines[3].split(': ')[1])
            page_fault_rate = float(lines[4].split(': ')[1])
            
            return {
                'trace': trace_file,
                'frames': frames,
                'algorithm': algorithm, 
                'total_frames': total_frames,
                'events': events,
                'disk_reads': disk_reads,
                'disk_writes': disk_writes,
                'page_fault_rate': page_fault_rate,
                'page_faults': int(page_fault_rate * events)
            }
        else:
            print(f"Error running {cmd}: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Exception running {cmd}: {e}")
        return None

def main():
    # 定義測試參數
    trace_files = [
        'trace/bzip.trace',
        'trace/swim.trace', 
        'trace/gcc.trace',
        'trace/sixpack.trace'
    ]
    
    algorithms = ['lru', 'clock', 'rand']
    
    # 定義各trace的測試frame範圍
    frame_sets = {
        'trace/bzip.trace': [10, 20, 50, 100, 200, 300, 400, 500],
        'trace/swim.trace': [10, 20, 50, 100, 500, 1000, 2000, 3000],
        'trace/gcc.trace': [10, 20, 50, 100, 1000, 2000, 3000, 4000, 5000],
        'trace/sixpack.trace': [10, 20, 50, 100, 1000, 2000, 3000, 4000, 5000]
    }
    
    results = []
    total_experiments = sum(len(frame_sets[trace]) * len(algorithms) for trace in trace_files)
    current = 0
    
    print(f"開始執行 {total_experiments} 個實驗...")
    
    # 執行所有實驗
    for trace in trace_files:
        for frames in frame_sets[trace]:
            for algorithm in algorithms:
                current += 1
                print(f"進度 {current}/{total_experiments}: {trace} {frames} frames {algorithm}")
                
                result = run_simulation(trace, frames, algorithm)
                if result:
                    results.append(result)
                else:
                    print(f"實驗失敗: {trace} {frames} {algorithm}")
    
    # 儲存結果到CSV
    output_file = 'experiment_results.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['trace', 'frames', 'algorithm', 'total_frames', 'events', 
                     'disk_reads', 'disk_writes', 'page_fault_rate', 'page_faults']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"\n實驗完成！結果已儲存到 {output_file}")
    print(f"總共收集了 {len(results)} 個數據點")

if __name__ == "__main__":
    main()