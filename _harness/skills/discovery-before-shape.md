# Skill: discovery-before-shape

- **Trigger:** `IF [Chạm kiến trúc / ranh giới tầng / thêm boundary input mới]`
- **Lane áp dụng:** normal | high-risk
- **Giai đoạn:** GĐ2 (trước khi định hình code ở GĐ3)

## INPUT (gom context trước — Discovery Before Shape)

- `02-STANDARDS.md` (Dependency Rule + Parse-First Boundary + sơ đồ layering).
- Code/tầng hiện có sẽ bị đụng tới; `docs/product/*` + story liên quan.

## STEPS (mệnh lệnh, có thứ tự)

1. **Khảo sát trước khi định hình** (KHÔNG viết code ở bước này):
   - Product surfaces: tính năng đụng tới ở đâu?
   - Runtime stack: ngôn ngữ/framework/tầng nào liên quan?
   - Core domains: domain model nào bị ảnh hưởng?
   - Boundary inputs: dữ liệu vào từ đâu, phải parse ở ranh giới nào?
   - Validation ladder: chứng minh đúng bằng mức nào (`validate:quick` →
     `test:platform`)?
2. Ghi phát hiện vào `design.md` (high-risk) hoặc story (normal).
3. Chốt hướng tầng: `interface`/`application`/`domain`/`infrastructure` — KHÔNG
   để `interface` gọi thẳng `database`.

## VERIFY (bằng chứng cơ học)

- Self-review ở [STOP] Cửa ải Kiến trúc (GĐ3): không vi phạm Dependency Rule;
  request đã được parse ở ranh giới.

## ARTIFACTS (đầu ra)

- Mục Domain Model / Interface Contract / Data Model trong `design.md` (hoặc
  story); ghi chú boundary + validation shape.

## FRICTION HOOKS

- `IF [phải suy đoán domain model/boundary vì thiếu nguồn-sự-thật]`: ghi
  friction
  - backlog.
- `IF [muốn đổi hướng kiến trúc tổng thể]`: xin phép người (Cửa ải Quản trị).

## EXIT (tiêu chí xong)

- 5 khảo sát đã trả lời; hướng tầng đã chốt và không vi phạm Dependency Rule.
