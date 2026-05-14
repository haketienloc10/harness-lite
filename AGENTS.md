# AGENTS.md

Repository này đã cài **Harness** để điều phối AI-assisted development bằng artifacts lifecycle state.

Các tệp trong thư mục `.harness/**/template/` chỉ là ví dụ và không được coi là các thành phần dự án đang hoạt động.

## Language Rule

Reply theo ngôn ngữ người dùng; giữ code, command, path, API name, logs, schema keys, package names, và identifiers ở dạng gốc.

## Quy tắc bắt buộc dùng Harness

Repository này dùng Harness cho mọi công việc triển khai.

Với mọi yêu cầu của user có thể dẫn tới sửa code, sửa test, thay đổi behavior, refactor, sửa generated artifact, hoặc sửa project artifact, agent bắt buộc phải dùng Harness workflow.

Workflow bắt buộc là:

```txt
Planner -> Contract Reviewer -> Generator -> Evaluator
```
Main agent là Coordinator.

Ranh giới role:

* Planner tạo hoặc cập nhật implementation contract.
* Contract Reviewer approve, reject, hoặc block contract.
* Generator chỉ implement approved contract.
* Evaluator verify generated result dựa trên approved contract.

Không role nào được approve chính output của mình.

Không role nào được âm thầm bỏ qua next lifecycle role.

## Quy tắc Coordinator

Coordinator chỉ làm nhiệm vụ điều phối.

Coordinator phải:

* xác định run hiện tại từ user request, context hiện tại, hoặc run mới vừa tạo,
* đọc run state tại `.harness/runs/{RUN-YYYYMMDD-NNN-task-slug}/run.yaml`,
* xác định current phase,
* xác định next required role,
* nếu user request dài, nhiều ý, mơ hồ, mâu thuẫn, hoặc có khả năng cần tách task, phải xác nhận các ý chính với user trước khi tạo Harness run,
* không tạo run từ một long request chưa rõ scope,
* sau khi user xác nhận, tạo request snapshot chứa full confirmed request,
* tạo request brief trung lập, ngắn gọn, chỉ gồm goal, explicit requirements, explicit constraints, explicit non-goals, ambiguity còn lại, và path tới full request snapshot,
* tạo dispatch file cho required role tiếp theo khi bắt đầu role mới hoặc chuyển phase,
* spawn required subagent,
* đọc final report ngắn gọn của subagent sau khi role hoàn tất,
* không đọc full role artifacts chỉ để xác nhận completion nếu final report đã đủ hợp lệ,
* cập nhật run state sau khi role hoàn tất, chỉ dựa trên status, artifact paths, evidence summary, blockers, và next lifecycle transition do role báo cáo.

Coordinator không được:

* sửa application code,
* tự làm việc của Planner,
* tự làm việc của Contract Reviewer,
* tự làm việc của Generator,
* tự làm việc của Evaluator,
* tự viết implementation contract thay Planner,
* tự viết review verdict thay Contract Reviewer,
* tự viết implementation output thay Generator,
* tự viết evaluation result thay Evaluator,
* tạo request brief chứa implementation plan, review verdict, evaluation result, hoặc suy luận chuyên môn thay cho Planner,
* duplicate nội dung request dài vào dispatch file,
* tự approve output do chính nó tạo,
* sửa dispatch đang được subagent thực thi, trừ khi dispatch sai, thiếu, hoặc không hợp lệ và cần dừng với `BLOCKED`,
* bỏ qua required subagent role.

Nếu không thể spawn required subagent, Coordinator phải dừng và báo `BLOCKED`.

## Quy tắc Subagent

Role behavior chi tiết của subagent được định nghĩa tại:

```txt
.codex/agents/*.toml
```

Subagent phải đọc dispatch file của mình trước và xem dispatch là source of truth cho role hiện tại.

Subagent chỉ được đọc các file được liệt kê trong dispatch và chỉ được ghi các file nằm trong allowed write scope.

Subagent không được full lifecycle discovery mặc định, không scan unrelated Harness runs, obsolete artifacts, project history, hoặc unrelated source files.

