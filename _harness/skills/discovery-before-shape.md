# Skill: discovery-before-shape

- **Trigger:** `IF [Chạm kiến trúc / ranh giới tầng / thêm boundary input mới]`
- **Lane áp dụng:** normal | high-risk
- **Giai đoạn:** GĐ2 (trước khi định hình code ở GĐ3)

## INPUT (gom context trước — Discovery Before Shape)

- `02-STANDARDS.md` (Dependency Rule + Parse-First Boundary + sơ đồ layering).
- Code/tầng hiện có sẽ bị đụng tới; `docs/product/*` + story liên quan.

## STEPS (công thức HOW — luật chi tiết ở 02-STANDARDS)

1. Trả lời đủ **5 khảo sát "Discovery Before Shape"** ở `02-STANDARDS.md §1`
   (product surfaces, runtime stack, core domains, boundary inputs, validation
   ladder). KHÔNG viết code ở bước này.
2. Ghi phát hiện vào `design.md` (high-risk) hoặc story (normal).
3. Chốt hướng tầng theo sơ đồ layering + Dependency Rule ở `02-STANDARDS.md`.

## VERIFY (bằng chứng cơ học)

- Self-review ở [STOP] Cửa ải Kiến trúc (GĐ3): không vi phạm Dependency Rule;
  request đã được parse ở ranh giới.

## ARTIFACTS (đầu ra)

- Mục Domain Model / Interface Contract / Data Model trong `design.md` (hoặc
  story); ghi chú boundary + validation shape.

## FRICTION HOOKS

- `IF [phải suy đoán domain model/boundary vì thiếu nguồn-sự-thật]`: ghi
  friction + backlog (GĐ5/GĐ6).
- `IF [muốn đổi hướng kiến trúc tổng thể]`: xin phép người (Cửa ải Quản trị).

## EXIT (tiêu chí xong)

- 5 khảo sát đã trả lời; hướng tầng đã chốt và không vi phạm Dependency Rule.
