# Skill chuyên biệt: Hợp đồng & Bảng đăng ký (Registry)

Skill là một **procedure mô-đun, nạp theo trigger**, giúp Agent thực thi một
loại tác vụ lặp lại theo cách nhất quán và **kiểm chứng được**. Skill KHÁC
policy (`02-STANDARDS.md`) và KHÁC tra cứu lệnh (`03-CLI_REFERENCE.md`): skill
chỉ _điều phối_ các bước + artifact + bằng chứng sẵn có, KHÔNG nhân bản nội dung
`docs/`.

## 1. Tiêu chí "đáng làm" (điều kiện để một skill tồn tại)

Một skill chỉ được thêm khi đạt ĐỦ cả ba:

1. **Đổi hành vi mà Agent sẽ không tự làm** — không phải kể lại luật đã có trong
   workflow / `02-STANDARDS.md`. Skill chỉ "nhắc lại good practice" hầu như
   không tạo cải tiến với model mạnh → KHÔNG thêm.
2. **Có cổng kiểm chứng cơ học** (`VERIFY`) + tiêu chí `EXIT` rõ ràng. Không
   kiểm chứng được thì không phải skill.
3. **Nạp theo trigger**, ≤ ~1 trang, **trỏ tới** docs thay vì sao chép taxonomy
   / "tại sao" của `docs/`.

## 2. Cách nạp Skill (on-demand)

- Khi tới Giai đoạn ghi ở cột "Giai đoạn" của registry, quét bảng bên dưới.
  Trigger nào khớp thì đọc ĐÚNG file skill đó (chỉ file đó, để tiết kiệm token).
- KHÔNG đọc trước toàn bộ `skills/*`. Skill chỉ nạp khi trigger khớp.

## 3. Vòng đời Skill

- **Thêm mới:** chỉ qua **GĐ6 (Growth)** khi quy trình thật sự cần (friction #4
  — bước thủ công lặp lại — hoặc thiếu capability). Tạo từ
  `skills/_TEMPLATE.md`. Đây là một _Harness Delta_.
- **Sửa/Loại bỏ:** cũng là _Harness Delta_ — ghi lý do (decision/backlog nếu
  cần). Nếu một skill không còn đổi được hành vi / không đo được giá trị, hãy
  loại bỏ.
- **Ràng buộc:** mỗi skill ≤ ~1 trang; BẮT BUỘC có mục `VERIFY` và `EXIT`; KHÔNG
  seed skill chỉ để kể lại luật đã có trong workflow / `02-STANDARDS.md`.

## 4. Khuôn Skill

Mọi skill theo `skills/_TEMPLATE.md`, gồm header (Trigger, Lane, Giai đoạn) + 6
mục cố định: `INPUT` → `STEPS` → `VERIFY` → `ARTIFACTS` → `FRICTION HOOKS` →
`EXIT`. Tên file: kebab-case dạng `động từ-danh từ`.

## 5. Bảng đăng ký (Registry)

| Trigger                                                      | Skill file                |
| ------------------------------------------------------------ | ------------------------- |
| `IF [GĐ3 xong code logic, TRƯỚC khi sang GĐ4]` (normal/high) | `skills/review-3-lens.md` |

> Registry chỉ thêm skill khi có procedure NẶNG/ĐẶC THÙ đổi được hành vi — KHÔNG
> seed skill chỉ để kể lại luật đã có. Mỗi dòng map `Trigger → skills/<tên>.md`.

## 6. Liên hệ Durable Layer (CLI)

Skill hiện thuần markdown. Khi ghi trace (GĐ5), nêu skill đã dùng trong
`--actions` hoặc `--notes` (vd `"skill: review-3-lens"`) để truy vết — KHÔNG cần
đổi binary. Finding "blocking" do skill phát hiện đi vào `backlog` (GĐ6) với
`--predicted`; lỗi thật quy về 1 trong 11 Responsibilities
(`docs/HARNESS_COMPONENTS.md`) qua `--friction`.
