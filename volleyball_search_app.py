# -*- coding: utf-8 -*-
# 台灣排球數據分析 Streamlit 應用程式 - 企業聯賽多賽季採集框架

import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
import io

# ⚠️ 警告：爬蟲代碼未實作，此處為結構框架。

# ====================================================================
# I. 數據模型與爬蟲指引
# ====================================================================

# 定義目標賽季
VLEAGUE_SEASONS = {
    '企業二十年 (2025-2026)': 'URL_PATTERN_20', # 假設未來的賽季
    '企業十九年 (2024-2025)': 'URL_PATTERN_19', # 假設未來的賽季
    '企業十八年 (2023-2024)': 'URL_PATTERN_18', # 根據實際網站填寫
    '企業十七年 (2022-2023)': 'URL_PATTERN_17', # 根據實際網站填寫
}

# 定義所有需要的數據欄位
VOLLEYBALL_STATS_COLUMNS = [
    '姓名', '隊伍', '位置', '身高(cm)', '體重(kg)', '上場局數', 
    '攻擊得分', '攻擊失誤', '攻擊次數', 
    '攔網得分', '發球得分', '發球失誤', 
    '接發成功率'
]

# --- 數據分析函數 (保持不變，用於計算效率) ---
def calculate_efficiency(df):
    """計算排球員的關鍵效率指標。"""
    
    numeric_cols = ['攻擊得分', '攻擊失誤', '攻擊次數', '攔網得分', '發球得分', '發球失誤', '上場局數', '身高(cm)', '體重(kg)']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['攻擊成功率(%)'] = ((df['攻擊得分'] - df['攻擊失誤']) / df['攻擊次數'] * 100).fillna(0).round(2)
    df['總得分'] = df['攻擊得分'] + df['攔網得分'] + df['發球得分']
    df['總失誤'] = df['攻擊失誤'] + df['發球失誤']
    df['淨得分'] = df['總得分'] - df['總失誤']
    df['場均淨得分'] = (df['淨得分'] / df['上場局數']).replace([float('inf'), -float('inf')], 0).fillna(0).round(2)
    
    return df

def analyze_player_role(stats):
    """根據關鍵數據指標分析球員類型。 (保持不變)"""
    if isinstance(stats, pd.DataFrame): stats = stats.iloc[0]
    if stats['上場局數'] == 0: return "該球員無數據或未上場。"
        
    avg_attack_score = stats['攻擊得分'] / stats['上場局數']
    avg_block_score = stats['攔網得分'] / stats['上場局數']
    attack_success_rate = stats['攻擊成功率(%)']
    position = stats['位置']
    
    if avg_attack_score > 5 and attack_success_rate >= 40:
        return "🔥 **高效得分機器**：主要進攻點，火力強勁且效率極高。"
    elif avg_block_score >= 1 and position == '副攻':
        return "🧱 **優秀攔網中樞**：主要貢獻來自攔網，是球隊防守的堅實後盾。"
    elif position == '自由球員' and stats.get('接發成功率', 0) >= 65: # 使用 .get 處理可能缺少的欄位
        return "🛡️ **後排指揮官**：確保一傳穩定，是戰術發動的核心。"
    else:
        return "可靠的輪換或特定戰術球員。"


# ====================================================================
# II. 企業聯賽數據爬蟲 (核心實作區)
# ====================================================================

