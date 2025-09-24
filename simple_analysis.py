#!/usr/bin/env python3
"""
簡化版數據分析腳本 - 只輸出統計數據，不生成圖表
"""

import pandas as pd

def analyze_data():
    """分析實驗數據並輸出統計結果"""
    
    # 載入數據
    try:
        df = pd.read_csv('experiment_results.csv')
        print(f"成功載入 {len(df)} 筆實驗數據")
    except FileNotFoundError:
        print("找不到 experiment_results.csv，請先執行實驗")
        return
    
    print("\n=== 基本統計 ===")
    traces = df['trace'].unique()
    algorithms = df['algorithm'].unique()
    
    print(f"Trace檔案: {len(traces)} 個")
    print(f"演算法: {list(algorithms)}")
    print(f"總實驗數: {len(df)} 個")
    
    print("\n=== 各程式記憶體需求分析 ===")
    
    for trace in traces:
        trace_name = trace.split('/')[-1].replace('.trace', '')
        trace_data = df[df['trace'] == trace]
        
        print(f"\n{trace_name.upper()}:")
        
        # 找出最大frame數下的表現（接近實際需求）
        max_frames = trace_data['frames'].max()
        high_memory = trace_data[trace_data['frames'] == max_frames]
        
        for alg in algorithms:
            alg_data = high_memory[high_memory['algorithm'] == alg]
            if not alg_data.empty:
                pf_rate = alg_data['page_fault_rate'].iloc[0]
                disk_reads = alg_data['disk_reads'].iloc[0]
                page_faults = alg_data['page_faults'].iloc[0]
                print(f"  {alg.upper()} ({max_frames} frames): "
                      f"PF率={pf_rate:.4f}, Page faults={page_faults}, "
                      f"約需 {page_faults} 頁 ({page_faults*4:.1f}KB)")
        
        print("\n  各frame數下的最佳演算法:")
        for frames in sorted(trace_data['frames'].unique()):
            frame_data = trace_data[trace_data['frames'] == frames].copy()
            if len(frame_data) >= 3:
                frame_data = frame_data.sort_values('page_fault_rate')
                best = frame_data.iloc[0]
                worst = frame_data.iloc[-1]
                print(f"    {frames:4d} frames: 最佳={best['algorithm'].upper()}"
                      f"({best['page_fault_rate']:.4f}), "
                      f"最差={worst['algorithm'].upper()}"
                      f"({worst['page_fault_rate']:.4f})")

    print("\n=== 演算法整體表現排名 ===")
    
    # 計算各演算法的平均排名
    algorithm_scores = {alg: [] for alg in algorithms}
    
    for trace in traces:
        trace_data = df[df['trace'] == trace]
        for frames in trace_data['frames'].unique():
            frame_data = trace_data[trace_data['frames'] == frames].copy()
            if len(frame_data) >= 3:  # 確保三種演算法都有數據
                frame_data = frame_data.sort_values('page_fault_rate')
                for i, (_, row) in enumerate(frame_data.iterrows()):
                    algorithm_scores[row['algorithm']].append(i + 1)
    
    print("平均排名 (1=最好, 3=最差):")
    for alg in algorithms:
        if algorithm_scores[alg]:
            avg_rank = sum(algorithm_scores[alg]) / len(algorithm_scores[alg])
            print(f"  {alg.upper()}: {avg_rank:.2f}")
    
    print("\n=== 記憶體限制影響分析 ===")
    
    for trace in traces:
        trace_name = trace.split('/')[-1].replace('.trace', '')
        trace_data = df[df['trace'] == trace]
        
        print(f"\n{trace_name.upper()} - 記憶體限制 vs 性能:")
        
        # 比較不同記憶體大小下的性能差異
        frames_list = sorted(trace_data['frames'].unique())
        min_frames = min(frames_list)
        max_frames = max(frames_list)
        
        for alg in algorithms:
            min_data = trace_data[(trace_data['frames'] == min_frames) & 
                                 (trace_data['algorithm'] == alg)]
            max_data = trace_data[(trace_data['frames'] == max_frames) & 
                                 (trace_data['algorithm'] == alg)]
            
            if not min_data.empty and not max_data.empty:
                min_pf = min_data['page_fault_rate'].iloc[0]
                max_pf = max_data['page_fault_rate'].iloc[0]
                improvement = (min_pf - max_pf) / min_pf * 100
                
                print(f"  {alg.upper()}: {min_frames}框={min_pf:.4f} → "
                      f"{max_frames}框={max_pf:.4f} "
                      f"(改善{improvement:.1f}%)")

if __name__ == "__main__":
    analyze_data()