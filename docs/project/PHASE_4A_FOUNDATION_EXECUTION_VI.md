# Phase 4A - Foundation Execution Document

## 1. Mục đích

Tài liệu này chuyển các mục W0-W3 trong `PHASE_4_ENHANCEMENT_EXECUTION_PLAN_VI.md` thành phạm vi triển khai có thể thực hiện, kiểm thử và review. Phase 4A chỉ hoàn tất khi có code, focused tests, regression tests và evidence tương ứng.

Phạm vi:

1. W0 - Hoàn tất baseline và xác nhận public API compatibility.
2. W1 - Implement configuration tập trung bằng `pydantic-settings`.
3. W2 - Tách domain ownership và chuẩn hóa `TableSpec`.
4. W3 - Tạo shared result, staging, audit, retry và checkpoint models/services.
5. Chạy unit tests foundation độc lập với database.

Ngoài phạm vi Phase 4A: triển khai Bronze/Silver/Gold reliability đầy đủ, orchestration end-to-end và CI production.

## 2. Baseline và nguyên tắc

### 2.1. Baseline Git

| Hạng mục | Giá trị hiện tại |
|---|---|
| Branch triển khai | `Phase4_A_EnhanceFoundation` |
| Commit baseline | `fc699b3` |
| Main đã merge trước Phase 4A | `7de3bf9` |
| Runtime hiện tại | `App.run()` health check, bootstrap placeholder và Bronze |
| Test policy | Unit test không phụ thuộc service ngoài; integration test phải được đánh dấu |

Baseline phải được cập nhật lại trong evidence khi bắt đầu implementation nếu branch hoặc commit thay đổi.

### 2.2. Nguyên tắc bắt buộc

- Không thêm logic mới vào compatibility wrapper.
- Không để connector hoặc business job tự đọc `os.getenv()`.
- Không log password, token hoặc full raw payload.
- Shared layer chỉ sở hữu mechanics dùng chung, không chứa business rule của domain.
- Retry chỉ áp dụng cho transient error và phải giữ nguyên logical identity.
- Validation failure phải ngăn publish downstream.
- Mỗi task phải có focused test trước khi chuyển sang `Done`.

## 3. Dependency và thứ tự thực hiện

```text
W0 baseline/API
    -> W1 Settings
        -> W2 domain ownership/TableSpec
            -> W3 shared models/services
                -> foundation unit tests
```

Không bắt đầu W2 nếu public API cần giữ chưa được inventory. Không bắt đầu W3 nếu Settings contract và domain ownership chưa được thống nhất.

## 4. W0 - Baseline và API compatibility

### Mục tiêu

Xác nhận behavior hiện tại, các entrypoint/import public và các ràng buộc cần bảo vệ trước khi refactor.

### Tasks

| ID | Việc thực hiện | Output | Acceptance criteria | Status |
|---|---|---|---|---|
| 0.1 | Chụp branch, commit và test baseline | Baseline report | Có command, kết quả và môi trường thực thi | Done |
| 0.2 | Inventory entrypoint | Danh sách `main.py`, `App`, CLI/job entrypoint | Xác định caller chính và exit behavior | Done |
| 0.3 | Inventory import public | Compatibility matrix | Import cũ được kiểm tra bằng test hoặc evidence | Done |
| 0.4 | Inventory table/domain | Ownership matrix | Ownership hiện tại và gap mục tiêu được ghi rõ cho W2 | Done |
| 0.5 | Ghi nhận behavior hiện tại | Regression notes | Không refactor dựa trên giả định chưa kiểm chứng | Done |

### Compatibility matrix tối thiểu

| API/entrypoint | Caller hiện tại | API cần giữ | Cách kiểm chứng |
|---|---|---|---|
| `src.app.app.App` | `main.py`/test | Constructor và `run()` | Import test + smoke test |
| Legacy Bronze job import | Existing tests/callers | Tên class, constructor, `run()` | Compatibility test |
| Connector public classes | App/services | Constructor và connect contract | Import/signature test |
| Silver/Gold callable surface | Pipeline/tests | Signature hiện tại trong migration | Contract test |

### Kết quả thực thi W0

