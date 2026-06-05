# Skill: record-trace-friction

- **Trigger:** `IF [GĐ5/GĐ6: ghi dấu vết + tiến hóa]`
- **Lane áp dụng:** mọi lane (tier trace theo lane)
- **Giai đoạn:** GĐ5 → GĐ6

## INPUT (gom context trước — Discovery Before Shape)

- `git status --short` (danh sách file chính xác).
- Kết quả lệnh `verify`, `intake_id`, `story_id`.

## STEPS (checklist mỏng — luật chi tiết ở GĐ5/GĐ6)

1. Thực hiện GĐ5: chọn `outcome` → ghi trace đúng tier theo lane (dấu phẩy,
   không JSON) → quy gán lỗi nếu `failed/partial` → áp 5 trigger Friction.
2. Thực hiện GĐ6: friction/thiếu capability → backlog `--predicted` /
   `--outcome`.

## VERIFY (bằng chứng cơ học)

- `harness-cli query traces` xác nhận trace đã ghi; `harness-cli query friction`
  / `query backlog` xác nhận friction/backlog (nếu có).

## ARTIFACTS (đầu ra)

- Trace record; friction (trong trace); backlog item (nếu cần).

## FRICTION HOOKS

- `IF [bước thủ công lặp lại]` (friction #4): cân nhắc tạo skill mới từ
  `skills/_TEMPLATE.md` (đăng ký vào `04-SKILLS.md`).

## EXIT (tiêu chí xong)

- Trace đã lưu; friction = `none` hoặc đã nêu đích danh; backlog đã thêm nếu
  cần.