Nếu dispatch, required inputs, allowed read scope, allowed write scope, hoặc run state bị thiếu, mâu thuẫn, hoặc không hợp lệ, subagent phải dừng và báo `BLOCKED`.

## Dispatch Contract

Mỗi role phải được dispatch thông qua dispatch file.

Dispatch files nằm tại:

```txt
.harness/runs/{RUN-YYYYMMDD-NNN-task-slug}/dispatch/
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

Dispatch phải liệt kê run state trong allowed read paths nếu role cần validation state.

Với long request, dispatch chỉ trỏ tới request brief và request snapshot; không duplicate full request content.

Nếu một edit target không nằm trong `allowed_write_paths`, không sửa file đó dù workspace sandbox cho phép.

Subagent phải xem dispatch file là source of truth cho task hiện tại.

Nếu dispatch mâu thuẫn với run state, subagent phải dừng và báo `BLOCKED`.

## Write Scope Rules

Chỉ Coordinator được sửa run state và dispatch files.

Chỉ Planner được sửa planner brief, implementation contract, và decision artifacts khi dispatch cho phép durable decision creation hoặc revision.

Chỉ Contract Reviewer được sửa review artifacts. Contract Reviewer có thể approve, reject, hoặc yêu cầu sửa decision artifacts thông qua review artifacts.

Chỉ Generator được sửa application code changes trong allowed write scope.

Chỉ Evaluator được sửa evaluation artifacts và test-matrix artifacts.

Planner có thể định nghĩa acceptance criteria và verification expectations trong implementation contract, nhưng không sửa test-matrix files trừ khi dispatch cho phép rõ ràng.

Generator không được sửa decisions hoặc test-matrix artifacts.

Evaluator không được sửa decisions, trừ khi dispatch cho phép rõ ràng để ghi evidence-backed invalidation proposal.

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
* decision: role-specific value như `planned`, `approved`, `rejected_requires_revision`, `implemented`, `pass`, `fail`, hoặc blocker cụ thể,
* role,
* files read,
* files changed,
* evidence checked,
* next recommended role,
* blockers, nếu có.

Tránh summary dài, lặp lại context, và giải thích suy đoán.

Coordinator nên dùng final report của subagent để advance state. Coordinator không đọc full role artifacts trừ khi final report bị thiếu, không hợp lệ, blocked, failed, hoặc mâu thuẫn với lifecycle/state/dispatch.

## Role Result Contract

| role | status | decision |
|---|---|---|
| harness_planner | DONE, BLOCKED | planned, blocked |
| harness_contract_reviewer | PASS, FAIL, BLOCKED | approved, rejected_requires_revision, blocked |
| harness_generator | DONE, BLOCKED | implemented, blocked |
| harness_evaluator | PASS, FAIL, BLOCKED | pass, fail, blocked_insufficient_evidence |

## Conflict Rule

Khi instruction mâu thuẫn, dùng thứ tự ưu tiên sau:

```txt
safety and runtime constraints
> User request
> dispatch file
> run state
> this AGENTS.md
> role-specific defaults
```

Nếu conflict ảnh hưởng tới permission, lifecycle order, hoặc write scope, dừng và báo `BLOCKED`.

## Run Layout

Run directory chuẩn:

```txt
.harness/runs/{RUN-YYYYMMDD-NNN-task-slug}/
  run.yaml
  00-request-snapshot.md
  00-request-brief.md
  01-planner-brief.md
  02-implementation-contract.md
  03-contract-review.md
  04-implementation-report.md
  05-evaluator-report.md
  dispatch/
    harness-planner.dispatch.md
    harness-contract-reviewer.dispatch.md
    harness-generator.dispatch.md
    harness-evaluator.dispatch.md
```

Template tham khảo nằm tại:

```txt
.harness/runs/template/run.yaml
.harness/runs/template/dispatch/role.dispatch.template.md
```

Files under `.harness/**/template/` are examples only and must not be treated as active project artifacts.