import streamlit as st
import datetime
import os
import base64
import json

# --- 1. НАСТРОЙКИ ---
st.set_page_config(page_title="Онлайн-табло Русского мира", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🔐 НАСТРОЙКИ ДОСТУПА (ЛОГИНЫ И ПАРОЛИ)
# ==========================================
# Формат: "логин": "пароль"
CREDENTIALS = {
    "user": "123",    # <--- Доступ только для просмотра
    "admin": "admin"  # <--- Полный доступ (Командир)
}
# ==========================================

DB_FILE = "db.json"

# --- СТИЛЬ И ФОН ---
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
    
    /* Скрытие меню Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Контейнеры */
    div[data-testid="stContainer"] {{
        background-color: rgba(20, 30, 20, 0.75);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 0, 0.1);
        border-radius: 6px;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
    }}
    
    h1, h2, h3, h4 {{ color: #ffffff !important; text-transform: uppercase; letter-spacing: 1px; }}
    
    input, select {{ 
        background-color: #111 !important; color: #00ff00 !important; border: 1px solid #333 !important; 
    }}
    
    div.stButton > button {{ 
        background: linear-gradient(0deg, #1b5e20, #2e7d32); 
        color: white !important; 
        border: 1px solid #4caf50; 
        width: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🚪 СИСТЕМА ВХОДА (LOGIN GATEKEEPER)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

def check_login():
    user = st.session_state["input_user"]
    pwd = st.session_state["input_pwd"]
    
    if user in CREDENTIALS and CREDENTIALS[user] == pwd:
        st.session_state.authenticated = True
        st.session_state.user_role = "admin" if user == "admin" else "viewer"
    else:
        st.error("⛔ ОШИБКА ДОСТУПА: Неверный логин или пароль")

if not st.session_state.authenticated:
    # ЭКРАН ВХОДА
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.container():
            if os.path.exists("images/logo.png"):
                st.image("images/logo.png", width=100)
            st.title("ВХОД В СИСТЕМУ")
            st.text_input("Позывной (Логин)", key="input_user")
            st.text_input("Ключ (Пароль)", type="password", key="input_pwd")
            st.button("ВОЙТИ", on_click=check_login)
    st.stop() # ОСТАНАВЛИВАЕТ ЗАГРУЗКУ САЙТА, ПОКА НЕ БУДЕТ ВХОДА

# ==========================================
# 🚀 ОСНОВНОЕ ПРИЛОЖЕНИЕ (ЗАГРУЖАЕТСЯ ТОЛЬКО ПОСЛЕ ВХОДА)
# ==========================================

# --- БАЗА ДАННЫХ ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.records, f, ensure_ascii=False, indent=4)

# --- СПИСОК ЦЕЛЕЙ ---
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

# ЗАГРУЗКА
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

# --- ШАПКА ПРИЛОЖЕНИЯ ---
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

# Кнопка выхода
with st.sidebar:
    st.write(f"Пользователь: **{role_text}**")
    if st.button("ВЫЙТИ ИЗ СИСТЕМЫ"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.rerun()

# --- ЛОГИКА ВКЛАДОК ---
# Если Админ - показываем 2 вкладки, иначе только сводку
if st.session_state.user_role == "admin":
    tab_list, tab_add = st.tabs(["📊 СВОДНАЯ ТАБЛИЦА", "➕ ВВОД ДАННЫХ"])
else:
    tab_list = st.container() # Просто контейнер, без вкладок
    tab_add = None

# 1. СВОДКА
with tab_list:
    # Фильтры
    c_filter, c_void = st.columns([1, 3])
    with c_filter:
        filter_mode = st.selectbox("📅 ПЕРИОД", ["Все время", "2025 год", "Этот месяц", "Последние 7 дней", "Сегодня"])

    # Итого
    grand_total = 0
    for item in data:
        base = item['initial'] if filter_mode == "Все время" else 0
        recs = filter_records(st.session_state.records[item['id']], filter_mode)
        added = sum(int(r.get('count', 1)) for r in recs)
        grand_total += base + added
    
    with col_stat:
        st.metric(f"ИТОГО ({filter_mode.upper()})", grand_total)

    st.markdown("---")
    
    # Карточки
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
                                    
                                    # Видео
                                    vid_link = rec.get('video_link', '')
                                    if vid_link:
                                        st.markdown(f"[🎥 **СМОТРЕТЬ ВИДЕО (ОК)**]({vid_link})")

                                    # Кнопка удаления ТОЛЬКО ДЛЯ АДМИНА
                                    if st.session_state.user_role == "admin":
                                        if st.button("УДАЛИТЬ", key=f"del_{item['id']}_{rec['time']}_{rec['date']}"):
                                            try:
                                                st.session_state.records[item['id']].remove(rec)
                                                save_data()
                                                st.rerun()
                                            except:
                                                pass
                                    st.divider()

# 2. ВВОД (Только админ)
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