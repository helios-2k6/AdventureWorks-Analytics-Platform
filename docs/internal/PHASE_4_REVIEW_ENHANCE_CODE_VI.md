# Phase 4 - Review và Enhance Code

## Bối cảnh Phase

| Hạng mục | Giá trị |
|---|---|
| Branch hiện tại | `Enhance_Project` |
| HEAD hiện tại | `f6a681a` - Fix Phase 3 runtime and document current workflow |
| Trạng thái branch | `Enhance_Project`, `main` và `origin/main` cùng trỏ đến một commit |
| Trạng thái worktree | Sạch tại thời điểm review |
| Baseline test hiện tại | `31 passed, 3 failed` |
| Nguyên nhân test fail | PostgreSQL không chạy tại `localhost:5432`; Docker daemon chưa khởi động |
| Kiến trúc hiện tại | Bronze được gọi từ `App`; Silver và Gold là các module độc lập |
| Mục tiêu Phase | Làm pipeline Sales đáng tin cậy, dễ quan sát, dễ test và chạy được như một workflow thống nhất |
| Owner | AI / User |
| Ngày review | 2026-09-03 |

## Quy ước trạng thái

- `Not started`: Chưa bắt đầu.
- `In progress`: Đang thực hiện.
- `Done`: Đã triển khai và có bằng chứng nghiệm thu.
- `Blocked`: Bị chặn bởi dependency hoặc môi trường.
- `Needs clarification`: Cần xác nhận thêm về phạm vi hoặc tiêu chí nghiệm thu.

## Đánh giá code hiện tại

| Khu vực | Hiện trạng | Tác động hiện tại | Mục tiêu sau enhance |
|---|---|---|---|
| Application orchestration | `App.run()` chỉ chạy health check, bootstrap placeholder và Bronze | Runtime chưa có một command điều khiển toàn bộ Bronze -> Silver -> Gold | Có một pipeline runner với stage, status, chính sách lỗi và kết quả rõ ràng |
| Bootstrap | `PlatformBootstrapJob.run()` chỉ trả về response thành công giả lập | Code ứng dụng chưa bảo đảm schema và metadata đã sẵn sàng | Bootstrap idempotent và kiểm tra version schema |
| Bronze ingestion | Job class load 7 bảng nguồn và kiểm tra row-count parity | Thiếu retry, audit, xử lý lỗi theo bảng và bảo vệ incremental rerun | Có report từng bảng, retry, audit và idempotency |
| Silver transformation | Script độc lập clean và ghi 6 bảng Silver | Không thể được `App` điều khiển hoặc báo cáo thống nhất | Có job/service có thể tái sử dụng và inject dependency |
| Gold loading | Script drop/recreate Gold rồi mới thêm constraints | Lỗi giữa chừng có thể khiến Gold không hoàn chỉnh hoặc không khả dụng | Dùng staging/publish để load an toàn và có thể phục hồi |
| Validation | Silver và Gold validation chạy bằng script riêng | Validation chưa được dùng như cổng chặn pipeline | Validation là stage bắt buộc trước khi publish |
| Configuration | Mỗi connector tự đọc environment variables | Cấu hình bị phân tán và khó kiểm tra thống nhất | Có settings typed dùng chung và validate lúc khởi động |
| Testing | Có unit test; database test chạy mặc định | Chạy test local sẽ fail nếu service ngoài chưa sẵn sàng | Tách unit/integration test, fixture và chính sách CI rõ ràng |
| Observability | Có logging và result dictionary nhưng còn hạn chế | Khó điều tra lỗi theo table hoặc theo run | Có structured log, run ID, metric và audit |
| Documentation | Workflow hiện tại đã được ghi nhận nhưng chưa có tracker Phase 4 | Công việc enhance chưa có cơ chế quản lý và nghiệm thu | Có checklist Phase 4 và evidence triển khai |

## Kết quả review kỹ thuật cần trao đổi

### Configuration và biến môi trường

| Phát hiện | Hành vi hiện tại | Rủi ro | Hướng đề xuất |
|---|---|---|---|
| Load `.env` chưa thống nhất | Có `.env.example`, nhưng runtime chính và shared connector chưa gọi `load_dotenv()` tập trung; chỉ một số script/test có gọi | Hành vi giữa `main.py`, script, test và shell session có thể khác nhau | Load configuration một lần khi application khởi động thông qua typed settings tập trung |
| Có credential mặc định | PostgreSQL connector mặc định `postgres/postgres`; Docker Compose cũng có default local | Thiếu cấu hình có thể bị che giấu; default không an toàn nếu chạy ngoài development | Chỉ cho phép default trong development; môi trường khác phải khai báo rõ; không log password |
| Configuration bị phân tán | Connector tự đọc environment variables riêng | Host, port, database, authentication, batch size và retry có thể không đồng nhất | Truyền một settings object đã validate vào connector, service và job |
| Startup validation chưa đủ | Thiếu host, driver hoặc credential chưa được báo thành một lỗi configuration rõ ràng | Lỗi chỉ xuất hiện muộn ở connection/query | Validate cấu hình trước health check và pipeline execution |

Luồng configuration đề xuất:

```text
.env / process environment
  -> Settings loader
	  -> validation
		  -> App / PipelineRunner
			  -> connectors, jobs và validators
```

#### Phương án đã chốt: dùng `pydantic-settings`

Project sẽ dùng `pydantic-settings` làm cơ chế configuration duy nhất cho Python application. Bổ sung dependency vào `requirements.txt`:

```text
pydantic-settings
```

Tạo `src/core/settings.py` với một settings object được cache:

```python
from functools import lru_cache

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=False,
		extra="ignore",
	)

	environment: str = "development"
	debug: bool = False
	log_level: str = "INFO"

	sql_server_host: str
	sql_server_port: int = 1433
	sql_server_database: str = "AdventureWorks2012"
	sql_server_driver: str = "ODBC Driver 17 for SQL Server"
	sql_server_auth_mode: str = "windows"
	sql_server_username: str | None = None
	sql_server_password: SecretStr | None = None

	postgres_host: str = "localhost"
	postgres_port: int = 5432
	postgres_database: str = "adventureworks_warehouse"
	postgres_username: str
	postgres_password: SecretStr

	batch_size: int = Field(default=10000, gt=0)
	retry_max_attempts: int = Field(default=3, ge=1, le=10)
	retry_initial_delay_seconds: float = Field(default=1.0, gt=0)
	retry_max_delay_seconds: float = Field(default=30.0, gt=0)

	@model_validator(mode="after")
	def validate_authentication(self):
		if self.sql_server_auth_mode == "sql":
			if not self.sql_server_username or not self.sql_server_password:
				raise ValueError(
					"SQL Server username and password are required "
					"when sql_server_auth_mode=sql"
				)

		if self.environment != "development":
			if self.postgres_password.get_secret_value() == "postgres":
				raise ValueError(
					"Default PostgreSQL password is not allowed outside development"
				)

		return self


@lru_cache
def get_settings() -> Settings:
	return Settings()
```

