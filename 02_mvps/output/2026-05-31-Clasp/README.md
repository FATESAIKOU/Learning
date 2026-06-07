# clasp + Google Apps Script 操作筆記

## 1. 安裝與認證

```bash
npm install -g @google/clasp
clasp login --redirect-port 8899
```

執行後會跳出瀏覽器視窗（或產出授權 URL），登入目標 Google 帳號並同意授權即可。

> 若想手動輸入授權 URL：`clasp login --no-localhost`

## 2. 專案初始化

```bash
# 在新的目錄中建立專案（會自動將現有目錄內容上傳）
clasp create --type standalone --title "專案名稱"
```

> 若已有現成專案想拉下來（逆向初始化）：`clasp clone <scriptId>`

`appsscript.json` 若需部署為網頁應用，需加入 `webapp` 區塊：

```json
{
  "timeZone": "Asia/Taipei",
  "dependencies": {},
  "webapp": {
    "access": "MYSELF",
    "executeAs": "USER_DEPLOYING"
  },
  "exceptionLogging": "STACKDRIVER",
  "runtimeVersion": "V8"
}
```

## 3. 上傳程式碼

```bash
clasp push        # 增量上傳
clasp push --force  # 強制全量上傳
```

上傳前可用 `clasp status` 查看哪些檔案會被追蹤。

## 4. 控管部署

```bash
clasp deploy --description "版本描述"  # 建立新部署版本
clasp deployments                       # 列出所有部署版本
```

部署後的 Web App 網址格式為：
`https://script.google.com/macros/s/<deploymentId>/exec`

### access 權限設定說明

| 值 | 說明 |
|---|---|
| `MYSELF` | 僅部署者本人可存取 |
| `ANYONE` | 任何人皆可存取 |
| `DOMAIN` | 同網域使用者可存取 |

> 注意：首次透過 API 建立專案前，需先到 https://script.google.com/home/usersettings 啟用「Google Apps Script API」。
