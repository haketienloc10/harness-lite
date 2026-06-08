# Skill: generate-knowledge-index

- **Trigger:**
  `IF [cần (tạo mới HOẶC làm mới) bản đồ onboarding repo: docs/KNOWLEDGE_INDEX.md]`
  — repo mới cài Harness chưa có index; HOẶC cấu trúc thư mục / tech stack đổi;
  HOẶC `harness-cli knowledge check` báo lỗi (thiếu/lệch/TODO). Bỏ qua nếu index
  đã có và `check` xanh.
- **Lane:** mọi lane (thường gắn GĐ2 khi onboard hoặc GĐ6 khi bảo trì).
- **Giai đoạn:** GĐ2 (Planning) hoặc GĐ6 (Growth).

Index = phần SỰ THẬT (Top-Level Structure, Key Technologies) do `harness-cli`
sinh tất định + phần NGỮ NGHĨA (Purpose, Key Concepts) do người/agent soạn và
được giữ lại giữa các marker. KHÔNG tự gõ tay phần sự thật.

## INPUT (đọc trước khi chạy)

- `_harness/03-CLI_REFERENCE.md` mục `knowledge` để biết cú pháp.
- `docs/GLOSSARY.md` + `README.md` (+ `docs/` nếu có) để soạn Purpose /
  Concepts.
- Index hiện tại nếu có: `docs/KNOWLEDGE_INDEX.md`.

## STEPS

1. **SCAFFOLD:** chạy `scripts/bin/harness-cli knowledge scaffold`. Lệnh tạo/làm
   mới `docs/KNOWLEDGE_INDEX.md`: regenerate Top-Level Structure + Key
   Technologies, GIỮ NGUYÊN Purpose/Key Concepts và mô tả từng mục đã soạn.
2. **AUTHOR:** điền giữa các marker — `KNOWLEDGE:PURPOSE:*` (1–3 câu repo dùng
   để làm gì) và `KNOWLEDGE:CONCEPTS:*` (thuật ngữ lõi, trỏ `docs/GLOSSARY.md`,
   KHÔNG nhân bản). Thay mọi `TODO: describe.` ở Top-Level Structure bằng mô tả
   1 dòng.
3. **FORMAT:** chạy `npx prettier --write docs/KNOWLEDGE_INDEX.md` (repo dùng
   `proseWrap: always`). Re-scaffold giữ nguyên nội dung đã soạn, an toàn.
4. **COMMIT:** `git add docs/KNOWLEDGE_INDEX.md`.

## VERIFY (bằng chứng cơ học)

- `scripts/bin/harness-cli knowledge check` exit `0` (không thiếu mục, không
  lệch cấu trúc so với cây thư mục hiện tại, không còn `TODO`).
- `npx prettier --check docs/KNOWLEDGE_INDEX.md` pass.

## ARTIFACTS (đầu ra)

- `docs/KNOWLEDGE_INDEX.md` (versioned).
- Trace GĐ5: ghi `"skill: generate-knowledge-index"` ở `--actions`/`--notes`.

## FRICTION HOOKS

- `IF [scaffold sinh tech sai/thiếu]` HOẶC `[mục cấu trúc gây nhiễu cần loại]`:
  ghi friction (GĐ5) + cân nhắc backlog (GĐ6) để chỉnh detection trong
  `harness-cli` thay vì sửa tay file.

## EXIT (tiêu chí xong)

- `knowledge check` xanh, prettier pass, file đã commit; Purpose + Key Concepts
  do người soạn, mọi mục cấu trúc có mô tả.
