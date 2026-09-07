# Study Log API

一個使用 FastAPI 與 SQLite 建立的讀書紀錄 API。

## 功能

- 新增讀書紀錄
- 查詢全部讀書紀錄
- 查詢單一讀書紀錄
- 依讀書科目篩選
- 依最低讀書分鐘數篩選
- 依讀書科目統計
- 可同時使用兩個篩選條件
- 刪除指定讀書紀錄
- 使用 SQLite 保存資料，伺服器重新啟動後仍會保留
- 使用 pytest 測試新增、查詢、篩選、刪除與驗證規則 
- 查詢總讀書次數、總分鐘數與平均分鐘數
- 修改指定讀書紀錄的分鐘數

## 安裝

在專案根目錄執行：

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

## 啟動

在專案根目錄執行：

```bash
./.venv/bin/python -m uvicorn main:app --reload --port 8034
```

開啟 API 文件：

```text
http://127.0.0.1:8034/docs
```

## API 端點

| 方法   | 路徑                                                   | 功能                                               |
|--------|--------------------------------------------------------|----------------------------------------------------|
| POST   | `/api/v1/study-sessions`                               | 新增讀書紀錄                                       |
| GET    | `/api/v1/study-sessions`                               | 查詢讀書紀錄；可使用 `subject`、`min_minutes` 篩選 |
| GET    | `/api/v1/study-sessions?subject=Python`                | 依讀書科目篩選                                     |
| GET    | `/api/v1/study-sessions?min_minutes=30`                | 依最低分鐘數篩選                                   |
| GET    | `/api/v1/study-sessions?subject=Python&min_minutes=30` | 同時使用兩個篩選條件                               |
| GET    | `/api/v1/study-sessions/{session_id}`                  | 查詢單一讀書紀錄                                   |
| GET    | `/api/v1/study-sessions/by-subject`                    | 依讀書科目統計                                     |
| GET    | `/api/v1/study-sessions/summary`                       | 查詢讀書統計                                       |
| DELETE | `/api/v1/study-sessions/{session_id}`                  | 刪除指定讀書紀錄                                   |
| PATCH | `/api/v1/study-sessions/{session_id}/minutes` | 修改讀書分鐘數 |

## 資料庫

資料儲存在本機 SQLite `study_sessions.db`。

`study_sessions.db` 與測試用的 `test_study_session.db` 都不會提交到 GitHub；執行 API 或測試時會自動建立。

## 測試

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 ./.venv/bin/python -m pytest test/test_main.py -v
```