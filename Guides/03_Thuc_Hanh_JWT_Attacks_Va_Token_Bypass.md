# Hướng Dẫn Thực Hành 03: Tấn Công & Khai Thác JWT (JSON Web Tokens)

> **Mục tiêu**: Nắm vững cấu trúc token JWT, cài đặt extension **JWT Editor** trên Burp Suite, và bẻ khóa 3 lỗ hổng JWT kinh điển: **Unverified Signature**, **None Algorithm**, và **Weak HMAC Secret Key**.

---

## 💡 Tổng Quan: Cấu Trúc JWT & Sai Lầm Của Backend Dev

Một chuỗi JWT gồm 3 phần được phân tách bằng dấu chấm (`.`):
```text
eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJzdWIiOiAid2llbmVyIiwgInJvbGUiOiAidXNlciJ9.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
  [         1. HEADER         ]   .   [          2. PAYLOAD          ]   .   [         3. SIGNATURE         ]
```
1. **Header**: Chứa metadata, định nghĩa loại token và thuật toán ký (ví dụ: `{"alg": "HS256", "typ": "JWT"}`).
2. **Payload**: Chứa các claims thông tin người dùng (ví dụ: `{"sub": "wiener", "role": "user"}`).
3. **Signature**: Chữ ký số đảm bảo token không bị giả mạo.

### Dev thường mắc 3 sai lầm chết người nào?
1. **Gọi hàm `decode()` thay vì `verify()`**: Chỉ giải mã Base64 để lấy thông tin `user_id` mà quên xác thực chữ ký `Signature`.
2. **Tin tưởng thuộc tính `alg` do Client gửi lên**: Nếu Client gửi `"alg": "none"`, thư viện tự động bỏ qua kiểm tra chữ ký!
3. **Đặt Secret Key quá yếu**: Đặt key là `"secret"`, `"admin123"`, `"jwtsecret"` khiến hacker brute-force ra key trong vòng vài giây.

---

## 🛠️ Chuẩn Bị Vũ Khí: Cài Đặt Extension "JWT Editor" trên Burp Suite

Để thao tác với JWT mượt mà nhất trong Burp Suite mà không cần sửa Base64 thủ công:
1. Mở Burp Suite ➔ Vào tab **Extensions** ➔ chọn tab con **BApp Store**.
2. Tìm kiếm từ khóa: `JWT Editor`.
3. Bấm nút **Install** ở góc phải (Hoàn toàn miễn phí).
4. Sau khi cài xong, trên thanh điều hướng của Burp sẽ xuất hiện tab mới: **JWT Editor Keys**, và trong tab **Repeater** sẽ có thêm tab con **JSON Web Token** cực kỳ tiện lợi.

---

## 🟢 LAB 1: JWT authentication bypass via unverified signature (Không kiểm tra chữ ký)
* **Link lab**: [JWT authentication bypass via unverified signature](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-unverified-signature)
* **Mức độ**: Apprentice
* **Tài khoản cấp sẵn**: `wiener` / `peter`
* **Mục tiêu**: Đăng nhập bằng `wiener`, sửa đổi payload JWT để mạo danh `administrator`, vào `/admin` xóa tài khoản `carlos`.

### 🔍 Góc nhìn Phân tích:
- **Lỗi của Dev**: Backend lấy token từ cookie/header, chỉ base64 decode phần Payload để đọc `sub: "wiener"` rồi query DB lấy user mà không hề chạy qua bước verify Signature.
- **Tư duy Breaker**: Sửa thẳng trường `sub` từ `"wiener"` thành `"administrator"` trong Payload, giữ nguyên Signature cũ (hoặc thậm chí để rác vào signature), backend vẫn tin tưởng 100%!

