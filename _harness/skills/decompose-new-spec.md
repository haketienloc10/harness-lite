# Skill: decompose-new-spec

- **Trigger:** `IF [Type == New spec]`
- **Lane áp dụng:** mọi lane (lane quyết định độ sâu story packet)
- **Giai đoạn:** GĐ2 (Planning — DOCS FIRST)

## INPUT (gom context trước — Discovery Before Shape)

- Spec gốc (coi là _input material_, KHÔNG phải spec sống).
- `docs/product/*` hiện có để biết chỗ ghép vào.
- `00-AGENTS.md` §1 (hierarchy nguồn sự thật).

## STEPS (công thức HOW — luật chi tiết ở GĐ2)

Trình tự thực thi; luật giữ ở workflow, không lặp lại ở đây:

1. Xé spec vào `docs/product/*` (theo "Xử lý theo Input Type" + [Quy tắc cấm]).
2. Lập candidate epics/stories theo chuẩn đặt tên ở GĐ2.
3. Open decision → decision record + `harness-cli decision add` (theo
   "Decisions" GĐ2).
4. Tạo story packet theo lane (theo "Cập nhật Product & Tạo Story" GĐ2).

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