Quy tắc configuration:

| Quy tắc | Quyết định |
|---|---|
| Thứ tự ưu tiên | Process environment variables override `.env`; `.env` chỉ override safe application defaults |
| Load `.env` | `SettingsConfigDict(env_file=".env")` load file local khi tạo `Settings`; không connector nào tự load `.env` riêng |
| Giá trị bắt buộc | `SQL_SERVER_HOST`, `POSTGRES_USERNAME` và `POSTGRES_PASSWORD` là bắt buộc, trừ khi có policy local-only được document rõ |
| SQL Server Windows Authentication | `SQL_SERVER_AUTH_MODE=windows`; username/password có thể rỗng và không được sử dụng |
| SQL Server SQL Authentication | `SQL_SERVER_AUTH_MODE=sql`; username/password là bắt buộc |
| Xử lý secret | Field password dùng `SecretStr`; password không được log hoặc đưa vào report |
| Credential mặc định | `postgres/postgres` chỉ được phép ở local development; staging/production phải cung cấp credential rõ ràng |
| Vòng đời Settings | `get_settings()` được cache; cùng một `Settings` instance được inject vào App, service, connector và job |
| Biến không liên quan | `extra="ignore"` ngăn environment variable ngoài phạm vi làm startup fail; các giá trị bắt buộc vẫn được validate |

Application boundary phải tạo settings trước health check:

```text
main.py
  -> settings = get_settings()
	  -> App(settings=settings)
		  -> health service / connectors / jobs
```

Connector phải nhận settings object thay vì tự gọi `os.getenv()`:

```python
class PostgreSQLConnector(BaseConnector):
	def __init__(self, settings: Settings):
		super().__init__()
		self.settings = settings

	def connect(self) -> bool:
		password = self.settings.postgres_password.get_secret_value()
		# Dùng settings.postgres_host, postgres_port, database và username ở đây.
```

Trong giai đoạn migration để giữ backward compatibility, constructor có thể tạm dùng `settings: Settings | None = None` và resolve `get_settings()` bên trong. Code application mới phải inject object tường minh. Các `os.getenv()` độc lập trong connector/job cũ cần được loại bỏ sau khi migration hoàn tất.

File `.env.example` phải document các tên biến đã chọn, bao gồm `SQL_SERVER_AUTH_MODE`, `BATCH_SIZE` và các retry setting. File `.env` thật chỉ dùng local và tiếp tục được bảo vệ bởi `.gitignore`.

Test configuration bắt buộc:

| Test | Kết quả mong đợi |
|---|---|
| `.env` hợp lệ | `Settings` load thành công với giá trị đúng kiểu |
| Process variable override `.env` | Giá trị từ process được ưu tiên |
| Thiếu PostgreSQL setting bắt buộc | `ValidationError` xảy ra trước health check |
| Windows SQL Server authentication | Không bắt buộc username/password |
| SQL Server SQL authentication thiếu credential | Validation fail với thông báo rõ |
| Default PostgreSQL password ngoài development | Validation fail |
| Batch/retry value không hợp lệ | Validation fail trước pipeline execution |
| Secret logging | Password không xuất hiện trong log hoặc rendered report |

### Đánh giá Bronze về read, batch và streaming
Cần quyết định rõ batch size, phạm vi commit, phạm vi retry, thứ tự đọc và chiến lược resume. Chỉ dùng `drop_duplicates()` theo từng batch là không an toàn nếu cùng business key có thể nằm ở các batch khác nhau.

#### Baseline Bronze đã chốt để implementation

Các quyết định sau đã được phê duyệt và bắt buộc dùng làm baseline implementation. Đây không còn là các phương án mở để lựa chọn:

| Khu vực quyết định | Quyết định đã chốt | Quy tắc implementation |
|---|---|---|
| Đọc source | Cursor batching bằng `fetchmany()` | `SalesExtractor` cung cấp batch iterator; canonical Bronze load không được dùng `fetchall()` |
| Dạng batch | Một pandas DataFrame cho mỗi batch | Bổ sung lineage và record hash deterministic trong batch trước khi load |
| Batch size ban đầu | `10,000` rows, cấu hình qua `Settings` | Giá trị phải được validate là số dương và có giới hạn hợp lý |
| Thứ tự source | `ORDER BY` ổn định theo source key | Offset/page number không được dùng làm resume checkpoint |
| Dedup Bronze | Giữ raw fidelity; không dedup business key ở Bronze | Dedup toàn cục thuộc Silver hoặc target rule đã được phê duyệt riêng |
| Target ghi dữ liệu | Run/load-specific staging table | Không replace Bronze đang publish khi extraction còn chạy |
| Phạm vi commit | Commit từng batch thành công vào staging | Chỉ ghi checkpoint sau khi commit batch tương ứng thành công |
| Publish table | Chỉ publish staging sau khi validation toàn table pass | Giữ Bronze hợp lệ cũ đến khi publish thành công |
| Phạm vi retry | Retry cùng logical batch, không tạo batch mới | Giữ nguyên `run_id`, `load_id`, `batch_id` ở mọi attempt |
| Điều kiện retry | Chỉ retry transient error đã phân loại | Không retry schema, authentication, SQL, contract hoặc deterministic validation error |
| Retry policy | Tối đa 3 attempts với exponential backoff có giới hạn và jitter | Phải log attempt number, delay, error class và outcome cuối |
| Bảo vệ idempotency | Deterministic record/batch identity kết hợp unique protection hoặc reconciliation | Commit không rõ phải được reconcile trước khi retry |
| Incremental checkpoint | Watermark hoặc key range ổn định, advance transactionally cùng batch thành công | Không advance checkpoint trước data commit |
| Dữ liệu rejected | Dùng quarantine mode cho lỗi cấp record có thể cô lập; lưu riêng với reason và load identity | Record hợp lệ tiếp tục vào staging; record lỗi không biến mất âm thầm và full payload không vào log thông thường |

Luồng Bronze canonical để implementation:

```text
create run_id/load_id
  -> query source với thứ tự ổn định
	  -> fetchmany(10_000)
		  -> tạo DataFrame batch
			  -> thêm lineage/hash
				  -> validate batch
					  -> ghi staging batch
						  -> commit data và checkpoint atomic
							  -> chỉ retry cùng identity khi transient error
								  -> validate toàn staging table
									  -> publish staging thành Bronze
```

