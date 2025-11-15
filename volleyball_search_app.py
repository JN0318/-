# -*- coding: utf-8 -*-
# 台灣排球數據分析 Streamlit 應用程式 - 企業聯賽多賽季採集框架 (最終佈局整合版)

import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
import io
import random  # 引入 random 模組，修復 NameError

# ====================================================================
# I. 數據模型與爬蟲指引
# ====================================================================

# 定義目標賽季及其 URL 模式 (此處為假數據，需要替換為實際的 URL 模式)
VLEAGUE_SEASONS = {
    '企業二十年 (2025-2026)': 'https://vleague.ctvba.org.tw/20/', 
    '企業十九年 (2024-2025)': 'https://vleague.ctvba.org.tw/19/', 
    '企業十八年 (2023-2024)': 'https://vleague.ctvba.org.tw/18/', 
    '企業十七年 (2022-2023)': 'https://vleague.ctvba.org.tw/17/', 
}

# 定義所有需要的數據欄位
VOLLEYBALL_STATS_COLUMNS = [
    '姓名', '隊伍', '位置', '身高(cm)', '體重(kg)', '上場局數', 
    '攻擊得分', '攻擊失誤', '攻擊次數', 
    '攔網得分', '發球得分', '發球失誤', 
    '接發成功率'
]

# --- 數據計算與分析邏輯 ---
def calculate_efficiency(df):
    """計算排球員的關鍵效率指標。"""
    
    numeric_cols = ['攻擊得分', '攻擊失誤', '攻擊次數', '攔網得分', '發球得分', '發球失誤', '上場局數', '身高(cm)', '體重(kg)', '接發成功率']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['攻擊成功率(%)'] = ((df['攻擊得分'] - df['攻擊失誤']) / df['攻擊次數'] * 100).fillna(0).round(2)
    df['總得分'] = df['攻擊得分'] + df['攔網得分'] + df['發球得分']
    df['總失誤'] = df['攻擊失誤'] + df['發球失誤']
    df['淨得分'] = df['總得分'] - df['總失誤']
    df['場均淨得分'] = (df['淨得分'] / df['上場局數']).replace([float('inf'), -float('inf')], 0).fillna(0).round(2)
    
    return df

def analyze_player_role(stats):
    """根據關鍵數據指標分析球員類型。"""
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
    elif position == '自由球員' and stats.get('接發成功率', 0) >= 65: 
        return "🛡️ **後排指揮官**：確保一傳穩定，是戰術發動的核心。"
    else:
        return "可靠的輪換或特定戰術球員。"

# ====================================================================
# II. 企業聯賽數據爬蟲 (核心實作區 - 假數據)
# ====================================================================

@st.cache_data(ttl=3600)
def fetch_all_data_for_season(season_id):
    """
    此函數為爬蟲佔位符，返回模擬的合併數據。
    
    ⚠️ 實作指引: 請用真正的網頁爬蟲代碼替換此函數內的假數據生成邏輯。
    """
    
    # -----------------------------------------------------------
    # 假數據生成邏輯 (需要您替換為真實的爬蟲結果)
    # -----------------------------------------------------------
    st.info(f"🚧 正在載入 **{season_id}** 模擬數據，請實作網頁爬蟲以獲取真實數據。")
    all_players_data = []
    
    # 模擬不同賽季的不同球隊和球員
    if season_id == '企業十七年 (2022-2023)':
        players_per_team = {
            '台電男排': [('吳X軒', '主攻', 190, 80), ('詹X益', '舉球', 180, 70), ('林X豪', '副攻', 195, 88)],
            '長力男排': [('陳X杰', '接應', 185, 75), ('黃X銘', '主攻', 188, 78), ('張X源', '自由', 175, 68)],
            '雲林美津濃': [('高X林', '副攻', 198, 90), ('劉X誠', '主攻', 192, 85)],
        }
    elif season_id == '企業十八年 (2023-2024)':
        players_per_team = {
            '臺北市': [('甲X', '主攻', 187, 77), ('乙X', '舉球', 179, 69)],
            '連莊': [('丙X', '接應', 186, 76), ('丁X', '副攻', 194, 87)],
            '台電男排': [('戊X', '主攻', 191, 81), ('己X', '自由', 176, 67)],
        }
    else: 
        st.warning(f"目前沒有 {season_id} 的模擬數據。")
        return pd.DataFrame(columns=VOLLEYBALL_STATS_COLUMNS)

    for team, players in players_per_team.items():
        for name, pos, height, weight in players:
            # 隨機生成統計數據
            attack_pts = round(random.uniform(50, 300), 0) if pos != '自由' else 0
            attack_err = round(random.uniform(5, 30), 0) if pos != '自由' else 0
            attack_attempts = round(random.uniform(100, 600), 0) if pos != '自由' else 0
            block_pts = round(random.uniform(5, 50), 0)
            service_pts = round(random.uniform(0, 15), 0)
            service_err = round(random.uniform(0, 10), 0)
            gp = round(random.uniform(20, 50), 0)
            reception_pct = round(random.uniform(50, 80), 0) if pos in ['自由', '主攻'] else 0

            all_players_data.append({
                '姓名': name,
                '隊伍': team,
                '位置': pos,
                '身高(cm)': height,
                '體重(kg)': weight,
                '上場局數': gp,
                '攻擊得分': attack_pts,
                '攻擊失誤': attack_err,
                '攻擊次數': attack_attempts,
                '攔網得分': block_pts,
                '發球得分': service_pts,
                '發球失誤': service_err,
                '接發成功率': reception_pct
            })

    final_df = pd.DataFrame(all_players_data)
    required_cols = [c for c in VOLLEYBALL_STATS_COLUMNS if c in final_df.columns]
    
    st.success(f"成功處理 {season_id} 男子組的 {len(final_df)} 筆數據。")
    return final_df[required_cols]

