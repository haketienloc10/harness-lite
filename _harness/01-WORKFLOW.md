# Trục Xương Sống: Quy trình 7 Giai đoạn (Harness Workflow)

## ĐỊNH MỨC TOKEN (Context Budget)

- **Tiny Lane:** ~2,000 tokens. Chỉ đọc `00-AGENTS.md`, intake docs, matrix
  query, và file cần sửa.
- **Normal Lane:** ~5,000 tokens. Đọc thêm product/story docs liên quan,
  architecture (nếu cần đổi cấu trúc), và validation expectations.
- **High-Risk Lane:** ~10,000 tokens. Đọc toàn bộ intake, architecture, quyết
  định liên quan, templates rủi ro cao.

---

## GIAI ĐOẠN 1: INTAKE (Phân loại)

- **1. Chọn Type:** `New spec` (Spec mới), `Spec slice` (Cắt spec),
  `Change request` (Thay đổi), `New initiative` (Sáng kiến lớn),
  `Maintenance request` (Bảo trì), `Harness improvement` (Cải tiến Harness).
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

- **Retrieval Triggers (Kích hoạt lấy thêm Context):**
  - `IF` chạm DB schema/migration: Đọc `docs/decisions/0004...` và
    `scripts/schema/`(bao gồm `scripts/schema/001-init.sql`) và
    `docs/decisions/0004-sqlite-durable-layer.md`.
  - `IF` chạm CLI/installer: Đọc `docs/decisions/0005...` và
    `crates/harness-cli/*`.
  - `IF` tác vụ liên quan đến cấp độ trưởng thành (maturity), đo lường hiệu năng
    (benchmark), khả năng quan sát (observability), hoặc chất lượng dấu vết
    (trace quality): BẮT BUỘC đọc `docs/HARNESS_COMPONENTS.md` và
    `docs/HARNESS_MATURITY.md`.
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

- **Validation Ladder (Thang đo):** `validate:quick` (lint/unit),
  `test:integration` (backend/DB), `test:e2e` (browser), `test:platform`
  (shell/mobile/desktop), `test:release`. KHÔNG báo cáo PASS nếu lệnh chưa tồn
  tại.
- **Status Của Story:** `planned` (kế hoạch), `in_progress` (đang code),
  `implemented` (đã code VÀ có proof), `changed` (hợp đồng đã đổi), `retired`
  (loại bỏ).
- **Hành động CLI:**
  1. `harness-cli story update --id <ID> --unit 1 ...` (Dùng giá trị 1/0).
  2. `harness-cli story update --id <ID> --verify "<command>"`.
  3. `harness-cli story verify <ID>`. Lệnh này sẽ thoát với mã 0 (pass) hoặc 1
     (fail). Nếu fail, Agent vẫn được phép chuyển sang Giai đoạn 5 để ghi nhận
     tác vụ dở dang (hệ thống sẽ tự in ra một cảnh báo).

---

## GIAI ĐOẠN 5: TRACE (Ghi dấu vết)

- **Trạng thái kết quả (Outcome):** Bắt buộc đánh giá thực tế và chọn một trong
  các giá trị: `completed`, `blocked`, `partial`, hoặc `failed`.
- **Bắt buộc theo Tier(Lưu ý: Các trường danh sách phải dùng định dạng JSON
  array text):**
  - `Minimal` (Cho Tiny): Cần `task_summary` (>10 ký tự), `outcome` (completed,
    blocked, partial, failed).
  - `Standard` (Cho Normal): Cần Minimum + `intake_id`, `story_id`, `agent`,
    `actions_taken` (JSON), `files_read` (JSON), `files_changed` (JSON),
    `errors` hoặc `friction`.
  - `Detailed` (Cho High-Risk): Cần Standard + `decisions_made` (JSON), `errors`
    (JSON, ghi 'none' nếu không có), `duration_seconds`, `token_estimate`.
- **Friction Protocol:** Friction phải NÊU ĐÍCH DANH VẤN ĐỀ, không nêu cảm xúc
  (Ví dụ Tốt: "Docs thiếu copy cho installer", Ví dụ Tồi: "Docs khó hiểu"). `IF`
  tác vụ thất bại (failed/blocked) và cần quy gán lỗi (failure attribution) cho
  một thành phần hệ thống cụ thể: BẮT BUỘC đọc và tham chiếu
  `docs/HARNESS_COMPONENTS.md` trong trường báo cáo.

---

## GIAI ĐOẠN 6: GROWTH (Tiến hóa)

- `IF` [Có Friction hoặc thiếu capability]: Đưa vào Backlog qua CLI.
- **Quy tắc Backlog Outcome Loop:** Khi tạo, BẮT BUỘC dùng
  `--predicted "<dự đoán kết quả>"`. Khi đóng, dùng
  `--outcome "<kết quả thực tế>"` để AI sau này so sánh. Rủi ro của backlog chỉ
  được chọn `tiny`, `normal`, hoặc `high-risk` (Không có 'low').

---

## GIAI ĐOẠN 7: DONE (Hoàn thành)

Một tác vụ chỉ được coi là xong (Done Definition) khi:

1. Đổi code xong HOẶC blocker được ghi chú lại.
2. Docs, Stories, Test Matrix được cập nhật thực tế.
3. Validation commands đã chạy.
4. Trace đã lưu.
5. Missing harness capabilities đã lưu vào Backlog.
6. Câu trả lời cuối cùng cho User phải nêu rõ cái gì ĐÃ THAY ĐỔI và cái gì KHÔNG
   ĐƯỢC THỬ.