Bất kỳ implementation nào dùng `fetchall()`, append trực tiếp vào published table, advance checkpoint trước commit, retry mù một write không rõ trạng thái hoặc silently drop rejected row đều không đạt baseline Phase 4 này.


| Bước | Implementation hiện tại | Đánh giá |
|---|---|---|
| Đọc SQL Server | `SalesExtractor` dùng `cursor.fetchall()` | Đọc toàn bộ source table vào memory; chưa batch/streaming khi đọc |
| Tạo DataFrame | Tất cả row được chuyển thành một DataFrame | Memory tăng theo kích thước source table |
| Ghi PostgreSQL | `to_sql(..., method="multi", chunksize=1000)` | Có batching khi ghi; chưa phải streaming end-to-end |
| Bronze utility cũ | `bronze_ingest.py` cũng dùng `fetchall()` và chuẩn bị toàn bộ values cho `executemany()` | Có cùng hạn chế về memory và recovery |

Luồng Bronze mục tiêu:

```text
SQL Server cursor
  -> fetchmany(batch_size)
	  -> DataFrame batch
		  -> lineage và record hash
			  -> batch validation
				  -> staging/load
					  -> batch audit
```

Cần quyết định rõ batch size, phạm vi commit, phạm vi retry, thứ tự đọc và chiến lược resume. Chỉ dùng `drop_duplicates()` theo từng batch là không an toàn nếu cùng business key có thể nằm ở các batch khác nhau.

### Xử lý lỗi và dữ liệu rejected ở Bronze

| Khu vực | Hành vi hiện tại | Tác động | Enhancement cần có |
|---|---|---|---|
| Cô lập lỗi theo table | `SalesBronzeIngestionJob` chưa có `try/except` theo table cho extract, load và validation | Một exception có thể dừng batch mà không có kết quả đầy đủ | Trả result cho mọi table đã thử chạy và có stop/continue policy rõ ràng |
| Row-level quarantine | Chưa có rejected-record hoặc error table | Record lỗi không được lưu để điều tra và không có lý do lỗi | Dùng quarantine mode cho lỗi cấp row có thể cô lập; thêm `bronze.rejected_records` hoặc thiết kế tương đương, có reason và run ID |
| Audit | Job chính chưa lưu đầy đủ start, finish, batch, count và error | Không có lịch sử vận hành bền vững | Lưu run ID, table, batch, rows read/written/rejected, status, error type và timestamp |
| Full-load safety | `if_exists="replace"` có thể thay target trước khi load lỗi ở bước sau | Run lỗi có thể làm Bronze không đầy đủ hoặc mất bảng hợp lệ cũ | Load vào staging rồi publish sau validation, hoặc dùng transaction có khả năng recovery |
| Logging | Connector có log connection failure nhưng job chưa log nhất quán context table/batch | Khó phân tích root cause | Dùng structured log với `run_id`, `stage`, `source_table`, `target_table`, `batch_id`, count, status và error đã sanitize |

Bronze dùng **quarantine mode** cho lỗi cấp record có thể cô lập an toàn: record hợp lệ trong batch tiếp tục vào staging, còn record lỗi được ghi vào quarantine table/file có reason và load identity. Policy này không được che giấu lỗi hệ thống, schema hoặc contract. Không ghi toàn bộ payload record vào log thông thường; log chỉ nên ghi identifier và metadata trừ khi data classification cho phép nhiều hơn.

Rejected-row threshold mặc định là `0` cho Bronze raw load, nhưng quarantine mode vẫn là cơ chế xử lý: record lỗi được ghi trạng thái `REJECTED`, table không được báo là `SUCCESS` tuyệt đối, và threshold cấu hình sẽ quyết định table được publish với trạng thái `SUCCESS_WITH_REJECTIONS` hay phải fail. Threshold phải là configuration tường minh và xuất hiện trong audit report.

Luồng xử lý lỗi cấp record:

```text
batch
	-> validate từng record
			-> record hợp lệ -> staging
			-> record lỗi -> bronze.rejected_records
												 -> reason + record_key + run/load/batch identity
	-> đánh giá rejected threshold
			-> trong policy: SUCCESS_WITH_REJECTIONS
			-> vượt policy: FAILED, không publish
```

### Đánh giá Silver về read, batch và error

| Khu vực | Hành vi hiện tại | Tác động | Enhancement cần có |
|---|---|---|---|
| Chiến lược đọc | `_read_bronze()` gọi `pd.read_sql_query()` không có `chunksize` | Toàn bộ Bronze table được load vào memory | Dùng chunk có kiểm soát hoặc SQL xử lý trong database cho bảng lớn |
| Transformation | Rename, type conversion, deduplication và selection chạy trên một DataFrame đầy đủ | Input lớn gây áp lực memory; dedup theo batch có thể sai | Dùng database-side deduplication/staging hoặc giữ state xuyên các batch |
| An toàn khi ghi | Silver ghi trực tiếp bằng `to_sql(..., if_exists="replace")` | Lỗi giữa chừng có thể để lại Silver bị replace dở | Ghi vào staging và chỉ publish sau khi transform/validation pass |
| Thiếu Person data | Thiếu `bronze.person` thì dùng `print()` và fallback name | Warning không structured và suy giảm chất lượng có thể bị bỏ qua | Log warning có context và nêu rõ fallback policy trong validation/report |
| Schema error | Chưa validate required column trước transformation | Column thiếu hoặc đổi tên sẽ lỗi muộn | Thêm input/output schema contract, error ghi rõ table và column |

Với Silver, streaming không tự động đúng: dedup toàn cục theo business key cần window function trong database, staging hoặc state xuyên suốt các batch. Hướng thực tế là clean/dedup trong PostgreSQL rồi publish Silver bằng flow atomic.

#### Baseline Silver đã chốt để implementation

Các quyết định sau đã được phê duyệt và bắt buộc dùng làm baseline implementation:

