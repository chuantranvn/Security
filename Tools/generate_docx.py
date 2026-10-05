import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def add_callout(doc, text_list, title="LƯU Ý / GÓC NHÌN BREAKER"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F0F7FF")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border only
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="2563EB"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_title = p.add_run(f"💡 {title}\n")
    run_title.bold = True
    run_title.font.name = "Segoe UI"
    run_title.font.size = Pt(10.5)
    run_title.font.color.rgb = RGBColor(37, 99, 235)
    
    for line in text_list:
        p2 = cell.add_paragraph()
        p2.paragraph_format.space_before = Pt(1)
        p2.paragraph_format.space_after = Pt(2)
        r = p2.add_run(line)
        r.font.name = "Segoe UI"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(30, 41, 59)
    
    # Empty space after table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="E2E8F0"/>
            <w:left w:val="single" w:sz="6" w:space="0" w:color="E2E8F0"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="E2E8F0"/>
            <w:right w:val="single" w:sz="6" w:space="0" w:color="E2E8F0"/>
        </w:tcBorders>
    ''')
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(15, 23, 42)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def build_document():
    doc = docx.Document()
    
    # Page Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Styles
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Segoe UI'
    font.size = Pt(11)
    font.color.rgb = RGBColor(30, 41, 59)
    
    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("NHẬT KÝ ĐÀO TẠO & THỰC HÀNH BẢO MẬT WEB\n(DEV SANG APPSEC / PENTEST)")
    r_title.bold = True
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(22)
    r_title.font.color.rgb = RGBColor(30, 64, 175) # #1E40AF
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(24)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Hồ sơ ghi nhận toàn bộ quá trình trao đổi, giải đáp kỹ thuật, tư duy khai thác và hướng dẫn 15 bài Lab PortSwigger")
    r_sub.italic = True
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    # Metadata Box
    meta_table = doc.add_table(rows=3, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Học viên / Lập trình viên:", "Adjim"),
        ("Mục tiêu đào tạo:", "Chuyển đổi Backend Dev sang AppSec / Penetration Tester chuyên nghiệp"),
        ("Tổng số Lab thực hành đã hoàn thành:", "15 bài Labs (Cơ bản Apprentice & Nâng cao Practitioner)"),
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        c1 = meta_table.cell(row_idx, 0)
        c2 = meta_table.cell(row_idx, 1)
        c1.width = Inches(2.6)
        c2.width = Inches(3.9)
        c1.paragraphs[0].add_run(k).bold = True
        c2.paragraphs[0].add_run(v)
        set_cell_background(c1, "F1F5F9")
        set_cell_background(c2, "FFFFFF")
        set_cell_margins(c1, 80, 80, 120, 120)
        set_cell_margins(c2, 80, 80, 120, 120)
        
    p_sep = doc.add_paragraph()
    p_sep.paragraph_format.space_after = Pt(18)

    # Helper function for Section Headings
    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(20)
        h.paragraph_format.space_after = Pt(8)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.bold = True
        r.font.name = "Segoe UI"
        r.font.size = Pt(16)
        r.font.color.rgb = RGBColor(30, 64, 175)
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.bold = True
        r.font.name = "Segoe UI"
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(15, 118, 110) # Teal
        return h

    def add_bullet(p_or_text, bold_prefix="", text=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(3)
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.bold = True
        if text:
            p.add_run(text)
        return p

    # --- PHẦN 1: TỔNG QUAN LỘ TRÌNH VÀ VŨ KHÍ ---
    add_h1("1. TỔNG QUAN LỘ TRÌNH & THIẾT LẬP VŨ KHÍ BURP SUITE")
    
    p = doc.add_paragraph()
    p.add_run("Cuộc hội thoại khởi đầu với việc xác định lộ trình học tập toàn diện từ một Backend Developer hướng đến vị trí Application Security (AppSec) / Pentest Engineer trong thời gian 6 - 9 tháng. Giai đoạn 1 tập trung xây dựng tư duy kẻ tấn công (Breaker Mindset) kết hợp với công cụ thực chiến hàng đầu ngành bảo mật: Burp Suite Community Edition.")
    
    add_h2("4 Vũ Khí Quyền Lực Nhất Trong Burp Suite:")
    add_bullet("", "Proxy > HTTP History: ", "Theo dõi toàn bộ lịch sử các request/response HTTP/HTTPS mà ứng dụng gửi đi, thay thế và vượt trội hơn tab Network của DevTools.")
    add_bullet("", "Repeater (Ctrl + R): ", "Tính năng quan trọng nhất của dân AppSec. Cho phép cô lập một request cụ thể, tự do chỉnh sửa Header, Cookie, Method, Request Body và gửi đi gửi lại nhiều lần để quan sát phản hồi.")
    add_bullet("", "Intruder (Ctrl + I): ", "Công cụ Fuzzing tự động cực mạnh. Cho phép đánh dấu vị trí payload bằng ký hiệu §...§ để brute-force tham số, quét dải IP nội bộ hoặc dò mật khẩu.")
    add_bullet("", "Decoder: ", "Công cụ giải mã nhanh URL encode, Base64, Hex, HTML entity ngay trong phần mềm.")

    # --- PHẦN 2: CHUYÊN ĐỀ 01 - ACCESS CONTROL CĂN BẢN ---
    add_h1("2. CHUYÊN ĐỀ 01: PHÂN QUYỀN CƠ BẢN (ACCESS CONTROL & IDOR)")
    
    p = doc.add_paragraph()
    p.add_run("Trong học phần đầu tiên, học viên đã hoàn thành 3 bài Lab cấp độ Apprentice, vạch trần sai lầm kinh điển của lập trình viên khi cho rằng 'người dùng không thấy link thì sẽ không truy cập được'.")

    add_bullet("", "Lab 1: Unprotected Admin Functionality (Security through Obscurity): ", "Lập trình viên giấu link quản trị /administrator-panel và chặn bot bằng robots.txt. Breaker chỉ cần đọc robots.txt để tìm ra endpoint nhạy cảm và truy cập trực tiếp xóa tài khoản carlos.")
    add_bullet("", "Lab 2: User Role Controlled by Request Parameter: ", "Backend cấp quyền bằng cách gửi Cookie thô: Cookie: Admin=false. Học viên dùng Repeater sửa thành Admin=true, leo thang đặc quyền (Privilege Escalation) lên admin.")
    add_bullet("", "Lab 3: Insecure Direct Object References (IDOR): ", "Tính năng tải lịch sử chat /download-transcript/2.txt không xác minh phiên làm việc. Học viên đổi tham số thành 1.txt để đọc trộm log chat chứa mật khẩu tài khoản carlos.")

    add_callout(doc, [
        "Nguyên tắc cốt lõi: Tuyệt đối không bao giờ tin tưởng bất kỳ dữ liệu nào đến từ phía Client (Cookie, LocalStorage, Hidden Input, URL Parameter).",
        "Mọi endpoint nhạy cảm bắt buộc phải được bảo vệ bằng Authorization Middleware ở tầng Backend (ví dụ RequireRole('ADMIN'))."
    ], title="BÀI HỌC VÀNG TỪ CHUYÊN ĐỀ 01")

    # --- PHẦN 3: CHUYÊN ĐỀ 02 - ACCESS CONTROL NÂNG CAO ---
    add_h1("3. CHUYÊN ĐỀ 02: BẺ KHÓA PHÂN QUYỀN NÂNG CAO (PRACTITIONER LEVEL)")
    
    p = doc.add_paragraph()
    p.add_run("Học viên tiếp tục giải quyết xuất sắc 3 bài Lab ở cấp độ Practitioner - mức độ khó tương đương kỳ thi chứng chỉ BSCP (Burp Suite Certified Practitioner).")

    add_bullet("", "Lab 4: User Role Can Be Modified in User Profile (Mass Assignment): ", "Khi người dùng cập nhật email qua API POST /my-account/change-email, Backend nhận toàn bộ JSON body và map thẳng vào User Model trong DB. Học viên chèn thêm trường \"roleid\": 2 vào JSON để tự thăng chức admin.")
    add_bullet("", "Lab 5: Method-based Access Control Can Be Circumvented: ", "Backend chỉ áp dụng middleware kiểm tra quyền quản trị trên HTTP method POST /admin-roles. Học viên dùng tính năng 'Change request method' của Burp để đổi thành GET /admin-roles?username=wiener&action=upgrade để vượt rào thành công.")
    add_bullet("", "Lab 6: URL-based Access Control Can Be Circumvented: ", "Phía trước hệ thống có Reverse Proxy chặn URL /admin. Tuy nhiên, Backend server hỗ trợ header ghi đè định tuyến X-Original-URL: /admin. Gửi request tới GET / kèm header này đã đánh lừa được Proxy và mở khóa trang quản trị.")

    # --- PHẦN 4: CHUYÊN ĐỀ 03 - TẤN CÔNG JWT ---
    add_h1("4. CHUYÊN ĐỀ 03: TẤN CÔNG & GIẢ MẠO TOKEN JWT (JSON WEB TOKENS)")
    
    p = doc.add_paragraph()
    p.add_run("JWT là chuẩn xác thực phổ biến nhất trong các kiến trúc Microservices và REST API hiện nay. Học phần này đi sâu vào 3 lỗ hổng cấu hình chết người của Backend:")

    add_bullet("", "Lab 7: JWT Authentication Bypass via Unverified Signature: ", "Backend lười chỉ gọi hàm jwt.decode() để lấy thông tin user mà không gọi jwt.verify(). Học viên chỉ việc sửa payload sub: wiener thành administrator, giữ nguyên chữ ký cũ và chiếm quyền admin.")
    add_bullet("", "Lab 8: JWT Authentication Bypass via Flawed Signature Verification (alg: none): ", "Học viên đổi Header thành {\"alg\":\"none\"} và xóa phần chữ ký ở đuôi (Header.Payload.). Thư viện Backend cấu hình sai tự động bỏ qua kiểm tra chữ ký.")
    add_bullet("", "Lab 9: Weak Signing Key Brute-Force: ", "Backend dùng Secret Key đối xứng quá yếu. Dùng danh sách từ khóa jwt.secrets.list để tìm ra Secret Key chính xác là 'secret1', sau đó dùng extension JWT Editor để tự ký một token quản trị hoàn toàn hợp lệ.")

    add_callout(doc, [
        "Vấn đề phát sinh & Lời giải: Học viên thắc mắc lệnh 'hashcat' chạy ở đâu? Hashcat vốn là tool chạy trên Linux/GPU, việc cài trên Windows rất phức tạp.",
        "Giải pháp nhanh chuẩn Dev: Đã lập trình sẵn file công cụ Python 'crack_jwt.py' sử dụng thư viện HMAC/Hashlib có sẵn trên máy để dò key chỉ trong 0.05 giây!",
        "Trong bài lab PortSwigger, Secret Key luôn là 'secret1' (Base64: c2VjcmV0MQ==)."
    ], title="CASE STUDY: GIẢI QUYẾT BÀI TOÁN CRACK JWT TRÊN WINDOWS")

    # --- PHẦN 5: CHUYÊN ĐỀ 04 - SSRF ---
    add_h1("5. CHUYÊN ĐỀ 04: SERVER-SIDE REQUEST FORGERY (SSRF)")
    
    p = doc.add_paragraph()
    p.add_run("SSRF là lỗ hổng biến chính máy chủ Backend thành 'con rối' để quay lại tấn công vào mạng nội bộ hoặc hạ tầng Cloud mà kẻ tấn công từ bên ngoài không thể chạm tới.")

    add_bullet("", "Lab 10: Basic SSRF Against Local Server: ", "Tính năng kiểm tra tồn kho nhận tham số stockApi. Học viên thay bằng http://localhost/admin/delete?username=carlos để ép máy chủ tự xóa tài khoản quản trị.")
    add_bullet("", "Lab 11: Basic SSRF Against Another Backend System: ", "Một server nội bộ ẩn giấu trong mạng LAN 192.168.0.X:8080. Học viên dùng Burp Intruder cấu hình payload Numbers từ 1 đến 255 để quét toàn bộ dải mạng, phát hiện IP nội bộ trả về 200 OK.")
    add_bullet("", "Lab 12: SSRF With Blacklist-Based Input Filter: ", "Backend cài blacklist chặn 127.0.0.1 và admin. Học viên áp dụng 2 kỹ thuật phá bộ lọc: Đổi 127.0.0.1 thành 127.1 và Double URL Encoding từ khóa admin thành %2561dmin.")

    add_callout(doc, [
        "Sự cố gặp phải khi dùng Burp Intruder: Lỗi 'No payload positions defined' khi bấm Start attack.",
        "Nguyên nhân: Trong Burp Suite, ký hiệu § không thể copy-paste như text thông thường.",
        "Cách khắc phục chuẩn: Bôi đen con số cần thay đổi bằng chuột và bấm nút 'Add §' trên thanh công cụ."
    ], title="KINH NGHIỆM THỰC HÀNH BURP INTRUDER")

    # --- PHẦN 6: PHƯƠNG PHÁP LUẬN BREAKER THỰC CHIẾN (PHẦN HỎI ĐÁP ĐẮT GIÁ) ---
    add_h1("6. PHƯƠNG PHÁP LUẬN BREAKER: LÀM SAO BIẾT BACKEND BỊ MISS Ở ĐÂU ĐỂ TẤN CÔNG?")
    
    p = doc.add_paragraph()
    p.add_run("Đây là câu hỏi trọng tâm nhất của học viên trước khi sang bài 5: 'Trong bài lab thì có sẵn đề bài và gợi ý, nhưng ngoài đời thật khi pentest một hệ thống web, làm sao để biết backend bị hổng ở đâu mà xâm nhập?'")
    p.add_run(" Dưới đây là 4 trụ cột phương pháp luận của chuyên gia bảo mật:")

    add_h2("Trụ cột 1: Nhận diện 'Mùi' của tính năng (Feature Smell & Attack Surface)")
    p_smell = doc.add_paragraph()
    p_smell.add_run("Mọi tính năng hiển thị trên giao diện đều phản chiếu một nghiệp vụ Backend cụ thể:")
    add_bullet("", "Tải link / preview / avatar / webhook: ", "Backend chắc chắn dùng HTTP client (axios, curl) ➔ Khả năng cao có SSRF.")
    add_bullet("", "Có URL ID / file transcript / invoice id: ", "Backend query theo ID ➔ Khả năng cao có IDOR / BOLA.")
    add_bullet("", "Form thanh toán, coupon, chuyển tiền: ", "Thao tác trừ tiền, ghi DB ➔ Nghi vấn Race Condition.")
    add_bullet("", "Bộ lọc, search, sorting cột dữ liệu: ", "Backend ghép câu truy vấn động ➔ Nghi vấn SQL Injection.")

    add_h2("Trụ cột 2: Kỹ thuật 'Thăm dò & Gây nhiễu' (Probing & Fuzzing)")
    p_probe = doc.add_paragraph()
    p_probe.add_run("Không tấn công ồ ạt, kẻ tấn công gửi các 'ký tự phá vỡ' (Probe) để kiểm tra phản ứng:")
    add_bullet("", "Gửi dấu nháy đơn ' hoặc \" : ", "Nếu web văng lỗi 500 hoặc báo cú pháp SQL ➔ Backend dính lỗi ghép chuỗi SQLi.")
    add_bullet("", "Gửi chuỗi template {{7*7}} hoặc ${7*7} : ", "Nếu web hiển thị số 49 ➔ Dính Server-Side Template Injection.")
    add_bullet("", "Đổi HTTP Method hoặc xóa Token : ", "Kiểm tra xem Middleware phân quyền có bị lọt lưới không.")

    add_h2("Trụ cột 3: Phân tích vi mô phản hồi (Differential Analysis)")
    add_bullet("", "Response Time (Thời gian phản hồi): ", "Gửi chuỗi delay pg_sleep(5), nếu server phản hồi chậm đúng 5 giây ➔ Chắc chắn dính Time-based Blind SQLi.")
    add_bullet("", "Content-Length & Error Verbosity: ", "So sánh kích thước gói tin và đọc chi tiết Stack Trace để đoán framework, ORM, hệ quản trị DB.")

    add_h2("Trụ cột 4: Tư duy 'Dev-to-Dev Empathy' (Lập trình viên thường lười ở đâu?)")
    p_dev = doc.add_paragraph()
    p_dev.add_run("Lợi thế lớn nhất của một Backend Dev khi học bảo mật là hiểu rõ tâm lý đồng nghiệp:")
    add_bullet("", "Lười tạo DTO riêng: ", "Hứng luôn toàn bộ request body vào Model DB ➔ Tạo ra Mass Assignment.")
    add_bullet("", "Tin tưởng Client-side validation: ", "Chỉ ẩn nút trên giao diện, quên viết middleware chặn route ở Backend.")
    add_bullet("", "Chỉ test đường thẳng (Happy Path): ", "Không bao giờ test trường hợp gửi 20 request trong 1 mili-giây hoặc truyền số lượng âm.")

    # --- PHẦN 7: CHUYÊN ĐỀ 05 - SQL INJECTION ---
    add_h1("7. CHUYÊN ĐỀ 05: ĐÁNH SẬP DATABASE VỚI SQL INJECTION (SQLi)")
    
    p = doc.add_paragraph()
    p.add_run("SQL Injection là 'ông vua' của các lỗ hổng Injection, xuất hiện khi lập trình viên trộn lẫn giữa Dữ liệu người dùng (Data) và Mã lệnh truy vấn (Code) thông qua việc ghép chuỗi thô.")

    add_bullet("", "Lab 13: SQL Injection in WHERE clause (Lấy dữ liệu ẩn): ", "Chèn payload ' OR 1=1-- vào tham số category để triệt tiêu điều kiện released = 1, phơi bày toàn bộ sản phẩm ẩn.")
    add_bullet("", "Lab 14: SQL Injection Login Bypass: ", "Nhập username là administrator'-- để vô hiệu hóa hoàn toàn phần kiểm tra mật khẩu, đăng nhập thẳng vào tài khoản admin.")
    add_bullet("", "Lab 15: SQL Injection UNION Attack: ", "Dùng UNION SELECT NULL, NULL-- để dò số lượng cột, sau đó dùng UNION SELECT username, password FROM users-- để rút cạn mật khẩu của toàn bộ cơ sở dữ liệu.")

    add_h2("Cách vá triệt để ở tầng Backend:")
    add_code_block(doc, "// Chuẩn mực: Luôn dùng Parameterized Queries (Prepared Statements)\n// Node.js (pg):\nawait pool.query('SELECT * FROM users WHERE username = $1', [username]);\n\n// Go Gin:\ndb.Query('SELECT * FROM users WHERE username = ? AND password = ?', username, password);\n\n// C# Dapper:\nconnection.QueryFirstOrDefaultAsync<User>('SELECT * FROM Users WHERE Username = @Username', new { Username = username });")

    # --- PHẦN 8: BẢNG TỔNG KẾT TIẾN ĐỘ ---
    add_h1("8. BẢNG TỔNG KẾT THÀNH TÍCH & TIẾN ĐỘ ĐÀO TẠO")
    
    summary_table = doc.add_table(rows=6, cols=4)
    summary_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers = ["Chuyên đề lỗ hổng", "Số bài Lab", "Cấp độ", "Trạng thái"]
    for i, h in enumerate(headers):
        cell = summary_table.cell(0, i)
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "1E40AF")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 100, 100, 120, 120)
        
    rows_data = [
        ("Access Control Cơ bản", "3 bài", "Apprentice", "✅ ĐÃ HOÀN THÀNH"),
        ("Access Control Nâng cao", "3 bài", "Practitioner", "✅ ĐÃ HOÀN THÀNH"),
        ("Tấn công Token JWT", "3 bài", "Practitioner", "✅ ĐÃ HOÀN THÀNH"),
        ("Tấn công nội bộ SSRF", "3 bài", "Practitioner", "✅ ĐÃ HOÀN THÀNH"),
        ("SQL Injection (SQLi)", "3 bài", "Practitioner", "✅ ĐÃ HOÀN THÀNH"),
    ]
    
    for row_idx, row_values in enumerate(rows_data, start=1):
        bg = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, val in enumerate(row_values):
            cell = summary_table.cell(row_idx, col_idx)
            r = cell.paragraphs[0].add_run(val)
            if col_idx == 3:
                r.bold = True
                if "ĐÃ HOÀN THÀNH" in val:
                    r.font.color.rgb = RGBColor(16, 185, 129) # Green
                else:
                    r.font.color.rgb = RGBColor(234, 88, 12) # Orange
            set_cell_background(cell, bg)
            set_cell_margins(cell, 90, 90, 110, 110)

    # Save to file
    out_dir = r"d:\Adjim Personal\Security"
    out_path = os.path.join(out_dir, "Nhat_Ky_Hoc_Tap_Va_Thuc_Hanh_Security.docx")
    doc.save(out_path)
    print(f"[SUCCESS] Đã tạo thành công file Word tại: {out_path}")

if __name__ == '__main__':
    build_document()
