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
    
    # 突出顯示最高的攻擊、攔網和發球數據
    styled_df = df.style.format({
        'points': "{:,.0f}",
        'blocks': "{:,.0f}",
        'aces': "{:,.0f}",
        'digs': "{:,.0f}",
        'assists': "{:,.0f}",
    }).highlight_max(subset=['points', 'blocks', 'aces', 'digs'], color='#fff3c7') # 淺黃色突出最大值

    return styled_df

def create_team_analysis_view(team_id):
    """顯示單一隊伍的詳細分析"""
    
    # 使用 .loc[team_id] 存取索引行
    team_info = TEAMS_DF.loc[team_id] 
    st.markdown(f"## {team_info['name']} 分析 ({team_info['trophy']})")
    
    # 隊伍備註
    st.info(f"**隊伍簡介 (2022-2025):** {team_info['note']}")
    
    # 篩選球員名單
    team_roster = PLAYERS_DF[PLAYERS_DF['team_id'] == team_id].drop(columns=['team_id'])
    
    # 重新命名欄位以便於中文顯示
    team_roster.columns = ['球員姓名', '位置', '活躍賽季 (企排)', '總得分', '總攔網', '總ACE球', '總防守', '總舉球']
    
    st.subheader(f"🏟️ {team_info['name']} 選手累積數據 (2022-2025)")
    st.caption("數據為企排 18-21 賽季的累積總和 (模擬數據)。")

    # 格式化並顯示數據框
    st.dataframe(
        format_dataframe_display(team_roster),
        use_container_width=True,
        hide_index=True,
        # 設置欄寬
        column_config={
            "球員姓名": st.column_config.Column(width="medium"),
            "位置": st.column_config.Column(width="small"),
            "活躍賽季 (企排)": st.column_config.Column(width="small"),
            "總得分": st.column_config.ProgressColumn("總得分", format="%f", min_value=0, max_value=team_roster['總得分'].max()),
            "總舉球": st.column_config.ProgressColumn("總舉球", format="%f", min_value=0, max_value=team_roster['總舉球'].max()),
        }
    )

    # 數據視覺化 (Top 3 Scoring Players)
    top_scorers = team_roster.sort_values(by='總得分', ascending=False).head(3)
    if not top_scorers.empty:
        st.subheader("📊 隊伍主力攻擊手表現 (總得分)")
        st.bar_chart(top_scorers.set_index('球員姓名')['總得分'])

def create_league_overview():
    """顯示聯賽總覽和頂尖球員分析"""
    st.subheader("🌟 聯賽頂尖球員總覽 (2022-2025 累積)")
    st.caption("此列表涵蓋所有隊伍中，在特定技術數據上最具統治力的選手。")
    
    # 數據整理
    analysis_df = PLAYERS_DF.merge(TEAMS_DF['name'], left_on='team_id', right_index=True)
    analysis_df.rename(columns={'name': '隊伍', 'player': '球員姓名', 'points': '總得分', 'blocks': '總攔網', 'aces': '總ACE球'}, inplace=True)
    
    
    # 定義要展示的指標
    metrics_to_show = {
        '總得分': '攻擊核心 (總得分)', 
        '總攔網': '防守堡壘 (總攔網)', 
        '總ACE球': '發球威脅 (總ACE球)'
    }
    
    cols = st.columns(3)
    
    for i, (col_name, title) in enumerate(metrics_to_show.items()):
        # 找到該指標的最高值球員
        top_player = analysis_df.loc[analysis_df[col_name].idxmax()]
        
        with cols[i]:
            st.metric(
                label=title,
                value=f"{top_player['球員姓名']} ({top_player['隊伍']})",
                delta=f"累積 {top_player[col_name]:,.0f} 次"
            )

    st.markdown("---")
    st.subheader("💡 重點觀察球員:")
    st.markdown("""
    * **Bryan Bagunas (連莊):** 作為外援，他在短時間內打出了驚人的得分效率，是連莊能夠打破台電王朝的關鍵。
    * **張祐晨 (Mizuno):** 本土新生代隊長，累積數據穩定且全面，在企排21年開始展現出MVP級的火力輸出。
    * **陳建禎 (台電):** 經驗豐富的領袖，即便數據可能不如外援華麗，但其防守和串聯作用對台電至關重要。
    """)


# --- 應用程式啟動設定 ---

st.set_page_config(
    page_title="台灣企業排球聯賽數據分析 (2022-2025)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 標題
st.title("🏐 台灣企業排球聯賽數據分析 (2022-2025)")
st.caption("涵蓋企排 18 年至 21 年男子組數據分析 (數據為模擬)。")
st.markdown("---")

# 選擇要分析的隊伍
# 修正後的邏輯：使用 iterrows() 取得索引 (team_id) 和資料行 (row['name'])
# 修正點：必須使用 index 來獲取索引值 (team_id)。
team_options = {row['name']: index for index, row in TEAMS_DF.iterrows()}
team_names = list(team_options.keys())
team_names.insert(0, "聯賽總覽") # 增加一個總覽選項

selected_team_name = st.selectbox(
    "選擇您想分析的隊伍或查看聯賽總覽:",
    team_names,
    key="team_select"
)

st.markdown("---")

# 根據選擇顯示內容
if selected_team_name == "聯賽總覽":
    create_league_overview()
else:
    selected_team_id = team_options[selected_team_name]
    create_team_analysis_view(selected_team_id)

st.markdown("""
<br><br><br>
<p style='font-size: 0.8rem; color: #a0a0a0;'>
* 數據備註：此處所有球員數據為模型模擬的 2022 年至 2025 年 (企排 18-21 賽季) 累積總和，用於展示應用程式功能，非官方真實數據。
</p>
""", unsafe_allow_html=True)
