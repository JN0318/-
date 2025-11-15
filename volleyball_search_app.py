# -*- coding: utf-8 -*-
# 台灣排球數據分析 Streamlit 應用程式 - 企業聯賽爬蟲框架

import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
import io

# ====================================================================
# I. 數據獲取與分析核心邏輯
# ====================================================================

# 定義排球員數據的基礎結構
VOLLEYBALL_STATS_COLUMNS = [
    '姓名', '隊伍', '位置', '上場局數', 
    '攻擊得分', '攻擊失誤', '攻擊次數', 
    '攔網得分', '發球得分', '發球失誤', 
    '接發成功率'
]

def calculate_efficiency(df):
    """計算排球員的關鍵效率指標。"""
    
    # 確保所有數值列為數值型態，並處理潛在的除零錯誤
    numeric_cols = ['攻擊得分', '攻擊失誤', '攻擊次數', '攔網得分', '發球得分', '發球失誤', '上場局數']
    for col in numeric_cols:
        # 將非數值內容（如 '-' 或 'N/A'）替換為 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 攻擊成功率 (Attack Success Rate)
    # 攻擊成功率 = (攻擊得分 - 攻擊失誤) / 攻擊次數
    df['攻擊成功率(%)'] = ((df['攻擊得分'] - df['攻擊失誤']) / df['攻擊次數'] * 100).fillna(0).round(2)
    
    # 總得分 (Total Points)
    df['總得分'] = df['攻擊得分'] + df['攔網得分'] + df['發球得分']
    df['總失誤'] = df['攻擊失誤'] + df['發球失誤']
    
    # 淨得分 (Net Points: 總得分 - 總失誤)
    df['淨得分'] = df['總得分'] - df['總失誤']
    
    # 場均淨得分 (Per Set Net Points)
    df['場均淨得分'] = (df['淨得分'] / df['上場局數']).replace([float('inf'), -float('inf')], 0).fillna(0).round(2)
    
    return df

def analyze_player_role(stats):
    """根據關鍵數據指標分析球員類型。 (僅針對單行數據)"""
    
    # 確保輸入是單行 Series 或 DataFrame
    if isinstance(stats, pd.DataFrame):
        stats = stats.iloc[0]

    if stats['上場局數'] == 0:
        return "該球員無數據或未上場。"
        
    # 根據場均表現判斷
    avg_attack_score = stats['攻擊得分'] / stats['上場局數']
    avg_block_score = stats['攔網得分'] / stats['上場局數']
    avg_ace_score = stats['發球得分'] / stats['上場局數']
    attack_success_rate = stats['攻擊成功率(%)']

    is_spiker = avg_attack_score > 5
    is_blocker = avg_block_score >= 1
    is_ace_server = avg_ace_score >= 0.5
    
    position = stats['位置']
    
    if is_spiker and attack_success_rate >= 40:
        return "🔥 **高效得分機器 (High-Efficiency Scorer)**：主要進攻點，火力強勁且效率極高。"
    elif is_blocker and position == '副攻':
        return "🧱 **優秀攔網中樞 (Elite Blocking)**：主要貢獻來自攔網，是球隊防守的堅實後盾。"
    elif is_ace_server:
        return "🎯 **發球威脅 (Serving Threat)**：發球能持續破壞對手一傳，創造得分機會。"
    elif position == '自由球員' and stats['接發成功率'] >= 65:
        return "🛡️ **後排指揮官 (Back-row Commander)**：確保一傳穩定，是戰術發動的核心。"
    else:
        return "可靠的輪換或特定戰術球員。"

# ====================================================================
# II. 企業聯賽數據爬蟲 (佔位符與指引)
# ====================================================================