| Khu vực quyết định | Quyết định đã chốt | Quy tắc implementation |
|---|---|---|
| Đọc source | Đọc Bronze theo chunk thành DataFrame | Dùng chunk có kiểm soát, ban đầu `10,000` rows; canonical Silver không load toàn bộ Bronze table vào memory |
| Mô hình xử lý | Hybrid pandas và database | Pandas xử lý mapping, type conversion, trim, flag và enrichment; database staging xử lý dedup toàn cục và publish |
| Input contract | Validate required Bronze columns trước transform | Missing table/column hoặc schema mismatch là lỗi cấp table; không quarantine toàn bộ table như lỗi row |
| Type conversion | Phát hiện rõ lỗi coercion | Không để `errors="coerce"` âm thầm che giấu giá trị lỗi; cô lập invalid row với reason và source identity |
| Deduplication | Dedup toàn cục sau khi stage đủ các chunk | Không `drop_duplicates()` độc lập từng chunk; dùng `ROW_NUMBER()`/`PARTITION BY` hoặc rule database tương đương |
| Thứ tự dedup | Giữ record mới nhất một cách deterministic | Dùng `_load_date DESC, _record_hash DESC` trừ khi có source-version rule cụ thể được duyệt |
| Lỗi cấp record | Dùng quarantine mode | Record hợp lệ tiếp tục vào staging; record lỗi vào `silver.rejected_records` kèm reason và identity |
| Lỗi hệ thống/schema | Fail closed | Không publish Silver mới khi connection, schema, contract hoặc deterministic validation fail |
| Phạm vi commit | Commit từng chunk vào staging theo run | Silver đang publish không bị tác động khi run chưa hoàn tất |
| Phạm vi retry | Retry cùng logical chunk | Giữ `run_id`, `table_load_id`, `batch_id`; chỉ retry transient error đã phân loại |
| Retry policy | Tối đa 3 attempts với exponential backoff có giới hạn và jitter | Log attempt, delay, error class và outcome cuối |
| Checkpoint | Ghi sau successful staging commit | Không advance progress trước data commit; reconcile commit không rõ trước khi retry |
| Rejected threshold | Mặc định `0` | Rejected row phải được ghi nhận; table không thể là `SUCCESS` tuyệt đối; chỉ publish `SUCCESS_WITH_REJECTIONS` khi threshold rõ ràng cho phép |
| Person enrichment | `bronze.person` là dependency bắt buộc cho bảng salesperson Silver | Thiếu Person làm fail salesperson transformation trừ khi có degraded mode được duyệt; không fallback âm thầm về ID |
| Publication | Validate toàn staging rồi atomic publish/swap | Giữ Silver version hợp lệ cũ đến khi bản thay thế pass toàn bộ check |
| Logging | Structured log theo stage/table/batch | Có context run/table/batch/attempt/error/status; không log secret hoặc full raw payload |

Luồng Silver canonical để implementation:

```text
identify Bronze snapshot/load
  -> create run_id/table_load_id
	  -> validate input schema
		  -> đọc Bronze theo chunk 10,000 rows
			  -> transform từng chunk bằng pandas
				  -> phát hiện conversion/data error
					  -> row hợp lệ -> Silver staging
					  -> row lỗi -> silver.rejected_records
						  -> commit chunk và checkpoint
							  -> chỉ retry cùng identity khi transient error
								  -> global deduplication trên staging
									  -> validate toàn staging table
										  -> publish/swap Silver atomic
```

Bất kỳ implementation nào đọc toàn bộ Bronze table vào memory, dedup độc lập từng chunk, âm thầm coerce dữ liệu lỗi thành null, fallback salesperson về ID khi chưa có degraded mode được duyệt, publish Silver partial hoặc retry mù một write không rõ trạng thái đều không đạt baseline Phase 4 này.

Các status bắt buộc của Silver result:

| Status | Ý nghĩa |
|---|---|
| `SUCCESS` | Tất cả chunk và validation pass, không có rejected row |
| `SUCCESS_WITH_REJECTIONS` | Row hợp lệ pass và rejected row nằm trong threshold đã được phê duyệt rõ |
| `FAILED` | Lỗi system/schema/contract, vượt rejected threshold hoặc validation fail; không publish Silver mới |

### Đánh giá Gold về read, batch và publish safety

| Khu vực | Hành vi hiện tại | Tác động | Enhancement cần có |
|---|---|---|---|
| Chiến lược đọc | Gold đọc toàn bộ Silver bằng `pd.read_sql_query()` không có `chunksize` | Toàn bộ Silver table nằm trong memory | Dùng database-side join hoặc batch có kiểm soát cho fact lớn |
| Tạo fact | Join header/detail và tính measures trong pandas | Memory và runtime tăng theo kích thước fact | Ưu tiên SQL staging cho fact join, hoặc batch có state bảo toàn grain và referential integrity |
| Thứ tự publish | `_reset_gold_tables()` drop Gold trước khi đọc và build xong Silver | Đây là rủi ro availability cao nhất; lỗi có thể làm mất Gold hợp lệ cuối cùng | Build dimensions/facts trong staging, validate rồi publish/swap |
| Constraints | Chỉ thêm constraint sau `to_sql(replace)` | Lỗi có thể để schema thiếu constraint hoặc không hoàn chỉnh | Quản lý DDL riêng và kiểm tra PK/FK/data type trước publish |
| Thời điểm validation | Referential integrity có thể chỉ phát hiện khi thêm constraint | Lỗi xuất hiện muộn sau destructive operation | Validate staging trước khi tác động vào Gold đang publish |

Luồng Gold mục tiêu:

```text
Read Silver
  -> build Gold staging tables
	  -> validate grain, keys, measures và references
		  -> add/verify constraints
			  -> publish hoặc swap
				  -> giữ Gold cũ đến khi thành công
```


#### Baseline Gold đã chốt để implementation

Các quyết định sau đã được phê duyệt và bắt buộc dùng làm baseline implementation:

| Khu vực quyết định | Quyết định đã chốt | Quy tắc implementation |
|---|---|---|
| Đọc dimension | Có thể full-read vì các dimension hiện còn nhỏ | Không ép streaming cho `dim_date`, `dim_customer`, `dim_product`, `dim_territory`, `dim_salesperson` nếu volume chưa yêu cầu |
| Đọc/build fact | Xử lý `fact_sales` theo batch hoặc SQL-side | Mục tiêu ban đầu là SQL JOIN/staging trong database; pandas chunk được phép ở bước migration |
| Thứ tự source | `ORDER BY sales_order_detail_id` ổn định | Checkpoint theo key/range, tuyệt đối không theo offset/page number |
| Fact grain | Một row cho mỗi `sales_order_detail_id` | Duplicate fact key là validation failure, không silently drop |
| Vị trí transformation | Ưu tiên PostgreSQL cho fact JOIN và measure lớn | Chỉ giữ pandas cho logic cần tương thích trong migration |
| Input snapshot | Build từ Silver snapshot/load đã xác định | Không trộn source version trong cùng Gold run |
| Target ghi dữ liệu | Run-specific staging tables | Không ghi trực tiếp vào Gold đang publish trong lúc build |
| Phạm vi commit | Commit từng fact batch vào staging | Gold publish hiện tại không bị tác động cho đến khi run hợp lệ hoàn toàn |
| Quarantine | Mặc định không quarantine ở Gold | Xử lý conversion issue ở Silver; Gold integrity/business-rule error làm fail build |
| Validation | Validate staging trước publication | Kiểm tra schema, grain, key, measure, null và referential integrity trước publish/tạo FK |
| Điều kiện retry | Chỉ transient database error đã phân loại | Không retry missing table/column, duplicate key, orphan key, business-rule violation hoặc KPI mismatch |
| Retry policy | Tối đa 3 attempts với exponential backoff có giới hạn và jitter | Retry cùng `run_id`, `table_load_id`, `batch_id`; log attempt và outcome cuối |
| Commit không rõ | Reconcile staging/audit trước retry | Không append mù fact batch sau client timeout |
| Idempotency | Unique `sales_order_detail_id` kết hợp batch identity | Chạy lặp phải tạo đúng một logical fact row cho mỗi detail key |
| Publication | Atomic publish/swap sau khi mọi validation pass | Giữ Gold version hợp lệ cũ khi build hoặc validation fail |
| Constraints | Add/verify constraint trên staging trước publish | Gold publish phải giữ PK/FK và data-type contract sau mỗi run |
| Logging | Structured log theo run/table/batch/attempt/error/status | Không log secret, full connection string hoặc full raw payload |

