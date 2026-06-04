# Trục Xương Sống: Quy trình 7 Giai đoạn (Harness Workflow)

## ĐỊNH MỨC TOKEN (Context Budget)

- **Tài liệu dùng chung (Luôn có thể truy xuất):** Bất cứ khi nào cần tương tác
  với `harness.db`, Agent luôn được phép đọc `_harness/03-CLI_REFERENCE.md` để
  lấy cú pháp.
- **Tiny Lane:** ~2,000 tokens. Chỉ đọc `00-AGENTS.md`, intake docs, matrix
  query, và file cần sửa.
- **Normal Lane:** ~5,000 tokens. Đọc thêm product/story docs liên quan,
  architecture (nếu cần đổi cấu trúc), và validation expectations.
- **High-Risk Lane:** ~10,000 tokens. Đọc toàn bộ intake, architecture, quyết
  định liên quan, templates rủi ro cao.

---

## GIAI ĐOẠN 1: INTAKE (Phân loại)

- **1. Chọn Type:** `New spec`, `Spec slice`, `Change request`,
  `New initiative`, `Maintenance request`, `Harness improvement`.
- **2. Đếm Rủi ro (Risk Flags):** (1) Auth, (2) Authorization, (3) Data model,
  (4) Audit/security, (5) External systems, (6) Public contracts, (7)
  Cross-platform, (8) Existing behavior, (9) Weak proof, (10) Multi-domain.
- **3. Hard Gates (Rào cản cứng):** Auth, Authorization, Data loss/migration,
  Audit/security, External provider, Làm yếu validation.
- **4. Thuật toán Lane:**
  - `IF` [Dính >= 1 Hard Gate] HOẶC [>= 4 Flags]: **Lane = high-risk**.
  - `IF` [2-3 Flags]: **Lane = normal**.
  - `IF` [0-1 Flags] VÀ [Sửa docs/copy/setup cơ bản]: **Lane = tiny**.
  - `IF` [0-1 Flags] VÀ [Đổi logic code]: **Lane = normal**.
- **5. Hành động:** Chạy
  `harness-cli intake --type "<loại>" --summary "<text>" --lane <lane>`.
- **[Quy tắc cấm]:** KHÔNG ĐƯỢC tạo hoặc mở rộng một file `SPEC.md` nguyên khối.
  Mọi thay đổi phải được xé nhỏ vào `docs/product/` và `docs/stories/`.

---

## GIAI ĐOẠN 2: PLANNING (Lập kế hoạch - DOCS FIRST)

- **Retrieval Triggers (Kích hoạt lấy Context):**
  - `IF` chạm database schema, durable records, migrations: Đọc
    `scripts/schema/` và `docs/decisions/0004-sqlite-durable-layer.md`.
  - `IF` chạm CLI/installer: Đọc `docs/decisions/0005...` và
    `crates/harness-cli/*`.
  - `IF` liên quan đến maturity, benchmark, trace quality: Đọc
    `docs/HARNESS_COMPONENTS.md`, `docs/HARNESS_MATURITY.md`.
- **Cập nhật Product & Tạo Story:**
  - `IF [Lane == tiny]`: Bỏ qua Story.
  - `IF [Lane == normal]`: Cập nhật `docs/product/*`. Tạo 1 file sao chép từ
    `docs/templates/story.md` VÀ lưu theo chuẩn
    `docs/stories/epics/EXX-<domain>/US-YYY-<title>.md`.
  - `IF [Lane == high-risk]`: Cập nhật `docs/product/*`. Tạo folder mới theo
    chuẩn `docs/stories/epics/EXX-<domain>/US-YYY-<title>/`. BẮT BUỘC điền đủ
    các neo nội dung:
    - `execplan.md`: (Phải có Scope, Work Phases, Stop Conditions).
    - `design.md`: (Phải có Domain Model, Interface Contract, Data Model).
    - `validation.md`: (Phải có Test Plan, Fixtures).
- **Decisions:** Nếu đổi Auth, API shape, Security, Data ownership -> BẮT BUỘC
  tạo file `docs/decisions/NNNN-*.md` VÀ chạy
  `harness-cli decision add --id <NNNN-id> --title "<Tên>" --doc docs/decisions/<file>.md`.
- **[STOP] Hard Gate:** KHÔNG ĐƯỢC phép viết hoặc sửa mã nguồn ứng dụng nếu
  Story Packet chưa được viết xong. Nếu hướng đi mông lung, DỪNG LẠI hỏi ý kiến
  con người.

---

## GIAI ĐOẠN 3: IMPLEMENTATION (Triển khai - CODE LATER)

