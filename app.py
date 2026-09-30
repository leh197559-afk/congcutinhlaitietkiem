import streamlit as st
import pandas as pd

# =========================
# CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="Tính lãi tiền gửi tiết kiệm",
    page_icon="💰",
    layout="wide"
)

# =========================
# CSS GIAO DIỆN
# =========================
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    .sub-title {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }

    .result-box {
        padding: 20px;
        border-radius: 12px;
        background-color: #f5f7fa;
        text-align: center;
        border: 1px solid #ddd;
    }

    .result-title {
        font-size: 16px;
        color: #555;
        margin-bottom: 8px;
    }

    .result-value {
        font-size: 25px;
        font-weight: bold;
    }

    .info-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #eef6ff;
        border-left: 5px solid #2196F3;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# TIÊU ĐỀ
# =========================
st.markdown(
    '<div class="main-title">💰 MÁY TÍNH LÃI TIỀN GỬI TIẾT KIỆM</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Tính lãi đơn và lãi kép theo tháng, quý hoặc cuối kỳ</div>',
    unsafe_allow_html=True
)

# =========================
# NHẬP DỮ LIỆU
# =========================
st.header("📋 Thông tin tiền gửi")

col1, col2 = st.columns(2)

with col1:
    so_tien = st.number_input(
        "💵 Số tiền gửi (VNĐ)",
        min_value=1000.0,
        value=100_000_000.0,
        step=1_000_000.0,
        format="%.0f"
    )

    ky_han = st.number_input(
        "📅 Kỳ hạn (tháng)",
        min_value=1,
        max_value=1200,
        value=12,
        step=1
    )

    lai_suat = st.number_input(
        "📈 Lãi suất (%/năm)",
        min_value=0.0,
        max_value=100.0,
        value=6.0,
        step=0.01,
        format="%.2f"
    )

with col2:
    loai_lai = st.selectbox(
        "🔢 Hình thức tính lãi",
        [
            "Lãi đơn",
            "Lãi kép"
        ]
    )

    hinh_thuc_lanh = st.selectbox(
        "💳 Hình thức nhận lãi",
        [
            "Lãnh lãi theo tháng",
            "Lãnh lãi theo quý",
            "Lãnh lãi cuối kỳ"
        ]
    )

    st.markdown("""
    <div class="info-box">
        <b>💡 Lưu ý:</b><br>
        Lãi suất được nhập theo %/năm.
        Kỳ hạn được tính theo số tháng.
    </div>
    """, unsafe_allow_html=True)


# =========================
# HÀM ĐỊNH DẠNG TIỀN
# =========================
def format_money(value):
    return f"{value:,.0f} VNĐ".replace(",", ".")


# =========================
# TÍNH TOÁN
# =========================

# Lãi suất dạng thập phân
lai_suat_nam = lai_suat / 100

# Tổng số tháng
tong_thang = int(ky_han)

# Xác định chu kỳ nhận lãi
if hinh_thuc_lanh == "Lãnh lãi theo tháng":
    chu_ky = 1
elif hinh_thuc_lanh == "Lãnh lãi theo quý":
    chu_ky = 3
else:
    chu_ky = tong_thang


# =========================
# LÃI ĐƠN
# =========================
def tinh_lai_don():
    """
    Lãi đơn:
    Tiền lãi = Gốc × lãi suất × thời gian
    """

    danh_sach = []

    so_du = so_tien
    tong_lai = 0

    # Trường hợp lãnh lãi cuối kỳ
    if hinh_thuc_lanh == "Lãnh lãi cuối kỳ":

        lai = so_tien * lai_suat_nam * (tong_thang / 12)

        tong_lai = lai

        danh_sach.append({
            "Kỳ": 1,
            "Thời gian": f"{tong_thang} tháng",
            "Tiền gốc": so_tien,
            "Tiền lãi kỳ này": lai,
            "Tổng tiền nhận": so_tien + lai
        })

    else:

        so_ky = tong_thang // chu_ky

        lai_moi_ky = so_tien * lai_suat_nam * (chu_ky / 12)

        for i in range(1, so_ky + 1):

            tong_lai += lai_moi_ky

            danh_sach.append({
                "Kỳ": i,
                "Thời gian": f"{i * chu_ky} tháng",
                "Tiền gốc": so_tien,
                "Tiền lãi kỳ này": lai_moi_ky,
                "Tổng tiền nhận": so_tien + lai_moi_ky
            })

    return tong_lai, danh_sach


