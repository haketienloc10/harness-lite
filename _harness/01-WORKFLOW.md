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

---

## GIAI ĐOẠN 2: PLANNING (Lập kế hoạch)

- **Retrieval Triggers (Kích hoạt lấy Context):**
  - `IF` chạm database schema, durable records, bảng trace, migrations: Đọc
    `scripts/schema/` (gồm `001-init.sql`) và
    `docs/decisions/0004-sqlite-durable-layer.md`.
  - `IF` chạm CLI/installer: Đọc `docs/decisions/0005...` và
    `crates/harness-cli/*`.
  - `IF` liên quan đến maturity, benchmark, observability, trace quality: Đọc
    `docs/HARNESS_COMPONENTS.md` và `docs/HARNESS_MATURITY.md`.
- **Tạo Story:**
  - `IF [Lane == tiny]`: Bỏ qua Story.
  - `IF [Lane == normal]`: Tạo 1 file từ `docs/templates/story.md`. Link product
    docs, cập nhật validation.
  - `IF [Lane == high-risk]`: Tạo folder từ `docs/templates/high-risk-story/`
    (gồm execplan, overview, design, validation).
- **Decisions:** Nếu đổi Auth, API shape, Security, Data ownership -> BẮT BUỘC
  tạo file `docs/decisions/NNNN-*.md` VÀ chạy `harness-cli decision add`.

---

## GIAI ĐOẠN 3: IMPLEMENTATION (Triển khai)

- **Quy tắc cứng:** Tuân thủ tuyệt đối "Dependency Rule" và "Parse-First
  Boundary" (Tra cứu tại `02-STANDARDS.md`).

---

## GIAI ĐOẠN 4: VALIDATION (Xác thực)

- **Validation Ladder:** `validate:quick`, `test:integration`, `test:e2e`,
  `test:platform`, `test:release`. KHÔNG báo cáo PASS nếu lệnh chưa tồn tại.
- **Story Status:** `planned`, `in_progress`, `implemented` (đã code VÀ có
  proof), `changed`, `retired`.
- **Hành động CLI:**
  1. Cập nhật matrix: `harness-cli story update --id <ID> --unit 1 ...` (Dùng
     1/0).
  2. Gắn verify command:
     `harness-cli story update --id <ID> --verify "<command>"`.
  3. Chạy xác thực: `harness-cli story verify <ID>`. _(Lệnh thoát mã 0=pass,
     1=fail. Nếu fail, Agent VẪN ĐƯỢC sang Giai đoạn 5 để ghi nhận tác vụ dở
     dang)._

---

## GIAI ĐOẠN 5: TRACE (Ghi dấu vết)

- **Outcome:** Chọn một trong: `completed`, `blocked`, `partial`, hoặc `failed`.
- **Tier Rules (Dữ liệu mảng bắt buộc dùng JSON array text):**
  - `Minimal` (Tiny): Cần `task_summary` (>10 ký tự), `outcome`.
  - `Standard` (Normal): Minimal + `intake_id`, `story_id`, `agent`,
    `actions_taken`, `files_read`, `files_changed`, `errors` hoặc `friction`.
  - `Detailed` (High-Risk): Standard + `decisions_made`, `errors` (ghi 'none'
    nếu không có), `duration_seconds`, `token_estimate`.
- **Friction & Failure Attribution:** Friction phải NÊU ĐÍCH DANH VẤN ĐỀ.
  `IF [Outcome == failed OR partial]`, Agent BẮT BUỘC quy gán lỗi vào ít nhất 1
  trong 11 danh mục (Responsibilities): _Task specification, Context selection,
  Tool access, Project memory, Task state, Observability, Failure attribution,
  Verification, Permissions, Entropy auditing, Intervention recording_.

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