| Hạng mục | Evidence |
|---|---|
| Git baseline | Branch `Phase4_A_EnhanceFoundation`, HEAD `fc699b3`, worktree có 2 tài liệu Phase 4A chưa commit tại thời điểm kiểm tra |
| Test baseline | `31 passed, 3 failed`; 3 failure do PostgreSQL `localhost:5432` không chạy |
| Entrypoint | `main.py` gọi `App().run()`; `App` điều phối health check, bootstrap placeholder và Bronze |
| Public API | `App`, `PlatformBootstrapJob`, `ConnectionHealthService`, `SalesBronzeIngestionJob`, `SalesExtractor`, `BronzeLoader`, `BronzeValidator`, `SQLServerConnector`, `PostgreSQLConnector` |
| Compatibility test | `tests/test_phase4a_w0_contract.py`: 3 passed |
| Ownership gap | `SalesBronzeIngestionJob` hiện load 5 Sales tables cùng `Production.Product` và `Person.Person`; việc tách thuộc W2 |

W0 đã hoàn tất việc baseline, inventory và xác nhận compatibility surface. Ownership target chưa được đánh dấu hoàn tất; gap hiện trạng được chuyển làm input bắt buộc cho W2.
### Definition of Done W0

- [x] Baseline command và kết quả được ghi lại.
- [x] Public imports và entrypoints có owner.
- [x] Compatibility tests được tạo cho API có caller thực tế.
- [x] Domain/table inventory và gap ownership được ghi nhận trước W2.

## 5. W1 - Centralized configuration

### Mục tiêu

Tạo một `Settings` object typed, validated và injectable; process environment phải override `.env`.

### Implementation scope

| ID | Implementation | Acceptance criteria | Test evidence | Status |
|---|---|---|---|---|
| 1.1 | Thêm `pydantic-settings` vào `requirements.txt` | Import được trong environment | Dependency/import test | Done |
| 1.2 | Tạo `src/core/settings.py` | Có `BaseSettings`, `SettingsConfigDict`, `SecretStr`, cached `get_settings()` | Settings construction test | Done |
| 1.3 | Định nghĩa connection fields | SQL Server/PostgreSQL host, port, database, driver và auth mode được parse đúng | Field parsing test | Done |
| 1.4 | Định nghĩa runtime fields | `batch_size > 0`, retry attempts trong `1..10`, delay hợp lệ | Invalid value test | Done |
| 1.5 | Validate authentication | `windows` không yêu cầu credential; `sql` bắt buộc username/password | Auth matrix test | Done |
| 1.6 | Redact secrets | Password dùng `SecretStr`, safe summary không chứa secret | Redaction test | Done |
| 1.7 | Inject Settings | App, connectors, services và jobs dùng cùng instance | Constructor/usage test | Done |
| 1.8 | Đồng bộ `.env.example` | Template khớp schema, không có secret thật | Template consistency test | Done |

### Settings contract

Các field tối thiểu:

```text
environment: development | test | staging | production
debug: bool
log_level: str
sql_server_host: str
sql_server_port: int
sql_server_database: str
sql_server_driver: str
sql_server_auth_mode: windows | sql
sql_server_username: str | None
sql_server_password: SecretStr | None
postgres_host: str
postgres_port: int
postgres_database: str
postgres_username: str
postgres_password: SecretStr
batch_size: int > 0
retry_max_attempts: int 1..10
retry_initial_delay_seconds: float > 0
retry_max_delay_seconds: float > 0
```

Rules:

- Process environment có precedence cao hơn `.env`.
- Thiếu hoặc sai configuration phải fail trước health check.
- Không dùng default credential ngoài development/test theo policy được phê duyệt.
- Safe summary chỉ được chứa host, port, database, auth mode, batch size và retry limits.

### Definition of Done W1

- [x] Có một Settings boundary duy nhất.
- [x] Connector canonical không còn tự đọc environment.
- [x] Auth validation và type validation có unit test.
- [x] Password không xuất hiện trong `repr`, log, exception report hoặc summary.
- [x] App và dependency nhận Settings qua injection.

## 6. W2 - Domain ownership và TableSpec

### Mục tiêu

Tách business ownership khỏi infrastructure mechanics và loại bỏ table mapping hard-code trong `run()`.

### Ownership contract

| Domain | Tables | Owner |
|---|---|---|
| Sales | `SalesOrderHeader`, `SalesOrderDetail`, `Customer`, `SalesTerritory`, `SalesPerson` | `SalesBronzeJob` |
| Production | `Product` | `ProductionBronzeJob` |
| Person | `Person` | `PersonBronzeJob` |

Tên schema/table thực tế phải được đối chiếu với source inventory trước khi implement.

### Implementation scope