### 🛠️ Các bước giải quyết:
1. Mở bài lab, đăng nhập với `wiener:peter`.
2. Mở Burp Suite ➔ **Proxy > HTTP history**, tìm request `GET /my-account`.
3. Quan sát Cookie trong request, bạn sẽ thấy cookie `session=eyJ...` (đây chính là JWT).
4. Bấm `Ctrl + R` để gửi request sang **Repeater**.
5. Trong Repeater:
   - Nếu đã cài extension **JWT Editor**: Bấm vào tab **JSON Web Token**, tại phần Payload sửa `"sub": "wiener"` thành `"sub": "administrator"`.
   - Nếu làm thủ công: Copy đoạn giữa (Payload), giải mã Base64 (dùng tab **Decoder** của Burp hoặc jwt.io), sửa `sub` thành `administrator`, encode lại thành Base64Url rồi dán đè vào đoạn giữa của cookie `session`.
6. Bấm **Send** ➔ Quan sát Response thấy xuất hiện đường dẫn `/admin`.
7. Sửa đường dẫn request từ `GET /my-account` thành `GET /admin/delete?username=carlos`.
8. Bấm **Send** ➔ Carlos bị xóa ➔ **Solved!**

#### 🛡️ Cách vá chuẩn ở Backend (Node.js):
```javascript
// SAI: jwt.decode(token) - Không kiểm tra chữ ký
// const user = jwt.decode(token);

// ĐÚNG: Luôn dùng jwt.verify với secret key an toàn
try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256'] });
    req.user = decoded;
} catch (err) {
    return res.status(401).json({ message: "Invalid token signature" });
}
```

---

## 🟢 LAB 2: JWT authentication bypass via flawed signature verification (Tấn công "alg": "none")
* **Link lab**: [JWT authentication bypass via flawed signature verification](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-flawed-signature-verification)
* **Mức độ**: Apprentice
* **Tài khoản cấp sẵn**: `wiener` / `peter`
* **Mục tiêu**: Đổi thuật toán mã hóa thành `none`, nâng quyền thành `administrator` và xóa `carlos`.

### 🔍 Góc nhìn Phân tích:
- **Lỗi của Dev & Thư viện**: Chuẩn JWT ban đầu có hỗ trợ thuật toán `"none"` (dành cho token không cần mã hóa, dùng debug). Nhiều thư viện JWT cũ hoặc cấu hình sai sẽ tự động bỏ qua bước kiểm tra chữ ký nếu thấy Header gửi lên `"alg": "none"`.
- **Tư duy Breaker**:
  - Đổi Header: `{"alg": "none", "typ": "JWT"}` (hoển cả các biến thể như `None`, `NONE`, `nOnE` nếu bị filter).
  - Đổi Payload: `{"sub": "administrator"}`.
  - Xóa sạch phần Signature (nhưng vẫn giữ lại dấu chấm cuối cùng: `Header.Payload.`).

### 🛠️ Các bước giải quyết:
1. Mở bài lab, đăng nhập với `wiener:peter`.
2. Bắt request `GET /my-account`, gửi sang **Repeater** (`Ctrl + R`).
3. Trong tab **Repeater**:
   - Nếu dùng extension **JWT Editor**: Bấm tab **JSON Web Token**, sửa `"sub": "administrator"`, ở thanh công cụ phía dưới chọn **Attack** ➔ chọn **"None" signing algorithm** ➔ Chọn kiểu biến thể chữ hoa/thường mặc định rồi bấm OK.
   - Nếu làm thủ công:
     - Header: `{"alg":"none","typ":"JWT"}` ➔ Base64Url encode là `eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0`
     - Payload: `{"sub":"administrator"}` ➔ Base64Url encode
     - Token ghép lại có dạng: `<Base64_Header>.<Base64_Payload>.` *(Lưu ý: Bắt buộc phải có dấu chấm `.` ở cuối nhưng không có ký tự chữ ký nào phía sau)*.
4. Thay token mới vào Cookie `session=...` trong Repeater.
5. Sửa URL thành `GET /admin/delete?username=carlos`.
6. Bấm **Send** ➔ Carlos bị xóa ➔ **Solved!**

