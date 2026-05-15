# Planner Brief

## Classification Summary

- Classification: Normal Run
- Why this is bounded: Yêu cầu hiện tại chỉ cần lập kế hoạch cho một webapp giao tiếp với `codex-cli`, không implement code, không tạo test, không chỉnh cấu hình production.
- If part of Epic, independent verification target: Không áp dụng.

## Related Epic

None

## Goal

Tạo kế hoạch triển khai một webapp cho phép người dùng gửi prompt tới `codex-cli`, gồm hai kiểu tương tác chính:

- Chat prompt thông thường.
- Slash command, ví dụ dạng `/command args`, được nhận diện trong UI và chuyển tới backend để thực thi qua `codex-cli` theo contract rõ ràng.

Run này chỉ tạo kế hoạch sẵn sàng để review/implement ở bước sau; không thực hiện scaffold hoặc chỉnh sửa mã nguồn ứng dụng.

## Context Summary

- Nguồn sự thật: `_harness/runs/2026-05-16-codex-cli-webapp-plan/00-input.md`.
- User muốn một webapp giao tiếp với `codex-cli`, ngoài chat còn hỗ trợ slash command.
- Kiểm tra tối thiểu repo không thấy scaffold webapp hiện hữu như `package.json`, `src/`, `app/`, `pages/`, `vite.config.*`, hoặc `next.config.*`; kế hoạch nên giả định đây là greenfield trong repo hiện tại, trừ khi contract reviewer hoặc user cung cấp nền tảng khác.
- Tài liệu và giao tiếp dùng tiếng Việt.

## In Scope

- Lập phạm vi chức năng tối thiểu cho webapp:
  - UI chat nhập prompt, hiển thị transcript, trạng thái đang chạy, lỗi, và kết quả.
  - Nhận diện slash command từ input bắt đầu bằng `/`.
  - Backend/API nhận request từ UI và gọi `codex-cli` bằng process execution có kiểm soát.
  - Trả kết quả dạng streaming nếu khả thi; nếu chưa đủ điều kiện, fallback response theo batch vẫn phải được nêu rõ.
  - Quản lý working directory/session tối thiểu để `codex-cli` có ngữ cảnh chạy.
- Xác định contract dữ liệu giữa UI và backend:
  - Request cho chat prompt.
  - Request cho slash command.
  - Response/result event, error event, trạng thái chạy/hủy.
- Xác định các luồng kiểm thử cần có cho lần implement sau:
  - Unit test parser slash command.
  - API test cho chat/slash command.
  - Test lỗi khi `codex-cli` không tồn tại hoặc trả non-zero exit.
  - Kiểm tra UI cơ bản cho nhập prompt, gửi command, và hiển thị lỗi.
- Xác định rủi ro bảo mật khi webapp có quyền chạy CLI:
  - Command injection.
  - Quyền truy cập filesystem.
  - Process timeout/cancellation.
  - Giới hạn working directory được phép.

## Out of Scope

- Không implement code trong run này.
- Không scaffold framework, không cài dependency, không tạo `package.json`.
- Không thay đổi source code ứng dụng, test, config, lockfile, generated artifact.
- Không thiết kế hệ thống multi-user, auth phức tạp, billing, cloud deployment, hoặc persistence dài hạn trừ khi user yêu cầu sau.
- Không tự mở rộng slash command thành command registry lớn; chỉ lập kế hoạch cho cơ chế parser/dispatch tối thiểu.
- Không gọi thật `codex-cli` trong run planner.

## Acceptance Criteria

- [ ] AC1: Planner brief mô tả rõ mục tiêu, phạm vi, out-of-scope và giả định greenfield dựa trên bằng chứng repo hiện tại.
- [ ] AC2: Plan nêu được kiến trúc đề xuất ở mức triển khai: UI, backend/API, process runner cho `codex-cli`, parser slash command, streaming/batch result.
- [ ] AC3: Plan xác định contract tối thiểu cho chat prompt và slash command để role sau có thể review trước khi implement.
- [ ] AC4: Plan có danh sách test/verification cụ thể cho lần implement sau, bao gồm happy path, lỗi CLI, parser slash command, và UI behavior.
- [ ] AC5: Plan nêu rõ rủi ro bảo mật/vận hành khi chạy CLI từ webapp và các guardrail cần có.

## Likely Impacted Areas

- Module: Greenfield webapp scaffold nếu implementation được duyệt ở run sau; chưa có module hiện hữu được xác định.
- Page/API: Một page chat chính; API endpoint hoặc server route để gửi prompt/slash command và nhận kết quả.
- Data model: Message transcript, command request, command result/error, run status; có thể chỉ lưu in-memory trong MVP.
- Test area: Slash command parser, API handler, process runner wrapper, UI interaction.

## Risks / Unknowns

- Chưa rõ `codex-cli` được gọi bằng binary/command chính xác nào, input/output format ổn định ra sao, có hỗ trợ streaming JSON/event hay chỉ stdout text.
- Chưa rõ webapp nên dùng framework nào; do repo chưa có scaffold, contract reviewer nên xác nhận stack trước khi generator implement.
- Chạy CLI từ web server có rủi ro bảo mật cao nếu nhận input tùy ý; implementation cần allowlist cwd, timeout, sanitize args, và không shell-interpolate raw input.
- Slash command có thể mơ hồ giữa lệnh nội bộ webapp và prompt bắt đầu bằng `/`; cần UX/contract rõ ràng để escape hoặc gửi như chat thường.
- Nếu cần phiên làm việc dài hạn với `codex-cli`, cần xác nhận cơ chế session/context của CLI trước khi thiết kế persistence.

## Planner Notes for Generator

Nếu plan được contract reviewer duyệt và có yêu cầu implement sau, generator nên đi theo thứ tự:

1. Xác nhận/thiết lập stack tối thiểu phù hợp repo. Nếu không có ràng buộc khác, chọn một webapp Node-based đơn giản có server API cục bộ để gọi process.
2. Tạo abstraction nhỏ cho `codex-cli` runner:
   - Dùng `spawn`/process API với argv array, không dùng shell string.
   - Có timeout, cancellation, capture stdout/stderr, exit code.
   - Giới hạn working directory trong repo hoặc directory được config rõ.
3. Tạo parser slash command thuần function:
   - Input bắt đầu bằng `/` được parse thành `{name, args, raw}`.
   - Input không bắt đầu bằng `/` là chat prompt.
   - Có test cho quoted args/empty command nếu phạm vi MVP chọn hỗ trợ.
4. Tạo API contract tối thiểu:
   - `POST /api/codex/chat` hoặc endpoint tương đương cho prompt thường.
   - `POST /api/codex/command` hoặc endpoint chung có field `type`.
   - Response gồm `status`, `stdout`/`content`, `stderr`, `exitCode`, `error`.
5. Tạo UI chat chính:
   - Input composer dùng chung cho chat và slash command.
   - Transcript phân biệt user prompt, slash command, assistant/result, error.
   - Disable send khi đang chạy hoặc hỗ trợ cancel nếu runner đã có cancellation.
6. Verification sau implement:
   - Unit test parser.
   - API/runner test với mock `codex-cli`.
   - UI smoke test cho gửi chat, gửi `/help` hoặc command mẫu, và hiển thị lỗi.
   - Manual check: chạy dev server, gửi prompt thường và slash command qua mock hoặc binary thật nếu có.