| ID | Implementation | Acceptance criteria | Test evidence | Status |
|---|---|---|---|---|
| 2.1 | Tạo immutable `TableSpec` | Có source/target, primary key, required columns, ordering key, incremental column | Spec validation test | Done |
| 2.2 | Tạo Sales specs/job | Sales job chỉ xử lý 5 Sales tables | Ownership test | Done |
| 2.3 | Tạo Production job | Product có result độc lập | Domain result test | Done |
| 2.4 | Tạo Person job | Person có result độc lập | Domain result test | Done |
| 2.5 | Tách shared mechanics | Job cung cấp specs/policy; runner xử lý mechanics | Architecture/import test | Done |
| 2.6 | Giữ compatibility wrapper | Wrapper delegate, không có business logic mới | Legacy regression test | Done |
| 2.7 | Xác nhận domain isolation | Một domain fail không làm mất result domain khác | Failure isolation test | Done |

### TableSpec contract

`TableSpec` nên là immutable dataclass hoặc model tương đương, gồm tối thiểu:

```text
source_schema
source_table
target_schema
target_table
primary_key
required_columns
ordering_key
incremental_column
```

Validation bắt buộc:

- Identifier không rỗng và được kiểm tra trước khi dùng trong SQL.
- Primary key phải thuộc hoặc được giải thích so với required columns.
- Ordering key phải ổn định cho batch/incremental read.
- Không đưa retry, staging hoặc database connection vào `TableSpec`.

### Definition of Done W2

- [x] Product và Person không còn nằm trong Sales job canonical.
- [x] Table mapping nằm trong specs, không nằm rải rác trong `run()`.
- [x] Shared runner không chứa business rule riêng.
- [x] Compatibility wrapper chỉ delegate.
- [x] Domain ownership và isolation có test.

### Kết quả thực thi W2

| Hạng mục | Evidence | Status |
|---|---|---|
| `TableSpec` | `src/shared/ingestion/ingestion_models.py`, immutable metadata với identifier validation và qualified names | Done |
| Sales ownership | `SalesBronzeJob` chỉ khai báo 5 Sales specs | Done |
| Production ownership | `ProductionBronzeJob` khai báo riêng `Production.Product` | Done |
| Person ownership | `PersonBronzeJob` khai báo riêng `Person.Person` | Done |
| Shared mechanics | `DomainBronzeJob` dùng chung extract/load/validate mechanics | Done |
| Compatibility | `SalesBronzeIngestionJob` delegate sang `SalesBronzeJob`, giữ signature cũ | Done |
| Focused tests | W0/W2 ownership/spec và Bronze regression -> `11 passed` | Done |
| Full regression | `python -m pytest -q` -> `48 passed` | Done |

## 7. W3 - Shared foundation models và services

### Mục tiêu

Chuẩn hóa contract dùng chung cho Bronze, Silver và Gold trước khi implement reliability của từng stage.

### Package shape đề xuất

```text
src/shared/ingestion/
├── ingestion_models.py
├── batch_ingestion_engine.py
├── retry_policy.py
├── checkpoint_manager.py
├── staging_manager.py
└── audit_service.py
```

Tên module có thể điều chỉnh theo structure thực tế, nhưng ownership của các contract phải giữ nguyên.

### Result contract

Mọi stage/table/batch phải có result tối thiểu:

```python
{
    "run_id": "...",
    "stage": "bronze",
    "source_table": "Sales.SalesOrderDetail",
    "target_table": "bronze.sales_order_detail",
    "status": "SUCCESS",
    "rows_read": 0,
    "rows_written": 0,
    "rows_rejected": 0,
    "attempt_count": 1,
    "started_at": "...",
    "finished_at": "...",
    "error_type": None,
    "error_message": None,
}
```

Status vocabulary tối thiểu: `SUCCESS`, `SUCCESS_WITH_REJECTIONS`, `PARTIAL_SUCCESS`, `FAILED`, `RETRYING`, `QUARANTINED`.

### Implementation scope

