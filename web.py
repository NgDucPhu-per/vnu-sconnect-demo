#Made by Nguyen Duc Phu

import streamlit as st
import sqlite3
import pandas as pd
import datetime

# ==========================================
# 1. CƠ SỞ DỮ LIỆU & HỆ THỐNG PHẦN THƯỞNG KÉP
# ==========================================
@st.cache_resource
def init_db():
    conn = sqlite3.connect('vnu_sconnect.db', check_same_thread=False)
    c = conn.cursor()
    
    # Thêm cột 'role' (admin / student)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, full_name TEXT, vnu_credit INTEGER, vnu_token INTEGER, major TEXT, role TEXT)''')
    
    # Thêm cột 'status' (pending / approved)
    c.execute('''CREATE TABLE IF NOT EXISTS documents
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, uploader TEXT, title TEXT, subject_code TEXT, category TEXT, drive_link TEXT, upvotes INTEGER, timestamp TEXT, status TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS mentors
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, strong_subjects TEXT, location TEXT, contact_info TEXT, status TEXT)''')
    
    # Dữ liệu mẫu 
    sample_users = [
        ('vnusconnect', 'Giảng viên', 0, 0, 'Trường Đại học Công nghệ', 'admin'),
        ('25022976', 'Nguyễn Đức Phú', 298, 0, 'Trí tuệ nhân tạo (UET)', 'student'),
        ('25022987', 'Đào Nhật Quang', 255, 0, 'Trí tuệ nhân tạo (UET)', 'student'),
        ('25022800', 'Lê Quỳnh Chi', 216, 0, 'Trí tuệ nhân tạo (UET)', 'student'),
        ('25041102', 'Sinh viên 1', 30, 0, 'Kinh tế quốc tế (UEB)', 'student'),
        ('22041102', 'Sinh viên 1', 30, 0, 'Kinh tế quốc tế (UEB)', 'student'),
        ('25060543', 'Sinh viên 2', 85, 0, 'Báo chí (USSH)', 'student'),
        ('23010099', 'Sinh viên 3', 10, 0, 'Luật học (VUL)', 'student'),
        ('25090221', 'Sinh viên 4', 0, 0, 'Y đa khoa (UMP)', 'student'),
        ('23071100', 'Sinh viên 5', 120, 0, 'Sư phạm Tiếng Anh (ULIS)', 'student'),
        ('24080334', 'Sinh viên 6', 35, 5, 'Quản trị kinh doanh (HSB)', 'student'),
    ]
    for u in sample_users:
        c.execute("INSERT OR IGNORE INTO users (username, full_name, vnu_credit, vnu_token, major, role) VALUES (?, ?, ?, ?, ?, ?)", u)
        
    conn.commit()
    return conn

def reward_user(username, amount):
    conn = init_db()
    c = conn.cursor()
    c.execute("UPDATE users SET vnu_credit = vnu_credit + ?, vnu_token = vnu_token + ? WHERE username = ?", (amount, amount, username))
    conn.commit()

def change_doc_status(doc_id, new_status):
    conn = init_db()
    c = conn.cursor()
    c.execute("UPDATE documents SET status = ? WHERE id = ?", (new_status, doc_id))
    conn.commit()

# ==========================================
# 2. KHỞI TẠO SESSION STATE (QUẢN LÝ ĐĂNG NHẬP)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.role = None
    st.session_state.full_name = None

# ==========================================
# 3. GIAO DIỆN WEB CHÍNH (UI)
# ==========================================
st.set_page_config(page_title="VNU S-Connect | Nền tảng Học tập", layout="wide", page_icon="🎓")
conn = init_db()

st.title("🎓 VNU S-CONNECT")
st.markdown("*Hệ sinh thái tri thức và Kết nối học tập nội bộ ĐHQGHN*")

