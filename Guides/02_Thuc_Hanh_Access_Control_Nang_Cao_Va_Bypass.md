# Hướng Dẫn Thực Hành 02: Bẻ Khóa Phân Quyền Nâng Cao (Practitioner Level)

> **Mục tiêu**: Nâng cấp từ cấp độ Cơ bản (Apprentice) lên Trung cấp (Practitioner). Khai thác các lỗ hổng phân quyền tinh vi thường gặp ở Backend: **Mass Assignment (JSON Tampering)**, **HTTP Method Bypass**, và **Header Override (`X-Original-URL`)**.

---

## 💡 Tổng Quan: Tư Duy Phân Quyền Tầng Sâu (Beyond Basic IDOR)

Ở bài thực hành 01, bạn đã thấy những lỗi sơ đẳng (quên kiểm tra route, tin tưởng cookie thô, IDOR tuần tự). Trong thực tế các hệ thống lớn, dev thường có cài đặt kiểm tra bảo mật, nhưng lại mắc các lỗi:
1. **Quá tin tưởng vào Request Body (Mass Assignment)**: Map trực tiếp JSON vào Entity Database.
2. **Kiểm tra lỏng lẻo ở HTTP Method**: Chỉ chặn `POST` mà quên chặn `GET` / `PUT`.
3. **Bất đồng bộ giữa Gateway & Backend (Proxy Header Confusion)**: Reverse proxy (Nginx, Kong) kiểm tra URL một đằng, Backend lại routing theo Header một nẻo (`X-Original-URL`).

Hãy cùng giải quyết 3 bài Lab Practitioner sau đây trên PortSwigger!

---

