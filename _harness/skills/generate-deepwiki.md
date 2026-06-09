# Skill: generate-deepwiki

- **Trigger:**
  `IF [cần (tạo mới HOẶC làm mới) DeepWiki của repo: docs/wiki/*.md]` — onboard
  repo cần wiki điều hướng (sơ đồ kiến trúc + tóm tắt + link nguồn); HOẶC cấu
  trúc / tech stack đổi khiến trang wiki lỗi thời; HOẶC thêm/bớt một Area lớn.
  Bỏ qua nếu wiki đã có và còn khớp cây thư mục hiện tại.
- **Lane:** mọi lane (thường gắn GĐ2 khi onboard hoặc GĐ6 khi bảo trì).
- **Giai đoạn:** GĐ2 (Planning) hoặc GĐ6 (Growth).

DeepWiki = bộ trang Markdown điều hướng codebase theo phong cách Devin DeepWiki:
**sơ đồ kiến trúc**, **tóm tắt theo Area**, và **link trỏ thẳng tới nguồn**. Đây
là _consumer_ của `docs/KNOWLEDGE_INDEX.md` (bản đồ Orient) + Hierarchy — KHÔNG
nhân bản chúng, chỉ trỏ tới và mở rộng theo từng Area. KHI MÂU THUẪN, nguồn
trong Hierarchy THẮNG.

## INPUT (đọc trước khi chạy)

- `docs/KNOWLEDGE_INDEX.md` — Purpose, Top-Level Structure, Key Technologies,
  Key Concepts (khung trang + danh sách Area). `knowledge check` đỏ ⇒ làm mới
  index TRƯỚC qua skill `generate-knowledge-index`.
- `docs/ARCHITECTURE.md` + `docs/GLOSSARY.md` + `README.md` để soạn tóm tắt / sơ
  đồ / thuật ngữ (trỏ GLOSSARY, KHÔNG chép lại).
- Cây thư mục thực tế: `git ls-files` (nguồn sự thật cho danh sách file + link).
- `.devin/wiki.json` nếu có: tôn trọng `pages` (tạo ĐÚNG các trang liệt kê) và
  `repo_notes` (ưu tiên / nhấn mạnh) để định hướng.

## STEPS

1. **ORIENT — chốt danh sách trang.** Nếu `.devin/wiki.json` có `pages`: dùng
   ĐÚNG danh sách đó (title/purpose/parent). Nếu không: gom Top-Level Structure
   của `KNOWLEDGE_INDEX.md` thành các Area lớn, mỗi Area 1 trang. Mỗi trang phải
   ánh xạ tới đường dẫn nguồn có thật.
2. **AUTHOR index `docs/wiki/README.md`:** (a) Purpose 1–3 câu khớp
   `KNOWLEDGE_INDEX.md`; (b) một sơ đồ kiến trúc Mermaid (` ```mermaid `) thể
   hiện quan hệ giữa các Area; (c) bảng "Trang" link tới MỌI trang con; (d) mục
   "Nguồn" link tới các thư mục top-level.
3. **AUTHOR mỗi trang Area `docs/wiki/<area>.md`:** Tóm tắt (mục đích Area);
   "File chính" liệt kê + link đường dẫn nguồn có thật; luồng/tương tác (Mermaid
   khi giúp ích); "Khái niệm liên quan" trỏ `docs/GLOSSARY.md`; footer "Nguồn"
   gồm link repo-relative; và link `[← Wiki](./README.md)` quay về index.
4. **CROSS-LINK:** index link tới mọi trang; mọi trang link về index; trỏ
   `KNOWLEDGE_INDEX.md` / `GLOSSARY.md` thay vì sao chép nội dung.
5. **FORMAT:** `npx prettier --write "docs/wiki/**/*.md"` (repo dùng
   `proseWrap: always`).

## VERIFY (bằng chứng cơ học)

- `test -f docs/wiki/README.md` (index tồn tại).
- `npx prettier --check "docs/wiki/**/*.md"` pass.
- KHÔNG còn placeholder: `! grep -rIn -e 'TODO' -e '<area>' -e 'TBD' docs/wiki`.
- KHÔNG có link `.md` nội bộ gãy:

  ```bash
  ! grep -rhoE '\]\(([^):#]+\.md)' docs/wiki | sed -E 's/^\]\(//' \
    | while read -r l; do [ -e "docs/wiki/$l" ] || echo "BROKEN $l"; done \
    | grep .
  ```

## ARTIFACTS (đầu ra)

- `docs/wiki/README.md` + `docs/wiki/<area>.md` (versioned).
- Trace GĐ5: ghi `"skill: generate-deepwiki"` ở `--actions`/`--notes`.

## FRICTION HOOKS

- `IF [Area không map được path]` HOẶC `[KNOWLEDGE_INDEX lệch cây thư mục]`: làm
  mới index TRƯỚC (skill `generate-knowledge-index`) rồi mới dựng wiki; ghi
  friction (GĐ5) + cân nhắc backlog (GĐ6).

## EXIT (tiêu chí xong)

- `docs/wiki/README.md` + mọi trang Area đã tạo/đổi; index link tới hết, mọi
  trang link về index.
- VERIFY xanh (prettier pass, không placeholder, không link gãy).
- Trace GĐ5 ghi `"skill: generate-deepwiki"`.

> **Vì sao tách khỏi KNOWLEDGE_INDEX (consume ↔ produce):** index là bản đồ
> Orient 1 file (router nhanh, đọc đầu mỗi tác vụ). DeepWiki là tài liệu SÂU
> theo Area để hiểu hệ thống — nó ĐỌC index làm khung rồi mở rộng. Khi cấu trúc
> / tech stack đổi: làm mới index TRƯỚC (`generate-knowledge-index`), rồi chạy
> skill này để wiki bám theo, đừng để hai tầng lệch nhau.
