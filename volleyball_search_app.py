# -*- coding: utf-8 -*-
# 台灣排球數據分析 Streamlit 應用程式 - 企業聯賽男子組增強版

import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
import io

# ====================================================================
# I. 數據模型與爬蟲指引
# ====================================================================

# 定義排球員數據的基礎結構 (新增 身高、體重)
VOLLEYBALL_STATS_COLUMNS = [
    '姓名', '隊伍', '位置', '身高(cm)', '體重(kg)', '上場局數', 
    '攻擊得分', '攻擊失誤', '攻擊次數', 
    '攔網得分', '發球得分', '發球失誤', 
    '接發成功率' # 這通常是自由球員和主攻手數據，其他位置可能為 N/A
]

# 爬蟲所需的 URL 示例 (您需要根據實際排協網站替換)
VLEAGUE_BASE_URL = "https://www.ctvba.org.tw/vleague" # 假設的排協聯賽頁面

# --- 數據計算與分析邏輯 (保持不變) ---
def calculate_efficiency(df):
    """計算排球員的關鍵效率指標。"""
    
    # 確保所有數值列為數值型態，並處理潛在的除零錯誤
    numeric_cols = ['攻擊得分', '攻擊失誤', '攻擊次數', '攔網得分', '發球得分', '發球失誤', '上場局數', '身高(cm)', '體重(kg)']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 攻擊成功率
    df['攻擊成功率(%)'] = ((df['攻擊得分'] - df['攻擊失誤']) / df['攻擊次數'] * 100).fillna(0).round(2)
    
    # 總得分, 總失誤, 淨得分, 場均淨得分
    df['總得分'] = df['攻擊得分'] + df['攔網得分'] + df['發球得分']
    df['總失誤'] = df['攻擊失誤'] + df['發球失誤']
    df['淨得分'] = df['總得分'] - df['總失誤']
    df['場均淨得分'] = (df['淨得分'] / df['上場局數']).replace([float('inf'), -float('inf')], 0).fillna(0).round(2)
    
    return df

def analyze_player_role(stats):
    """根據關鍵數據指標分析球員類型。 (保持不變)"""
    if isinstance(stats, pd.DataFrame):
        stats = stats.iloc[0]

    if stats['上場局數'] == 0:
        return "該球員無數據或未上場。"
        
    avg_attack_score = stats['攻擊得分'] / stats['上場局數']
    avg_block_score = stats['攔網得分'] / stats['上場局數']
    attack_success_rate = stats['攻擊成功率(%)']
    position = stats['位置']
    
    # 根據場均表現判斷
    if avg_attack_score > 5 and attack_success_rate >= 40:
        return "🔥 **高效得分機器**：主要進攻點，火力強勁且效率極高。"
    elif avg_block_score >= 1 and position == '副攻':
        return "🧱 **優秀攔網中樞**：主要貢獻來自攔網，是球隊防守的堅實後盾。"
    elif position == '自由球員' and stats['接發成功率'] >= 65:
        return "🛡️ **後排指揮官**：確保一傳穩定，是戰術發動的核心。"
    else:
        return "可靠的輪換或特定戰術球員。"

# ====================================================================
# II. 企業聯賽數據爬蟲 (男子組)
# ====================================================================

@st.cache_data(ttl=3600)
def scrape_vleague_stats(season_id):
    """
    實作指引:
    1. 尋找 V. League 該賽季的球員名單頁面 (Roster Page)，爬取 姓名、隊伍、位置、身高、體重。
    2. 尋找 V. League 該賽季的球員統計數據頁面 (Stats Page)，爬取 攻擊、攔網、發球等得分。
    3. 根據球員姓名 (或背號) 將兩份數據表格 (DataFrame) 進行合併 (Merge)。
    """
    
    st.info(f"🚧 正在嘗試爬取 **企業聯賽 {season_id} 男子組** 數據...")
    
    # --- 假數據作為爬蟲成功前的示例 ---
    # 這些數據需要您爬取實際網站並替換
    if season_id == '企業十七年 (2022-2023)':
        roster_data = {
            '姓名': ['吳 X 軒', '陳 X 均', '林 X 豪'],
            '隊伍': ['台電', '連莊', '長力'],
            '位置': ['主攻', '副攻', '接應'],
            '身高(cm)': [190, 195, 185],
            '體重(kg)': [80, 88, 75],
            '接發成功率': [68, 10, 30]
        }
        stats_data = {
            '姓名': ['吳 X 軒', '陳 X 均', '林 X 豪'],
            '上場局數': [50, 45, 48],
            '攻擊得分': [250, 100, 220],
            '攻擊失誤': [15, 10, 25],
            '攻擊次數': [500, 200, 450],
            '攔網得分': [35, 50, 15],
            '發球得分': [12, 5, 6],
            '發球失誤': [18, 8, 15]
        }
    elif season_id == '企業十八年 (2023-2024)':
        roster_data = {
            '姓名': ['XXX', 'YYY', 'ZZZ'],
            '隊伍': ['臺北市', '新北市', '連莊'],
            '位置': ['主攻', '副攻', '自由球員'],
            '身高(cm)': [188, 192, 178],
            '體重(kg)': [78, 85, 70],
            '接發成功率': [55, 5, 75]
        }
        stats_data = {
            '姓名': ['XXX', 'YYY', 'ZZZ'],
            '上場局數': [30, 25, 40],
            '攻擊得分': [150, 80, 0],
            '攻擊失誤': [15, 5, 0],
            '攻擊次數': [300, 150, 0],
            '攔網得分': [20, 30, 0],
            '發球得分': [10, 2, 0],
            '發球失誤': [10, 5, 1]
        }
    else:
        return None
        
    # 將名單和統計數據合併 (這也是您在實作爬蟲後要做的關鍵步驟)
    df_roster = pd.DataFrame(roster_data)
    df_stats = pd.DataFrame(stats_data)
    
    if df_roster.empty or df_stats.empty:
        return None

    # 使用 '姓名' 作為鍵進行合併
    final_df = pd.merge(df_roster, df_stats, on='姓名', how='inner')
    
    # 確保列名順序與 VOLLEYBALL_STATS_COLUMNS 匹配
    required_cols = [c for c in VOLLEYBALL_STATS_COLUMNS if c in final_df.columns]
    
    return final_df[required_cols]

