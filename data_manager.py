import pandas as pd
import os
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "trades.xlsx")

import uuid

def load_data():
    """从 Excel 文件加载交易数据。如果不存在则创建。"""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "ID", "代码", "名称", "买入日期", "买入价格", "买入数量", 
            "卖出日期", "卖出价格", "卖出数量", "位置", "战法", 
            "操作", "两点印证", "备注", "盈亏", "盈亏比例"
        ])
        return df
    try:
        df = pd.read_excel(DATA_FILE)
        # 迁移旧列名
        if "印证" in df.columns and "两点印证" not in df.columns:
             df.rename(columns={"印证": "两点印证"}, inplace=True)
             df.to_excel(DATA_FILE, index=False)
        
        # 确保 ID 列存在
        if "ID" not in df.columns:
            df["ID"] = [str(uuid.uuid4()) for _ in range(len(df))]
            df.to_excel(DATA_FILE, index=False)
        # 确保 ID 为字符串类型
        df["ID"] = df["ID"].astype(str)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def _calculate_pnl(row):
    """辅助函数：计算单行数据的盈亏。"""
    if pd.notna(row.get("卖出价格")) and pd.notna(row.get("卖出数量")):
        try:
            buy_cost = float(row["买入价格"]) * int(row["买入数量"])
            sell_revenue = float(row["卖出价格"]) * int(row["卖出数量"])
            pnl = sell_revenue - buy_cost
            pnl_percent = (pnl / buy_cost) * 100 if buy_cost != 0 else 0
            return pnl, pnl_percent
        except (ValueError, TypeError):
            pass
    return None, None

def save_trade(trade_data):
    """将新交易保存到 Excel 文件。"""
    df = load_data()
    
    # 生成 ID
    trade_data["ID"] = str(uuid.uuid4())
    
    # 计算盈亏
    pnl, pnl_percent = _calculate_pnl(trade_data)
    if pnl is not None:
        trade_data["盈亏"] = pnl
        trade_data["盈亏比例"] = pnl_percent
    
    new_row = pd.DataFrame([trade_data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)
    return True

def update_trade(trade_id, updated_data):
    """更新现有交易。"""
    df = load_data()
    if "ID" not in df.columns:
        return False
    
    idx = df[df["ID"] == trade_id].index
    if len(idx) == 0:
        return False
    
    # 更新字段
    for key, value in updated_data.items():
        df.at[idx[0], key] = value
        
    # 重新计算该行的盈亏
    row = df.iloc[idx[0]].to_dict()
    pnl, pnl_percent = _calculate_pnl(row)
    df.at[idx[0], "盈亏"] = pnl
    df.at[idx[0], "盈亏比例"] = pnl_percent

    df.to_excel(DATA_FILE, index=False)
    return True

def delete_trade(trade_id):
    """根据 ID 删除交易。"""
    df = load_data()
    if "ID" not in df.columns:
        return False
    
    df = df[df["ID"] != trade_id]
    df.to_excel(DATA_FILE, index=False)
    return True

def get_stock_name(code):
    """从新浪 API 获取股票名称。"""
    if not code:
        return ""
    
    # 简单的市场前缀判断逻辑
    if code.startswith("6"):
        code_with_prefix = f"sh{code}"
    elif code.startswith("0") or code.startswith("3"):
        code_with_prefix = f"sz{code}"
    elif code.startswith("4") or code.startswith("8"): # 通常是北交所
         code_with_prefix = f"bj{code}"
    else:
        code_with_prefix = f"sh{code}" # 默认回退

    url = f"http://hq.sinajs.cn/list={code_with_prefix}"
    try:
        headers = {"Referer": "https://finance.sina.com.cn"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.text
            # 格式: var hq_str_sh600519="贵州茅台,..."
            if '="' in content:
                data = content.split('="')[1]
                # 检查数据是否以引号开头（通常是空响应）
                if data and not data.startswith('"'):
                    name = data.split(',')[0]
                    return name
    except Exception as e:
        print(f"Error fetching stock name: {e}")
    return "未知股票"
