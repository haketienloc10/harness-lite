# AGENTS.md

Repository này đã cài **Harness** để điều phối AI-assisted development bằng artifacts, lifecycle state.

## Language Rule

Reply theo ngôn ngữ người dùng; giữ code, command, path, API name, logs, schema keys, package names, và identifiers ở dạng gốc.

## Mô hình cốt lõi

Harness work được chia thành:

- Coordinator: điều phối lifecycle của run và dispatch công việc.
- Subagent: thực hiện công việc theo role từ dispatch file.
- Project state: ghi nhận task/run đang active ở cấp project.
- Run state: ghi nhận trạng thái lifecycle của một run.
- Dispatch file: định nghĩa role được đọc gì, được sửa gì, và khi nào hoàn thành.

Vị trí chuẩn:

```txt
.codex/agents/*.toml
.harness/project/state.yaml
.harness/runs/<RUN_ID>/run.yaml
.harness/runs/<RUN_ID>/dispatch/*.dispatch.md
```

## Project State

Trạng thái hiện tại của project nằm tại:

```txt
.harness/project/state.yaml
```

Agent phải đọc project state trước khi bắt đầu hoặc tiếp tục Harness work.

Luôn dùng project state trước. Không scan toàn bộ run directories để tự suy đoán task đang active.

Project state chỉ nên chứa active run pointer, current status, current phase, next role, locks, và blocked runs.

Coordinator sở hữu quyền cập nhật project state.

Subagent có thể đọc project state để validation, nhưng không được cập nhật project state trừ khi dispatch cho phép rõ ràng trong write scope.

## Quy tắc Coordinator

Coordinator chỉ làm nhiệm vụ điều phối.

Coordinator phải:

* đọc project state,
* xác định active run,
* xác định current phase,
* xác định next required role,
* tạo hoặc cập nhật dispatch files,
* spawn required subagent,
* cập nhật project state và run state sau khi role hoàn tất.

Coordinator không được:

* sửa application code,
* tự làm việc của Planner,
* tự làm việc của Contract Reviewer,
* tự làm việc của Generator,
* tự làm việc của Evaluator,
* tự approve output do chính nó tạo,
* bỏ qua required subagent role.

Nếu không thể spawn required subagent, Coordinator phải dừng và báo `BLOCKED`.

## Quy tắc Subagent

Role behavior của subagent được định nghĩa tại:

```txt
.codex/agents/*.toml
```

Subagent phải đọc dispatch file của mình trước.

Subagent chỉ được đọc các file được liệt kê trong dispatch, trừ khi cần validation vì dispatch bị thiếu hoặc không hợp lệ.

Subagent chỉ được ghi các file nằm trong allowed write scope.

Subagent không được full lifecycle discovery mặc định.

Subagent không được scan unrelated Harness runs, obsolete artifacts, project history, hoặc unrelated source files.

Subagent phải dừng và báo `BLOCKED` nếu:

* dispatch file bị thiếu,
* required artifact paths bị thiếu,
* allowed read scope không rõ,
* allowed write scope không rõ,
* project state không cho phép role hiện tại chạy,
* run state không cho phép role hiện tại chạy,
* required input artifacts bị thiếu hoặc không hợp lệ.

## Lifecycle Roles

Minimal Harness lifecycle:

```txt
Planner -> Contract Reviewer -> Generator -> Evaluator
```

Ranh giới role:

* Planner tạo hoặc cập nhật implementation contract.
* Contract Reviewer approve, reject, hoặc block contract.
* Generator chỉ implement approved contract.
* Evaluator verify generated result dựa trên approved contract.

Không role nào được approve chính output của mình.

Không role nào được âm thầm bỏ qua next lifecycle role.

## Dispatch Contract

Mỗi role phải được dispatch thông qua dispatch file.

Dispatch files nằm tại:

```txt
.harness/runs/<RUN_ID>/dispatch/
```

Một dispatch file phải định nghĩa:

* run id,
* role,
* current phase,
* required input artifacts,
* allowed read paths,
* allowed write paths,
* completion criteria,
* blocked conditions.

Subagent phải xem dispatch file là source of truth cho task hiện tại.

Nếu dispatch mâu thuẫn với project state hoặc run state, subagent phải dừng và báo `BLOCKED`.

## Write Scope Rules

Chỉ Generator được sửa application code.

Chỉ Coordinator được sửa Harness state files, trừ khi dispatch cho phép role khác rõ ràng.

Chỉ Planner được sửa contract artifacts.

Chỉ Contract Reviewer được sửa review artifacts.

Chỉ Evaluator được sửa evaluation artifacts.

Không ghi ngoài allowed write scope.

Không opportunistically sửa unrelated files.

## Token Discipline

Đọc tập file nhỏ nhất đủ để hoàn thành nhiệm vụ.

Ưu tiên path/pointer thay vì copy nội dung dài.

Ưu tiên dispatch paths thay vì scan directory.

Không copy toàn bộ artifact content vào response trừ khi bắt buộc.

Không giải thích toàn bộ lifecycle trừ khi được yêu cầu.

Chỉ report status ngắn gọn.

## Output Discipline

Khi kết thúc một role task, chỉ report:

* status: `PASS`, `FAIL`, `BLOCKED`, hoặc `DONE`,
* role,
* files read,
* files changed,
* evidence checked,
* next recommended role,
* blockers, nếu có.

Tránh summary dài, lặp lại context, và giải thích suy đoán.

## Conflict Rule

Khi instruction mâu thuẫn, dùng thứ tự ưu tiên sau:

```txt
User request
> safety and runtime constraints
> dispatch file
> project state
> run state
> this AGENTS.md
> role-specific defaults
```

Nếu conflict ảnh hưởng tới permission, lifecycle order, hoặc write scope, dừng và báo `BLOCKED`.