Luồng Gold canonical để implementation:

```text
identify Silver snapshot/load
  -> create run_id/table_load_id
      -> build dimension nhỏ trong staging
          -> build fact bằng database-side JOIN hoặc batch ổn định
              -> validate schema, grain, measure, key, null và reference
                  -> add/verify staging constraints
                      -> reconcile commit không rõ nếu có
                          -> atomic publish/swap sang Gold
                              -> giữ Gold cũ khi fail
```

Policy lỗi của Gold:

| Loại lỗi | Policy |
|---|---|
| Transient database error | Retry cùng atomic batch/unit |
| Missing Silver table/column | Fail closed; không publish |
| Duplicate fact key | Fail closed; không silently dedup |
| Orphan dimension key | Fail closed; validate trước publish |
| Measure/business-rule violation | Fail closed; điều tra Silver hoặc rule |
| Row-level conversion issue từ source | Phải xử lý ở Silver quarantine trước khi vào Gold |
| Build fail sau staging commit | Giữ Gold đang publish không đổi; cleanup hoặc expire staging lỗi |

Bất kỳ implementation nào drop Gold đang publish trước khi build thành công, ghi trực tiếp vào Gold publish, dùng offset checkpoint, silently drop fact row, mặc định quarantine lỗi integrity ở Gold hoặc retry mù một write không rõ trạng thái đều không đạt baseline Phase 4 này.

### Hành vi context manager của connector

| Phát hiện | Hành vi hiện tại | Tác động | Hướng đề xuất |
|---|---|---|---|
| Connection fail không raise ngay khi entry | `BaseConnector.__enter__()` gọi `connect()` nhưng bỏ qua kết quả `False` | Block `with` vẫn tiếp tục rồi mới lỗi `Not connected` | Raise `ConnectionError` rõ ràng ngay khi không kết nối được |
| Ranh giới lỗi chưa rõ | Connection failure và query failure tách xa nhau qua nhiều call site | Mất context lỗi ban đầu khi troubleshoot | Xem connection establishment là boundary nghiêm ngặt; ghi context connector/config nhưng không ghi secret |

### Ưu tiên cho buổi trao đổi kỹ thuật tiếp theo

| Ưu tiên | Nội dung cần quyết định |
|---|---|
| P0 | Central settings và `.env` loading; fail-fast health/config gate; Gold staging/publish an toàn; per-stage/per-table error handling |
| P1 | Bronze batch read; Silver/Gold batch hoặc database-side transformation; audit table; retry/backoff; rejected-data handling |
| P2 | Resume từ batch lỗi; incremental theo watermark; chính sách row-level quarantine; operational metrics |

### Review cơ chế retry và idempotency

#### Đánh giá hiện tại

| Khu vực | Hành vi hiện tại | Đánh giá |
|---|---|---|
| Retry implementation | Pipeline hiện chưa có retry, backoff, attempt counter hoặc phân loại lỗi retryable | Lỗi connection/load tạm thời làm operation fail ngay |
| Identity khi ghi Bronze | Full mode dùng `replace`; incremental mode dùng `append` | Chạy lại có thể thay dữ liệu hợp lệ hoặc tạo duplicate |
| Batch checkpoint | Chưa lưu batch ID, watermark, checkpoint hoặc progress đã commit | Run restart không biết an toàn nên resume từ đâu |
| Bảo vệ duplicate | Chưa có unique constraint hoặc chiến lược `ON CONFLICT`/upsert cho record load | Retry sau một commit không chắc chắn có thể tạo duplicate |
| Silver và Gold rebuild | Silver/Gold dùng full DataFrame và flow destructive `replace`/drop | Retry transformation dở dang có thể expose bảng không nhất quán |

#### Nguyên tắc cốt lõi

Retry và idempotency giải quyết hai vấn đề khác nhau:

- **Retry** trả lời: “Có nên thử lại operation sau lỗi không?”
- **Idempotency** trả lời: “Nếu operation chạy nhiều lần, trạng thái dữ liệu cuối có vẫn đúng không?”

Chỉ bật retry sau khi đã có idempotent boundary. Retry đơn thuần có thể biến một database commit không chắc chắn thành duplicate data.

#### Identity đề xuất cho operation idempotent

Mỗi pipeline run và batch cần identity ổn định:

```text
run_id       = một lần chạy toàn pipeline
load_id      = một lần load source-to-target trong run
batch_id     = một batch có thứ tự trong load
record_key   = source primary key hoặc record hash deterministic
```

Retry cho cùng operation phải dùng lại `load_id` và `batch_id`; không được tạo logical load identity mới ở mỗi attempt.

#### Chính sách retry đề xuất

| Quy tắc | Đề xuất |
|---|---|
| Lỗi được retry | Network timeout, connection reset, database tạm thời unavailable, deadlock và các transient error đã phân loại rõ |
| Lỗi không retry | Missing table/column, authentication failure, SQL invalid, schema mismatch, data contract failure và validation failure deterministic |
| Backoff | Exponential backoff có jitter, ví dụ 1s, 2s, 4s, sau đó giới hạn maximum |
| Số attempt | Maximum nhỏ, ví dụ 3 attempts; cấu hình được theo environment |
| Transaction boundary | Retry toàn bộ atomic unit; không mù quáng retry một phần transaction sau commit không chắc chắn |
| Observability | Log attempt number, run/load/batch ID, error class, wait time và outcome cuối; không log secret/full payload |
| Stop policy | Khi retry hết, đánh dấu batch/table/stage failed và chặn publication nếu stage bắt buộc |

#### Thiết kế Bronze đề xuất

Dùng staging table và uniqueness rule deterministic trước khi publish:

```text
fetch batch
  -> tính record_key
	  -> ghi staging với run_id/load_id/batch_id
		  -> commit atomic
			  -> ghi checkpoint
				  -> retry cùng batch nếu transient failure
```