@st.cache_data(ttl=3600)
def fetch_and_merge_stats(season_id):
    """
    此函數負責協調爬蟲並合併數據。
    
    步驟 1: 爬取名單數據 (Roster)
    步驟 2: 爬取統計數據 (Stats)
    步驟 3: 合併數據 (Merge)
    """
    
    # -----------------------------------------------------------
    # ⚠️ 實作區塊 1: 名單數據爬蟲 (身高, 體重, 位置)
    # -----------------------------------------------------------
    st.info(f"步驟 1/3: 採集 {season_id} 球員名單中...")
    
    # URL 範例: 找到該賽季男子組所有隊伍名單頁
    # roster_url = VLEAGUE_SEASONS[season_id] + "/men_roster.html" 
    
    # 假設您爬取成功並返回一個 DataFrame
    # 需包含: 姓名, 隊伍, 位置, 身高(cm), 體重(kg), 接發成功率(選填)
    roster_df = pd.DataFrame({
        '姓名': ['李X志', '陳X杰', '高X林'], 
        '隊伍': ['台電', '長力', '雲林美津濃'], 
        '位置': ['主攻', '接應', '副攻'], 
        '身高(cm)': [185, 190, 198], 
        '體重(kg)': [75, 80, 90], 
        '接發成功率': [60, 55, 10]
    })
    
    # -----------------------------------------------------------
    # ⚠️ 實作區塊 2: 統計數據爬蟲 (得分, 效率)
    # -----------------------------------------------------------
    st.info(f"步驟 2/3: 採集 {season_id} 統計數據中...")
    
    # stats_url = VLEAGUE_SEASONS[season_id] + "/men_stats_player.html"
    
    # 假設您爬取成功並返回一個 DataFrame
    # 需包含: 姓名, 上場局數, 攻擊得分, 攻擊失誤, 攻擊次數, 攔網得分, 發球得分, 發球失誤
    stats_df = pd.DataFrame({
        '姓名': ['李X志', '陳X杰', '高X林'],
        '上場局數': [35, 40, 38],
        '攻擊得分': [150, 220, 90],
        '攻擊失誤': [10, 20, 5],
        '攻擊次數': [400, 550, 180],
        '攔網得分': [15, 10, 45],
        '發球得分': [5, 8, 2],
        '發球失誤': [8, 12, 4]
    })
    
    if roster_df.empty or stats_df.empty:
        return None

    # -----------------------------------------------------------
    # 步驟 3: 合併數據
    # -----------------------------------------------------------
    st.info("步驟 3/3: 合併名單與統計數據...")
    
    # 使用 '姓名' 作為合併鍵 (確保姓名是唯一且準確的)
    final_df = pd.merge(roster_df, stats_df, on='姓名', how='inner')
    
    # 確保所有需要的列都存在，如果不存在，則補上 0 (例如接發成功率可能只在名單爬蟲中)
    missing_cols = [col for col in VOLLEYBALL_STATS_COLUMNS if col not in final_df.columns]
    for col in missing_cols:
        final_df[col] = 0
    
    return final_df[VOLLEYBALL_STATS_COLUMNS]


# ====================================================================
# III. Streamlit 界面邏輯
# ====================================================================

st.set_page_config(layout="wide", page_title="台灣企業排球聯賽男子組數據")
st.title("🏐 企業排球聯賽男子組數據分析儀表板 (企業 17-20 年)")

# --- 側邊欄: 數據獲取參數 ---
with st.sidebar:
    st.header("數據獲取參數")
    
    # 賽季選擇
    selected_season = st.selectbox(
        "選擇企業聯賽賽季:",
        options=list(VLEAGUE_SEASONS.keys()),
        index=3, # 預設選擇企業十七年
        key='vleague_season'
    )
    
    st.subheader("目標組別: 男子組 🧑‍🤝‍🧑")
    
    if st.button("🔄 採集並分析數據"):
        # 呼叫爬蟲函數
        vleague_df = fetch_and_merge_stats(selected_season)
        
        if vleague_df is not None and not vleague_df.empty:
            st.session_state['volleyball_df'] = vleague_df
            st.success(f"成功處理 {selected_season} 男子組的 {len(vleague_df)} 筆數據。")
        else:
            st.error("無法獲取該賽季數據。請檢查爬蟲函數是否需要更新或該賽季數據不存在。")
            st.session_state['volleyball_df'] = pd.DataFrame(columns=VOLLEYBALL_STATS_COLUMNS)

# --- 主區域: 數據處理與結果顯示 ---

if 'volleyball_df' not in st.session_state or st.session_state['volleyball_df'].empty:
    st.warning("請在左側邊欄選擇賽季，並點擊 **採集並分析數據**。")
else:
    current_df = st.session_state['volleyball_df'].copy()
    processed_df = calculate_efficiency(current_df)

    st.subheader(f"📊 {st.session_state['vleague_season']} 男子組球員總體效率排名")
    
    # 顯示欄位順序
    display_cols = ['姓名', '隊伍', '位置', '身高(cm)', '體重(kg)', '總得分', '淨得分', '場均淨得分', '攻擊成功率(%)', '接發成功率']
    
    st.dataframe(
        processed_df.sort_values(by='場均淨得分', ascending=False), 
        use_container_width=True,
        column_order=[col for col in display_cols if col in processed_df.columns],
        column_config={
            "攻擊成功率(%)": st.column_config.ProgressColumn("攻擊成功率", format="%.2f%%", min_value=0, max_value=60),
            "場均淨得分": st.column_config.NumberColumn("場均貢獻度", format="%.2f"),
            "接發成功率": st.column_config.ProgressColumn("接發成功率", format="%.0f%%", min_value=0, max_value=100),
            "總得分": "總得分", "淨得分": "淨得分", "身高(cm)": "身高", "體重(kg)": "體重"
        }
    )

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
