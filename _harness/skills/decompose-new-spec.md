# Skill: decompose-new-spec

- **Trigger:** `IF [Type == New spec]`
- **Lane áp dụng:** mọi lane (lane quyết định độ sâu story packet)
- **Giai đoạn:** GĐ2 (Planning — DOCS FIRST)

## INPUT (gom context trước — Discovery Before Shape)

- Spec gốc (coi là _input material_, KHÔNG phải spec sống).
- `docs/product/*` hiện có để biết chỗ ghép vào.
- `00-AGENTS.md` §1 (hierarchy nguồn sự thật).

## STEPS (mệnh lệnh, có thứ tự)

1. Coi spec là input; KHÔNG tạo/mở rộng file `SPEC.md` nguyên khối ([Quy tắc
   cấm] ở GĐ2).
2. Xé nhỏ nội dung vào `docs/product/*` (mỗi chủ đề một file nhỏ).
3. Liệt kê candidate epics/stories; đặt theo chuẩn
   `docs/stories/epics/EXX-<domain>/US-YYY-<title>(.md|/)`.
4. Với mỗi open decision (Auth/API/Security/Data ownership): tạo
   `docs/decisions/NNNN-*.md` + chạy
   `harness-cli decision add --id <NNNN-id> --title "<Tên>" --doc <file>`.
5. Tạo story packet theo lane (tiny: bỏ story; normal: 1 file; high-risk: 4
   neo).

## VERIFY (bằng chứng cơ học)

- Mỗi story có verify command; chạy `harness-cli story verify <ID>` khi đã code.
- `harness-cli query matrix` không còn yêu cầu nào "mồ côi" ngoài product/story.

## ARTIFACTS (đầu ra)

- `docs/product/*`, `docs/stories/epics/*`, `docs/decisions/*`, intake record.

## FRICTION HOOKS

- `IF [spec mơ hồ/mâu thuẫn/thiếu nguồn-sự-thật]`: ghi friction (GĐ5) + backlog.

## EXIT (tiêu chí xong)

- Không còn spec nguyên khối; mọi yêu cầu đã nằm trong `docs/product/*` +
  `docs/stories/*`; open decisions đã có file + bản ghi durable.
