import streamlit as st
import datetime
import os
import base64
import json

# ==========================================
# 1. ГЛОБАЛЬНЫЕ НАСТРОЙКИ
# ==========================================
st.set_page_config(page_title="Магазин 'Уютное Хобби'", page_icon="🧶", layout="wide", initial_sidebar_state="collapsed")

# 🔐 ДОСТУПЫ
CREDENTIALS = {
    "user": "123",    # Наблюдатель
    "admin": "admin"  # Командир
}
DB_FILE = "db.json"

if 'captcha_passed' not in st.session_state:
    st.session_state.captcha_passed = False
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# ==========================================
# 2. ФУНКЦИИ ПРОВЕРКИ
# ==========================================
def check_captcha():
    selection = set(st.session_state.get("captcha_select", []))
    correct = {"Отпуск", "Отход", "Обед", "Отдых"} 
    
    if selection == correct:
        st.session_state.captcha_passed = True
    else:
        st.error("Проверка не пройдена. Попробуйте еще раз.")

def check_login():
    user = st.session_state.get("input_login", "")
    pwd = st.session_state.get("input_password", "")
    
    if user in CREDENTIALS and CREDENTIALS[user] == pwd:
        st.session_state.authenticated = True
        st.session_state.user_role = "admin" if user == "admin" else "viewer"
    else:
        st.error("Неверный логин или пароль")

# ==========================================
# 3. ЭКРАН 0: КАПЧА (ЛЕГЕНДА - УРОВЕНЬ 1)
# ==========================================
if not st.session_state.captcha_passed:
    st.markdown("""
        <style>
        .stApp { background-color: #e6e0d4; color: #4a403a; }
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Стили для контейнера капчи */
        div[data-testid="stVerticalBlock"] > div:has(div.stForm) {
            background-color: #fdfcf8;
            border: 2px dashed #bfa5a3;
            padding: 40px;
            border-radius: 10px;
            max-width: 900px;
            margin: auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        /* Принудительно красим текст в капче в темный */
        div[data-testid="stVerticalBlock"] p, 
        div[data-testid="stVerticalBlock"] label,
        div[data-testid="stVerticalBlock"] span,
        div[data-testid="stVerticalBlock"] h1,
        div[data-testid="stVerticalBlock"] h3 {
            color: #4a403a !important;
        }

        h1 { color: #8e5e5e !important; font-family: 'Comic Sans MS', cursive, sans-serif; }
        
        div.stButton > button {
            background-color: #bfa5a3; 
            color: white !important; border: none; width: 100%;
            border-radius: 8px; font-size: 18px; padding: 10px;
        }
        div.stButton > button:hover { background-color: #a68b89; }
        
        /* Поля выбора (мультиселект) светлые */
        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #ccc;
        }
        
        .shop-nav {
            display: flex; justify-content: space-around; padding: 15px;
            background: #fff; border-bottom: 1px solid #ccc; margin-bottom: 30px;
            color: #555 !important; font-weight: bold; font-family: Arial;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="shop-nav">
            <span>🧶 Каталог пряжи</span>
            <span>🪡 Спицы и крючки</span>
            <span>📦 Доставка и оплата</span>
            <span>🔥 Акции -50%</span>
            <span>📞 Контакты</span>
        </div>
    """, unsafe_allow_html=True)
    
    c_space_l, c_main, c_space_r = st.columns([1, 6, 1])
    
    with c_main:
        st.title("🧵 Клуб 'Уютное Хобби'")
        st.markdown("### 🛡️ Анти-бот проверка")
        st.info("В связи с атаками ботов, пожалуйста, подтвердите, что вы человек. Выберите слова, связанные с **приемом пищи и отдыхом**.")
        
        with st.form("captcha_form"):
            options = [
                "Отпуск", "Ужин", "Семнадцать", "Генератор", 
                "Снежинка", "Отход", "Сиреневый", "Коричневый", 
                "Берет", "Корзина", "Картина", "Обед", 
                "Картонка", "Топор", "Квартира", "Преступление", 
                "Наказание", "Отдых"
            ]
            
            st.multiselect("Выберите нужные слова:", options, key="captcha_select")
            st.markdown("<br>", unsafe_allow_html=True)
            st.form_submit_button("✅ ПОДТВЕРДИТЬ", on_click=check_captcha)
            
        st.caption("Система защиты 'Handmade-Guard'. Мы заботимся о безопасности ваших заказов.")
        
        cols = st.columns(4)
        cols[0].markdown("📦 **Быстрая доставка**")
        cols[1].markdown("💳 **Оплата картой**")
        cols[2].markdown("⭐ **Гарантия качества**")
        cols[3].markdown("🎁 **Подарки в заказе**")
    
    st.stop() 

