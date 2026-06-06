# Skill: tdd-workflow

- **Trigger:** `IF [GĐ3: triển khai code logic]` (bỏ qua nếu docs-only/tiny)
- **Lane áp dụng:** normal | high-risk
- **Giai đoạn:** GĐ3 (Implementation) → GĐ4 (Validation)

## INPUT (gom context trước — Discovery Before Shape)

- `execplan.md` / `design.md` của story (đặc biệt mục Interface Contract).
- `02-STANDARDS.md`: Dependency Rule, Parse-First Boundary, Test Matrix
  (Unit/Integration/E2E/Platform).
- Lệnh test/coverage thật của dự án (qua Validation Ladder ở GĐ4).

## STEPS (chu trình TDD — mệnh lệnh, có thứ tự)

1. **Interface trước:** chốt type/contract của đơn vị cần làm (DTO/Command, chữ
   ký hàm, ranh giới tầng) theo `design.md`; KHÔNG viết logic ở bước này.
2. **RED:** viết test thất bại trước, đúng tier Test Matrix phù hợp; chạy để xác
   nhận nó FAIL vì lý do đúng (chưa có implementation).
3. **GREEN:** viết code tối thiểu cho test PASS; không thêm tính năng ngoài
   test.
4. **REFACTOR:** dọn code/test khi đang xanh; giữ test luôn PASS; không phá
   Dependency Rule / Parse-First Boundary.
5. **Lặp** 2→4 cho từng hành vi tới khi đủ phạm vi story.

## VERIFY (bằng chứng cơ học)

- Gắn + chạy: `harness-cli story update --id <ID> --verify "<lệnh test>"` →
  `harness-cli story verify <ID>` (đọc log trước khi đánh `1` — Cửa ải Bằng
  chứng GĐ4).
- **Coverage ≥ 80%** ở phạm vi vừa làm; nếu < 80%, bổ sung test (về RED) trước
  khi coi là xong.

## ARTIFACTS (đầu ra)

- Test mới (theo tier Matrix) + code implementation; cập nhật matrix story
  (`--unit/--integration/...` = 1/0); trace ghi `"skill: tdd-workflow"`.

## FRICTION HOOKS

- `IF [không viết được test trước vì interface/design còn mơ hồ]`: quay lại GĐ2;
  ghi friction (GĐ5).
- `IF [test không chạy được / coverage tool thiếu / quá tốn kém]`: ghi
  friction + backlog (GĐ6).
- `IF [muốn hạ ngưỡng coverage < 80% hoặc bỏ tier test bắt buộc]`: CHẶN, xin
  phép người (Cửa ải Quản trị — GĐ7).

## EXIT (tiêu chí xong)

- Mọi hành vi trong scope có test PASS; `story verify` exit 0 (đã đọc log);
  coverage ≥ 80%; matrix đã cập nhật; không vi phạm Dependency Rule.
