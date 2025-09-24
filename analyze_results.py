#!/usr/bin/env python3
"""
增強版數據分析和圖表生成腳本
修復matplotlib問題並生成高品質圖表
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 使用非GUI後端
import matplotlib.pyplot as plt
import numpy as np

def create_performance_plots_enhanced(df):
    """為每個trace創建增強版性能比較圖"""
    
    # 設定matplotlib樣式
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = (15, 10)
    plt.rcParams['font.size'] = 10
    
    traces = df['trace'].unique()
    algorithms = df['algorithm'].unique()
    colors = {'lru': '#1f77b4', 'clock': '#ff7f0e', 'rand': '#2ca02c'}
    markers = {'lru': 'o', 'clock': 's', 'rand': '^'}
    
    for trace in traces:
        trace_name = trace.split('/')[-1].replace('.trace', '')
        trace_data = df[df['trace'] == trace]
        
        # 創建2x2子圖
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'{trace_name.upper()} - Page Replacement Algorithm Performance', fontsize=16, fontweight='bold')
        
        # 子圖1: Page Fault Rate vs Frames
        for alg in algorithms:
            alg_data = trace_data[trace_data['algorithm'] == alg].sort_values('frames')
            if not alg_data.empty:
                ax1.plot(alg_data['frames'], alg_data['page_fault_rate'], 
                        marker=markers[alg], linewidth=2, markersize=6,
                        label=alg.upper(), color=colors[alg])
        
        ax1.set_xlabel('Memory Frames')
        ax1.set_ylabel('Page Fault Rate')
        ax1.set_title('Page Fault Rate vs Memory Frames')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 設定詳細的x軸刻度
        frame_values = sorted(trace_data['frames'].unique())
        ax1.set_xticks(frame_values[::max(1, len(frame_values)//10)])  # 顯示約10個刻度
        ax1.tick_params(axis='x', rotation=45)
        
        # y軸用對數但設定詳細刻度
        ax1.set_yscale('log')
        y_values = trace_data['page_fault_rate'].values
        y_min, y_max = y_values.min(), y_values.max()
        ax1.set_ylim(y_min*0.5, y_max*2)
        
        # 子圖2: Disk Reads vs Frames
        for alg in algorithms:
            alg_data = trace_data[trace_data['algorithm'] == alg].sort_values('frames')
            if not alg_data.empty:
                ax2.plot(alg_data['frames'], alg_data['disk_reads'], 
                        marker=markers[alg], linewidth=2, markersize=6,
                        label=alg.upper(), color=colors[alg])
        
        ax2.set_xlabel('Memory Frames')
        ax2.set_ylabel('Disk Reads')
        ax2.set_title('Disk Reads vs Memory Frames')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 設定詳細的x軸刻度
        ax2.set_xticks(frame_values[::max(1, len(frame_values)//10)])
        ax2.tick_params(axis='x', rotation=45)
        
        # y軸用對數但設定詳細刻度
        ax2.set_yscale('log')
        y_reads = trace_data['disk_reads'].values
        y_min, y_max = y_reads.min(), y_reads.max()
        ax2.set_ylim(y_min*0.5, y_max*2)
        
        # 子圖3: Disk Writes vs Frames
        for alg in algorithms:
            alg_data = trace_data[trace_data['algorithm'] == alg].sort_values('frames')
            if not alg_data.empty:
                ax3.plot(alg_data['frames'], alg_data['disk_writes'], 
                        marker=markers[alg], linewidth=2, markersize=6,
                        label=alg.upper(), color=colors[alg])
        
        ax3.set_xlabel('Memory Frames')
        ax3.set_ylabel('Disk Writes')
        ax3.set_title('Disk Writes vs Memory Frames')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 設定詳細的x軸刻度
        ax3.set_xticks(frame_values[::max(1, len(frame_values)//10)])  
        ax3.tick_params(axis='x', rotation=45)
        
        # y軸用對數但設定詳細刻度
        ax3.set_yscale('log')
        y_writes = trace_data['disk_writes'].values
        y_writes = y_writes[y_writes > 0]  # 排除0值避免log錯誤
        if len(y_writes) > 0:
            y_min, y_max = y_writes.min(), y_writes.max()
            ax3.set_ylim(max(1, y_min*0.5), y_max*2)
        
        # 子圖4: 演算法效能排名熱圖
        frame_counts = sorted(trace_data['frames'].unique())
        ranking_data = []
        
        for frames in frame_counts:
            frame_data = trace_data[trace_data['frames'] == frames].copy()
            if len(frame_data) >= 3:
                frame_data = frame_data.sort_values('page_fault_rate')
                for i, (_, row) in enumerate(frame_data.iterrows()):
                    ranking_data.append({
                        'frames': frames,
                        'algorithm': row['algorithm'],
                        'rank': i + 1,
                        'page_fault_rate': row['page_fault_rate']
                    })
        
        if ranking_data:
            rank_df = pd.DataFrame(ranking_data)
            pivot_table = rank_df.pivot(index='algorithm', columns='frames', values='rank')
            
            im = ax4.imshow(pivot_table.values, cmap='RdYlGn_r', aspect='auto', vmin=1, vmax=3)
            ax4.set_xticks(range(len(pivot_table.columns)))
            ax4.set_xticklabels(pivot_table.columns, rotation=45)
            ax4.set_yticks(range(len(pivot_table.index)))
            ax4.set_yticklabels([alg.upper() for alg in pivot_table.index])
            ax4.set_title('Algorithm Ranking Heatmap\\n(1=Best, 3=Worst)')
            ax4.set_xlabel('Memory Frames')
            
            # 添加數值標註
            for i in range(len(pivot_table.index)):
                for j in range(len(pivot_table.columns)):
                    if not pd.isna(pivot_table.iloc[i, j]):
                        ax4.text(j, i, f'{int(pivot_table.iloc[i, j])}', 
                                ha='center', va='center', fontweight='bold')
            
            # 添加顏色條
            cbar = plt.colorbar(im, ax=ax4, shrink=0.8)
            cbar.set_label('Ranking')
        
        plt.tight_layout()
        filename = f'performance_png/{trace_name}_detailed_performance.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"已保存 {filename}")

def analyze_data_detailed():
    """詳細分析實驗數據"""
    
    try:
        df = pd.read_csv('experiment_results.csv')
        print(f"成功載入 {len(df)} 筆實驗數據")
    except FileNotFoundError:
        print("找不到 experiment_results.csv，請先執行實驗")
        return None
    
    print("\\n=== 測試範圍統計 ===")
    
    traces = df['trace'].unique()
    for trace in traces:
        trace_name = trace.split('/')[-1].replace('.trace', '')
        trace_data = df[df['trace'] == trace]
        frame_counts = sorted(trace_data['frames'].unique())
        
        print(f"\\n{trace_name.upper()}:")
        print(f"  測試點數: {len(frame_counts)}")
        print(f"  Frame範圍: {min(frame_counts)} - {max(frame_counts)}")
        print(f"  測試點: {frame_counts}")
    
    # 生成增強圖表
    create_performance_plots_enhanced(df)
    
    return df

def main():
    """主函數"""
    print("開始詳細分析實驗數據...")
    
    df = analyze_data_detailed()
    if df is not None:
        print("\\n數據分析和圖表生成完成！")
        print("\\n生成的圖表文件:")
        traces = df['trace'].unique()
        for trace in traces:
            trace_name = trace.split('/')[-1].replace('.trace', '')
            print(f"  - {trace_name}_detailed_performance.png")

if __name__ == "__main__":
    main()