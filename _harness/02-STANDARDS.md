# Tiêu chuẩn Kỹ thuật & Kiểm thử

## 1. QUY TẮC KIẾN TRÚC (ARCHITECTURE)

**Discovery Before Shape:** Trước khi định hình code/kiến trúc, BẮT BUỘC xác
định: (1) product surfaces (browser/mobile/desktop/CLI/API/worker); (2) runtime
stack (ngôn ngữ, framework, DB, queue, provider, hosting); (3) core domains; (4)
boundary inputs (request, env, webhook, file, credential); (5) validation
ladder. Chỉ tạo folder/scaffold thật khi một Story bước vào triển khai.

```text
domain <- application <- infrastructure <- interface <- app surfaces
```

**Dependency Rule (Quy tắc phụ thuộc):** Inner layers KHÔNG phụ thuộc outer
layers.

| Tầng (Layer)       | Được phép phụ thuộc vào                  | KHÔNG được phụ thuộc vào                           |
| ------------------ | ---------------------------------------- | -------------------------------------------------- |
| **domain**         | Không gì cả (trừ pure utilities)         | framework, database, UI, provider, process/env     |
| **application**    | domain                                   | framework, UI, provider, database concrete clients |
| **infrastructure** | domain, application                      | interface controllers hoặc UI                      |
| **interface**      | tất cả backend layers (domain/app/infra) | UI state hoặc platform shell assumptions           |
| **app surfaces**   | API contracts và app-facing clients      | domain internals trực tiếp                         |

- **Parse-First Boundary:** Dữ liệu chưa rõ định dạng (HTTP request, env vars,
  rows từ DB, webhooks,...) PHẢI được parse thành typed DTO/Command trước khi
  vào application/domain. Code bên trong thao tác bằng Type (`UserId`,
  `DateRange`), không thao tác bằng raw string.
- **Command/Query Separation:** Command xử lý ghi (đổi trạng thái, sinh audit
  log). Query xử lý đọc.
- **Observability Contract:** Một request = Một dòng JSON log chuẩn gồm:
  `timestamp`, `level`, `request_id`, `user_id`, `action`, `duration_ms`,
  `status_code`, `message`.

## 2. MA TRẬN KIỂM THỬ (TEST MATRIX)

KHÔNG đánh dấu row là `implemented` nếu chưa có bài test.

- **Unit:** Kiểm chứng pure domain và application rules.
- **Integration:** Kiểm chứng backend, data integrity, provider behavior, jobs.
- **E2E:** Kiểm chứng user-visible browser flows.
- **Platform:** Kiểm chứng shell, deployment, mobile, desktop (những thứ không
  test được ở tầng dưới).
