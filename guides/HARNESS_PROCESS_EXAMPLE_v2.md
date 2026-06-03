Mô phỏng Workflow Harness: Tính năng Đăng nhập JWT
Kịch bản (Scenario):
Người dùng (Human) yêu cầu: "Hãy thêm tính năng Đăng nhập bằng Email và Password, trả về JWT token."
GIAI ĐOẠN 0: ENTRYPOINT & PHÂN TÍCH BAN ĐẦU
Dựa theo 00-AGENTS.md, Agent nhận thức rằng mình không được phép tùy tiện sửa thẳng vào một file code nguyên khối. Mọi thay đổi phải đi từ quy trình đánh giá rủi ro và được ghi nhận vào cơ sở dữ liệu SQLite (harness.db) thông qua CLI.
GIAI ĐOẠN 1: INTAKE (Phân loại)
1. Phân tích yêu cầu:
Type: New spec (Đây là một tính năng hoàn toàn mới).
Risk Flags:
Auth: Có (Đăng nhập).
Audit/security: Có (Xử lý mật khẩu, tạo JWT).
Data model: Có (Cần schema lưu User và Password hash).
Public contracts: Có (API endpoint /login).
=> Tổng cộng: 4 Risk Flags.
Hard Gates: Chạm rào cản cứng về Auth và Audit/security.
2. Quyết định Lane:
Thuật toán: IF [Dính >= 1 Hard Gate] HOẶC [>= 4 Flags] -> Lane = high-risk.
=> Tác vụ này được phân loại vào High-Risk Lane (~10,000 tokens context).
3. Hành động CLI:
Agent ghi nhận intake vào cơ sở dữ liệu:
scripts/bin/harness-cli intake --type "New spec" --summary "Implement Email/Password login returning JWT token" --lane high-risk


(Giả định CLI trả về ID: INT-001)
GIAI ĐOẠN 2: PLANNING (Lập kế hoạch)
Vì đây là high-risk lane, Agent phải thực hiện các bước chuẩn bị nghiêm ngặt.
1. Tạo Story:
Agent tạo cấu trúc thư mục rủi ro cao cho Story này tại docs/stories/high-risk-story/auth-jwt-login/ bao gồm các file: execplan.md, overview.md, design.md, validation.md.
Đăng ký Story với Harness CLI:
scripts/bin/harness-cli story add --id STY-AUTH-01 --title "Email/Password JWT Login" --lane high-risk


2. Quyết định Kiến trúc (Decision Record - ADR):
Bắt buộc phải có vì liên quan đến Auth và Security. Agent tạo file docs/decisions/0001-use-jwt-for-auth.md (Quyết định sử dụng thuật toán nào cho JWT, thời gian hết hạn, thuật toán hash bcrypt).
scripts/bin/harness-cli decision add --id DEC-001 --title "Use JWT and Bcrypt for session/auth" --doc docs/decisions/0001-use-jwt-for-auth.md


GIAI ĐOẠN 3: IMPLEMENTATION (Triển khai)
Agent bắt đầu viết code, tuân thủ tuyệt đối 02-STANDARDS.md:
Parse-First Boundary: Tại API Controller (tầng app surfaces), payload HTTP POST /login bắt buộc phải được parse và validate thành LoginCommand { email: EmailAddress, password: PlainTextPassword } trước khi truyền vào. Không truyền raw JSON object.
Dependency Rule:
domain: Định nghĩa User entity, PasswordHasher interface, TokenGenerator interface. Không import thư viện JWT hay Bcrypt ở đây.
application: Viết LoginCommandHandler nhận LoginCommand, gọi DB lấy User, dùng PasswordHasher để check, dùng TokenGenerator để tạo JWT.
infrastructure: Implement BcryptPasswordHasher và JwtTokenGenerator.
Observability: Thêm JSON log khi login thành công/thất bại: {"action": "login_attempt", "user_id": "...", "status_code": 200, ...}
GIAI ĐOẠN 4: VALIDATION (Xác thực)
Agent cần chứng minh code hoạt động theo Test Matrix.
Unit Test: Test LoginCommandHandler với mock (pure logic).
Integration Test: Test với Database thực và thư viện mã hóa thực.
Hành động CLI:
Gắn lệnh chạy test cho Story này:
scripts/bin/harness-cli story update --id STY-AUTH-01 --verify "npm run test:integration --grep 'Auth'"


Chạy verify (Hệ thống Harness tự động chạy):
scripts/bin/harness-cli story verify STY-AUTH-01


Cập nhật Proof (Bằng chứng) vào DB sau khi test pass:
scripts/bin/harness-cli story update --id STY-AUTH-01 --unit 1 --integration 1 --e2e 0 --platform 0 --status implemented


GIAI ĐOẠN 5: TRACE (Ghi dấu vết)
Vì là high-risk lane, Agent phải ghi vết cấp độ Detailed. Agent ghi nhận lại toàn bộ thao tác:
scripts/bin/harness-cli trace \
  --summary "Implemented secure Email/Password login flow with JWT emission" \
  --outcome completed \
  --intake INT-001 \
  --story STY-AUTH-01 \
  --agent "Gemini-Harness-Agent" \
  --actions '["Created ADR 0001", "Implemented Domain/App/Infra layers", "Added Integration tests"]' \
  --read '["02-STANDARDS.md", "docs/templates/high-risk-story"]' \
  --changed '["src/domain/auth/*", "src/app/auth/*", "src/infra/auth/*", "docs/stories/*", "docs/decisions/0001*"]' \
  --decisions '["DEC-001"]' \
  --errors '["none"]' \
  --friction '["Harness CLI lacks a template generator command for high-risk story folders, had to manually create multiple markdown files"]' \
  --duration 45 \
  --tokens 8500 \
  --notes "Strict adherence to Parse-First Boundary implemented for HTTP requests."


GIAI ĐOẠN 6: GROWTH (Tiến hóa)
Trong quá trình làm, Agent nhận thấy một sự thiếu sót (Friction) được nêu trong Trace: Không có lệnh tự động sinh thư mục cho story high-risk. Agent đưa nó vào Backlog để tương lai cải thiện Harness:
scripts/bin/harness-cli backlog add \
  --title "CLI scaffolding for high-risk stories" \
  --pain "Manually creating execplan.md, overview.md... is error-prone and slow" \
  --risk normal \
  --predicted "Save 3-5 minutes per high-risk task by automating boilerplate"


GIAI ĐOẠN 7: DONE (Hoàn thành)
Agent rà soát lại Done Definition (Định nghĩa hoàn thành):
[x] Đổi code xong.
[x] Docs, Stories, Decisions đã cập nhật.
[x] Validation (Integration/Unit) đã chạy và pass.
[x] Trace chi tiết đã lưu.
[x] Backlog ticket cho tooling đã được tạo.
