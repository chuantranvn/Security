# Write-up Lab 02: User role controlled by request parameter

* **Nền tảng**: PortSwigger Web Security Academy
* **Chủ đề**: Access Control (Kiểm soát truy cập)
* **Mức độ**: Apprentice (Cơ bản)
* **Link Lab**: [User role controlled by request parameter](https://portswigger.net/web-security/access-control/lab-user-role-controlled-by-request-parameter)
* **Tài khoản cấp sẵn**: `wiener` / `peter`

---

## 1. Mục Tiêu Bài Lab
Đăng nhập bằng tài khoản người dùng thông thường (`wiener:peter`), khai thác lỗ hổng phân quyền qua tham số/cookie do Client gửi lên để truy cập trang Admin và xóa tài khoản của `carlos`.

---

## 2. Phân Tích Lỗ Hổng Dưới Góc Nhìn Backend Dev

### ❌ Đoạn code "ngây thơ" của Backend (Anti-pattern):
Giả sử backend viết bằng Node.js / Express:
```javascript
app.get('/admin', (req, res) => {
    // SAI LẦM CHẾT NGƯỜI: Tin tưởng hoàn toàn vào Cookie do trình duyệt gửi lên
    if (req.cookies.Admin === 'true') {
        return res.render('admin-panel');
    }
    return res.status(401).send("Unauthorized");
});
```

### 💡 Tại sao lỗ hổng này xảy ra?
Dev nghĩ rằng Cookie là thứ được backend cấp phát (`Set-Cookie: Admin=false`), thì client sẽ chỉ giữ nguyên giá trị đó gửi lên. Dev quên mất rằng: **Toàn bộ dữ liệu nằm ở phía Client (Cookie, LocalStorage, Query Params, Request Body, Header) đều có thể bị kẻ tấn công sửa đổi tùy ý trước khi gửi về Server**.

---

## 3. Các Bước Khai Thác Bằng Burp Suite

### Bước 1: Đăng nhập với user bình thường
1. Mở bài lab bằng trình duyệt Chromium của Burp.
2. Bấm vào link **My account** ở thanh điều hướng.
3. Đăng nhập với username: `wiener`, password: `peter`.

### Bước 2: Bắt gói tin và phân tích trên Burp Suite
1. Mở cửa sổ Burp Suite, vào tab **Proxy** ➔ chọn tab con **HTTP history**.
2. Tìm dòng request `POST /login` hoặc `GET /my-account`.
3. Nhìn vào khung **Response** của `POST /login` hoặc khung **Request** của `GET /my-account`. Bạn sẽ thấy một dòng Cookie đáng ngờ:
   ```http
   Cookie: session=xxxxxx; Admin=false
   ```

### Bước 3: Thử nghiệm sửa đổi bằng Repeater (`Ctrl + R`)
1. Bấm chuột phải vào request `GET /my-account` ➔ chọn **Send to Repeater** (hoặc gõ phím tắt `Ctrl + R`).
2. Chuyển sang tab **Repeater** trên thanh menu chính của Burp.
3. Trong khung Request, sửa:
   ```http
   Admin=false  --->  Admin=true
   ```
4. Bấm nút **Send** màu cam ở góc trên bên trái.
5. Quan sát khung Response bên phải:
   - Dùng thanh tìm kiếm ở dưới khung Response, gõ chữ `Admin panel`.
   - Bạn sẽ thấy HTML trả về đã xuất hiện liên kết: `<a href="/admin">Admin panel</a>`.

### Bước 4: Khai thác thực tế trên Trình duyệt để Solve Lab
Có 2 cách để hoàn thành bài:

* **Cách 1 (Dùng ngay Burp Repeater)**:
  - Trong tab Repeater, sửa dòng đầu tiên thành:
    ```http
    GET /admin/delete?username=carlos HTTP/2
    Cookie: session=xxxxxx; Admin=true
    ```
  - Bấm **Send** ➔ Backend xử lý xóa carlos ngay lập tức ➔ Solved!

* **Cách 2 (Sửa Cookie trên Trình duyệt)**:
  - Trên trình duyệt Chromium của Burp, bấm phím `F12` để mở DevTools.
  - Chuyển sang tab **Application** (hoặc **Storage**) ➔ chọn mục **Cookies**.
  - Tìm cookie có tên `Admin`, nhấp đúp vào giá trị `false` và sửa thành `true`.
  - Nhấn `F5` tải lại trang. Lúc này menu sẽ xuất hiện nút **Admin panel**.
  - Bấm vào **Admin panel** ➔ Bấm nút **Delete** cạnh tài khoản `carlos`.
  - **Kết quả**: Banner xanh **Congratulations, you solved the lab!** hiện lên.

---

## 4. Cách Vá Chuẩn Ở Tầng Backend

### Nguyên tắc vàng:
> **Không bao giờ lưu trạng thái phân quyền (Role / Permissions) dưới dạng Plaintext ở Client.**

### Giải pháp 1: Lưu Session ở Server (Stateful)
Lưu Session ID trong Cookie, còn Role lưu trong Database hoặc Redis:
```go
// Go + Gin
func AdminOnlyMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        sessionID := c.GetHeader("Session-ID")
        user := db.GetUserBySession(sessionID)
        
        if user == nil || user.Role != "ADMIN" {
            c.AbortWithStatusJSON(403, gin.H{"error": "Forbidden"})
            return
        }
        c.Next()
    }
}
```

### Giải pháp 2: Sử dụng JWT có chữ ký bảo mật (Stateless)
Nếu dùng Token/JWT, Role phải nằm trong Payload của JWT và được **ký điện tử (Signed)** bằng Secret Key an toàn ở Server. Khi User tự ý sửa Role trong Payload, chữ ký (Signature) sẽ bị sai lệch và Server sẽ từ chối request ngay lập tức.
