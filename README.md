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
