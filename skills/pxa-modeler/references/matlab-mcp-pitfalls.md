# MATLAB / Simulink 操作踩過的坑

> pxa-modeler 的參考檔，補充 MathWorks 官方 skill，不取代它們。每一條都是實際
> 發生過的問題；新踩到的坑加在對應類別，並在 `CHANGELOG.md` 記一行。

## 1. 執行與 workspace
| 坑 | 做法 |
|---|---|
| 執行腳本檔的工具會把工作目錄換到腳本所在資料夾 | 專案腳本從專案根目錄以名稱呼叫 |
| 腳本開頭的 `clear all` 會清掉使用者的 base workspace | 執行前先說 |
| 探查用的暫時變數留在共用 workspace | 變數加前綴（例 `zz_`），結束時 clear |
| 模型參數 struct 從 base workspace 讀，測試與回放會跟使用者手上的值互相蓋掉 | 測試與回放用 `Simulink.SimulationInput` 的 `setVariable` / `setExternalInput` 帶入，不動 base；只有使用者要在桌面上手動跑時才寫 base，並確認是新值 |
| `StopTime` 是 `inf` 的模型跑不完，會卡住整個共用 session | 模擬前先查 `StopTime`，一律給有限值 |
| 模型開著時換工作目錄 | 不換；會弄壞 harness 快取 |
| 別的 session 可能同時用同一個 MATLAB | 只關自己載入的模型（`close_system(name, 0)`），不用 `bdclose all` |
| 測試執行工具會快取函式 | 改了被測函式後 `clear functions` 再跑 |

## 2. 模型編輯工具做不到、要用 MATLAB 指令補的
`new_system` / `save_system`、MATLAB Function 的程式碼與埠型別、Bus Element 共用埠、
Selector 多維索引、Area 註解（`add_block("built-in/Area", …)`）、`BlockMirror`、
`ReferenceBlock`、mask（`Simulink.Mask`）。用到時在對話中逐條列出。

- 設定 `Position` 會重設翻面，`BlockMirror` 放最後做。
- 模型編輯工具不存檔，收尾要 `save_system`。

## 3. Library
| 坑 | 做法 |
|---|---|
| harness 載入或 `open_system` 後 library 會自己上鎖 | 編輯前 `set_param(lib, "Lock", "off")` |
| 使用者也會手動編輯 | 動手前看 `Lock` 與 `Dirty` |
| 在 library 內 `add_block` 複製出的是 link | 把 `LinkStatus` 設為 `none` |
| 要改 link 指向 | `set_param(blk, "ReferenceBlock", …)` |

## 4. Mask
| 坑 | 做法 |
|---|---|
| 重建 mask 時殘留舊內容 | 先清 Display 與 Initialization，再移除參數 |
| icon 文字的 `\newline`、`\times` 被吃掉 | 用字元串接，不用 `sprintf` |
| library 加 mask 後 harness 沒更新 | harness 關掉重開 |
| 警告 `Unrecognized … 'iconText'` | mask 初始化呼叫的函式不在 path 上 |

## 5. 線性化
| 坑 | 做法 |
|---|---|
| 有 Transport Delay 時 `findop` 的穩態 trim 解不出 | 用模擬快照當操作點 |
| Saturation 預設 Treat as gain，飽和中的方塊給錯的小訊號增益 | 逐塊檢查 `LinearizeAsGain` |
| 非線性小階躍比對時階躍被內插成斜坡 | 用重複時間戳做出真階躍 |

## 6. 排版
| 坑 | 做法 |
|---|---|
| 自動排版做不出「回授翻面在下」 | 用 `model_edit` 的 `configure Position` 逐塊放置（`layout_mode` 用 `incremental`） |
| 自動走線把分支全疊在源頭 | 逐支重接 |
| 自動排版會打亂使用者手排的圖 | 先備份，複製手排方塊再改差異 |

建完用 `print -s` 輸出圖檔檢視版面。

## 7. 記錄與回放
| 坑 | 做法 |
|---|---|
| Root Outport 的 `yout` 元素以線名命名 | 進 Outport 的線要命名 |
| Inport 預設內插，回放變成斜坡 | 關掉 Interpolate 才是 ZOH |
| 最後一筆資料沒被模擬到 | `StopTime` 設最後一筆時間再加一步 |
| HIL log 同一個 topic 有多個 instance，其中有模擬器給的假裝置（定值） | 先逐個 instance 看數值與取樣間隔，確認哪個是真量測再用 |
| log 欄位存在但全是 0 | 不代表有量測；使用前看數值分布 |

## 8. 規格書數位化
| 坑 | 做法 |
|---|---|
| 檔名含不換行空白，工具打不開 | 先複製成普通檔名（原檔不動） |
| 圖有 soft mask，抽出來是黑底 | 先合成到白底 |
| 向量圖 | 直接讀路徑頂點，不必影像描點 |
| Windows 路徑寫進 Python 一般字串，`\b`、`\a` 變控制字元 | 一律用 raw string |

## 9. 單位與測試
| 坑 | 做法 |
|---|---|
| `convforce` 沒有 kgf | gf → N 用 `g0 = 9.80665`（ISO 80000-3）並註明 |
| `verifyEqual` 的診斷字串位置 | 放在 `AbsTol=` / `RelTol=` 之前 |
| 測試檔找不到資料 | 路徑用 `mfilename("fullpath")` 組 |
