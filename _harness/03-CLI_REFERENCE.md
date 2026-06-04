# Tra cứu lệnh Harness CLI

Giao tiếp với `harness.db` qua `scripts/bin/harness-cli` (macOS/Linux) hoặc
`scripts/bin/harness-cli.exe` (Windows).

## 1. Setup & Truy vấn chung

- `scripts/bin/harness-cli init` (Khởi tạo DB)
- `scripts/bin/harness-cli query matrix` (Xem matrix dạng human-readable)
- `scripts/bin/harness-cli query matrix --numeric` (Xem dạng 1/0 để copy)
- `scripts/bin/harness-cli query backlog --open` (hoặc `--closed`)
- `scripts/bin/harness-cli query stats`
- `scripts/bin/harness-cli query friction`

## 2. Intake

- `scripts/bin/harness-cli intake --type "<type>" --summary "<text>" --lane <tiny|normal|high-risk>`

## 3. Story & Verify

- Thêm mới:
  `scripts/bin/harness-cli story add --id <id> --title "<text>" --lane <lane>`
- Cập nhật Proof (dùng số 1/0):
  `scripts/bin/harness-cli story update --id <id> --unit 1 --integration 1 --e2e 0 --platform 0 --status <status>`
- Gắn lệnh Verify:
  `scripts/bin/harness-cli story update --id <id> --verify "<command>"`
- Chạy Verify: `scripts/bin/harness-cli story verify <id>`

## 4. Decision

- `scripts/bin/harness-cli decision add --id <id> --title "<text>" --doc docs/decisions/<file>.md --notes "<notes>"`

## 5. Trace

- Chấm điểm trace: `scripts/bin/harness-cli score-trace --id <id>`
- Ghi trace (CHÚ Ý: Các trường danh sách phải dùng DẤU PHẨY, KHÔNG dùng ngoặc
  vuông JSON. Dùng 'none' nếu không có lỗi/ma sát):
  ```bash
  scripts/bin/harness-cli trace \
    --summary "<text>" \
    --outcome <completed|blocked|partial|failed> \
    --intake <id> \
    --story <id> \
    --agent <name> \
    --actions "action1,action2" \
    --read "file1,file2" \
    --changed "file1,file2" \
    --decisions "decision1,decision2" \
    --errors "none" \
    --friction "Problem description. Attribution: Task specification." \
    --duration <seconds> \
    --tokens <estimate> \
    --notes "<text>"
  ```

## 6. Backlog

- Thêm mới:
  `scripts/bin/harness-cli backlog add --title "<short name>" --pain "<what was hard>" --risk <tiny|normal|high-risk> --predicted "<measurable impact>"`
