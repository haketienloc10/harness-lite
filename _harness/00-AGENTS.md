# Giai đoạn 0: Entrypoint & Triết lý cốt lõi

Dự án sử dụng **Harness** — hệ điều hành cấp repository giúp Agent biến yêu cầu
thành thay đổi an toàn.

**Quy tắc định dạng:** Mọi file markdown bắt buộc sử dụng 80-character hard
wrapping cho các đoạn văn bản chuẩn.

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

## 2. Đầu ra của một tác vụ

Mỗi tác vụ tạo ra một trong hai (hoặc cả hai) kết quả:

- **Product Delta:** Thay đổi về code, test, API shape, data model, hoặc product
  docs.
- **Harness Delta:** Thay đổi về docs, templates, validation, backlog items,
  hoặc decision records để giúp tác vụ sau dễ dàng hơn.

**[HÀNH ĐỘNG TIẾP THEO]:** Agent BẮT BUỘC chuyển sang đọc
`_harness/01-WORKFLOW.md` để bắt đầu quy trình.
