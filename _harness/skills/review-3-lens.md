# Skill: review-3-lens

- **Trigger:** `IF [GĐ3 đã xong code logic, TRƯỚC khi sang GĐ4 Validation]` (bỏ
  qua nếu docs-only/tiny).
- **Lane áp dụng:** normal | high-risk.
- **Giai đoạn:** Cổng GĐ3 → GĐ4 (thay cho "Cửa ải Kiến trúc" đơn lẻ).

Mục tiêu: chạy MỘT vòng review độc lập, đa góc với "mắt mới" rồi **gate** kết
quả — thứ Agent hiếm khi tự làm có kỷ luật. Self-check nội tuyến lúc code (GĐ3)
là _phòng ngừa_; skill này là _kiểm chứng độc lập_, vì cùng bối cảnh viết ra bug
thường không thấy bug.

## INPUT (gom context trước — Discovery Before Shape)

- Diff vừa viết: lấy danh sách file qua `git status --short` + đọc nội dung thay
  đổi.
- `02-STANDARDS.md`: Dependency Rule, Parse-First Boundary, Command/Query, Test
  Matrix, Observability Contract.
- Story packet (`execplan.md`/`design.md`, mục Interface Contract + Validation)
  và intake (Type/Lane + Risk Flags/Hard Gates đã đếm ở GĐ1).
- `docs/HARNESS_COMPONENTS.md` (11 Responsibilities) để quy gán finding.

## STEPS (3 lens — mỗi lens là một pass độc lập, xuất verdict riêng)

> Mỗi lens KHÔNG sửa code; chỉ xuất danh sách finding, mỗi finding gắn
> `severity = blocking | minor` + một `responsibility`. Ba lens nên chạy **độc
> lập** (có thể là 3 sub-agent song song để giảm thiên kiến); nếu chạy tuần tự,
> đừng để kết luận lens trước dẫn dắt lens sau.

1. **Lens 1 — Quality & Architecture:** `interface` có gọi thẳng `database`? Dữ
   liệu biên đã parse thành typed DTO/Command (Parse-First) trước khi vào
   application/domain? Inner layer có phụ thuộc outer layer? Command/Query tách
   bạch? Logic có đúng `design.md` và xử lý đúng đầu vào không.
2. **Lens 2 — Security & Risk:** chạm Hard Gate nào (auth, authorization,
   data-loss/migration, audit/security, external provider, làm yếu validation)?
   Input từ biên đã validate? Có secret/credential lộ trong code/log? Mỗi rủi ro
   chạm Hard Gate BẮT BUỘC có decision record (`docs/decisions/NNNN-*.md`).
3. **Lens 3 — Maintainability & Proof:** test đủ tier Test Matrix cho hành vi
   vừa thêm? Proof có thực sự khớp claim? Naming/coupling/độ phức tạp có cản
   phiên sau? Có log JSON theo Observability Contract khi cần?

## VERIFY (bằng chứng cơ học)

- Chạy lại proof và ĐỌC log trước khi kết luận Lens 3:
  `harness-cli story verify <ID>` (Cửa ải Bằng chứng GĐ4 — cấm suy diễn kết
  quả).
- Tổng hợp finding theo severity. **Mỗi finding `blocking` phải** hoặc (a) đã
  sửa code rồi `story verify` lại pass, hoặc (b) ghi backlog (GĐ6) bằng
  `harness-cli backlog add --predicted "<tác động kỳ vọng>"`.
- **Gate:** KHÔNG đánh proof `1` vào matrix / không sang GĐ4 sign-off khi còn
  finding `blocking` chưa xử lý.

## ARTIFACTS (đầu ra)

- Khối review có cấu trúc (3 verdict + finding list) đưa vào trace GĐ5
  (`--notes`), kèm `"skill: review-3-lens"` trong `--actions`/`--notes`.
- Finding `blocking` chưa sửa ngay → 1 `backlog` item (có `--predicted`).
- Nếu review lộ ra lỗi thật/luật thiếu → `--friction` với `Attribution:` về đúng
  1 trong 11 Responsibilities.

## FRICTION HOOKS

- `IF [review phải suy đoán một luật/nguồn-sự-thật còn thiếu]` HOẶC
  `[lỗi cùng loại lặp lại]`: ghi friction (GĐ5) + thêm backlog (GĐ6).

## EXIT (tiêu chí xong)

- Cả 3 lens đều có verdict.
- 0 finding `blocking` tồn đọng (đã sửa + re-verify, hoặc đã ghi backlog).
- `story verify <ID>` đã chạy và log đã đọc.
- Trace GĐ5 ghi `"skill: review-3-lens"`.
