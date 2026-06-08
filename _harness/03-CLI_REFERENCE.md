# Tra cứu lệnh Harness CLI

Trạng thái vận hành (intake, story, decision, backlog, trace) sống trong
`harness.db` và được thao tác qua `scripts/bin/harness-cli` (macOS/Linux) hoặc
`scripts/bin/harness-cli.exe` (Windows). Agent và người PHẢI dùng binary này cho
mọi việc Harness; KHÔNG sửa tay `harness.db`. Schema nằm dưới `scripts/schema/`.

## Quy ước giá trị

- **Input type** (`--type`): `new spec`, `spec slice`, `change request`,
  `new initiative`, `maintenance request`, `harness improvement`.
- **Lane / risk** (`--lane`, `--risk`): `tiny`, `normal`, `high-risk`. `low`
  KHÔNG hợp lệ.
- **Outcome** (`--outcome`): `completed`, `blocked`, `partial`, `failed`.
- **Proof booleans** (`--unit/--integration/--e2e/--platform`): dùng SỐ `1`/`0`
  (`1` = yes, `0` = no). CLI từ chối chữ `yes`/`no`.
- **Trường danh sách của trace** (`--actions/--read/--changed/--decisions`...):
  chuỗi phân tách bằng DẤU PHẨY, KHÔNG dùng ngoặc vuông JSON. Dùng `none` khi
  rỗng.

## 1. Setup

```bash
scripts/bin/harness-cli init        # Khởi tạo harness.db nếu chưa có
scripts/bin/harness-cli --version   # Xem phiên bản CLI
```

## 2. Intake (phân loại đầu vào)

```bash
scripts/bin/harness-cli intake --type <type> --summary "<text>" --lane <lane>
```

## 3. Story & Verify

```bash
# Thêm story (có thể gắn luôn lệnh proof cơ học bằng --verify)
scripts/bin/harness-cli story add --id <id> --title "<text>" --lane <lane> \
  --verify "<command>"

# Cập nhật status
scripts/bin/harness-cli story update --id <id> --status <status>

# Cập nhật proof booleans (số 1/0)
scripts/bin/harness-cli story update --id <id> \
  --unit 1 --integration 1 --e2e 0 --platform 0

# Cấu hình / đổi lệnh verify
scripts/bin/harness-cli story update --id <id> --verify "<command>"

# Chạy verify (chỉ nhận story id)
scripts/bin/harness-cli story verify <id>
```

- `story verify` chạy lệnh từ gốc repo, ghi `last_verified_at` +
  `last_verified_result`, thoát `0` nếu pass / `1` nếu fail.
- Khi `trace --story <id>` trỏ tới story có lệnh verify CHƯA từng pass, trace
  vẫn ghi nhưng in cảnh báo trước khi đóng.
- Lấy giá trị proof để copy ngược vào `story update`: dùng
  `query matrix --numeric` (xem mục 6).

## 4. Decision (quyết định)

```bash
scripts/bin/harness-cli decision add \
  --id <id> \
  --title "<text>" \
  --doc docs/decisions/<file>.md \
  --notes "<notes>"
```

- High-risk đụng auth, authorization, sở hữu dữ liệu, API shape, audit/security,
  hoặc validation: ghi quyết định ở CẢ hai nơi — file markdown dưới
  `docs/decisions/` (từ `docs/templates/decision.md`) VÀ bản ghi durable ở trên.
- Trường `--decisions` của trace chỉ là bằng chứng, KHÔNG thay cho bản ghi
  decision durable.

## 5. Trace (ghi vết thực thi)

```bash
scripts/bin/harness-cli trace \
  --summary "<text>" \
  --intake <id> \
  --story <id> \
  --agent <name> \
  --outcome <outcome> \
  --duration <seconds> \
  --tokens <estimate> \
  --actions "action1,action2" \
  --read "file1,file2" \
  --changed "file1,file2" \
  --decisions "decision1,decision2" \
  --errors "none" \
  --friction "Mô tả. Attribution: <nguồn>." \
  --notes "<text>"
```

- Độ sâu trường theo tier (lane) — xem `docs/TRACE_SPEC.md`. Lane càng cao,
  trace càng phải đầy đủ (actions, read, changed, intake/story, friction).
- Xem điểm trace in tự động ngay sau `trace`. Chỉ dùng `score-trace --id <id>`
  khi cần chấm lại một trace lịch sử cụ thể:

```bash
scripts/bin/harness-cli score-trace --id <id>
```

## 6. Query (truy vấn durable layer)

```bash
scripts/bin/harness-cli query matrix             # Proof map dạng yes/no
scripts/bin/harness-cli query matrix --numeric   # Dạng 1/0 để copy vào update
scripts/bin/harness-cli query backlog --open     # Item proposed/accepted
scripts/bin/harness-cli query backlog --closed   # So predicted với outcome
scripts/bin/harness-cli query traces             # Danh sách trace đã ghi
scripts/bin/harness-cli query friction           # Ma sát theo từng task
scripts/bin/harness-cli query stats              # Thống kê tổng quan
```

## 7. Backlog (vòng cải tiến từ friction)

```bash
# Thêm đề xuất cải tiến
scripts/bin/harness-cli backlog add \
  --title "<short name>" \
  --pain "<what was hard>" \
  --risk <tiny|normal|high-risk> \
  --predicted "<measurable impact>"

# Đóng item kèm kết quả thực đo
scripts/bin/harness-cli backlog close --id <id> --outcome "<actual result>"
```

- Outcome loop: điền `--predicted` lúc tạo (tác động kỳ vọng), điền `--outcome`
  lúc đóng (kết quả đo thực / bằng chứng review), rồi đối chiếu bằng
  `query backlog --open` và `query backlog --closed`.

## 8. Knowledge (bản đồ onboarding repo)

```bash
# Tạo/làm mới docs/KNOWLEDGE_INDEX.md (regenerate Structure + Technologies;
# giữ nguyên Purpose/Key Concepts và mô tả đã soạn giữa các marker)
scripts/bin/harness-cli knowledge scaffold

# Cổng cơ học: file có đủ mục, không lệch cấu trúc, không còn TODO (exit != 0 nếu lỗi)
scripts/bin/harness-cli knowledge check
```

- Phần tất định (Top-Level Structure, Key Technologies) do CLI sinh; phần ngữ
  nghĩa (Purpose, Key Concepts) do người/agent soạn và được giữ lại. Quy trình
  đầy đủ ở `skills/generate-knowledge-index.md`.
- Sau `scaffold` luôn chạy `npx prettier --write docs/KNOWLEDGE_INDEX.md` (repo
  dùng `proseWrap: always`); round-trip là idempotent.