# =========================
# LÃI KÉP
# =========================
def tinh_lai_kep():
    """
    Lãi kép:
    Tiền lãi được cộng vào vốn sau mỗi kỳ.

    Công thức:
    A = P × (1 + r)^n

    Trong đó:
    P = tiền gốc
    r = lãi suất mỗi kỳ
    n = số kỳ
    """

    danh_sach = []

    so_du = so_tien
    tong_lai = 0

    # ---------------------------------
    # LÃNH LÃI CUỐI KỲ
    # ---------------------------------
    if hinh_thuc_lanh == "Lãnh lãi cuối kỳ":

        lai_suat_ky = lai_suat_nam / 12
        so_ky = tong_thang

        for i in range(1, so_ky + 1):

            tien_lai = so_du * lai_suat_ky
            so_du += tien_lai
            tong_lai += tien_lai

            danh_sach.append({
                "Kỳ": i,
                "Thời gian": f"{i} tháng",
                "Tiền gốc đầu kỳ": so_du - tien_lai,
                "Tiền lãi kỳ này": tien_lai,
                "Số dư cuối kỳ": so_du
            })

    # ---------------------------------
    # LÃNH LÃI THEO THÁNG / QUÝ
    # ---------------------------------
    else:

        so_ky = tong_thang // chu_ky

        # Lãi suất của mỗi chu kỳ
        lai_suat_ky = lai_suat_nam * (chu_ky / 12)

        for i in range(1, so_ky + 1):

            tien_lai = so_du * lai_suat_ky

            tong_lai += tien_lai

            so_du += tien_lai

            danh_sach.append({
                "Kỳ": i,
                "Thời gian": f"{i * chu_ky} tháng",
                "Tiền gốc đầu kỳ": so_du - tien_lai,
                "Tiền lãi kỳ này": tien_lai,
                "Số dư cuối kỳ": so_du
            })

    return tong_lai, danh_sach


# =========================
# NÚT TÍNH
# =========================
st.divider()

if st.button("🧮 TÍNH TIỀN LÃI", type="primary", use_container_width=True):

    # Kiểm tra dữ liệu
    if so_tien <= 0:
        st.error("Số tiền gửi phải lớn hơn 0.")
        st.stop()

    if lai_suat < 0:
        st.error("Lãi suất không được âm.")
        st.stop()

    # Tính toán
    if loai_lai == "Lãi đơn":
        tong_lai, danh_sach = tinh_lai_don()
    else:
        tong_lai, danh_sach = tinh_lai_kep()

    tong_tien = so_tien + tong_lai

    # =========================
    # HIỂN THỊ KẾT QUẢ
    # =========================
    st.header("📊 Kết quả tính toán")

    # Tiền lãi định kỳ
    if hinh_thuc_lanh == "Lãnh lãi cuối kỳ":
        tien_lai_dinh_ky = tong_lai
    else:
        if len(danh_sach) > 0:
            tien_lai_dinh_ky = danh_sach[0]["Tiền lãi kỳ này"]
        else:
            tien_lai_dinh_ky = 0

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="result-box">
            <div class="result-title">💵 Tiền lãi định kỳ</div>
            <div class="result-value">%s</div>
        </div>
        """ % format_money(tien_lai_dinh_ky),
        unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="result-box">
            <div class="result-title">📈 Tổng tiền lãi</div>
            <div class="result-value">%s</div>
        </div>
        """ % format_money(tong_lai),
        unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="result-box">
            <div class="result-title">💰 Tổng gốc + lãi</div>
            <div class="result-value">%s</div>
        </div>
        """ % format_money(tong_tien),
        unsafe_allow_html=True)

    # =========================
    # THÔNG TIN TÓM TẮT
    # =========================
    st.subheader("📝 Thông tin khoản gửi")

    thong_tin = pd.DataFrame({
        "Thông tin": [
            "Số tiền gửi",
            "Kỳ hạn",
            "Lãi suất",
            "Hình thức tính",
            "Hình thức nhận lãi"
        ],
        "Giá trị": [
            format_money(so_tien),
            f"{tong_thang} tháng",
            f"{lai_suat:.2f}%/năm",
            loai_lai,
            hinh_thuc_lanh
        ]
    })

    st.table(thong_tin)

    # =========================
    # BẢNG CHI TIẾT
    # =========================
    st.subheader("📋 Chi tiết tiền lãi")

    df = pd.DataFrame(danh_sach)

    # Định dạng số tiền
    for column in df.columns:
        if any(keyword in column for keyword in [
            "Tiền gốc",
            "Tiền lãi",
            "Tổng tiền",
            "Số dư"
        ]):
            df[column] = df[column].apply(format_money)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # KẾT LUẬN
    # =========================
    st.success(
        f"🎉 Sau {tong_thang} tháng, "
        f"bạn nhận được tổng cộng **{format_money(tong_tien)}**, "
        f"trong đó tiền lãi là **{format_money(tong_lai)}**."
    )

# =========================
# CÔNG THỨC
# =========================
with st.expander("📚 Xem công thức tính"):

    st.markdown("""
### 1. Lãi đơn

Lãi đơn không cộng tiền lãi vào tiền gốc để tiếp tục tính lãi.

**Công thức:**

> Tiền lãi = Tiền gốc × Lãi suất năm × Số tháng / 12

---

### 2. Lãi kép

Lãi kép cộng tiền lãi vào tiền gốc sau mỗi kỳ để tiếp tục tính lãi cho kỳ tiếp theo.

**Công thức tổng quát:**

> Tổng tiền = Tiền gốc × (1 + lãi suất mỗi kỳ) ^ số kỳ

---

### 3. Lãnh lãi theo tháng

Tiền lãi được tính và nhận sau mỗi tháng.

### 4. Lãnh lãi theo quý

Tiền lãi được tính và nhận sau mỗi 3 tháng.

### 5. Lãnh lãi cuối kỳ

Toàn bộ tiền lãi được tính cho toàn bộ kỳ hạn và nhận khi đáo hạn.
""")

st.divider()

st.caption("💰 Ứng dụng tính lãi tiền gửi tiết kiệm bằng Streamlit")