| ID | Implementation | Acceptance criteria | Test evidence | Status |
|---|---|---|---|---|
| 3.1 | Tạo status/result models | Bronze/Silver/Gold dùng cùng vocabulary và fields | Model serialization test | Done |
| 3.2 | Tạo run/load/batch identity | Retry giữ nguyên logical IDs | Identity test | Done |
| 3.3 | Tạo audit models/service contract | Có run/table/batch, counts, attempts, timestamps và errors | Audit contract test | Done |
| 3.4 | Tạo `StagingManager` contract | Identifier được validate; published table chưa bị chạm trước publish | Staging safety test | Done |
| 3.5 | Tạo error classifier | Phân biệt transient và deterministic | Classifier matrix test | Done |
| 3.6 | Tạo retry policy/executor contract | Tối đa 3 attempts, backoff+jitter, injectable clock/sleeper | Retry behavior test | Done |
| 3.7 | Tạo checkpoint contract | Checkpoint chỉ advance sau successful commit | Checkpoint ordering test | Done |
| 3.8 | Tạo fake fixtures | Foundation tests không cần live database | Fixture smoke test | Done |

### Invariants cần bảo vệ

- `run_id`, `load_id` và `batch_id` là logical identity; `attempt_count` không tạo identity mới.
- Checkpoint không được ghi trước data commit.
- Chỉ transient error được retry.
- Hết retry phải trả `FAILED`, không nuốt exception và không publish.
- Staging identifier phải được validate, không nối chuỗi input tùy ý vào SQL.
- Audit phải giữ được outcome cuối cùng và thông tin các attempts.
- Shared models không biết Sales/Production/Person business rules.

### Definition of Done W3

- [x] Result contract được dùng nhất quán trong foundation.
- [x] Retry, staging, audit và checkpoint có boundary rõ.
- [x] Identity/retry/commit ordering có test độc lập.
- [x] Error classification có matrix cho transient/deterministic cases.
- [x] Không cần database thật để chạy foundation unit tests.

### Kết quả thực thi W3

| Hạng mục | Evidence | Status |
|---|---|---|
| Models/contracts | `ingestion_models.py`: status, execution identity, result và audit records | Done |
| Retry | `retry_policy.py`: classifier, exponential backoff+jitter, max attempts và injectable sleeper | Done |
| Staging | `staging_manager.py`: identifier validation, validation gate, publish preservation và cleanup | Done |
| Checkpoint | `checkpoint_manager.py`: không advance trước commit | Done |
| Audit | `audit_service.py`: run/table/batch history in-memory, không chứa secret | Done |
| Focused tests | W3 foundation tests -> `10 passed` | Done |
| Full regression | `python -m pytest -q` -> `58 passed` | Done |

## 8. Foundation unit tests

### Test layout đề xuất

```text
tests/
├── test_settings.py
├── test_domain_ownership.py
├── test_table_spec.py
├── test_ingestion_models.py
├── test_retry_policy.py
├── test_staging_manager.py
├── test_checkpoint_manager.py
└── test_audit_service.py
```

Có thể gộp file khi phù hợp với structure hiện tại, nhưng mỗi contract phải có test dễ định vị.

### Scenarios bắt buộc

| Nhóm | Scenarios |
|---|---|
| Settings | `.env`, environment override, invalid type, auth windows/sql, secret redaction |
| Compatibility | Legacy import, constructor/signature, wrapper delegation |
| Ownership | Table thuộc đúng domain; Sales không chứa Product/Person |
| TableSpec | Required fields, invalid identifiers, stable ordering key, immutability |
| Result | Status/count serialization, success/failure/error fields |
| Retry | Transient retry, deterministic no-retry, max attempts, backoff injection |
| Identity | Retry giữ cùng run/load/batch IDs |
| Staging | Safe identifier, cleanup, publish guard |
| Checkpoint | Không advance trước commit; advance sau commit |
| Audit | Ghi attempt và final outcome, không ghi secret |

### Commands và evidence

Từ thư mục repository:

```powershell
python -m pytest -m "not integration" -q
python -m pytest tests/test_settings.py tests/test_table_spec.py tests/test_ingestion_models.py -q
```

Nếu test file chưa tồn tại, phải tạo test trước khi cập nhật status. Kết quả cần lưu trong PR/commit notes hoặc evidence document gồm command, số test pass/fail và nguyên nhân của test bị block bởi môi trường.

## 9. Gate chuyển task

| Gate | Điều kiện |
|---|---|
| G0 -> W1 | Baseline và compatibility inventory hoàn tất |
| W1 -> W2 | Settings tests pass; injection boundary được xác nhận |
| W2 -> W3 | Ownership/TableSpec tests pass; wrapper regression pass |
| W3 -> Test completion | Models/services contract pass; fake fixtures chạy không cần database |
| Phase 4A complete | Focused tests và `pytest -m "not integration"` pass; evidence được cập nhật |

