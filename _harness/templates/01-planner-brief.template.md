# [PLANNER_BRIEF_DOCUMENT]

> **INSTRUCTIONS FOR LLM**: Tuân thủ nghiêm ngặt định dạng bên dưới. Thay thế các nội dung trong ngoặc vuông `[...]` bằng dữ liệu tương ứng. Không tự ý thêm các phần mới. Nếu một trường không có dữ liệu hoặc không áp dụng, hãy điền `None` hoặc `N/A`.

## 1. META_CLASSIFICATION
- **Classification**: [ENUM: NORMAL_RUN | EPIC_CHILD_RUN]
- **Related_Epic**: [Điền ID/Tên của Epic liên quan HOẶC `None` nếu là Normal Run]
- **Why_Bounded**: [Giải thích ngắn gọn tại sao scope của tác vụ này đã được giới hạn an toàn]
- **Independent_Verification_Target**: [IF EPIC_CHILD_RUN: Mô tả cách kiểm thử độc lập phần này. IF NORMAL_RUN: Điền `N/A`]

## 2. OBJECTIVES_AND_CONTEXT
### 2.1. Goal
> [Mục tiêu cốt lõi cần đạt được. RÀNG BUỘC: Viết lại rõ ràng, súc tích, định lượng được nếu có thể. Tối đa 2 câu.]

### 2.2. Context_Summary
> [Tóm tắt bối cảnh và lý do (The "Why"). RÀNG BUỘC: Tuyệt đối KHÔNG đi sâu vào chi tiết kỹ thuật/implementation (No over-specifying). Tối đa 3-4 câu.]

## 3. SCOPE_BOUNDARIES
### 3.1. In_Scope
- [Hạng mục/Tính năng 1 nằm trong phạm vi]
- [Hạng mục/Tính năng 2 nằm trong phạm vi]

### 3.2. Out_Of_Scope
- [Hạng mục/Tác vụ ngoại trừ, đặc biệt là những thứ dễ gây hiểu lầm là có trong scope]

## 4. ACCEPTANCE_CRITERIA (AC)
> RÀNG BUỘC: Viết AC dưới góc độ hành vi của hệ thống hoặc người dùng (Behavior-driven).
- [ ] AC1: [Điều kiện nghiệm thu 1]
- [ ] AC2: [Điều kiện nghiệm thu 2]
- [ ] AC3: [Điều kiện nghiệm thu 3]

## 5. IMPACT_AND_RISK_ASSESSMENT
### 5.1. Likely_Impacted_Areas
- **Module**: [Tên các module bị ảnh hưởng HOẶC `None`]
- **Page_API**: [Danh sách Route/URL/API Endpoints HOẶC `None`]
- **Data_Model**: [Các bảng DB/Schema/Collection cần thay đổi HOẶC `None`]
- **Test_Area**: [Khu vực trọng tâm QA cần chú ý HOẶC `None`]

### 5.2. Risks_And_Unknowns
- [Liệt kê rủi ro 1 - e.g., third-party dependency, performance issue]
- [Liệt kê các ẩn số (Unknowns) cần điều tra thêm HOẶC điền `None`]

## 6. HANDOFF_NOTES
### Planner_Notes_For_Generator
- [Chỉ thị trực tiếp 1. RÀNG BUỘC: Tập trung vào các lưu ý đặc biệt, những cạm bẫy (pitfalls) cần tránh khi implement.]
- [Chỉ thị trực tiếp 2]