# Hướng Dẫn Thực Hành 01: Làm Chủ Burp Suite & Bẻ Khóa Lỗ Hổng Phân Quyền (Access Control)

> **Mục tiêu**: Nắm vững cách bắt gói tin bằng Burp Suite, tư duy khai thác lỗi phân quyền tầng Backend và hoàn thành 3 bài lab đầu tiên trên PortSwigger Academy.

---

## Phần 1: Thiết Lập Vũ Khí - Burp Suite Community Edition

### 1. Cài đặt & Khởi động
1. Tải bộ cài: [PortSwigger Burp Suite Community](https://portswigger.net/burp/communitydownload).
2. Chạy file cài đặt, chọn mặc định cho đến khi hoàn tất.
3. Mở phần mềm:
   - Màn hình khởi động chọn **Temporary project** ➔ Bấm **Next**.
   - Chọn **Use Burp defaults** ➔ Bấm **Start Burp**.

### 2. Mẹo sử dụng Embedded Chromium (Không cần cấu hình chứng chỉ CA)
* Vào tab **Proxy** ➔ chọn tab con **Intercept**.
* Nhìn sang phải có nút màu cam: **Open Browser**. Bấm vào đây.
* Burp sẽ bật một trình duyệt Chromium độc lập:
  - Đã tích hợp sẵn Certificate của PortSwigger.
  - Mọi request trên trình duyệt này đều tự động đi qua Burp Suite.
  - Không ảnh hưởng đến Chrome/Edge cá nhân của bạn.

### 3. Phím tắt & 4 Tab quyền lực nhất trong Burp Suite mà Dev cần nhớ
- **Proxy > HTTP History**: Xem toàn bộ lịch sử các request/response mà app vừa gửi đi (thay thế tab Network của F12).
- **Repeater (`Ctrl + R`)**: Tính năng quan trọng nhất! Đứng ở HTTP History, chọn request nghi vấn, ấn `Ctrl + R` để bắn nó sang tab Repeater. Tại đây bạn có thể tùy ý sửa Header, Cookie, Payload JSON rồi ấn **Send** để xem backend phản hồi ra sao.
- **Intruder (`Ctrl + I`)**: Dùng để Fuzzing (brute-force password, dò tìm parameter ẩn, quét dải ID `1` đến `1000`).
- **Decoder**: Giải mã Base64, URL encode, Hash nhanh chóng mà không cần mở website bên ngoài.

---

## Phần 2: Thực Hành Giải 3 Bài Lab Access Control (PortSwigger)

Đăng ký tài khoản miễn phí tại: [PortSwigger Web Security Academy](https://portswigger.net/web-security).

---

### 🟢 LAB 1: Unprotected admin functionality (Bảo mật bằng sự che giấu - Security through Obscurity)
* **Link lab**: [Unprotected admin functionality](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality)
* **Mức độ**: Dễ (Apprentice)
* **Mục tiêu**: Truy cập vào trang Admin chưa được phân quyền và xóa tài khoản của user `carlos`.

#### 🔍 Góc nhìn Phân tích:
- **Lỗi của Dev**: Dev tạo trang admin nhưng không viết middleware kiểm tra quyền admin trên route đó. Dev nghĩ: *"Mình chỉ giấu link trên giao diện, user bình thường không biết URL thì không vào được"*. Thậm chí dev còn thêm URL này vào `robots.txt` để dặn bot tìm kiếm không quét.
- **Tư duy Breaker**: File `/robots.txt` là file công khai ai cũng đọc được. Hacker luôn kiểm tra `/robots.txt` đầu tiên để xem dev "cấm" cái gì, vì chỗ cấm thường là chỗ quan trọng.

#### 🛠️ Các bước giải quyết:
1. Mở link bài lab trong trình duyệt của Burp Suite.
2. Thêm `/robots.txt` vào sau URL bài lab (Ví dụ: `https://<lab-id>.web-security-academy.net/robots.txt`).
3. Đọc nội dung file trả về:
   ```text
   User-agent: *
   Disallow: /administrator-panel
   ```
4. Copy đường dẫn `/administrator-panel` dán lên trình duyệt.
5. Trang quản trị hiện ra mà không hề đòi hỏi mật khẩu admin! Bấm nút **Delete** ở dòng tài khoản `carlos`.
6. **Kết quả**: Thông báo **Congratulations, you solved the lab!** hiện lên.

#### 🛡️ Cách vá chuẩn ở tầng Backend (Node / Java / Go / .NET):
Không bao giờ dựa vào việc giấu URL. Mọi request đến endpoint admin đều phải đi qua **Authorization Middleware**:
```go
// Ví dụ Go (Gin Framework)
adminRoutes := r.Group("/admin")
adminRoutes.Use(AuthMiddleware(), RequireRole("ADMIN"))
{
    adminRoutes.DELETE("/users/:id", deleteUserHandler)
}
```

---

### 🟢 LAB 2: User role controlled by request parameter (Tham số phân quyền phía Client)
* **Link lab**: [User role controlled by request parameter](https://portswigger.net/web-security/access-control/lab-user-role-controlled-by-request-parameter)
* **Mức độ**: Dễ (Apprentice)
* **Tài khoản cấp sẵn**: `wiener` / `peter`
* **Mục tiêu**: Đăng nhập bằng `wiener`, nâng quyền lên admin và xóa tài khoản `carlos`.

#### 🔍 Góc nhìn Phân tích:
- **Lỗi của Dev**: Khi user đăng nhập thành công, backend gán quyền vào Cookie và gửi về cho browser: `Cookie: Admin=false`. Khi user gửi request tiếp theo, backend lại đọc chính cookie này để quyết định user có phải admin hay không!
- **Tư duy Breaker**: Mọi thứ nằm trên Client (Cookie, LocalStorage, Hidden input, Header) đều do kẻ tấn công toàn quyền chỉnh sửa.

#### 🛠️ Các bước giải quyết:
1. Mở bài lab, bấm **My account**, đăng nhập với `wiener:peter`.
2. Mở Burp Suite, vào tab **Proxy > HTTP history**, tìm request `POST /login` hoặc `GET /my-account`.
3. Nhìn vào Cookie trong Request/Response, bạn sẽ thấy:
   ```http
   Cookie: session=xxxx; Admin=false
   ```
4. Bấm chuột phải vào request ➔ chọn **Send to Repeater** (hoặc `Ctrl + R`).
5. Trong tab Repeater, sửa:
   ```http
   Cookie: session=xxxx; Admin=true
   ```
6. Bấm **Send**, xem Response trả về thấy xuất hiện link `/admin`.
7. Quay lại trình duyệt Burp, mở F12 (Application > Cookies) hoặc dùng tiện ích chỉnh sửa Cookie, đổi giá trị `Admin` từ `false` thành `true`.
8. Tải lại trang (F5) ➔ xuất hiện **Admin panel** ➔ Vào xóa tài khoản `carlos` ➔ **Solved!**

#### 🛡️ Cách vá chuẩn ở tầng Backend:
Không bao giờ tin tưởng Role do client gửi lên trong cookie thô. Phải lưu session ở server (Redis/DB) hoặc dùng **Signed JWT** mà secret key được bảo vệ bí mật ở server:
```csharp
// Ví dụ .NET: Chỉ đọc Claims từ Token đã được Server xác thực chữ ký (Signature)
[Authorize(Roles = "Admin")]
[HttpDelete("api/users/{id}")]
public IActionResult DeleteUser(int id) { ... }
```

---

### 🟢 LAB 3: Insecure direct object references (IDOR)
* **Link lab**: [Insecure direct object references](https://portswigger.net/web-security/access-control/lab-insecure-direct-object-references)
* **Mức độ**: Dễ (Apprentice)
* **Mục tiêu**: Tìm lịch sử chat của user khác để tìm mật khẩu của tài khoản `carlos`, sau đó đăng nhập bằng `carlos`.

#### 🔍 Góc nhìn Phân tích:
- **Lỗi của Dev**: Khi user tải file lịch sử chat, backend gọi file theo số thứ tự tăng dần: `/download-transcript/1.txt`, `/download-transcript/2.txt` mà không kiểm tra xem file đó có thuộc phiên làm việc của user hiện tại hay không.
- **Tư duy Breaker**: Thay đổi ID liên tục (1, 2, 3,...) để đọc trộm dữ liệu nhạy cảm của toàn bộ người dùng khác.

#### 🛠️ Các bước giải quyết:
1. Vào lab, bấm vào tính năng **Live chat**.
2. Gửi một tin nhắn bất kỳ (ví dụ: `hello`).
3. Bấm nút **View transcript** để tải file log chat về máy.
4. Mở Burp Suite ➔ **Proxy > HTTP history**, tìm request tải transcript:
   ```http
   GET /download-transcript/2.txt HTTP/1.1
   ```
5. Gửi request sang **Repeater** (`Ctrl + R`).
6. Sửa số `2.txt` thành `1.txt` và bấm **Send**.
7. Đọc nội dung Response của file `1.txt`, bạn sẽ thấy một đoạn chat trước đó có chứa password của `carlos`!
8. Dùng password vừa trộm được quay lại trang **My account**, đăng nhập `carlos` ➔ **Solved!**

---

## Checklist Hoàn Thành Của Bạn
- [x] Tải và mở được Burp Suite Community.
- [x] Bật được Embedded Browser và bắt được request.
- [x] Giải quyết xong Lab 1.
- [x] Giải quyết xong Lab 2.
- [x] Giải quyết xong Lab 3.
