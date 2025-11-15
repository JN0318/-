import streamlit as st
import pandas as pd
import numpy as np

# --- 模擬數據集 (2022 - 2025 企排 18-21 年) ---

# 1. 隊伍資料
TEAMS_DATA = [
    {"team_id": "LC", "name": "連莊排球隊", "trophy": "🏆🏆🏆 (企排18, 19, 20 總冠軍)", "note": "2022年起中斷台電王朝，確立新霸主地位。"},
    {"team_id": "TP", "name": "屏東台電", "trophy": "🥈🥈 (企排18, 19 亞軍)", "note": "傳統強權，在 2022 年前曾達成八連霸。"},
    {"team_id": "MZ", "name": "雲林Mizuno", "trophy": "🥉🥉", "note": "具備強大韌性的挑戰者，近年有顯著的本土戰力提升。"},
    {"team_id": "TSG", "name": "臺中太陽神", "trophy": "無", "note": "聯賽中堅力量，年輕球員的成長搖籃。"},
    {"team_id": "TTI", "name": "桃園台灣產險", "trophy": "無", "note": "穩定的參賽隊伍，時常能帶給強隊壓力。"},
]
# 設定 team_id 為索引
TEAMS_DF = pd.DataFrame(TEAMS_DATA).set_index("team_id")

# 2. 球員數據 (累積總和: 2022-2025 賽季)
# 數據為模擬，但基於真實球員角色與表現趨勢
PLAYERS_DATA = [
    # 連莊排球隊 (LC)
    {"team_id": "LC", "player": "Bryan Bagunas (菲)", "position": "主攻手 (外援)", "active_seasons": "18, 19", "points": 1200, "blocks": 80, "aces": 60, "digs": 450, "assists": 20},
    {"team_id": "LC", "player": "吳宗軒", "position": "主攻手", "active_seasons": "18, 19, 20", "points": 950, "blocks": 50, "aces": 35, "digs": 380, "assists": 15},
    {"team_id": "LC", "player": "施琅 (Veasna, 柬)", "position": "主攻手 (外援)", "active_seasons": "20", "points": 600, "blocks": 40, "aces": 30, "digs": 220, "assists": 10},
    {"team_id": "LC", "player": "呂姜耀凱", "position": "快攻手", "active_seasons": "18, 19, 20", "points": 450, "blocks": 95, "aces": 18, "digs": 150, "assists": 5},
    
    # 屏東台電 (TP)
    {"team_id": "TP", "player": "陳建禎", "position": "主攻手/隊長", "active_seasons": "18, 19, 20", "points": 700, "blocks": 45, "aces": 40, "digs": 500, "assists": 20},
    {"team_id": "TP", "player": "戴儒謙", "position": "舉球員", "active_seasons": "18, 19, 20", "points": 150, "blocks": 30, "aces": 25, "digs": 400, "assists": 1200},
    {"team_id": "TP", "player": "黃建逢", "position": "主攻手", "active_seasons": "18, 19", "points": 650, "blocks": 55, "aces": 30, "digs": 250, "assists": 10},
    {"team_id": "TP", "player": "莊明叡", "position": "自由球員", "active_seasons": "19, 20", "points": 0, "blocks": 0, "aces": 0, "digs": 900, "assists": 150},

    # 雲林Mizuno (MZ)
    {"team_id": "MZ", "player": "張祐晨", "position": "主攻手/隊長", "active_seasons": "18, 19, 20, 21", "points": 1100, "blocks": 65, "aces": 55, "digs": 480, "assists": 25},
    {"team_id": "MZ", "player": "蘇彥辰", "position": "副攻手", "active_seasons": "20, 21", "points": 450, "blocks": 20, "aces": 35, "digs": 180, "assists": 10},
    {"team_id": "MZ", "player": "洪榮發", "position": "快攻手", "active_seasons": "19, 20, 21", "points": 550, "blocks": 110, "aces": 22, "digs": 120, "assists": 8},
    
    # 臺中太陽神 (TSG)
    {"team_id": "TSG", "player": "高偉誠", "position": "舉球員", "active_seasons": "18, 19, 20", "points": 120, "blocks": 25, "aces": 20, "digs": 350, "assists": 900},
    {"team_id": "TSG", "player": "陳昭銘", "position": "主攻手", "active_seasons": "18, 19", "points": 500, "blocks": 30, "aces": 15, "digs": 200, "assists": 12},

    # 桃園台灣產險 (TTI)
    {"team_id": "TTI", "player": "李興國", "position": "主攻手", "active_seasons": "19, 20, 21", "points": 750, "blocks": 40, "aces": 30, "digs": 300, "assists": 15},
]
PLAYERS_DF = pd.DataFrame(PLAYERS_DATA)

# --- Streamlit 應用程式主體 ---

def format_dataframe_display(df):
    """應用 Streamlit 格式化和顏色到數據框"""
    
    # 修正點：使用已重新命名為中文的欄位名稱
    styled_df = df.style.format({
        '總得分': "{:,.0f}", 
        '總攔網': "{:,.0f}", 
        '總ACE球': "{:,.0f}", 
        '總防守': "{:,.0f}", 
        '總舉球': "{:,.0f}", 
    }).highlight_max(subset=['總得分', '總攔網', '總ACE球', '總防守'], color='#fff3c7') 

    return styled_df

def create_team_analysis_view(team_id):
    """顯示單一隊伍的詳細分析"""
    
    # 使用 .loc[team_id] 存取索引行
    team_info = TEAMS_DF.loc[team_id] 
    st.markdown(f"## {team_info['name']} 分析 ({team_info['trophy']})")
    
    # 隊伍備註
    st.info(f"**隊伍簡介 (2022-2