Với incremental load, đọc theo watermark ổn định hoặc source key range, enforce unique idempotency key, dùng upsert hoặc `ON CONFLICT` khi phù hợp với business rule, và chỉ advance watermark trong cùng transaction với batch commit thành công.

Quy tắc quan trọng: **không advance checkpoint trước khi data commit thành công**. Nếu commit outcome không rõ, phải query lại idempotency key để reconcile trước khi retry.

#### Thiết kế Silver và Gold đề xuất

Silver transformation phải deterministic với cùng Bronze snapshot và transformation version. Retry nên chạy lại staging transformation, không append thêm một bản Silver thứ hai. Dedup toàn cục cần window function trong database, staging hoặc state xuyên suốt các batch.

Gold nên được build trong staging table theo run. Retry chỉ rebuild staging run đó, còn Gold đang publish không bị tác động. Validate grain, measure, key và reference trước atomic publish/swap. Không nên retry flow hiện tại `DROP Gold -> to_sql(replace)` vì boundary destructive này không idempotent và không an toàn về availability.

#### Test nghiệm thu bắt buộc

| Scenario | Kết quả mong đợi |
|---|---|
| Read failure tạm thời trước khi ghi | Cùng batch được retry và chỉ load một lần |
| Write failure tạm thời trước commit | Retry tạo một logical batch, không duplicate |
| Lỗi sau commit nhưng trước checkpoint | Reconciliation phát hiện batch đã commit; retry không tạo duplicate |
| Chạy cùng full run hai lần | Target publish vẫn đúng và không có duplicate record |
| Retry incremental run với cùng watermark | Không duplicate business record; watermark chỉ advance một lần |
| Retry Silver transformation | Silver publish cũ vẫn hợp lệ cho đến khi bản thay thế pass validation |
| Gold build fail trong lúc retry | Gold publish cũ vẫn khả dụng và không thay đổi |

## Baseline tách domain và kiến trúc Bronze

### Phát hiện hiện tại

`SalesBronzeIngestionJob` hiện điều phối 7 table thuộc 3 khu vực nghiệp vụ: Sales, Production và Person. Các thành phần kỹ thuật đã được tách một phần thành extractor, loader và validator, nhưng ownership theo domain và mapping table vẫn đang bị coupling trong một Sales job.

### Kiến trúc đã chốt

Project sẽ tách Bronze theo **business domain**, không tách máy móc mỗi table một file:

```text
PipelineRunner
	-> SalesBronzeJob
	-> ProductionBronzeJob
	-> PersonBronzeJob
```

| Khu vực quyết định | Quyết định đã chốt | Quy tắc implementation |
|---|---|---|
| Ownership domain | Mỗi business domain có một Bronze job | Sales quản lý order header/detail, customer, territory, salesperson; Production quản lý product; Person quản lý person data |
| Granularity table | Dùng table specification thay vì một class/file cho mỗi table đơn giản | Chỉ tạo class riêng khi query, schema, watermark, quarantine hoặc business policy khác biệt đáng kể |
| Xử lý dùng chung | Tạo một shared ingestion engine | Batch read, staging, retry, audit, checkpoint, quarantine và publish không được duplicate trong domain job |
| Metadata table | Đưa extraction map vào định nghĩa `TableSpec` | Lưu source schema/table, target table, primary key, required columns, ordering key và incremental column trong specification |
| Domain policy | Giữ rule theo domain/feature | Không đưa Sales, Production hoặc Person business rule vào shared ingestion engine |
| Ownership Product và Person | Loại `Production.Product` và `Person.Person` khỏi Sales Bronze job | Sales có thể khai báo Person là dependency enrich ở Silver, nhưng không sở hữu Person ingestion |
| Orchestration | Domain job trả structured result độc lập | Pipeline quyết định một domain fail là partial success hay fail toàn workflow bắt buộc |
| Compatibility | Giữ Sales job hiện tại như compatibility wrapper tạm thời | Wrapper delegate sang Sales domain job trong giai đoạn migration; không thêm logic mới vào wrapper |
| Testing | Test shared engine, domain job và table specification riêng | Domain này fail không được buộc phải chạy live domain không liên quan |

Cấu trúc đề xuất:

```text
src/
├── shared/
│   └── ingestion/
│       ├── batch_ingestion_engine.py
│       ├── checkpoint_manager.py
│       ├── ingestion_models.py
│       └── retry_policy.py
└── features/
		├── sales/
		│   ├── domain/bronze/table_specs.py
		│   └── jobs/sales_bronze_job.py
		├── production/
		│   ├── domain/bronze/table_specs.py
		│   └── jobs/production_bronze_job.py
		└── person/
				├── domain/bronze/table_specs.py
				└── jobs/person_bronze_job.py
```

Ví dụ table specification:

```python
@dataclass(frozen=True)
class TableSpec:
		source_schema: str
		source_table: str
		target_table: str
		primary_key: str
		required_columns: tuple[str, ...]
		ordering_key: str
		incremental_column: str | None = None
```

Shared engine sở hữu execution mechanics. Domain job chỉ cung cấp table specification, domain policy và dependency. Table chỉ khác source/target name hoặc key metadata phải giữ là specification, không tạo class mới.

Thứ tự migration:

1. Tách `extraction_map` hiện tại thành các định nghĩa `TableSpec`.
2. Tạo `SalesBronzeJob` chỉ gồm các table thuộc Sales.
3. Tạo `ProductionBronzeJob` cho Product và `PersonBronzeJob` cho Person.
4. Đưa batch/retry/audit/checkpoint/staging mechanics vào shared engine.
5. Inject settings, extractor, loader, validator và policy vào domain job.
6. Giữ `SalesBronzeIngestionJob` làm compatibility wrapper delegate.
7. Thêm test độc lập cho shared engine và từng domain job.

Bất kỳ implementation nào tạo một platform Bronze job khổng lồ, duplicate batch/retry mechanics ở từng domain, đưa domain rule vào shared infrastructure hoặc tạo một class cho mỗi table đơn giản không có behavior riêng đều không đạt baseline Phase 4 này.

## Checklist công việc chính

