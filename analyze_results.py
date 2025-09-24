#!/usr/bin/env python3
"""
數據分析和圖表生成腳本
從experiment_results.csv讀取數據，生成報告所需的圖表
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 使用非GUI後端
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def load_and_analyze_data(csv_file='experiment_results.csv'):
    """載入並分析實驗數據"""
    try:
        df = pd.read_csv(csv_file)
        print(f"成功載入 {len(df)} 筆實驗數據")
        return df
    except FileNotFoundError:
        print(f"找不到 {csv_file}，請先執行實驗")
        return None

def create_performance_plots(df):
    """為每個trace創建性能比較圖"""
    
    # 設定matplotlib支援中文
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    traces = df['trace'].unique()
    algorithms = df['algorithm'].unique()
    
    # 為每個trace創建圖表
    for trace in traces:
        trace_name = trace.split('/')[-1].replace('.trace', '')
        trace_data = df[df['trace'] == trace]
        
        plt.figure(figsize=(12, 8))
        
        # 子圖1: Page Fault Rate vs Frames
        plt.subplot(2, 2, 1)
        for alg in algorithms:
            alg_data = trace_data[trace_data['algorithm'] == alg]
            plt.plot(alg_data['frames'], alg_data['page_fault_rate'], 
                    marker='o', linewidth=2, label=alg.upper())
        
        plt.xlabel('Memory Frames')
        plt.ylabel('Page Fault Rate')
        plt.title(f'{trace_name.upper()}: Page Fault Rate vs Memory Frames')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.yscale('log')
        
        # 子圖2: Disk Reads vs Frames
        plt.subplot(2, 2, 2)
        for alg in algorithms:
            alg_data = trace_data[trace_data['algorithm'] == alg]
            plt.plot(alg_data['frames'], alg_data['disk_reads'], 
                    marker='s', linewidth=2, label=alg.upper())
        
        plt.xlabel('Memory Frames')
        plt.ylabel('Disk Reads')
        plt.title(f'{trace_name.upper()}: Disk Reads vs Memory Frames')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.yscale('log')
        
        # 子圖3: Disk Writes vs Frames
        plt.subplot(2, 2, 3)
        for alg in algorithms:
            alg_data = trace_data[trace_data['algorithm'] == alg]
            plt.plot(alg_data['frames'], alg_data['disk_writes'], 
                    marker='^', linewidth=2, label=alg.upper())
        
        plt.xlabel('Memory Frames')
        plt.ylabel('Disk Writes')
        plt.title(f'{trace_name.upper()}: Disk Writes vs Memory Frames')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 子圖4: Total I/O Operations vs Frames
        plt.subplot(2, 2, 4)
        for alg in algorithms:
            alg_data = trace_data[trace_data['algorithm'] == alg]
            total_io = alg_data['disk_reads'] + alg_data['disk_writes']
            plt.plot(alg_data['frames'], total_io, 
                    marker='d', linewidth=2, label=alg.upper())
        
        plt.xlabel('Memory Frames')
        plt.ylabel('Total I/O Operations')
        plt.title(f'{trace_name.upper()}: Total I/O vs Memory Frames')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.yscale('log')
        
        plt.tight_layout()
        plt.savefig(f'{trace_name}_performance.png', dpi=300, bbox_inches='tight')
        plt.close()  # 關閉圖表釋放記憶體
        
        print(f"已保存 {trace_name}_performance.png")

def generate_summary_table(df):
    """生成摘要統計表"""
    
    print("\n=== 實驗結果摘要 ===")
    
    for trace in df['trace'].unique():
        trace_name = trace.split('/')[-1].replace('.trace', '')
        trace_data = df[df['trace'] == trace]
        
        print(f"\n{trace_name.upper()} 程式:")
        
        # 找出在大記憶體下的最佳性能（當作基準）
        high_memory = trace_data[trace_data['frames'] == trace_data['frames'].max()]
        min_page_faults = high_memory['page_faults'].min()
        
        print(f"  大記憶體下最少page faults: {min_page_faults}")
        
        # 各演算法在不同記憶體限制下的表現
        for frames in sorted(trace_data['frames'].unique()):
            frame_data = trace_data[trace_data['frames'] == frames]
            print(f"\n  {frames} frames:")
            
            for alg in ['lru', 'clock', 'rand']:
                alg_data = frame_data[frame_data['algorithm'] == alg]
                if not alg_data.empty:
                    pf_rate = alg_data['page_fault_rate'].iloc[0]
                    disk_reads = alg_data['disk_reads'].iloc[0]
                    disk_writes = alg_data['disk_writes'].iloc[0]
                    print(f"    {alg.upper()}: PF率={pf_rate:.4f}, 讀={disk_reads}, 寫={disk_writes}")

def analyze_algorithm_performance(df):
    """分析各演算法的相對性能"""
    
    print("\n=== 演算法性能分析 ===")
    
    # 計算各演算法的平均排名
    algorithm_rankings = {}
    
    for trace in df['trace'].unique():
        trace_name = trace.split('/')[-1].replace('.trace', '')
        trace_data = df[df['trace'] == trace]
        
        print(f"\n{trace_name.upper()}:")
        
        for frames in sorted(trace_data['frames'].unique()):
            frame_data = trace_data[trace_data['frames'] == frames].copy()
            
            if len(frame_data) >= 3:  # 確保三種演算法都有數據
                # 按page fault rate排序
                frame_data = frame_data.sort_values('page_fault_rate')
                
                print(f"  {frames} frames 排名:")
                for i, (_, row) in enumerate(frame_data.iterrows()):
                    alg = row['algorithm']
                    pf_rate = row['page_fault_rate']
                    print(f"    第{i+1}名: {alg.upper()} (PF率={pf_rate:.4f})")
                    
                    # 記錄排名用於統計
                    if alg not in algorithm_rankings:
                        algorithm_rankings[alg] = []
                    algorithm_rankings[alg].append(i+1)
    
    # 計算平均排名
    print(f"\n平均排名 (1=最好, 3=最差):")
    for alg in ['lru', 'clock', 'rand']:
        if alg in algorithm_rankings:
            avg_rank = np.mean(algorithm_rankings[alg])
            print(f"  {alg.upper()}: {avg_rank:.2f}")

def main():
    """主函數"""
    print("開始分析實驗數據...")
    
    # 載入數據
    df = load_and_analyze_data()
    if df is None:
        return
    
    # 生成性能圖表  
    create_performance_plots(df)
    
    # 生成摘要表
    generate_summary_table(df)
    
    # 演算法性能分析
    analyze_algorithm_performance(df)
    
    print("\n數據分析完成！")

if __name__ == "__main__":
    main()