import streamlit as st
import datetime
import os
import base64
import json

# --- 1. НАСТРОЙКИ ---
st.set_page_config(page_title="Онлайн-табло Русского мира", layout="wide", initial_sidebar_state="collapsed")

DB_FILE = "db.json"

# --- БАЗА ДАННЫХ ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.records, f, ensure_ascii=False, indent=4)

# --- ДИЗАЙН ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_image_css = ""
if os.path.exists("images/bg.jpg"):
    bin_str = get_base64_of_bin_file("images/bg.jpg")
    bg_image_css = f"""
        .stApp {{
            background-image: linear_gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.85)), url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
    """

st.markdown(f"""
    <style>
    {bg_image_css}
    .stApp {{ color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }}
    
    div[data-testid="stContainer"] {{
        background-color: rgba(20, 30, 20, 0.75);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 0, 0.1);
        border-radius: 6px;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
    }}
    
    h1, h2, h3, h4 {{ color: #ffffff !important; text-transform: uppercase; letter-spacing: 1px; }}
    
    /* Элементы ввода */
    input, select, div[data-testid="stDateInput"] {{ 
        background-color: rgba(0, 0, 0, 0.8) !important; 
        color: #00ff00 !important; 
        border: 1px solid #333 !important; 
    }}
    
    /* Скроллбар */
    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-track {{ background: #111; }}
    ::-webkit-scrollbar-thumb {{ background: #2e7d32; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #00ff00; }}

    div.stButton > button {{ 
        background: linear-gradient(0deg, #1b5e20, #2e7d32); 
        color: white; 
        border: 1px solid #4caf50; 
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ШАПКА ---
col_logo, col_title, col_stat = st.columns([1, 5, 2])
with col_logo:
    if os.path.exists("images/logo.png"):
        st.image("images/logo.png", width=100)
    else:
        st.markdown("<h1>🛡️</h1>", unsafe_allow_html=True)

with col_title:
    st.title("ОНЛАЙН-ТАБЛО РУССКОГО МИРА")
    st.caption("ОПЕРАТИВНЫЙ МОДУЛЬ КОНТРОЛЯ")

# --- СПИСОК ЦЕЛЕЙ ---
# В поле "initial" впиши цифры, которые УЖЕ должны быть на табло (старые результаты)
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

# --- ФУНКЦИЯ ФИЛЬТРАЦИИ ПО ДАТАМ ---
def filter_records(records, mode):
    filtered = []
    today = datetime.date.today()
    
    for rec in records:
        try:
            rec_date = datetime.datetime.strptime(rec['date'], "%Y-%m-%d").date()
        except:
            continue # Если дата кривая, пропускаем

        if mode == "Все время":
            filtered.append(rec)
        elif mode == "2025 год":
            if rec_date.year == 2025:
                filtered.append(rec)
        elif mode == "Этот месяц":
            if rec_date.year == today.year and rec_date.month == today.month:
                filtered.append(rec)
        elif mode == "Последние 7 дней":
            delta = today - rec_date
            if 0 <= delta.days <= 7:
                filtered.append(rec)
        elif mode == "Сегодня":
            if rec_date == today:
                filtered.append(rec)
                
    return filtered

# --- ИНТЕРФЕЙС ---
tab_list, tab_add = st.tabs(["📊 СВОДНАЯ ТАБЛИЦА", "➕ ВВОД ДАННЫХ"])

# 1. СВОДКА
with tab_list:
    # Меню фильтра
    c_filter, c_void = st.columns([1, 3])
    with c_filter:
        filter_mode = st.selectbox("📅 ПЕРИОД ОТОБРАЖЕНИЯ", 
                                   ["Все время", "2025 год", "Этот месяц", "Последние 7 дней", "Сегодня"])

    # Считаем общую сумму по фильтру
    grand_total = 0
    
    # Сначала пробежимся и посчитаем всё, чтобы показать общую цифру
    for item in data:
        # Берем начальное значение только если выбран режим "Все время"
        base = item['initial'] if filter_mode == "Все время" else 0
        recs = filter_records(st.session_state.records[item['id']], filter_mode)
        # Суммируем количество в записях (поле 'count')
        added = sum(int(r.get('count', 1)) for r in recs)
        grand_total += base + added
    
    with col_stat:
        st.metric(f"ИТОГО ({filter_mode.upper()})", grand_total)

    st.markdown("---")
    
    # Отрисовка карточек
    col_left, col_right = st.columns(2)
    for i, item in enumerate(data):
        current_col = col_left if i % 2 == 0 else col_right
        with current_col:
            # Получаем все записи
            all_records = st.session_state.records[item['id']]
            # Фильтруем их для отображения
            filtered_recs = filter_records(all_records, filter_mode)
            
            # Считаем сумму
            base_count = item['initial'] if filter_mode == "Все время" else 0
            # Учитываем поле 'count' (количество), если его нет - считаем как 1
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
                    # Показываем крупно число
                    st.markdown(f"<h2 style='color: #00ff00; margin:0;'>{total_count}</h2>", unsafe_allow_html=True)
                    
                    if len(filtered_recs) > 0:
                        with st.expander(f"Детализация ({len(filtered_recs)} записей)"):
                            with st.container(height=250):
                                # Показываем отфильтрованные записи (новые сверху)
                                for rec in reversed(filtered_recs): 
                                    # Чтобы найти реальный индекс для удаления, нужно поискать в оригинальном списке
                                    # Это немного сложно, поэтому удалять лучше только в режиме "Все время"
                                    # Или просто искать по совпадению. 
                                    # Для простоты: кнопку удаления показываем, но предупреждаем.
                                    
                                    qty = rec.get('count', 1)
                                    st.markdown(f"**+{qty} шт.** | 📅 {rec['date']}")
                                    st.caption(f"⏰ {rec['time']} | 📝 {rec['calc']}")
                                    
                                    loc_text = rec.get('coords', '')
                                    if not loc_text:
                                        # Поддержка старого формата
                                        old_x = rec.get('x', '')
                                        old_y = rec.get('y', '')
                                        if old_x or old_y:
                                            loc_text = f"X:{old_x} Y:{old_y}"
                                    
                                    if loc_text:
                                        st.text(f"📍 {loc_text}")
                                    
                                    st.divider()
                                
                                if filter_mode != "Все время":
                                    st.info("⚠️ Удаление доступно только в режиме 'Все время'")
                                else:
                                    # В режиме "Все время" можно удалять, так как списки совпадают (почти)
                                    # Но для надежности лучше сделать кнопку удаления во Вводе или отдельном меню.
                                    # Тут я оставлю упрощенный вариант просмотра.
                                    pass

# 2. ВВОД
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
                # Ряд 1: Дата, Время, КОЛИЧЕСТВО
                r1_c1, r1_c2, r1_c3 = st.columns([2, 2, 2])
                
                f_date = r1_c1.date_input("Дата", value=datetime.date.today(), min_value=datetime.date(2000, 1, 1))
                f_time = r1_c2.text_input("Время", value=datetime.datetime.now().strftime("%H:%M"))
                
                # --- НОВОЕ ПОЛЕ: КОЛИЧЕСТВО ---
                f_count = r1_c3.number_input("КОЛИЧЕСТВО", min_value=1, value=1, step=1)
                
                # Описание
                f_calc = st.text_input("Примечание / Характер действий")
                
                st.markdown("---")
                f_coords = st.text_input("Координаты / Ориентир", placeholder="Квадрат...")
                
                if st.form_submit_button("ВНЕСТИ РЕЗУЛЬТАТ"):
                    st.session_state.records[selected_id].append({
                        "date": str(f_date),
                        "time": f_time,
                        "count": f_count, # Сохраняем количество
                        "calc": f_calc,
                        "coords": f_coords
                    })
                    save_data()
                    st.toast(f"Добавлено: {selected_name} (+{f_count})", icon="✅")
                    st.rerun()

    # Блок удаления последних записей (для исправлений)
    st.markdown("---")
    with st.expander("🛠️ ИСПРАВЛЕНИЕ ОШИБОК (Удаление последних записей)"):
        recs = st.session_state.records[selected_id]
        if recs:
            st.write(f"Последние записи для: **{selected_name}**")
            for i in range(len(recs) - 1, -1, -1):
                r = recs[i]
                col_txt, col_btn = st.columns([4, 1])
                with col_txt:
                    st.caption(f"{r['date']} | +{r.get('count', 1)} шт. | {r['calc']}")
                with col_btn:
                    if st.button("Удалить", key=f"del_last_{selected_id}_{i}"):
                        delete_record(selected_id, i)
                        st.rerun()
                if i < len(recs) - 5: break # Показываем только 5 последних
        else:
            st.write("Нет записей для этого объекта.")