| Done | Main task | Subtask | Mô tả | Ưu tiên | Status | Tác động hiện tại | Lợi ích sau enhance | Tiêu chí nghiệm thu / Evidence | Dependency |
|---|---|---|---|---|---|---|---|---|---|
| [ ] | Orchestration pipeline | Định nghĩa pipeline contract | Xác định stage, input, output, status, chính sách lỗi và schema kết quả | P0 | Not started | Runtime dừng ở Bronze và chưa có contract thống nhất | Mọi stage có hành vi dự đoán được và kết quả machine-readable | Contract được ghi tài liệu; result có status stage và row count | Xác nhận phạm vi |
| [ ] | Orchestration pipeline | Implement `PipelineRunner` | Điều phối Bronze, Silver, Silver validation, Gold và Gold KPI validation | P0 | Not started | Operator phải chạy nhiều command thủ công | Một command chạy được toàn bộ Sales pipeline | Command chạy đúng thứ tự và trả về report đầy đủ | Pipeline contract |
| [ ] | Orchestration pipeline | Thêm CLI options | Hỗ trợ `full`, `incremental` khi phù hợp, chọn stage và log level | P0 | Not started | Hành vi runtime bị ẩn trong code và script | Execution lặp lại được với tham số rõ ràng | Option không hợp lệ phải fail rõ ràng; help text đầy đủ | Pipeline runner |
| [ ] | Orchestration pipeline | Thêm process exit codes | Chỉ trả exit code `0` khi các stage bắt buộc thành công | P0 | Not started | Automation không nhận biết được pipeline thành công hay thất bại | CI, scheduler và operator phát hiện được lỗi | Run thành công exit `0`; lỗi load/validation exit non-zero | Pipeline runner |
| [ ] | Orchestration pipeline | Xử lý exception theo stage | Ghi nhận lỗi theo stage và dừng/tiếp tục theo policy | P0 | Not started | Exception hiện tại không cung cấp đủ context | Lỗi được tổng hợp theo stage và nguyên nhân | Report có failed stage, error message và final status | Pipeline contract |
| [ ] | Health và readiness | Biến health check thành pipeline gate | Không cho xử lý dữ liệu khi SQL Server/PostgreSQL không sẵn sàng | P0 | Not started | Health `degraded` nhưng Bootstrap và Bronze vẫn tiếp tục chạy | Tránh các lỗi có thể dự đoán và partial processing | Khi dependency lỗi, không stage downstream nào được chạy | Pipeline runner; health service |
| [ ] | Health và readiness | Kiểm tra schema và required table | Kiểm tra schema Bronze/Silver/Gold và object bắt buộc | P1 | Not started | Kết nối thành công chưa đồng nghĩa warehouse sử dụng được | Phát hiện sớm lỗi readiness với thông báo cụ thể | Report chỉ rõ schema/table còn thiếu | Bootstrap và database access |
| [ ] | Bootstrap và migration | Thay thế bootstrap placeholder | Tạo hoặc kiểm tra schema, metadata table và object theo cách idempotent | P1 | Not started | Application báo thành công dù platform chưa thực sự được chuẩn bị | Môi trường mới và môi trường cũ được chuẩn bị nhất quán | Bootstrap chạy lặp lại không gây thay đổi phá hủy | PostgreSQL |
| [ ] | Bootstrap và migration | Thêm schema versioning | Ghi nhận và kiểm tra version database schema | P1 | Not started | Docker initialization chỉ tự chạy khi volume được tạo lần đầu | Thay đổi database có thể truy vết và triển khai được | Có version table và migration check được test | Bootstrap implementation |
| [ ] | Bronze reliability | Validate mode nghiêm ngặt | Từ chối mode không hỗ trợ thay vì coi mọi giá trị khác `full` là append | P0 | Not started | Typo có thể âm thầm kích hoạt hành vi không an toàn | Request vận hành sai fail trước khi thay đổi dữ liệu | Chỉ mode đã document được chấp nhận | Bronze job |
| [ ] | Bronze reliability | Cô lập lỗi theo table | Trả result cho từng table và áp dụng chính sách dừng/tiếp tục rõ ràng | P1 | Not started | Một table lỗi có thể dừng cả batch mà không có report đầy đủ | Operator thấy toàn bộ table đã chạy và lỗi tương ứng | Report xác định table, stage và count bị lỗi | Pipeline contract |
| [ ] | Bronze reliability | Thêm retry và backoff | Retry lỗi kết nối/load có tính tạm thời | P1 | Not started | Lỗi kết nối tạm thời làm cả run thất bại | Scheduled execution bền vững hơn | Retry count và lỗi cuối được ghi nhận và test | Connector behavior |
| [ ] | Bronze reliability | Thêm run audit metadata | Lưu run ID, timestamp, mode, table, count, status và error | P1 | Not started | Không có lịch sử lâu dài để điều tra vận hành | Có thể truy vấn lịch sử load và lineage | Mỗi table đã thử chạy đều có audit row | PostgreSQL metadata tables |
| [ ] | Bronze reliability | Làm incremental load idempotent | Xác định watermark/hash strategy và ngăn duplicate khi append | P1 | Not started | Chạy lại append có thể tạo duplicate | Rerun an toàn và incremental processing có kiểm soát | Cùng một input chạy lại không tạo duplicate business record | Quyết định incremental design |
| [ ] | Bronze quality | Dùng đầy đủ Bronze validation | Gọi lineage, critical-column, null-tolerance và count checks trong job | P1 | Not started | `validate_table()` tồn tại nhưng job chính chỉ kiểm tra count | Phát hiện lỗi chất lượng trước khi transform | Job result bao gồm toàn bộ quality check | Validation contract |
| [ ] | Silver transformation | Đóng gói Silver thành job/service | Chuyển orchestration từ `run()` độc lập sang class/service có thể tái sử dụng | P0 | Not started | Silver không inject dependency hoặc được điều khiển thống nhất | Silver chạy được từ CLI, App, test hoặc scheduler | Job nhận dependency/config và trả standard result | Pipeline contract |
| [ ] | Silver transformation | Định nghĩa transformation contract | Kiểm tra input column và output schema trước khi ghi | P1 | Not started | Thiếu column gây lỗi muộn và thiếu context | Phát hiện schema drift sớm | Contract failure chỉ rõ table và column thiếu | Silver job |
| [ ] | Silver quality | Biến validation thành gate | Trả failure/non-zero khi duplicate, null, row-loss hoặc orphan check fail | P0 | Not started | Có thể tạo report nhưng vẫn chạy Gold dù dữ liệu lỗi | Silver không hợp lệ không được feed vào Gold | Pipeline dừng trước Gold khi Silver validation fail | Silver validation service |
| [ ] | Silver quality | Quyết định phạm vi enrich customer/person | Xác định customer name lấy từ `Person.Person` hay giữ account-based | P2 | Needs clarification | Quy tắc tên customer chưa nhất quán với kỳ vọng nghiệp vụ | Ý nghĩa customer dimension rõ ràng | Quyết định được ghi lại kèm test và rule chất lượng | Quyết định nghiệp vụ |
| [ ] | Gold reliability | Đóng gói Gold thành job/service | Cho phép Gold được gọi theo pipeline contract chung | P0 | Not started | Gold chỉ chạy được bằng standalone script | Gold tham gia lifecycle có kiểm soát | Job trả table count và publication status | Pipeline contract |
| [ ] | Gold reliability | Thay thế destructive publish flow | Load vào staging và chỉ publish sau khi build/validation thành công | P0 | Not started | `DROP` và `to_sql(replace)` có thể làm Gold mất dữ liệu khi lỗi | Gold đang publish vẫn được giữ đến khi bản mới hợp lệ | Build lỗi không ảnh hưởng Gold cũ; build thành công publish đầy đủ | PostgreSQL strategy |
| [ ] | Gold reliability | Bảo toàn constraint và data type | Quản lý DDL riêng với data load và tạo constraint nhất quán | P1 | Not started | Replace table có thể xóa constraint và làm schema không ổn định | Gold contract ổn định sau mỗi rerun | PK/FK/type assertions pass sau mỗi publish | Gold publish design |
| [ ] | Gold quality | Validate referential integrity trước publish | Kiểm tra orphan key và dimension bắt buộc trước khi tạo FK | P0 | Not started | Constraint creation có thể fail muộn sau khi data đã ghi | Lỗi được phát hiện trước publication | Pre-publish report có zero invalid reference | Gold job |
| [ ] | Configuration | Tạo typed settings tập trung | Gom cấu hình SQL Server, PostgreSQL, batch, retry và logging | P1 | Not started | Connector tự diễn giải environment variables riêng | Cấu hình được validate một lần và dùng thống nhất | Thiếu/sai config tạo startup error rõ ràng | Phạm vi settings |
| [ ] | Configuration | Kiểm tra environment template | Giữ `.env.example` đồng bộ với runtime settings bắt buộc | P1 | Not started | Môi trường mới có thể thiếu biến cần thiết | Setup reproducible hơn | Automated check phát hiện key thiếu trong template | Settings model |
| [ ] | Testing | Mark integration tests | Tách test cần database khỏi pure unit test | P0 | Not started | `pytest` fail local khi PostgreSQL/SQL Server không chạy | Developer chạy unit test nhanh độc lập | `pytest -m "not integration"` deterministic; marker tồn tại | Pytest config |
| [ ] | Testing | Thêm fixture và mock cho service | Test thứ tự stage mà không cần database thật | P0 | Not started | Contract test hiện chưa kiểm tra execution order và failure gate | Hành vi orchestration được test nhanh và rẻ | Test success, degraded health, stage failure và exit status | Pipeline runner |
| [ ] | Testing | Thiết lập integration test | Có PostgreSQL startup/fixture được kiểm soát và prerequisite SQL Server rõ ràng | P1 | Blocked | Integration test hiện fail vì Docker/PostgreSQL unavailable | Integration evidence reproducible | Setup được document và connectivity/schema test pass | Docker daemon; SQL Server |
| [ ] | Testing | Thêm regression test cho rerun | Test full rerun, partial failure, duplicate prevention và publish safety | P1 | Not started | Edge case vận hành chưa được kiểm chứng | Enhancement không làm giảm data integrity | Scenario rerun/failure có assertion tự động | Bronze/Gold reliability |
| [ ] | Observability | Chuẩn hóa structured logging | Ghi run ID, stage, table, status, duration và error context | P1 | Not started | Log hiện thiên về connection và text tự do | Điều tra nhanh hơn và tích hợp automation tốt hơn | Log lọc được theo run/stage/table | Pipeline runner |
| [ ] | Observability | Tạo pipeline summary report | Tạo summary Markdown/JSON cho mỗi run | P1 | Not started | Kết quả bị phân tán trong console và nhiều report | Operator/reviewer có một evidence artifact | Report có stage status, count, duration và failure | Standard result contract |
| [ ] | Delivery | Thêm CI checks | Chạy unit test, integration-aware test, lint, format và type check | P1 | Not started | Chất lượng phụ thuộc vào chạy local thủ công | Phát hiện regression trước khi merge | CI status bắt buộc trước khi merge enhancement branch | Test commands |
| [ ] | Delivery | Cập nhật tài liệu vận hành | Ghi rõ one-command execution, prerequisite, recovery và troubleshooting | P1 | Not started | Tài liệu hiện mô tả manual workflow nhưng chưa mô tả target operation | Người dùng chạy và khôi phục platform nhất quán | README/runbook khớp behavior đã implement | Pipeline implementation |

