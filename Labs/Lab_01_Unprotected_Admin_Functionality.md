# Write-up Lab 01: Unprotected admin functionality

* **Nền tảng**: PortSwigger Web Security Academy
* **Chủ đề**: Access Control (Kiểm soát truy cập)
* **Mức độ**: Apprentice (Cơ bản)
* **Link Lab**: [Unprotected admin functionality](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality)
* **Trạng thái**: ✅ **SOLVED**

---

## 1. Mục Tiêu Bài Lab
Truy cập vào trang quản trị ẩn chưa được cấu hình phân quyền và xóa tài khoản của người dùng `carlos`.

---

## 2. Phân Tích Lỗ Hổng: Security through Obscurity (Bảo mật bằng sự che giấu)
* **Sai lầm của Dev**: Thay vì viết Middleware/Decorator kiểm tra quyền Admin (`AuthMiddleware`), Dev chỉ đơn giản là:
  1. Giấu nút "Admin" trên giao diện của người dùng thông thường.
  2. Đặt URL ngẫu nhiên hoặc khó đoán (như `/admin-panel-secret` hoặc `/admin-xxxxx`).
  3. Thêm URL này vào `/robots.txt` với chỉ thị `Disallow: /admin-xxxxx` để tránh bị Google search index.
* **Hệ quả**: File `robots.txt` là tài nguyên công khai. Kẻ tấn công luôn đọc file này đầu tiên để biết các thư mục/route nhạy cảm mà dev cố tình che giấu.

---

## 3. Các Bước Khai Thác Đã Thực Hiện
1. Mở bài lab trên trình duyệt của Burp Suite.
2. Truy cập URL: `https://<lab-id>.web-security-academy.net/robots.txt`.
3. Nhận thấy nội dung file chứa dòng cấm:
   ```text
   User-agent: *
   Disallow: /administrator-panel
   ```
4. Truy cập trực tiếp: `https://<lab-id>.web-security-academy.net/administrator-panel`.
5. Bấm nút **Delete** tại dòng của user `carlos` ➔ **Hoàn thành bài lab (Solved)**.

---

## 4. Cách Phòng Thủ Chuẩn
Áp dụng cơ chế phân quyền RBAC (Role-Based Access Control) bắt buộc trên mọi Route/Endpoint nội bộ:
```csharp
// .NET C#
[Authorize(Roles = "Administrator")]
[Route("admin-panel")]
public class AdminController : Controller { ... }
```
```javascript
// Node.js Express
app.use('/admin', verifyToken, requireRole('ADMIN'), adminRouter);
```