#### 🛡️ Cách vá chuẩn ở Backend:
Luôn chỉ định rõ danh sách thuật toán hợp lệ (Algorithm Whitelisting) khi gọi hàm xác thực:
```go
// Go (golang-jwt): Luôn ép kiểu thuật toán kiểm tra
token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
    if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
        return nil, fmt.Errorf("unexpected signing algorithm: %v", token.Header["alg"])
    }
    return []byte(os.Getenv("JWT_SECRET")), nil
})
```

---

## 🟢 LAB 3: JWT authentication bypass via weak signing key (Brute-force Secret Key)
* **Link lab**: [JWT authentication bypass via weak signing key](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-weak-signing-key)
* **Mức độ**: Practitioner
* **Tài khoản cấp sẵn**: `wiener` / `peter`
* **Mục tiêu**: Brute-force tìm Secret Key của JWT, tự ký một token mới cho `administrator` và xóa `carlos`.

### 🔍 Góc nhìn Phân tích:
- **Lỗi của Dev**: Đặt chuỗi bí mật (Secret Key) để ký thuật toán HMAC-SHA256 quá ngắn hoặc từ phổ biến trong từ điển (`secret`, `password`, `key123`).
- **Tư duy Breaker**: Vì thuật toán đối xứng HMAC chỉ dùng một Secret Key duy nhất để vừa ký vừa xác thực, kẻ tấn công có token hợp lệ có thể brute-force offline trên máy tính bằng danh sách từ điển (Wordlist) để tìm ra key.

### 🛠️ Các bước giải quyết:
1. Mở bài lab, đăng nhập bằng `wiener:peter`.
2. Bắt request `GET /my-account`, copy toàn bộ chuỗi JWT token trong cookie `session`.
3. **Tìm Secret Key**:
   - *Cách 1 (Nhanh nhất)*: PortSwigger đặt mặc định Secret Key của bài này là **`secret1`**.
   - *Cách 2 (Dùng script Python có sẵn)*: Mở Terminal gõ `python "d:/Adjim Personal/Security/Tools/crack_jwt.py" "<jwt_token>"` để tự động dò tìm qua file từ điển `jwt.secrets.list`.
   - *Cách 3 (Dành cho máy Linux/Kali)*: Dùng Hashcat (`hashcat -a 0 -m 16500 <token> jwt.secrets.list`) hoặc John the Ripper.
4. **Tự ký token Admin**:
   - Vào Burp Suite ➔ Tab **JWT Editor Keys** ➔ Bấm **New Symmetric Key**.
   - Bấm **Generate**, sau đó tại trường `"k"` (Key value), dán chuỗi Secret Key vừa crack được vào (Lưu ý: base64 encoded string của key). Hoặc bấm **Save**.
   - Quay lại tab **Repeater**, ở tab **JSON Web Token**, sửa `"sub": "administrator"`.
   - Bấm nút **Sign** ở phía dưới ➔ Chọn key vừa tạo ➔ Bấm **OK**.
5. Gửi request đến `GET /admin/delete?username=carlos`.
6. Bấm **Send** ➔ **Solved!**

#### 🛡️ Cách vá chuẩn ở Backend:
1. Sử dụng Secret Key có độ dài tối thiểu 256 bits (32 bytes ngẫu nhiên mã hóa an toàn Cryptographically Secure):
   ```bash
   # Tạo key ngẫu nhiên an toàn trên Linux/Mac/Git Bash:
   openssl rand -base64 32
   ```
2. Lưu key trong biến môi trường hoặc Secret Manager (AWS Secrets Manager, HashiCorp Vault), không bao giờ hardcode vào source code.

---

## Checklist Hoàn Thành Của Bạn
- [x] Cài đặt thành công extension **JWT Editor** trên Burp Suite.
- [x] Giải quyết xong Lab 1: Unverified signature bypass.
- [x] Giải quyết xong Lab 2: Flawed signature verification (`"alg": "none"`).
- [x] Giải quyết xong Lab 3: Weak signing key (Brute-force Secret Key).