## Thứ tự triển khai đề xuất

| Thứ tự | Phạm vi | Lý do |
|---:|---|---|
| 1 | Mark integration test và document prerequisite môi trường | Tạo baseline test đáng tin cậy ngay lập tức |
| 2 | Định nghĩa result/status contract và implement `PipelineRunner` | Tạo control point cho các enhancement tiếp theo |
| 3 | Thêm health gate, exception handling, exit code và service test | Làm behavior execution rõ ràng và có thể automation |
| 4 | Implement bootstrap thật và central settings | Loại bỏ các giả định môi trường ẩn |
| 5 | Thêm Bronze audit, retry, strict mode và incremental idempotency | Bảo vệ ingestion và rerun |
| 6 | Đóng gói Silver/Gold và biến validation thành gate bắt buộc | Đưa các script hiện tại vào cùng một lifecycle |
| 7 | Thay destructive Gold publish bằng staging/publish | Bảo vệ dataset Gold đang được sử dụng |
| 8 | Thêm observability, CI và runbook | Làm solution dễ vận hành trong môi trường shared/scheduled |

## Definition of Done cho Phase 4

- [ ] Có một command được document để chạy Sales pipeline cần thiết.
- [ ] Health/readiness failure ngăn downstream processing không an toàn.
- [ ] Mỗi stage trả standard result gồm status, count, duration và error.
- [ ] Silver và Gold validation được thực thi như pipeline gate.
- [ ] Bronze load có audit history và behavior rerun rõ ràng.
- [ ] Gold publish không xóa dataset hợp lệ cuối cùng khi build fail.
- [ ] Unit test chạy không cần external service; integration test được mark và document rõ ràng.
- [ ] CI chạy các command test, lint, format và type-check đã thống nhất.
- [ ] Tài liệu vận hành và checklist này phản ánh đúng behavior đã implement.

## Nhật ký bằng chứng

| Ngày | Hạng mục | Kết quả | Evidence |
|---|---|---|---|
| 2026-09-03 | Review branch và worktree | `Enhance_Project` tại `f6a681a`; worktree sạch | Git branch/status review |
| 2026-09-03 | Baseline test | `31 passed, 3 failed` | `pytest -q` |
| 2026-09-03 | Môi trường database | PostgreSQL unavailable tại `localhost:5432`; Docker daemon unavailable | PostgreSQL connection errors và `docker compose ps` |
