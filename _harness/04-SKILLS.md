# Skill chuyên biệt: Hợp đồng & Bảng đăng ký (Registry)

Skill là một **procedure mô-đun, kích hoạt theo trigger**, giúp Agent thực thi
một loại tác vụ lặp lại một cách nhất quán. Skill KHÁC với policy
(`02-STANDARDS.md`) và KHÁC với tra cứu lệnh (`03-CLI_REFERENCE.md`): skill chỉ
_điều phối_ các bước

- artifact + bằng chứng sẵn có, KHÔNG nhân bản nội dung của `docs/`.

## 1. Cách nạp Skill (on-demand)

- Ở **GĐ2**, sau khi chốt `Type` + `Lane`, quét bảng registry bên dưới. Trigger
  nào khớp thì đọc ĐÚNG file skill đó (chỉ file đó, để tiết kiệm token).
- KHÔNG đọc trước toàn bộ `skills/*`. Skill chỉ nạp khi trigger khớp.

## 2. Vòng đời Skill

- **Thêm mới:** chỉ qua **GĐ6 (Growth)** khi friction #4 (bước thủ công lặp lại)
  xuất hiện. Tạo skill từ `skills/_TEMPLATE.md`. Đây là một _Harness Delta_.
- **Sửa/Loại bỏ:** cũng là _Harness Delta_ — ghi lý do (decision/backlog nếu
  cần).
- **Ràng buộc:** mỗi skill ≤ ~1 trang; BẮT BUỘC có mục `VERIFY` và `EXIT` (nếu
  không kiểm chứng được thì không phải skill); KHÔNG sao chép taxonomy/“tại sao”
  của `docs/` — chỉ trỏ tới.

## 3. Khuôn Skill

Mọi skill theo `skills/_TEMPLATE.md`, gồm header (Trigger, Lane, Giai đoạn) + 6
mục cố định: `INPUT` → `STEPS` → `VERIFY` → `ARTIFACTS` → `FRICTION HOOKS` →
`EXIT`. Tên file: kebab-case dạng `động từ-danh từ`.

## 4. Bảng đăng ký (Registry)

| Trigger                                | Skill file                         |
| -------------------------------------- | ---------------------------------- |
| `IF [Type == New spec]`                | `skills/decompose-new-spec.md`     |
| `IF [Lane == high-risk]`               | `skills/high-risk-change.md`       |
| `IF [Chạm kiến trúc/ranh giới tầng]`   | `skills/discovery-before-shape.md` |
| `IF [GĐ5/GĐ6: ghi dấu vết + tiến hóa]` | `skills/record-trace-friction.md`  |

## 5. Liên hệ Durable Layer (CLI)

Skill hiện thuần markdown. Khi ghi trace, nêu skill đã dùng trong `--actions`
hoặc `--notes` (vd `"skill: high-risk-change"`) để truy vết — KHÔNG cần đổi
binary. (Việc đưa skill vào `harness.db` / lệnh `harness-cli skill ...` là việc
tương lai, nằm ngoài phạm vi hiện tại.)