# --- THANH BÊN: ĐĂNG NHẬP / ĐĂNG XUẤT ---
with st.sidebar:
    if not st.session_state.logged_in:
        st.header("🔐 Đăng nhập hệ thống")
        st.caption("@vnu.edu.vn")
        
        msv_input = st.text_input("Tên đăng nhập:")
        pass_input = st.text_input("Mật khẩu:", type="password", help="Bản demo: Nhập mật khẩu bất kỳ")
        
        st.info("Gợi ý test:\n- Admin: **vnusconnect**\n- Sinh viên: **25022976**")
        
        if st.button("Đăng nhập"):
            df_user = pd.read_sql_query(f"SELECT * FROM users WHERE username='{msv_input}'", conn)
            if not df_user.empty:
                st.session_state.logged_in = True
                st.session_state.current_user = df_user['username'][0]
                st.session_state.full_name = df_user['full_name'][0]
                st.session_state.role = df_user['role'][0]
                st.rerun() 
            else:
                st.error("Tài khoản không tồn tại trong hệ thống!")
    else:
        st.header("👤 Không gian cá nhân")
        st.write(f"Xin chào, **{st.session_state.full_name}**")
        
        if st.session_state.role == 'admin':
            st.error("🔥 BẠN LÀ QUẢN TRỊ VIÊN (ADMIN)")
        else:
            st.success("🎓 Sinh viên ĐHQGHN")
            
        df_points = pd.read_sql_query(f"SELECT vnu_credit, vnu_token FROM users WHERE username='{st.session_state.current_user}'", conn)
        st.divider()
        st.info(f"🌟 **VNU-Credit**: **{df_points['vnu_credit'][0]}**")
        st.warning(f"🪙 **VNU-Token**: **{df_points['vnu_token'][0]}**")
        
        if st.button("Đăng xuất"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.role = None
            st.session_state.full_name = None
            st.rerun()

if not st.session_state.logged_in:
    st.warning("👈 Vui lòng đăng nhập ở thanh công cụ bên trái để truy cập hệ thống.")
    st.stop() 

# ---------------------------------------------------------
# GIAO DIỆN DÀNH CHO ADMIN
# ---------------------------------------------------------
if st.session_state.role == 'admin':
    tab_duyet, tab_qltv = st.tabs(["🛡️ Quản lý & Phê duyệt Bài đăng", "📚 Quản lý toàn bộ Thư viện"])
    
    with tab_duyet:
        # CƠ CHẾ ĐỒNG BỘ: Fragment tự động chạy lại ngầm mỗi 1.5 giây
        @st.fragment(run_every=1.5)
        def view_pending_documents():
            st.subheader("Danh sách Tài liệu Chờ phê duyệt")
            df_pending = pd.read_sql_query("SELECT * FROM documents WHERE status='pending'", conn)
            
            if not df_pending.empty:
                for _, row in df_pending.iterrows():
                    with st.expander(f"🔴 [CHỜ DUYỆT] {row['title']} - Đăng bởi: {row['uploader']}", expanded=True):
                        st.write(f"**Mã HP:** {row['subject_code']} | **Đơn vị:** {row['category']}")
                        st.markdown(f"[🔗 Kiểm tra nội dung]({row['drive_link']})")
                        
                        col1, col2, col3 = st.columns([1, 1, 4])
                        with col1:
                            if st.button("✅ Phê duyệt", key=f"app_{row['id']}"):
                                change_doc_status(row['id'], 'approved')
                                reward_user(row['uploader'], 10) 
                                st.toast(f"Đã duyệt bài và cộng điểm cho {row['uploader']}!")
                                st.rerun()
                        with col2:
                            if st.button("❌ Từ chối", key=f"rej_{row['id']}"):
                                change_doc_status(row['id'], 'rejected')
                                st.toast("Đã từ chối tài liệu này.")
                                st.rerun()
            else:
                st.success("Hiện không có bài đăng nào cần phê duyệt.")
        
        # Gọi hàm fragment
        view_pending_documents()

    with tab_qltv:
        @st.fragment(run_every=5)
        def view_all_library():
            st.subheader("Kho dữ liệu hệ thống")
            st.dataframe(pd.read_sql_query("SELECT id, title, uploader, status, timestamp FROM documents", conn), use_container_width=True)
        view_all_library()

# ---------------------------------------------------------
# GIAO DIỆN DÀNH CHO SINH VIÊN (STUDENT)
# ---------------------------------------------------------
else:
    tab_lib, tab_upload, tab_mentor, tab_ranking = st.tabs([
        "📚 Thư viện", 
        "📤 Đóng góp Tài liệu", 
        "🤝 Mentor", 
        "🏆 Bảng vàng"
    ])
    
    with tab_lib:
        # CƠ CHẾ ĐỒNG BỘ: Fragment tự động chạy lại ngầm mỗi 3 giây
        @st.fragment(run_every=1.5)
        def view_student_library():
            st.subheader("📚 Kho tài liệu học thuật")
            search_query = st.text_input("🔍 Tìm kiếm theo Mã học phần (VD: MAT1092, INT2204...):", "").strip()
            st.markdown("---")
            
            query_docs = """
                SELECT d.*, u.full_name AS uploader_name, u.vnu_credit AS uploader_credit
                FROM documents d
                JOIN users u ON d.uploader = u.username
                WHERE d.status = 'approved'
                ORDER BY d.upvotes DESC
            """
            df_docs = pd.read_sql_query(query_docs, conn)
            
            if search_query:
                filtered_docs = df_docs[df_docs['subject_code'].str.contains(search_query, case=False, na=False)]
            else:
                filtered_docs = df_docs

            if not filtered_docs.empty:
                for _, row in filtered_docs.iterrows():
                    stars_count = min(5, (row['upvotes'] // 5) + 1) if row['upvotes'] > 0 else 0
                    star_display = "⭐" * stars_count if stars_count > 0 else "😶 *Chưa có đánh giá*"

                    with st.expander(f"📄 {row['title']} | Mã HP: {row['subject_code']}"):
                        col_info, col_vote = st.columns([3, 1])

                        with col_info:
                            st.write(f"**🏫 Đơn vị:** {row['category']}")
                            st.write(f"**👤 Người đăng:** {row['uploader_name']} (Credit: {row['uploader_credit']})")
                            st.write(f"**📅 Ngày đăng:** {row['timestamp']}")
                            st.markdown(f"**Đánh giá:** {star_display} ({row['upvotes']} lượt)")
                            st.link_button("🚀 Mở tài liệu ", row['drive_link'], use_container_width=True)

                        with col_vote:
                            st.write("**Vote tài liệu này?**")
                            if st.button("✨ Tặng 1 Sao", key=f"star_{row['id']}"):
                                cursor = conn.cursor()
                                cursor.execute("UPDATE documents SET upvotes = upvotes + 1 WHERE id = ?", (row['id'],))
                                conn.commit()
                                reward_user(row['uploader'], 2)
                                st.toast(f"Bạn đã tặng 1 sao cho tài liệu '{row['title']}'!")
                                st.rerun()
                        st.caption("Gợi ý: Tài liệu có nhiều sao sẽ được ưu tiên hiển thị lên đầu bảng.")
            else:
                if search_query:
                    st.info(f"Không tìm thấy tài liệu nào cho Mã học phần: **{search_query}**")
                else:
                    st.info("Hiện chưa có tài liệu nào được phê duyệt.")
        
        # Gọi hàm fragment
        view_student_library()

    with tab_upload:
        st.subheader("📤 Chia sẻ tài liệu")
        st.markdown("---")
        st.info("Tài liệu của bạn sẽ được gửi tới Ban Cố Vấn để kiểm duyệt.")
        
        doc_title = st.text_input("Tên tài liệu:")
        subject_code = st.text_input("Mã học phần:")
        category = st.selectbox("Thuộc đơn vị quản lý môn học:", ["VNU-UET", "VNU-USSH", "VNU-HUS", "VNU-UEB", "VNU-ULIS", "VNU-UED", "VNU-VJU", "VNU-UMP", "VNU-UL", "VNU"])
        drive_link = st.text_input("Link tài liệu:")
        
        if st.button("Gửi chờ duyệt"):
            if doc_title and subject_code and drive_link:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO documents (uploader, title, subject_code, category, drive_link, timestamp, upvotes, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                          (st.session_state.current_user, doc_title, subject_code.upper(), category, drive_link, now, 0, 'pending'))
                conn.commit()
                st.success("Tải lên thành công! Yêu cầu của bạn đã được gửi.")
            else:
                st.warning("Vui lòng điền đầy đủ các trường thông tin.")
                
    with tab_mentor:
        st.subheader("🤝 Kết nối sinh viên")
        st.markdown("---")
        action = st.radio("Bạn muốn làm gì?", ["Tìm Mentor / Đồng đội", "Đăng ký làm Mentor"])
        if action == "Tìm Mentor / Đồng đội":
            query_mentor = "SELECT m.*, u.full_name, u.vnu_credit, u.major, u.role FROM mentors m JOIN users u ON m.username = u.username WHERE m.status = 'Sẵn sàng'"
            df_mentors = pd.read_sql_query(query_mentor, conn)
            if not df_mentors.empty:
                for _, m in df_mentors.iterrows():
                    role_vn = "🛡️ Quản trị viên" if m['role'] == 'admin' else "🎓 Sinh viên"
                    with st.expander(f"**👤 Mentor:** {m['full_name']} | **⭐ Điểm uy tín:** {m['vnu_credit']} PT | 📍 {m['location']}"):
                        st.markdown(f"**Vai trò:** {role_vn}")
                        st.write(f"**Chuyên ngành:** {m['major']}")
                        st.write(f"**📚 Thế mạnh môn:** {m['strong_subjects']}")
                        st.write(f"**📞 Liên hệ:** {m['contact_info']}")
            else:
                st.info("Hiện tại chưa có Mentor nào đăng ký.")
        else:
            m_subjects = st.text_input("Môn học bạn đăng ký:")
            m_location = st.selectbox("Vị trí thường trực:", ["KTX Hòa Lạc (Khu B)", "KTX Hòa Lạc (Khu C)", "Thư viện ĐHQGHN", "Xuân Thủy", "Khác"])
            m_contact = st.text_input("Cách thức liên hệ (Zalo/Email/SĐT):")
            if st.button("Đăng ký ngay"):
                if m_subjects and m_contact:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO mentors (username, strong_subjects, location, contact_info, status) VALUES (?, ?, ?, ?, ?)",
                                   (st.session_state.current_user, m_subjects, m_location, m_contact, "Sẵn sàng"))
                    conn.commit()
                    st.success("Đăng ký thành công!")
                else:
                    st.warning("Vui lòng điền đủ thông tin.")

    with tab_ranking:
        @st.fragment(run_every=10)
        def view_leaderboard():
            st.subheader("🏆 Bảng vàng Tích lũy")
            st.markdown("---")
            df_leaderboard = pd.read_sql_query("SELECT full_name AS 'Họ và Tên', vnu_credit AS 'Điểm Danh Tiếng' FROM users WHERE role='student' ORDER BY vnu_credit DESC", conn)
            st.dataframe(df_leaderboard, use_container_width=True, hide_index=True)
        view_leaderboard()
