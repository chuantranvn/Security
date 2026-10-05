# Hướng Dẫn Thực Hành 06: Khai Thác Lỗi Bất Đồng Bộ (Race Conditions & Concurrency)

> **Mục tiêu**: Hiểu rõ điểm yếu bất đồng bộ trong xử lý giao dịch Backend, làm chủ kỹ thuật **Single-packet Attack (Gửi request song song trong 1 microsecond)** trên Burp Suite Repeater, và bẻ khóa các lỗi logic thanh toán / áp mã giảm giá (Discount Coupon Abuse).

---

## 💡 Tổng Quan: "Tử Huyệt" Concurrency Của Backend Developer

Trong các bài toán thực tế như:
- Nhập mã giảm giá (Coupon).
- Đặt cược, chuyển tiền ví điện tử.
- Rút tiền ngân hàng, thanh toán đơn hàng.

Lập trình viên thường viết code theo tư duy tuần tự:
```go
// Code dính lỗi Race Condition kinh điển:
func ApplyCoupon(user User, coupon Code) {
    if !coupon.HasBeenUsed(user) {              // 1. Kiểm tra (Check)
        time.Sleep(10 * time.Millisecond)        // (Độ trễ xử lý DB / mạng)
        user.ApplyDiscount(coupon.Value)        // 2. Trừ tiền / áp dụng
        coupon.MarkAsUsed(user)                 // 3. Đánh dấu đã dùng (Update)
    }
}
```

### Kẻ tấn công làm gì?
Giữa bước **(1) Kiểm tra** và bước **(3) Đánh dấu**, luôn có một khoảng trống thời gian cực ngắn gọi là **Race Window** (Cửa sổ đua tranh).
Nếu kẻ tấn công gửi **20 request áp mã giảm giá cùng một lúc chính xác trong 1 microsecond**:
- Cả 20 request đều đi qua bước (1) trước khi bất kỳ request nào kịp chạy tới bước (3).
- Kết quả: Mã giảm giá 20% được áp dụng 20 lần ➔ Món hàng trị giá $1,300 được giảm giá về $0!

---

## 🛠️ Vũ Khí Mới Của Burp Suite: "Send Group in Parallel"

Trước đây cần phải dùng script Python hoặc extension Turbo Intruder. Bây giờ Burp Suite đã tích hợp sẵn tính năng **Single-packet Attack** cực kỳ tiện lợi:
1. Gửi request vào **Repeater** (`Ctrl + R`).
2. Nhân bản request thành 20 tab (chuột phải vào tab ➔ **Duplicate tab** hoặc bấm tổ hợp phím nhiều lần).
3. Bấm vào dấu `+` cạnh các tab ➔ Tạo **Tab group** (đặt tên ví dụ: `Race-Attack`).
4. Nhìn vào nút **Send** màu cam: Bấm vào mũi tên nhỏ bên cạnh ➔ Chọn **Send group (parallel)**.
5. Khi bấm nút, Burp sẽ đồng bộ toàn bộ TCP/HTTP packets để bắn tất cả 20 request đến server cùng 1 tích tắc!

---

