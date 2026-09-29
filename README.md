---
title: Cờ Vua vs Stockfish
emoji: ♟️
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "5.29.0"
app_file: app.py
pinned: false
license: mit
---

# ♟️ Cờ Vua – Chơi với Stockfish

Ứng dụng cờ vua tương tác chạy trên Hugging Face Spaces.

## Tính năng

- **Bàn cờ trực quan** – hiển thị quân cờ bằng ký hiệu Unicode chuẩn
- **Click để đi quân** – chọn quân bằng cách click vào ô, rồi click ô đến (không cần nhập tọa độ)
- **Highlight nước đi hợp lệ** – khi chọn quân, tất cả ô đến hợp lệ được đánh dấu
- **Xoay bàn cờ** – khi chọn quân đen, bàn cờ tự động xoay ngược chiều
- **AI Stockfish** – đối thủ sử dụng Stockfish engine
- **Đi lại (Undo)** – hoàn tác nước đi cuối cùng của bạn và phản hồi của Stockfish
- **🛠️ Nhập / chỉnh bàn cờ** – đặt, thay thế hoặc xóa quân cờ trên từng ô
- **Nhập FEN** – có thể chỉnh trực tiếp toàn bộ vị trí bằng FEN
- **Chạy CPU-only** – không cần GPU; Stockfish chạy bằng CPU

## Chỉnh bàn cờ

Mở **🛠️ Nhập / chỉnh bàn cờ** để:

1. Chọn ô cờ và loại quân rồi bấm **Đặt / thay quân**
2. Bấm **Xóa ô** để bỏ quân tại một ô
3. Bấm **Xóa toàn bộ** để tạo bàn trống
4. Hoặc sửa trực tiếp FEN rồi bấm **Kiểm tra FEN**
5. Bấm **Dùng vị trí này** để chơi từ vị trí tùy chỉnh

Trình chỉnh sửa cho phép tạo cả vị trí thế cờ đặc biệt. Khi bắt đầu ván, ứng dụng vẫn kiểm tra tính hợp lệ của vị trí trước khi cho Stockfish chơi.

## Cách chơi

1. Chọn màu quân (**Trắng ♔** hoặc **Đen ♚**)
2. Bấm **🎮 Ván mới** để bắt đầu
3. Click vào quân cờ của bạn → các ô hợp lệ được tô màu xanh
4. Click vào ô đích để di chuyển
5. Bấm **⏪ Đi lại** nếu muốn hoàn tác

## Yêu cầu hệ thống (tự động cài khi deploy)

- `stockfish` (apt) – chess engine
- `gradio>=4.0` – UI framework
- `chess` – thư viện cờ vua Python
