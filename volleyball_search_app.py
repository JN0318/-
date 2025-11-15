import streamlit as st

# 企業排球聯賽 (TVL) 男子組數據
# 數據基於企排18年 (2022) 到 企排21年 (2025) 的分析結果
ENT_VOLLEYBALL_DATA = [
    # 連莊排球隊 (企排三連霸霸主)
    {"type": "Player", "name": "Bryan Bagunas", "team": "連莊排球隊", "role": "主攻手 (外援)", "notes": "企排18年總冠軍賽MVP，菲律賓籍強勢外援。"},
    {"type": "Player", "name": "吳宗軒", "team": "連莊排球隊", "role": "主攻手", "notes": "台灣黃金左手，連莊三連霸（18-20年）的本土核心。"},
    {"type": "Player", "name": "施琅 (Voeurn Veasna)", "team": "連莊排球隊", "role": "主攻手 (外援)", "notes": "柬埔寨籍外援，企排20年關鍵得分手。"},
    {"type": "Team", "name": "連莊排球隊", "team": "連莊排球隊", "role": "男子組隊伍", "notes": "企排18, 19, 20年三連霸霸主。"},
    
    # 屏東台電 (傳統強權)
    {"type": "Player", "name": "陳建禎", "team": "屏東台電", "role": "主攻手/精神領袖", "notes": "台灣男排隊長神舉，台電八連霸時代的核心人物。"},
    {"type": "Team", "name": "屏東台電", "team": "屏東台電", "role": "男子組隊伍", "notes": "傳統強權，企排18年被連莊中斷八連霸。"},
    
    # 雲林Mizuno (新興挑戰者)
    {"type": "Player", "name": "張祐晨", "team": "雲林Mizuno", "role": "主攻手 (隊長)", "notes": "企排21年開季表現火燙，帶領美津濃挑戰強權。"},
    {"type": "Player", "name": "蘇彥辰", "team": "雲林Mizuno", "role": "發球手/攻擊手", "notes": "企排21年對戰桃園臺產時，連續ACE球鎖定勝局。"},
    {"type": "Player", "name": "洪榮發", "team": "雲林Mizuno", "role": "攻擊手", "notes": "企排20年季後賽的得分主力之一。"},
    {"type": "Team", "name": "雲林Mizuno", "team": "雲林Mizuno", "role": "男子組隊伍", "notes": "企排聯賽中堅力量，企排21年展現強勢挑戰者姿態。"},

    # 其他企排隊伍
    {"type": "Team", "name": "桃園台灣產險", "team": "桃園台灣產險", "role": "男子組隊伍", "notes": "企排中段班隊伍，具備挑戰強權的能力。"},
    {"type": "Team", "name": "臺北Conti", "team": "臺北Conti", "role": "男子組隊伍", "notes": "企排中段班隊伍，由年輕選手組成。"},
    {"type": "Team", "name": "臺中太陽神", "team": "臺中太陽神", "role": "男子組隊伍", "notes": "企業聯賽隊伍之一。"},
]

# 設置 Streamlit 頁面配置
st.set_page_config(
    page_title="企業排球聯賽球員與隊伍搜尋",
    layout="wide",
    initial_sidebar_state="expanded"
)

def create_card(item):
    """根據數據創建 Streamlit 資訊卡片"""
    is_player = item['type'] == 'Player'
    icon = '🏐' if is_player else '🏟️'
    
    # 使用 Streamlit markdown 和 metrics 創建卡片樣式
    st.markdown(
        f"""
        <div style="
            border: 1px solid #e0e0e0;
            border-top: 5px solid {'#10b981' if is_player else '#3b82f6'};
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        ">
            <h3 style="font-weight: bold; font-size: 1.25rem;">{icon} {item['name']}</h3>
            <p style="font-size: 0.875rem; color: {'#10b981' if is_player else '#3b82f6'}; font-weight: 600;">
                {item['type']}
            </p>
            <hr style="margin: 0.5rem 0; border-top: 1px solid #e0e0e0;">
            <p style="font-size: 0.95rem;">
                <span style="font-weight: 600;">所屬隊伍:</span> {item['team']}<br>
                <span style="font-weight: 600;">主要角色:</span> {item['role']}<br>
                <span style="font-weight: 600;">備註:</span> <span style="font-size: 0.8rem; color: #6b7280;">{item['notes']}</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    """主應用程式函數"""
    st.title("台灣企業排球聯賽 Player/Team Search")
    st.markdown("---")
    st.header("🔍 企業排球聯賽 (TVL) 資訊")
    st.caption("此應用程式僅包含企業排球聯賽（TVL/企排）的男子組隊伍與球員數據。")

    # 搜尋輸入框
    search_term = st.text_input(
        "輸入球員或隊伍名稱:", 
        placeholder="例如: 張祐晨, 連莊, 台電...", 
        key="search_input"
    ).lower().strip()

    # 執行篩選邏輯
    if search_term:
        filtered_results = [
            item for item in ENT_VOLLEYBALL_DATA 
            if search_term in item['name'].lower() 
            or search_term in item['team'].lower() 
            or search_term in item['role'].lower() 
            or search_term in item['notes'].lower()
        ]
    else:
        filtered_results = ENT_VOLLEYBALL_DATA

    st.markdown("---")

    # 顯示結果
    if filtered_results:
        st.subheader(f"共找到 {len(filtered_results)} 筆結果:")
        
        # 使用 st.columns 創建響應式卡片網格 (3欄)
        cols = st.columns(3)
        
        for index, item in enumerate(filtered_results):
            with cols[index % 3]: # 循環分配到 3 欄中
                create_card(item)
    else:
        st.error(f"找不到符合 **{search_term}** 的結果。請嘗試其他關鍵字。")

if __name__ == "__main__":
    main()
