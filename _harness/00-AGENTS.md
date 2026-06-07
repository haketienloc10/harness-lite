# Giai đoạn 0: Entrypoint & Triết lý cốt lõi

Dự án sử dụng **Harness** — hệ điều hành cấp repository giúp Agent biến yêu cầu
thành thay đổi an toàn.

## 1. Triết lý cốt lõi

- **Harness v0 Scope:** Hệ thống hiện tại cố tình KHÔNG BAO GỒM stack ứng dụng,
  mã nguồn scaffold, hoặc spec dự án nguyên khối. Các thành phần này chỉ xuất
  hiện khi một Story cần đến chúng.
- **Hierarchy (Phân cấp Nguồn sự thật):** Spec người dùng -> `docs/product/*` ->
  `docs/stories/*` -> `scripts/bin/harness-cli query matrix` ->
  `docs/decisions/*`. KHÔNG mở rộng một file Spec nguyên khối; hãy cập nhật các
  file docs nhỏ hơn.
- **Durable Layer:** Chính sách nằm ở file Markdown, còn dữ liệu vận hành
  (intake, story, quyết định, trace) PHẢI lưu bằng SQLite (`harness.db`) thông
  qua CLI. BẮT BUỘC tra cứu `_harness/03-CLI_REFERENCE.md` để biết cú pháp và
  tham số chuẩn xác của mọi lệnh `harness-cli`.
- **Tài liệu tham chiếu sâu (khi cần):** `_harness/*` là bộ khung thực thi
  chính. Khi cần chi tiết hơn (mô hình tổng thể, lý do, taxonomy, maturity), tra
  cứu `docs/*` — KHÔNG bắt buộc đọc hết; entrypoint thực thi vẫn là
  `_harness/01-WORKFLOW.md`.
- **Skill chuyên biệt (nạp on-demand):** `_harness/04-SKILLS.md` là hợp đồng +
  bảng đăng ký skill. KHÔNG preload; chỉ nạp file skill khi trigger khớp ở đúng
  giai đoạn (xem ĐỊNH MỨC TOKEN trong `01-WORKFLOW.md`).

## 2. Đầu ra của một tác vụ

Mỗi tác vụ tạo ra một trong hai (hoặc cả hai) kết quả:

- **Product Delta:** Thay đổi về code, test, API shape, data model, hoặc product
  docs.
- **Harness Delta:** Thay đổi về docs, templates, validation, backlog items,
  hoặc decision records để giúp tác vụ sau dễ dàng hơn.

**[HÀNH ĐỘNG TIẾP THEO]:** Agent BẮT BUỘC chuyển sang đọc
`_harness/01-WORKFLOW.md` để bắt đầu quy trình.

## 3. Định dạng Giao tiếp (UI Output)

Trong MỌI phản hồi gửi cho người dùng, bạn BẮT BUỘC phải mở đầu bằng khối hiển
thị tiến độ hành động hiện tại (Execution Tracker) của bạn theo định dạng sau:

```text
Action Plan
  └ ✔ [Tên bước đã hoàn thành 1]
    ✔ [Tên bước đã hoàn thành 2]
    ...
    □ [Tên bước đang/sắp thực hiện 10]
    □ [Tên bước sắp thực hiện 11]
```
