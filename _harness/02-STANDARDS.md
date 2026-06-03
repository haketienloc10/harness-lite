# Tiêu chuẩn Kỹ thuật & Kiểm thử

## 1. QUY TẮC KIẾN TRÚC (ARCHITECTURE)

**Dependency Rule (Bảng quy tắc phụ thuộc):** Inner layers không phụ thuộc outer
layers. | Tầng (Layer) | Được phép phụ thuộc vào | KHÔNG được phép phụ thuộc vào
| | :--- | :--- | :--- | | **domain** | Không gì cả (trừ pure utilities) |
framework, database, UI, provider, process/env | | **application** | domain |
framework, UI, provider, database concrete clients | | **infrastructure** |
domain, application | interface controllers hoặc UI | | **interface** | tất cả
backend layers (domain, app, infra) | UI state hoặc platform shell assumptions |
| **app surfaces** | API contracts và app-facing clients | domain internals trực
tiếp |

- **Parse-First Boundary:** Mọi dữ liệu không xác định (HTTP request, env vars,
  rows từ DB, webhooks,...) PHẢI được parse thành typed DTO hoặc command trước
  khi vào tầng application/domain. Code bên trong thao tác bằng type (`UserId`,
  `DateRange`), không thao tác bằng raw string.
- **Command/Query Separation:** Command xử lý ghi (đổi trạng thái, audit). Query
  xử lý đọc.
- **Observability Contract:** Một request = Một dòng JSON log chuẩn gồm:
  `timestamp`, `level`, `request_id`, `user_id`, `action`, `duration_ms`,
  `status_code`, `message`.

## 2. MA TRẬN KIỂM THỬ (TEST MATRIX & EVIDENCE RULES)

KHÔNG đánh dấu row là `implemented` nếu chưa có bài test.

- **Unit:** Kiểm chứng pure domain và application rules.
- **Integration:** Kiểm chứng backend, data integrity, provider behavior, jobs.
- **E2E:** Kiểm chứng user-visible browser flows.
- **Platform:** Kiểm chứng shell, deployment, mobile, desktop (những thứ không
  test được ở tầng dưới).
- _Lưu ý:_ Một story có thể không cần đánh tick 1 (có) ở toàn bộ cột nếu trong
  Story Packet có giải thích lý do.