@st.cache_data(ttl=3600) # 緩存 1 小時，避免頻繁請求
def scrape_vleague_stats(season_id, gender):
    """
    此函數為企業排球聯賽數據爬蟲的佔位符。
    
    ⚠️ 實作指引:
    1. 找到企業聯賽的統計數據頁面 URL (例如：排協官網的歷年賽事數據頁)。
    2. 確定頁面中球員數據表格的 HTML 結構 (<table> 或特定的 <div>)。
    3. 使用 requests.get(url) 獲取網頁內容。
    4. 使用 BeautifulSoup 解析內容並找到數據表格。
    5. 將表格數據轉換為 Pandas DataFrame，並確保列名與 VOLLEYBALL_STATS_COLUMNS 匹配。
    """
    
    st.info(f"🚧 正在嘗試爬取 **企業聯賽 {season_id}** 賽季的 **{gender}** 組數據...")
    
    # 由於沒有公開 API，這裡返回一個假數據作為示例
    if season_id == '企業十七年 (2022-2023)':
        data = [
            ['吳 X 軒', '台電男排', '主攻', 50, 250, 30, 500, 35, 12, 18, 65],
            ['陳 X 均', '連莊男排', '副攻', 45, 100, 10, 200, 50, 5, 8, 15],
            ['林 X 豪', '長力男排', '接應', 48, 220, 25, 450, 15, 6, 15, 30],
            ['邱 X 鳳', '台電女排', '主攻', 60, 300, 40, 650, 25, 15, 20, 70],
        ]
    elif season_id == '企業十八年 (2023-2024)':
        data = [
            ['XXX', '臺北市', '主攻', 30, 150, 15, 300, 20, 10, 10, 60],
            ['YYY', '新北市', '副攻', 25, 80, 5, 150, 30, 2, 5, 10],
        ]
    else:
        return None
        
    # 創建並返回 DataFrame
    cols = ['姓名', '隊伍'] + VOLLEYBALL_STATS_COLUMNS[2:]
    df = pd.DataFrame(data, columns=cols)
    
    # 篩選性別 (這裡需要真正的爬蟲來區分，目前假設數據中都包含隊伍名，可以間接判斷)
    if gender == '男子組':
        df = df[df['隊伍'].str.contains('男|臺北市|連莊', na=False)]
    else:
        df = df[df['隊伍'].str.contains('女|臺北市|極速超跑', na=False)]
        
    return df

# ====================================================================
# III. Streamlit 界面邏輯
# ====================================================================

st.set_page_config(layout="wide", page_title="台灣排球數據分析")
st.title("🏐 企業排球聯賽數據分析儀表板")

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
            # 依據爬蟲目標新增更多賽季
        ],
        key='vleague_season'
    )
    
    # 性別選擇
    selected_gender = st.radio(
        "選擇組別:",
        options=['男子組', '女子組'],
        key='vleague_gender'
    )
    
    if st.button("🔄 獲取並分析數據"):
        # 呼叫爬蟲函數 (目前為假數據)
        with st.spinner(f"正在載入 {selected_season} {selected_gender} 數據..."):
            vleague_df = scrape_vleague_stats(selected_season, selected_gender)
        
        if vleague_df is not None and not vleague_df.empty:
            st.session_state['volleyball_df'] = vleague_df
            st.success(f"成功載入 {selected_season} {selected_gender} 的 {len(vleague_df)} 筆數據。")
        else:
            st.error("無法獲取該賽季數據。請檢查爬蟲是否需要更新或該賽季數據不存在。")
            st.session_state['volleyball_df'] = pd.DataFrame(columns=['姓名', '隊伍'] + VOLLEYBALL_STATS_COLUMNS[2:])

    st.markdown("---")
    st.caption("數據需透過網頁爬蟲實作。當前顯示為模擬數據。")


# --- 主區域: 數據處理與結果顯示 ---

# 確保 DataFrame 存在
if 'volleyball_df' not in st.session_state or st.session_state['volleyball_df'].empty:
    st.warning("請在左側邊欄選擇賽季和組別，並點擊獲取數據。")
else:
    current_df = st.session_state['volleyball_df'].copy()
    
    # 1. 計算所有效率指標
    processed_df = calculate_efficiency(current_df)

    st.subheader(f"📊 {selected_season} {selected_gender} 球員效率排名")
    
    # 移除隊伍欄位，只留下關鍵的指標排名
    display_cols = ['姓名', '隊伍', '位置', '上場局數', '總得分', '淨得分', '場均淨得分', '攻擊成功率(%)', '接發成功率']
    
    st.dataframe(
        processed_df.sort_values(by='場均淨得分', ascending=False), 
        use_container_width=True,
        column_order=display_cols,
        column_config={
            "攻擊成功率(%)": st.column_config.ProgressColumn("攻擊成功率", format="%.2f%%", min_value=0, max_value=60),
            "場均淨得分": st.column_config.NumberColumn("場均貢獻度", format="%.2f"),
            "接發成功率": st.column_config.ProgressColumn("接發成功率", format="%.0f%%", min_value=0, max_value=100),
            "總得分": "總得分", "淨得分": "淨得分"
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
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("場均貢獻度", player_stats['場均淨得分'].iloc[0])
            col2.metric("攻擊成功率", f"{player_stats['攻擊成功率(%)'].iloc[0]}%")
            col3.metric("總得分", player_stats['總得分'].iloc[0].astype(int))
            col4.metric("隊伍", player_stats['隊伍'].iloc[0])
            
            st.markdown(f"#### 🏐 {selected_player_name} 角色定位分析:")
            analysis_text = analyze_player_role(player_stats)
            st.markdown(f"> {analysis_text}")
