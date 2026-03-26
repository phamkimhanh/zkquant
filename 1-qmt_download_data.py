# -*- coding: utf-8 -*-
"""
A股数据下载脚本
使用akshare下载A股股票（600032）的历史数据
保存到本地CSV文件，供后续策略分析使用

注意：运行此脚本需要安装akshare库：pip install akshare
"""
import os
import pandas as pd
import akshare as ak


# 数据下载参数配置
STOCK_CODE = '600032'  # 浙江新能股票代码
STOCK_NAME = '浙江新能'
DATA_START = '20240101'   # 数据开始日期（需要足够的历史数据计算MACD）
DATA_END = '20251231'     # 数据结束日期


def download_stock_data():
    """
    下载股票历史数据并保存到CSV文件
    """
    print(f"开始下载股票数据")
    print(f"股票：{STOCK_NAME}({STOCK_CODE})")
    print(f"日期范围：{DATA_START} 至 {DATA_END}")
    print("-" * 60)

    try:
        # 使用akshare下载历史数据
        print("步骤1：使用akshare下载历史数据...")

        # 转换日期格式为akshare所需的格式
        start_date = pd.to_datetime(DATA_START).strftime('%Y%m%d')
        end_date = pd.to_datetime(DATA_END).strftime('%Y%m%d')

        # 获取历史数据（前复权）
        df = ak.stock_zh_a_hist(
            symbol=STOCK_CODE,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"  # 前复权
        )

        if df is None or len(df) == 0:
            print("错误：无法获取历史数据")
            return None

        # 重命名列以保持一致性
        df = df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume'
        })

        # 选择需要的列
        df = df[['date', 'open', 'close', 'high', 'low', 'volume']].copy()

        # 确保日期格式正确
        df['date'] = pd.to_datetime(df['date'])

        # 过滤掉无效数据
        df = df.dropna(subset=['date', 'close'])
        df = df.sort_values('date').reset_index(drop=True)
        
        print(f"成功获取 {len(df)} 条历史数据")
        print(f"数据日期范围：{df['date'].iloc[0].strftime('%Y-%m-%d')} 至 {df['date'].iloc[-1].strftime('%Y-%m-%d')}")

        # 步骤2：保存到CSV文件
        print("\n步骤2：保存数据到CSV文件...")
        output_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(output_dir, exist_ok=True)

        # 保存完整数据
        output_file = os.path.join(output_dir, f'{STOCK_CODE}_daily.csv')
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"数据已保存至：{output_file}")
        
        # 显示数据预览
        print("\n数据预览（前5行）：")
        print(df.head().to_string(index=False))
        print("\n数据预览（后5行）：")
        print(df.tail().to_string(index=False))
        
        # 显示数据统计
        print("\n数据统计信息：")
        print(f"  总记录数：{len(df)}")
        print(f"  收盘价范围：{df['close'].min():.2f} - {df['close'].max():.2f}")
        if 'volume' in df.columns:
            print(f"  成交量范围：{df['volume'].min():,.0f} - {df['volume'].max():,.0f}")
        
        return output_file
        
    except Exception as e:
        print(f"下载数据过程中发生错误：{e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = download_stock_data()
    
    if result:
        print("\n" + "=" * 60)
        print("数据下载完成!")
        print(f"数据文件：{result}")
        print("=" * 60)
        print("\n提示：现在可以运行 6b-macd_strategy_analysis.py 进行策略分析")
    else:
        print("\n数据下载失败，请检查错误信息。")