# ====================================================================
# III. Streamlit 界面邏輯 (Image 1 風格)
# ====================================================================

st.set_page_config(layout="centered", page_title="台灣排球數據分析 (男子組)")
st.title("🏐 企業排球聯賽男子排球員個人數據與歷史分析")
st.markdown("##### 台灣男子組 (企業 17-20 年)")

# --- Session State 初始化 ---
if 'volleyball_data_cache' not in st.session_state:
    # 預先載入一個賽季的數據
    initial_season = '企業十七年 (2022-2023)'
    st.session_state['volleyball_data_cache'] = {
        'season_key': initial_season,
        'data': fetch_all_data_for_season(initial_season)
    }

# --- 側邊欄: 主要篩選器 ---
with st.sidebar:
    st.header("選擇球員")
    
    # 1. 賽季選擇
    selected_season_key = st.selectbox(
        "選擇聯賽賽季:",
        options=list(VLEAGUE_SEASONS.keys()),
        index=list(VLEAGUE_SEASONS.keys()).index(st.session_state['volleyball_data_cache']['season_key']), 
        key='report_season_key'
    )
    
    # 檢查是否需要重新載入數據
    if st.session_state['volleyball_data_cache'].get('season_key') != selected_season_key:
        with st.spinner(f"正在載入 {selected_season_key} 數據..."):
            df = fetch_all_data_for_season(selected_season_key)
            st.session_state['volleyball_data_cache'] = {
                'season_key': selected_season_key,
                'data': df
            }
            
    current_season_df = st.session_state['volleyball_data_cache']['data']

    selected_player_name = None

    if current_season_df.empty:
        st.warning(f"當前賽季 ({selected_season_key}) 沒有可用的數據。")
    else:
        # 2. 隊伍選擇 (動態更新)
        team_options = ['所有隊伍'] + sorted(current_season_df['隊伍'].unique().tolist())
        selected_team = st.selectbox(
            "選擇球隊:",
            options=team_options,
            key='report_team_select'
        )
        
        # 根據隊伍篩選球員
        if selected_team != '所有隊伍':
            filtered_players_df = current_season_df[current_season_df['隊伍'] == selected_team]
        else:
            filtered_players_df = current_season_df

        # 3. 球員選擇 (動態更新)
        player_options = sorted(filtered_players_df['姓名'].unique().tolist())
        if not player_options:
            st.warning("所選隊伍或賽季無球員數據。")
        else:
            selected_player_name = st.selectbox(
                "選擇球員:",
                options=player_options,
                key='report_player_select'
            )

    st.markdown("---")
    st.caption("目標組別: 男子組 🧑‍🤝‍🧑")


# --- 主內容區: 球員報告 (類似 Image 1 風格) ---
if selected_player_name and not current_season_df.empty:
    player_stats = current_season_df[current_season_df['姓名'] == selected_player_name].reset_index(drop=True)
    processed_player_stats = calculate_efficiency(player_stats.copy())
    
    if not processed_player_stats.empty:
        player_data = processed_player_stats.iloc[0]

        # 頂部標題
        st.markdown(f"## 👤 **{player_data['姓名']}** 個人表現報告")
        st.markdown(f"#### 隸屬隊伍: **{player_data['隊伍']}** ({selected_season_key})")
        
        st.markdown("---")
        
        # 1. 身體與基本資料
        st.subheader("1. 身體與基本資料")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**位置:** **{player_data['位置']}**")
        with col2:
            st.markdown(f"**身高:** **{int(player_data['身高(cm)'])} cm**")
        with col3:
            st.markdown(f"**體重:** **{int(player_data['體重(kg)'])} kg**")
        with col4:
            st.markdown(f"**上場局數:** **{int(player_data['上場局數'])} 局**")

        st.markdown("---")
        
        # 2. 核心貢獻 (分區塊呈現)
        st.subheader("2. 核心貢獻數據")

        # 進攻效率
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("##### 攻擊表現")
            st.metric("攻擊成功率", f"{player_data['攻擊成功率(%)']:.2f}%", help="攻擊得分減攻擊失誤除以攻擊總次數")
            st.metric("攻擊得分", int(player_data['攻擊得分']))
            st.metric("攻擊次數", int(player_data['攻擊次數']))
        
        # 防守與發球
        with col_b:
            st.markdown("##### 攔網 / 發球 / 接發")
            st.metric("攔網得分", int(player_data['攔網得分']))
            st.metric("發球得分 (Ace)", int(player_data['發球得分']))
            st.metric("接發成功率", f"{int(player_data['接發成功率'])}%", help="一傳成功率")

        st.markdown("---")
        
        # 3. 總體效率與定位
        st.subheader("3. 總體效率與定位")
        
        col_c, col_d, col_e = st.columns(3)
        with col_c:
            st.metric("總得分", int(player_data['總得分']))
        with col_d:
            st.metric("淨得分", int(player_data['淨得分']), help="總得分 - 總失誤")
        with col_e:
            st.metric("場均貢獻度", f"{player_data['場均淨得分']:.2f}", help="每局的淨得分貢獻")

        with st.expander("🏐 角色定位分析"):
            analysis_text = analyze_player_role(player_data)
            st.markdown(f"> {analysis_text}")

        st.markdown("---")
        # 4. 歷史表現 (預留區)
        st.subheader("4. 歷史表現與獎項 (未來功能)")
        st.info("此處將用於比較該球員在不同賽季的數據變化。")
            
    else:
        st.warning("所選球員無數據可供分析。")

else:
    st.info("請在左側邊欄選擇賽季、球隊和球員以查看詳細報告。")
    