- **Quy tắc cứng:** Chỉ bắt đầu viết code khi Giai đoạn 2 đã hoàn tất. Tuân thủ
  tuyệt đối "Dependency Rule" và "Parse-First Boundary" (Tra cứu tại
  `02-STANDARDS.md`). Bám sát chính xác những gì đã thiết kế trong `execplan.md`
  hoặc `design.md`.
- **[STOP] Cửa ải Kiến trúc:** Trước khi sang Giai đoạn 4, Agent BẮT BUỘC phải
  tự kiểm tra (self-review) mã nguồn vừa viết: Tầng `interface` có gọi thẳng vào
  `database` không? Dữ liệu request đã được parse chưa? Nếu vi phạm, phải tự sửa
  code ngay.

---

## GIAI ĐOẠN 4: VALIDATION (Xác thực)

- **Validation Ladder:** `validate:quick`, `test:integration`, `test:e2e`,
  `test:platform`, `test:release`. KHÔNG báo cáo PASS nếu lệnh chưa tồn tại.
- **Story Status:** `planned`, `in_progress`, `implemented` (đã code VÀ có
  proof), `changed`, `retired`.
- **Hành động CLI:**
  1. Gắn verify command:
     `harness-cli story update --id <ID> --verify "<command>"`.
  2. Chạy xác thực: `harness-cli story verify <ID>`. _(Lệnh thoát mã 0=pass,
     1=fail. Nếu fail, Agent VẪN ĐƯỢC sang Giai đoạn 5 để ghi nhận tác vụ dở
     dang)._
  3. Cập nhật matrix: `harness-cli story update --id <ID> --unit 1 ...` (Dùng
     1/0).
- **[STOP] Cửa ải Bằng chứng:** BẮT BUỘC phải đọc log output (stdout/stderr) của
  lệnh `verify` trước khi đánh dấu `1` (pass) vào matrix. Cấm tự suy diễn kết
  quả. (Nếu verify fail, vẫn được sang Giai đoạn 5 để ghi Trace partial/failed).

---

## GIAI ĐOẠN 5: TRACE (Ghi dấu vết)

- **Kiểm tra File:** BẮT BUỘC chạy lệnh `git status --short` để lấy chính xác
  danh sách file trước khi ghi nhận.
- **Outcome:** Chọn một trong: `completed`, `blocked`, `partial`, hoặc `failed`.
- **Tier Rules & Cú pháp CLI:** (CHÚ Ý: Lệnh CLI nhận danh sách ngăn cách bằng
  DẤU PHẨY, KHÔNG truyền ngoặc vuông JSON array).
  - `Minimal` (Tiny): Cần `task_summary` (>10 ký tự), `outcome`.
  - `Standard` (Normal): Minimal + `intake_id`, `story_id`, `agent`,
    `actions_taken` (dấu phẩy), `files_read` (dấu phẩy), `files_changed` (dấu
    phẩy), `errors` hoặc `friction`.
  - `Detailed` (High-Risk): Standard + `decisions_made` (dấu phẩy), `errors`
    (ghi 'none' nếu không có), `duration_seconds`, `token_estimate`.
- **Friction & Failure Attribution:** Friction phải NÊU ĐÍCH DANH VẤN ĐỀ (ghi
  'none' nếu đã kiểm tra và không có vấn đề).
  `IF [Outcome == failed OR partial]`, BẮT BUỘC quy gán lỗi vào 1 trong 11
  Responsibilities (VD: _Task specification_, _Data model_...).

---

## GIAI ĐOẠN 6: GROWTH (Tiến hóa)

- `IF` [Có Friction hoặc thiếu capability]: Thêm vào Backlog qua CLI.
- **Backlog Protocol:** BẮT BUỘC dùng `--predicted "<kết quả dự đoán>"`. Khi
  đóng ticket dùng `--outcome "<thực tế>"`. (Risk chỉ được chọn `tiny`,
  `normal`, `high-risk`).

---

## GIAI ĐOẠN 7: DONE (Hoàn thành)

Một tác vụ chỉ được coi là xong khi: Đổi code xong (hoặc block đã log),
Docs/Matrix cập nhật, Validation đã chạy, Trace đã lưu.

- **Rào cản Maturity (Anti-Hallucination):**
  - KHÔNG claim H3 nếu chưa có đối chiếu benchmark và quy gán lỗi theo
    Component.
  - KHÔNG claim H4 nếu chưa có hệ thống batch verification.
  - KHÔNG claim H5 nếu hệ thống tiến hóa tự động chưa chạy.
- **Hành động:** Trả lời User, tóm tắt rõ ID, thay đổi, và những gì không được
  thử.