## 10. Evidence log

Cập nhật bảng này sau mỗi task hoàn thành. Không chuyển `Status` sang `Done` nếu thiếu file/symbol, command và kết quả kiểm chứng.

| Date | Task | Files/symbols | Validation command | Result | Status |
|---|---|---|---|---|---|
| 2026-09-04 | Tạo execution document | `docs/project/PHASE_4A_FOUNDATION_EXECUTION_VI.md` | Markdown review | Created | Done |
| 2026-09-04 | Execute W0 baseline/API compatibility | `tests/test_phase4a_w0_contract.py`, `main.py`, `src/app/app.py`, Sales Bronze job | `python -m pytest tests/test_phase4a_w0_contract.py -q` | 3 passed; baseline suite 31 passed, 3 blocked by PostgreSQL unavailable | Done |
| 2026-09-04 | Execute W1 centralized configuration | `src/core/settings.py`, connectors, App, `.env.example`, `tests/test_settings.py` | `python -m pytest tests/test_settings.py -q` | 7 passed | Done |
| 2026-09-04 | Execute W2 domain ownership and TableSpec | Domain jobs, shared runner, `tests/test_phase4a_w2_domain_ownership.py` | `python -m pytest tests/test_phase4a_w2_domain_ownership.py -q` | 4 passed | Done |
| 2026-09-04 | Execute W3 foundation models/services | Shared ingestion models/services and W3 tests | `python -m pytest tests/test_ingestion_models.py tests/test_retry_policy.py tests/test_staging_manager.py tests/test_checkpoint_manager.py tests/test_audit_service.py -q` | 10 passed | Done |
| 2026-09-04 | Run Phase 4A foundation suite | W0-W3 foundation tests | `python -m pytest tests/test_settings.py tests/test_phase4a_w0_contract.py tests/test_phase4a_w2_domain_ownership.py tests/test_ingestion_models.py tests/test_retry_policy.py tests/test_staging_manager.py tests/test_checkpoint_manager.py tests/test_audit_service.py -q` | 24 passed | Done |
| 2026-09-04 | Run full regression suite | All repository tests | `python -m pytest -q` | 58 passed | Done |

## 11. Definition of Done Phase 4A

- [x] W0 baseline và public API compatibility có evidence.
- [x] W1 centralized `Settings` hoạt động và được inject.
- [x] W2 domain ownership và immutable `TableSpec` được kiểm thử.
- [x] W3 result/staging/audit/retry/checkpoint contracts được kiểm thử.
- [x] Retry không tạo logical identity mới và checkpoint không advance trước commit.
- [x] Secrets không xuất hiện trong log hoặc evidence.
- [x] Foundation unit tests chạy độc lập với database.
- [x] Regression suite phù hợp pass.
- [x] Checklist và README được cập nhật theo runtime thực tế.

## 12. Tài liệu liên quan

## W1 Execution Evidence

- Standard environment: repository-local `.venv` using Python 3.11 64-bit at `A:\Workspace\DataEngineer\AdventureWorks Analytics Platform\.venv\Scripts\python.exe`. All project commands must use this interpreter; do not use the old shared `python\.venv` environment.
- Installation record: `python -m pip install -r requirements.txt` completed successfully in the standard environment.
- Environment check: runtime imports for `pandas`, `psycopg2`, `pyodbc`, `sqlalchemy`, and `pydantic_settings` are available.
- Dependency: added `pydantic-settings==2.4.0` to `requirements.txt` and installed it in the Pylance-selected venv.
- Implementation: added `src/core/settings.py` with typed settings, `.env` loading, environment override, auth/runtime validation, `SecretStr`, and `safe_summary()`.
- Injection: passed Settings through App, health service, Bronze job, extractor, loader, and database connectors.
- Focused validation: `tests/test_settings.py` and `tests/test_phase4a_w0_contract.py` -> `10 passed`; `tests/test_phase0_connectivity.py` -> `5 passed`.
- Connector injection is now validated in the standard environment.
- Full regression: `python -m pytest -q` -> `44 passed`.

- `docs/internal/PHASE_4_ENHANCEMENT_EXECUTION_PLAN_VI.md`
- `docs/internal/PHASE_4_REVIEW_ENHANCE_CODE_VI.md`
- `docs/project/WORKING_STANDARDS.md`
- `tests/test_architecture_contract.py`
- `pytest.ini`