# ====================================================================
# III. Streamlit 界面邏輯
# ====================================================================

st.set_page_config(layout="wide", page_title="台灣排球數據分析 (男子組)")
st.title("🏐 企業排球聯賽男子組數據分析儀表板")

# --- 側邊欄: 數據獲取參數 ---
with st.sidebar:
    st.header("數據獲取參數")
    
    # 賽季選擇
    selected_season = st.selectbox(
        "選擇企業聯賽賽季:",
        options=[
            '企業十八年 (2023-2024)', 
            '企業十七年 (2022-2023)', 
            '企業十六年 (2021-2022)',
        ],
        key='vleague_season'
    )
    
    st.subheader("目標組別: 男子組 🧑‍🤝‍🧑")
    
    if st.button("🔄 獲取並分析數據"):
        # 呼叫爬蟲函數 (目前為假數據)
        with st.spinner(f"正在載入 {selected_season} 男子組數據..."):
            vleague_df = scrape_vleague_stats(selected_season)
        
        if vleague_df is not None and not vleague_df.empty:
            st.session_state['volleyball_df'] = vleague_df
            st.success(f"成功載入 {selected_season} 男子組的 {len(vleague_df)} 筆數據。")
        else:
            st.error("無法獲取該賽季數據。請檢查爬蟲是否需要更新或該賽季數據不存在。")
            st.session_state['volleyball_df'] = pd.DataFrame(columns=VOLLEYBALL_STATS_COLUMNS)

    st.markdown("---")
    st.caption("數據來源: 企業排球聯賽（需實作網頁爬蟲）")


# --- 主區域: 數據處理與結果顯示 ---

if 'volleyball_df' not in st.session_state or st.session_state['volleyball_df'].empty:
    st.warning("請在左側邊欄選擇賽季，並點擊獲取數據。")
else:
    current_df = st.session_state['volleyball_df'].copy()
    processed_df = calculate_efficiency(current_df)

    st.subheader(f"📊 {st.session_state['vleague_season']} 男子組球員效率排名")
    
    display_cols = ['姓名', '隊伍', '位置', '身高(cm)', '體重(kg)', '總得分', '淨得分', '場均淨得分', '攻擊成功率(%)', '接發成功率']
    
    st.dataframe(
        processed_df.sort_values(by='場均淨得分', ascending=False), 
        use_container_width=True,
        column_order=display_cols,
        column_config={
            "攻擊成功率(%)": st.column_config.ProgressColumn("攻擊成功率", format="%.2f%%", min_value=0, max_value=60),
            "場均淨得分": st.column_config.NumberColumn("場均貢獻度", format="%.2f"),
            "接發成功率": st.column_config.ProgressColumn("接發成功率", format="%.0f%%", min_value=0, max_value=100),
            "總得分": "總得分", "淨得分": "淨得分", "身高(cm)": "身高", "體重(kg)": "體重"
        }
    )

    # 2. 選擇球員進行深度分析
    st.markdown("---")
    st.subheader("🔍 單一球員角色分析")

    player_list = processed_df['姓名'].tolist()
    if player_list:
        selected_player_name = st.selectbox("選擇要分析的球員:", options=player_list)
        
        if selected_player_name:
            player_stats = processed_df[processed_df['姓名'] == selected_player_name].reset_index(drop=True)
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("位置", player_stats['位置'].iloc[0])
            col2.metric("身高/體重", f"{int(player_stats['身高(cm)'].iloc[0])}cm/{int(player_stats['體重(kg)'].iloc[0])}kg")
            col3.metric("場均貢獻度", player_stats['場均淨得分'].iloc[0])
            col4.metric("攻擊成功率", f"{player_stats['攻擊成功率(%)'].iloc[0]}%")
            col5.metric("總得分", player_stats['總得分'].iloc[0].astype(int))
            
            st.markdown(f"#### 🏐 {selected_player_name} 角色定位分析:")
            analysis_text = analyze_player_role(player_stats)
            st.markdown(f"> {analysis_text}")
