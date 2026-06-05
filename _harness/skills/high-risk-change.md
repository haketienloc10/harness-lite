# Skill: high-risk-change

- **Trigger:** `IF [Lane == high-risk]` (dính ≥ 1 Hard Gate hoặc ≥ 4 Flags)
- **Lane áp dụng:** high-risk
- **Giai đoạn:** GĐ2 → GĐ5

## INPUT (gom context trước — Discovery Before Shape)

- Toàn bộ intake liên quan, architecture đụng chạm, decisions cũ.
- Templates rủi ro cao: `docs/templates/high-risk-story/*`.

## STEPS (mệnh lệnh, có thứ tự)

1. Tạo folder story 4 neo: `overview.md`, `execplan.md`, `design.md`,
   `validation.md` (điền đủ các mục bắt buộc của từng neo theo GĐ2).
2. BẮT BUỘC tạo decision record cho Auth / API shape / Security / Data ownership
   - `harness-cli decision add ...`.
3. Triển khai bám `02-STANDARDS.md` (Dependency Rule + Parse-First Boundary).
4. Qua **[STOP] Cửa ải Kiến trúc** (self-review tầng/parse) trước GĐ4.
5. GĐ4: chạy validation ladder tới mức phù hợp; **đọc log** trước khi đánh `1`
   ([STOP] Cửa ải Bằng chứng).

## VERIFY (bằng chứng cơ học)

- `harness-cli story update --id <ID> --verify "<command>"` →
  `harness-cli story verify <ID>` (đọc stdout/stderr trước khi PASS).

## ARTIFACTS (đầu ra)

- Story 4 neo, decision record(s), trace tier `Detailed`.

## FRICTION HOOKS

- `IF [validation không chạy được/quá đắt/không rõ]`: ghi friction + backlog.
- `IF [phải làm yếu validation HOẶC đổi luật lane/hard gate]`: CHẶN, xin phép
  người trước (Cửa ải Quản trị — GĐ7).

## EXIT (tiêu chí xong)

- Đủ 4 neo + decision record + proof đã đọc log + trace `Detailed` đã lưu.
