# Nguyên Tắc Làm Việc Của Agent Trong Dự Án Này

## Tự Động Cập Nhật Nhật Ký Thực Hành (.docx)
- **Quy tắc bắt buộc**: Mỗi khi người dùng hoàn thành một bài lab mới, đặt câu hỏi phương pháp luận/kỹ thuật quan trọng, hoặc bước sang một chuyên đề mới:
  1. Cập nhật nội dung tương ứng vào công cụ sinh tài liệu `d:/Adjim Personal/Security/Tools/generate_docx.py`.
  2. Tự động chạy lại script `python "d:/Adjim Personal/Security/Tools/generate_docx.py"` để đồng bộ nội dung mới nhất vào file tài liệu Word:
     `d:/Adjim Personal/Security/Nhat_Ky_Hoc_Tap_Va_Thuc_Hanh_Security.docx`.
  3. Cập nhật các checklist trong thư mục `Guides/` và `Roadmap.md`.
- **Mục tiêu**: Đảm bảo file Word `.docx` luôn là một cuốn cẩm nang toàn diện, cập nhật theo thời gian thực toàn bộ hành trình đào tạo của người dùng mà không cần người dùng phải nhắc lại.