## 🟢 LAB 1: User role can be modified in user profile (Lỗ hổng Mass Assignment)
* **Link lab**: [User role can be modified in user profile](https://portswigger.net/web-security/access-control/lab-user-role-can-be-modified-in-user-profile)
* **Mức độ**: Practitioner
* **Tài khoản cấp sẵn**: `wiener` / `peter`
* **Mục tiêu**: Đăng nhập bằng `wiener`, cập nhật email và khai thác JSON payload để tự phong làm admin, sau đó xóa tài khoản `carlos`.

### 🔍 Góc nhìn Phân tích:
- **Lỗi của Dev**: Trong nhiều framework (Spring Boot, ASP.NET, Express/Prisma, Ruby on Rails), dev thường bind thẳng Object từ client vào Database Entity:
  ```go
  // Ví dụ nguy hiểm: Map toàn bộ request body vào User struct
  var user User
  c.BindJSON(&user) // Client gửi roleid: 2 là DB tự cập nhật luôn!
  db.Save(&user)
  ```
- **Tư duy Breaker**: Khi quan sát API response trả về sau khi update profile, nếu thấy có trường `"roleid": 1` (hoặc `"role": "user"`, `"is_admin": false`), hãy thử nhét ngược lại trường đó vào JSON gửi lên với giá trị cao hơn (`"roleid": 2`).

### 🛠️ Các bước giải quyết:
1. Mở bài lab, đăng nhập với `wiener:peter`.
2. Vào **My account**, cập nhật địa chỉ email (ví dụ: `test@test.com`) và bấm **Update email**.
3. Mở Burp Suite ➔ **Proxy > HTTP history**, tìm request:
   ```http
   POST /my-account/change-email
   ```
4. Bấm `Ctrl + R` để gửi sang **Repeater**.
5. Quan sát Response trả về của request gốc, bạn sẽ thấy JSON response có cấu trúc:
   ```json
   {
     "username": "wiener",
     "email": "test@test.com",
     "roleid": 1
   }
   ```
6. Trong tab Repeater, sửa Request Body thành:
   ```json
   {
     "email": "hacked@test.com",
     "roleid": 2
   }
   ```
7. Bấm **Send**. Xem Response trả về xác nhận `"roleid": 2`.
8. Quay lại trình duyệt, tải lại trang (F5) hoặc truy cập `/admin`.
9. Bấm nút **Delete** tài khoản `carlos` ➔ **Solved!**

#### 🛡️ Cách vá chuẩn ở Backend:
Áp dụng mẫu thiết kế **DTO (Data Transfer Object)** và **White-listing**: Chỉ cho phép các trường người dùng được phép sửa. Tuyệt đối không map trực tiếp Request vào Model DB.
```csharp
// Ví dụ C# DTO an toàn
public class UpdateEmailRequest {
    [EmailAddress]
    public string Email { get; set; } // Chỉ nhận đúng Email, bỏ qua roleid
}
```

---

## 🟢 LAB 2: Method-based access control can be circumvented (Bypass qua HTTP Method)
* **Link lab**: [Method-based access control can be circumvented](https://portswigger.net/web-security/access-control/lab-method-based-access-control-can-be-circumvented)
* **Mức độ**: Practitioner
* **Tài khoản cấp sẵn**:
  - Quản trị viên: `administrator` / `admin`
  - Nạn nhân/Attacker: `wiener` / `peter`
* **Mục tiêu**: Đăng nhập bằng `wiener`, lợi dụng lỗ hổng kiểm tra sai HTTP Method để tự cấp quyền admin cho `wiener`.

### 🔍 Góc nhìn Phân tích:
- **Lỗi của Dev**: Khi cấu hình middleware bảo vệ, dev chỉ cấu hình kiểm tra quyền trên method `POST`:
  ```javascript
  // Lỗi điển hình: Chỉ chặn POST
  app.post('/admin-roles', checkAdminPermission, handleRolePromotion);
  // Nhưng router hoặc framework lại cho phép xử lý cả GET hoặc hỗ trợ method spoofing!
  ```
- **Tư duy Breaker**: Nếu không gửi được bằng `POST` vì bị 401/403, hãy thử đổi method sang `GET`, `POST` với query string, hoặc dùng header `X-HTTP-Method-Override: POST`.

### 🛠️ Các bước giải quyết:
1. Đăng nhập bằng tài khoản `administrator:admin`.
2. Vào **Admin panel**, nâng quyền cho tài khoản `carlos` (Bấm nút **Upgrade user**).
3. Đăng xuất tài khoản `administrator`.
4. Mở Burp Suite ➔ **Proxy > HTTP history**, tìm request nâng quyền vừa rồi:
   ```http
   POST /admin-roles HTTP/1.1
   ...
   username=carlos&action=upgrade
   ```
5. Gửi request sang **Repeater** (`Ctrl + R`).
6. Đăng nhập lại vào trình duyệt với tài khoản `wiener:peter`. Copy giá trị `session` cookie của `wiener`.
7. Dán `session` cookie của `wiener` vào request trong Repeater.
8. Thử bấm **Send** ➔ Server trả về `401 Unauthorized` (vì `wiener` không có quyền thực hiện POST).
9. Bấm chuột phải vào bất kỳ đâu trong khung Request của Repeater ➔ Chọn **Change request method** (Burp sẽ tự động đổi `POST` thành `GET` và đưa parameters lên URL):
   ```http
   GET /admin-roles?username=wiener&action=upgrade HTTP/1.1
   Cookie: session=<SESSION_CỦA_WIENER>
   ```
10. Bấm **Send** ➔ Server trả về `302 Found` hoặc `200 OK`!
11. Quay lại trình duyệt f5 trang `wiener` ➔ Bạn đã trở thành Admin ➔ **Solved!**

#### 🛡️ Cách vá chuẩn ở Backend:
Áp dụng nguyên tắc **Deny by default**. Middleware phân quyền phải áp dụng cho toàn bộ đường dẫn `/admin-roles` bất kể HTTP Method là gì:
```go
// Go Gin: Bảo vệ toàn bộ endpoint bất kể Method
adminGroup := r.Group("/admin-roles")
adminGroup.Use(RequireRole("ADMIN"))
adminGroup.POST("", upgradeHandler)
adminGroup.GET("", upgradeHandler)
```

---

## 🟢 LAB 3: URL-based access control can be circumvented (Header Override Bypass)
* **Link lab**: [URL-based access control can be circumvented](https://portswigger.net/web-security/access-control/lab-url-based-access-control-can-be-circumvented)
* **Mức độ**: Practitioner
* **Tài khoản cấp sẵn**: `administrator` (dùng để quan sát) - Mục tiêu chính không cần đăng nhập.
* **Mục tiêu**: Vượt qua hệ thống kiểm soát quyền trên URL để vào `/admin` và xóa `carlos`.

### 🔍 Góc nhìn Phân tích:
- **Lỗi của Dev & Kiến trúc mạng**:
  - Hệ thống đặt một Reverse Proxy / WAF phía trước. Proxy này có rule: *"Nếu URL bắt đầu bằng `/admin` thì chặn lại trừ khi có IP nội bộ hoặc session admin"*.
  - Tuy nhiên, server ứng dụng Backend phía sau lại hỗ trợ header ghi đè URL như `X-Original-URL` hoặc `X-Rewrite-URL` (thường thấy trong một số framework như Symfony, Zend, Spring Framework cũ hoặc IIS).
- **Tư duy Breaker**: Gửi request tới trang chủ `GET /` (được Proxy cho phép qua), nhưng kẹp thêm header `X-Original-URL: /admin` để Backend bên trong tự định tuyến vào trang Admin!

### 🛠️ Các bước giải quyết:
1. Mở bài lab lên trình duyệt.
2. Thử truy cập trực tiếp `https://<lab-id>.web-security-academy.net/admin` ➔ Bị chặn: `Access denied`.
3. Mở Burp Suite ➔ **Proxy > HTTP history**, tìm request `GET /` (hoặc gửi request `GET /` sang Repeater).
4. Trong Repeater, thêm header sau vào request:
   ```http
   GET / HTTP/1.1
   Host: <lab-id>.web-security-academy.net
   X-Original-URL: /admin
   ```
5. Bấm **Send** ➔ Bạn sẽ thấy Response trả về mã `200 OK` cùng giao diện trang Quản trị Admin Panel!
6. Để thực hiện hành động xóa user `carlos`, bạn tiếp tục lợi dụng header này:
   ```http
   GET /?username=carlos HTTP/1.1
   Host: <lab-id>.web-security-academy.net
   X-Original-URL: /admin/delete
   ```
7. Bấm **Send** ➔ Hệ thống xóa `carlos` và trả về thông báo ➔ **Solved!**

#### 🛡️ Cách vá chuẩn ở Backend:
1. Vô hiệu hóa tính năng URL override từ HTTP headers nếu không thực sự dùng đến.
2. Cấu hình Reverse Proxy / WAF phải strip (xóa bỏ) toàn bộ các header nhạy cảm dạng `X-Original-URL`, `X-Rewrite-URL`, `X-Forwarded-Prefix` gửi từ Client internet trước khi chuyển tiếp cho Backend.

---

## Checklist Hoàn Thành Của Bạn
- [x] Giải quyết xong Lab 1: User role can be modified in user profile (Mass Assignment).
- [x] Giải quyết xong Lab 2: Method-based access control can be circumvented (Change Request Method).
- [x] Giải quyết xong Lab 3: URL-based access control can be circumvented (`X-Original-URL`).