# ==========================================
# 4. ЭКРАН 1: МАГАЗИН ВХОД (ЛЕГЕНДА - УРОВЕНЬ 2)
# ==========================================
if not st.session_state.authenticated:
    st.markdown("""
        <style>
        .stApp { background-color: #e6e0d4; }
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Широкий контейнер входа */
        div[data-testid="stVerticalBlock"] > div:has(div.stForm) {
            background-color: #ffffff; 
            padding: 0px; 
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15); 
            max-width: 900px;
            margin: auto;
            border: 1px solid #e6d0ce;
            overflow: hidden;
        }
        
        h1 { color: #c71585 !important; font-family: 'Verdana', sans-serif; font-size: 32px !important; margin-bottom: 20px;}
        
        /* !ВАЖНО! Принудительно красим ВЕСЬ текст внутри формы в черный/серый */
        div[data-testid="stForm"] p, 
        div[data-testid="stForm"] label, 
        div[data-testid="stForm"] div,
        div[data-testid="stForm"] span {
            color: #333333 !important;
        }
        
        /* Но текст внутри кнопки оставляем белым */
        div.stButton > button p {
            color: #ffffff !important;
        }
        
        /* Кнопка */
        div.stButton > button { 
            background-color: #c71585 !important; 
            border: none; 
            width: 100%; 
            height: 60px;
            border-radius: 8px;
            margin-top: 10px;
        }
        div.stButton > button:hover { background-color: #a0106a !important; }
        
        /* Поля ввода: делаем их светлыми с черным текстом */
        input {
            background-color: #f0f2f6 !important;
            color: #000000 !important;
            border: 1px solid #ccc !important;
        }
        
        /* Баннер слева */
        .login-banner {
            background-color: #fae1dd;
            height: 100%;
            padding: 40px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        /* Текст внутри баннера (принудительно темный) */
        .login-banner h3, .login-banner p, .login-banner div {
            color: #8a4a4a !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Меню сверху
    st.markdown("""
        <div style="text-align:center; padding: 20px; font-family: Arial; color: #666 !important; margin-bottom: 20px;">
            Главная &nbsp; > &nbsp; Личный кабинет &nbsp; > &nbsp; <b>Авторизация</b>
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        c_banner, c_input = st.columns([2, 3])
        
        with c_banner:
            st.markdown("""
                <div class="login-banner">
                    <div style="font-size: 60px;">🧵</div>
                    <h3>🎉 SALE</h3>
                    <p>Скидка 20% на мериносовую шерсть!</p>
                    <br>
                    <p style="font-size: 12px;">Промокод: WINTER24</p>
                </div>
            """, unsafe_allow_html=True)
            
        with c_input:
            st.markdown("<div style='padding: 30px;'>", unsafe_allow_html=True)
            st.title("Вход в кабинет")
            
            st.text_input("E-mail или телефон", key="input_login", placeholder="ivanova@example.com")
            st.text_input("Пароль", type="password", key="input_password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Галочки (текст будет черным благодаря CSS выше)
            st.checkbox("Запомнить меня")
            st.checkbox("Соглашаюсь на подписку журнала по рукоделию 'Шустрая спица'", value=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.form_submit_button("ВОЙТИ В АККАУНТ", on_click=check_login)
            
            st.markdown("<div style='text-align:center; margin-top:15px;'><a href='#' style='color:#c71585; text-decoration: none;'>Забыли пароль?</a></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ==========================================
# 5. ЭКРАН 3: БОЕВАЯ СИСТЕМА
# ==========================================

# --- СТИЛЬ И ЛОГИКА ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_image_css = ""
if os.path.exists("images/bg.jpg"):
    bin_str = get_base64_of_bin_file("images/bg.jpg")
    bg_image_css = f"""
        .stApp {{
            background-image: linear_gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.95)), url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
    """

st.markdown(f"""
    <style>
    :root {{ color-scheme: dark; }}
    {bg_image_css}
    
    .stApp {{ background-color: #1a1c19 !important; color: #e0e0e0 !important; font-family: 'Segoe UI', sans-serif; }}
    
    h1, h2, h3, h4 {{ color: #ffffff !important; text-transform: uppercase; letter-spacing: 1px; }}
    p, label, span, div {{ color: #e0e0e0 !important; }}
    
    div[data-testid="stContainer"] {{
        background-color: rgba(20, 30, 20, 0.75);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 0, 0.1);
        border-radius: 6px;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
    }}
    
    input, select, textarea, div[data-testid="stDateInput"] > div {{ 
        background-color: #111 !important; color: #00ff00 !important; border: 1px solid #333 !important; 
    }}
    
    div.stButton > button {{ 
        background: linear-gradient(0deg, #1b5e20, #2e7d32); 
        color: white !important; 
        border: 1px solid #4caf50; 
        border-radius: 4px;
        font-size: 14px;
        width: 100%;
        height: auto;
    }}
    div[data-testid="stMetricValue"] {{ color: #00ff00 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- ФУНКЦИОНАЛ ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.records, f, ensure_ascii=False, indent=4)

data = [
    {"id": "tank", "name": "Танк", "image": "images/tank.gif", "initial": 350},
    {"id": "sau", "name": "САУ", "image": "images/sau.gif", "initial": 120},
    {"id": "art_gun", "name": "Орудие пол. арт.", "image": "images/gun.gif", "initial": 200},
    {"id": "btr", "name": "БТР", "image": "images/btr.gif", "initial": 400},
    {"id": "bmp", "name": "БМП", "image": "images/bmp.gif", "initial": 380},
    {"id": "bbm", "name": "ББМ", "image": "images/bbm.gif", "initial": 150},
    {"id": "quad", "name": "Квадроцикл", "image": "images/quad.gif", "initial": 50},
    {"id": "pickup", "name": "Пикап", "image": "images/pickup.gif", "initial": 90},
    {"id": "truck", "name": "Грузовой авто", "image": "images/truck.gif", "initial": 300},
    {"id": "uav_r18", "name": "БпЛА R-18", "image": "images/uav.gif", "initial": 0},
    {"id": "uav_eq", "name": "Оборудование БпЛА", "image": "images/uav_eq.gif", "initial": 0},
    {"id": "ant", "name": "Антенны связи", "image": "images/ant.gif", "initial": 20},
    {"id": "nrtk", "name": "НРТК", "image": "images/nrtk.gif", "initial": 0},
    {"id": "rls", "name": "РЛС", "image": "images/rls.gif", "initial": 15},
    {"id": "reb", "name": "Станция РЭБ", "image": "images/reb.gif", "initial": 10},
    {"id": "infantry", "name": "Личный состав", "image": "images/inf.gif", "initial": 1500},
    {"id": "shelter", "name": "Укрытия с л/с", "image": "images/shelter.gif", "initial": 100},
]

if 'records' not in st.session_state:
    loaded_data = load_data()
    st.session_state.records = {item['id']: [] for item in data}
    for k, v in loaded_data.items():
        if k in st.session_state.records:
            st.session_state.records[k] = v

def delete_record(item_id, index):
    del st.session_state.records[item_id][index]
    save_data()

def filter_records(records, mode):
    filtered = []
    today = datetime.date.today()
    for rec in records:
        try:
            rec_date = datetime.datetime.strptime(rec['date'], "%Y-%m-%d").date()
        except:
            continue
        if mode == "Все время": filtered.append(rec)
        elif mode == "2025 год":
            if rec_date.year == 2025: filtered.append(rec)
        elif mode == "Этот месяц":
            if rec_date.year == today.year and rec_date.month == today.month: filtered.append(rec)
        elif mode == "Последние 7 дней":
            delta = today - rec_date
            if 0 <= delta.days <= 7: filtered.append(rec)
        elif mode == "Сегодня":
            if rec_date == today: filtered.append(rec)
    return filtered

# --- ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---
col_logo, col_title, col_stat = st.columns([1, 5, 2])
with col_logo:
    if os.path.exists("images/logo.png"):
        st.image("images/logo.png", width=100)
    else:
        st.markdown("<h1>🛡️</h1>", unsafe_allow_html=True)

with col_title:
    role_text = "КОМАНДИР" if st.session_state.user_role == "admin" else "НАБЛЮДАТЕЛЬ"
    st.title("ОНЛАЙН-ТАБЛО РУССКОГО МИРА")
    st.caption(f"РЕЖИМ ДОСТУПА: {role_text}")

with st.sidebar:
    st.write("Меню")
    if st.button("ВЫЙТИ ИЗ СИСТЕМЫ"):
        st.session_state.authenticated = False
        st.session_state.captcha_passed = False 
        st.session_state.user_role = None
        st.rerun()

# --- ВКЛАДКИ ---
if st.session_state.user_role == "admin":
    tab_list, tab_add = st.tabs(["📊 СВОДНАЯ ТАБЛИЦА", "➕ ВВОД ДАННЫХ"])
else:
    tab_list = st.container()
    tab_add = None

# 1. СВОДКА
with tab_list:
    c_filter, c_void = st.columns([1, 3])
    with c_filter:
        filter_mode = st.selectbox("📅 ПЕРИОД", ["Все время", "2025 год", "Этот месяц", "Последние 7 дней", "Сегодня"])

    grand_total = 0
    for item in data:
        base = item['initial'] if filter_mode == "Все время" else 0
        recs = filter_records(st.session_state.records[item['id']], filter_mode)
        added = sum(int(r.get('count', 1)) for r in recs)
        grand_total += base + added
    
    with col_stat:
        st.metric(f"ИТОГО ({filter_mode.upper()})", grand_total)

    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    for i, item in enumerate(data):
        current_col = col_left if i % 2 == 0 else col_right
        with current_col:
            all_records = st.session_state.records[item['id']]
            filtered_recs = filter_records(all_records, filter_mode)
            
            base_count = item['initial'] if filter_mode == "Все время" else 0
            added_count = sum(int(r.get('count', 1)) for r in filtered_recs)
            total_count = base_count + added_count
            
            with st.container():
                c1, c2 = st.columns([1, 3])
                with c1:
                    if os.path.exists(item["image"]):
                        st.image(item["image"], use_container_width=True)
                    else:
                        st.write("📷")
                with c2:
                    st.markdown(f"#### {item['name']}")
                    st.markdown(f"<h2 style='color: #00ff00; margin:0;'>{total_count}</h2>", unsafe_allow_html=True)
                    
                    if len(filtered_recs) > 0:
                        with st.expander(f"Детализация ({len(filtered_recs)})"):
                            with st.container(height=250):
                                for rec in reversed(filtered_recs): 
                                    qty = rec.get('count', 1)
                                    st.markdown(f"**+{qty} шт.** | 📅 {rec['date']}")
                                    st.caption(f"⏰ {rec['time']} | 📝 {rec['calc']}")
                                    
                                    loc_text = rec.get('coords', '')
                                    if not loc_text:
                                        if rec.get('x') or rec.get('y'):
                                            loc_text = f"X:{rec.get('x')} Y:{rec.get('y')}"
                                    if loc_text:
                                        st.text(f"📍 {loc_text}")
                                    
                                    vid_link = rec.get('video_link', '')
                                    if vid_link:
                                        st.markdown(f"[🎥 **СМОТРЕТЬ ВИДЕО (ОК)**]({vid_link})")

                                    if st.session_state.user_role == "admin":
                                        if st.button("УДАЛИТЬ", key=f"del_{item['id']}_{rec['time']}_{rec['date']}"):
                                            try:
                                                st.session_state.records[item['id']].remove(rec)
                                                save_data()
                                                st.rerun()
                                            except:
                                                pass
                                    st.divider()

# 2. ВВОД
if st.session_state.user_role == "admin" and tab_add:
    with tab_add:
        st.subheader("РЕГИСТРАЦИЯ ЦЕЛИ")
        with st.container():
            options = {item["name"]: item["id"] for item in data}
            selected_name = st.selectbox("ВЫБЕРИТЕ ОБЪЕКТ", list(options.keys()), key="select_obj")
            selected_id = options[selected_name]
            selected_item = next(item for item in data if item["id"] == selected_id)

            c1, c2 = st.columns([1, 4])
            with c1:
                if os.path.exists(selected_item["image"]):
                    st.image(selected_item["image"])

            with c2:
                with st.form("add_form", clear_on_submit=True):
                    r1_c1, r1_c2, r1_c3 = st.columns([2, 2, 2])
                    f_date = r1_c1.date_input("Дата", value=datetime.date.today(), min_value=datetime.date(2000, 1, 1))
                    f_time = r1_c2.text_input("Время", value=datetime.datetime.now().strftime("%H:%M"))
                    f_count = r1_c3.number_input("КОЛИЧЕСТВО", min_value=1, value=1, step=1)
                    
                    f_calc = st.text_input("Примечание / Характер действий")
                    f_coords = st.text_input("Координаты / Ориентир")
                    f_video = st.text_input("Ссылка на видео")
                    
                    if st.form_submit_button("ВНЕСТИ РЕЗУЛЬТАТ"):
                        st.session_state.records[selected_id].append({
                            "date": str(f_date),
                            "time": f_time,
                            "count": f_count,
                            "calc": f_calc,
                            "coords": f_coords,
                            "video_link": f_video
                        })
                        save_data()
                        st.toast(f"Добавлено: {selected_name}", icon="✅")
                        st.rerun()