## 🟢 LAB 1: Limit overrun race conditions (Áp dụng Coupon lặp vô tận)
* **Link lab**: [Limit overrun race conditions](https://portswigger.net/web-security/race-conditions/lab-race-conditions-limit-overrun)
* **Mức độ**: Practitioner
* **Tài khoản cấp sẵn**: `wiener` / `peter` (Số dư trong ví: $50)
* **Mục tiêu**: Mua món hàng "Lightweight l33t leather jacket" trị giá **$1,337** với mã giảm giá 20% `PROMO20` (vốn chỉ được dùng 1 lần duy nhất).

### 🔍 Góc nhìn Phân tích:
- Mã giảm giá `PROMO20` giảm 20% giá trị đơn hàng.
- Nếu chỉ dùng 1 lần, giá giảm từ $1337 xuống ~$1070 (vẫn không đủ $50 để mua).
- Nếu ta khai thác Race Condition để áp dụng mã này liên tiếp ~15 lần cùng 1 lúc, giá sẽ giảm dần về dưới $50!

### 🛠️ Các bước giải quyết:
1. Mở bài lab, đăng nhập với `wiener:peter`.
2. Ra trang chủ, bấm vào áo khoác **Lightweight l33t leather jacket** ➔ Bấm **Add to cart**.
3. Vào trang giỏ hàng (Cart), nhập mã coupon:
   `PROMO20` ➔ Bấm **Apply**.
4. Mở Burp Suite ➔ **Proxy > HTTP history**, tìm request:
   ```http
   POST /cart/coupon HTTP/1.1
   ...
   csrf=...&coupon=PROMO20
   ```
5. Gửi request này sang **Repeater** (`Ctrl + R`).
6. Tạo một nhóm tab (Tab Group) trong Repeater:
   - Chuột phải vào tab request coupon ➔ Chọn **Add tab to group** ➔ **Create tab group** ➔ Đặt tên là `Race`.
   - Nhân bản (Duplicate) tab đó ra thành khoảng **20 tab** nằm trong cùng nhóm `Race`.
7. Tại thanh công cụ của Repeater, cạnh nút **Send**, bấm vào mũi tên xổ xuống ➔ Chọn **Send group (parallel)**.
8. Bấm nút **Send group (parallel)**.
9. Quan sát các response trả về:
   - Bạn sẽ thấy nhiều tab cùng trả về `200 OK` với thông báo *"Coupon applied"* thay vì chỉ có 1 tab!
10. Quay lại trình duyệt, F5 lại trang giỏ hàng:
    - Giá của chiếc áo đã bị giảm xuống dưới $50 (thậm chí về $0)!
11. Bấm nút **Place order** ➔ Thanh toán thành công ➔ **Solved!**

---

## 🟢 LAB 2: Bypassing rate limits via race conditions (Bypass khóa Brute-force)
* **Link lab**: [Bypassing rate limits via race conditions](https://portswigger.net/web-security/race-conditions/lab-race-conditions-bypassing-rate-limits)
* **Mức độ**: Practitioner
* **Mục tiêu**: Bẻ khóa mật khẩu của người dùng `carlos`. Bình thường sau 3 lần nhập sai thì IP sẽ bị khóa trong nhiều phút. Dùng Race Condition để gửi hàng chục mật khẩu trước khi bộ đếm rate-limit kịp tăng!

### 🔍 Góc nhìn Phân tích:
- Cơ chế chống Brute-force thông thường:
  ```python
  if attempts >= 3:
      lock_account()
  else:
      check_password()
      attempts += 1
  ```
- Nếu gửi song song (parallel) 15 mật khẩu cùng lúc, tất cả đều vượt qua điều kiện `attempts < 3` trước khi số đếm được cập nhật.

---

## 🛡️ Cách Vá Chuẩn Race Condition Ở Tầng Backend

### 1. Database Row-Level Locking (Pessimistic Locking)
Khóa bản ghi bằng `SELECT ... FOR UPDATE` để ngăn các thread khác đọc/ghi cùng thời điểm:
```sql
BEGIN TRANSACTION;
-- Khóa dòng dữ liệu của user này lại, các request khác phải chờ
SELECT * FROM users WHERE id = 1 FOR UPDATE;
-- Thực hiện kiểm tra và áp dụng coupon...
COMMIT;
```

### 2. Distributed Locks với Redis (Redlock)
Đối với kiến trúc Microservices phân tán nhiều instance:
```javascript
// Sử dụng Redlock để giữ khóa trong suốt thời gian xử lý giao dịch
const lock = await redlock.acquire([`locks:users:${userId}:coupon`], 1000);
try {
    // Áp dụng mã giảm giá...
} finally {
    await lock.release();
}
```

### 3. Database Unique Constraints
Tạo ràng buộc duy nhất `UNIQUE(user_id, coupon_id)` ở tầng DB Schema để bảo vệ lớp phòng thủ cuối cùng: dù code có lọt thì DB cũng sẽ văng lỗi Conflict (409) và chặn đứng việc ghi đúp.

---

## Checklist Hoàn Thành Của Bạn
- [ ] Giải quyết xong Lab 1: Limit overrun race conditions (Coupon PROMO20).
- [ ] Giải quyết xong Lab 2: Bypassing rate limits via race conditions.
