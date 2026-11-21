---
name: pxa-matlab-style
description: PXA 系列的 MATLAB 撰碼風格。凡是撰寫、修改、重構、審查或統一 MATLAB m-file（腳本、函式、參數 preset、trim / 線性化 / 控制設計、log 回放與分析、Simulink 批次模擬、繪圖與報告匯出）的風格、命名、版面、檔頭，都要先讀本 skill，即使使用者沒有點名。不適用於 MATLAB / Simulink App 自動產生的程式（Control System Tuner 等），也不處理 m-file 轉 C/C++。
argument-hint: "[選填：要寫或要統一風格的 .m 檔]"
---

# pxa-matlab-style：MATLAB 撰碼風格 v0.2

> 📋 版本變更見 `CHANGELOG.md`。
> 以 MathWorks MATLAB Coding Guidelines 為底，本檔是 PXA 的慣例，衝突時以本檔為準。
> 專案 `CLAUDE.md` 的授權與寫入流程（寫入清單、確認、版本控制）優先於本檔。
> 程式須相容專案指定的 MATLAB 版本；`Name=Value` 語法需要 R2021a 以上。

## 0. 適用範圍：先分類，再動手

| 類別 | 說明 | 處理 |
|---|---|---|
| 1 | 使用者自己寫的 | 套用本檔；**只改風格，不改邏輯** |
| 2 | 使用者寫好、Claude 協助修改 | 套用本檔 |
| 3 | Claude 完全產出 | 套用本檔（新程式一律從本檔出發） |
| 4 | MATLAB / Simulink App 自動產生 | **不動**。辨識特徵：位於 `tuner\` 資料夾、開頭為 `%% Create system data with slTuner interface`、由 App 的 Generate Script 匯出 |

無法判斷屬於哪一類時，先問使用者，不要猜。

## 1. 版面

| 項目 | 規則 |
|---|---|
| 行寬 | ≤ 75 字元（含檔頭）；超過就用 `...` 斷行，續行縮排 4 格 |
| 斷行位置 | 運算子、逗號留在上一行的行尾；字串用 `+` 接續 |
| 縮排 | 4 個空格，不用 tab |
| 分段 | 只用 `%%`（§3） |
| 子標題 | 純註解，以空行分組；**禁用** `% ====`、`% ----`、`% --- x ---`、`% ***` 等 banner 或框線 |
| 註解位置 | 一律放在程式碼上一行；**禁止行尾註解** |
| 單位標註 | 寫在上一行註解的結尾：`% <description>, <unit>` |
| 註解語言 | 英文 |
| 一行一敘述 | 原則上一行只寫一個敘述；例外見 §5 case table，以及檔頭的清除指令 |
| 空白 | 逗號後空一格；`=`、關係運算子、邏輯運算子兩側各空一格；`:` `*` `/` `^` 不留空白；括號內側不留空白 |

## 2. 檔頭

檔頭是檔案的規格。欄位順序固定，用不到的欄位整段省略，不留空欄。

### 2.1 腳本

```matlab
%% <Project> <Subject> <Purpose>
%
% Strategy: <what the script does and why it is done this way; the
%   quantities held constant, the cases compared, what is saved>
%
% Per MathWorks guidance:
%   "<sentence quoted from the documentation>"
%   Ref: <page title> (MathWorks <product>)
%
% Sources:
%   <data sheet / paper / log, with revision or date>
%
% Assumptions:
%   <name> = <value and where it comes from>
%
% Inputs:
%   <files read>
%
% Outputs:
%   <files written>
%
% Workflow:
%   1. <step name>
%   2. <step name>
%
% Model:     <Simulink models used>
% Author:    <name>
% Modified:  YYYY-MM-DD HH:MM:SS (GMT+8)
%   - <this change only>
%
% Copyright <year> <organization>

clear all; close all; clc

%% Initialization
```

| 欄位 | 規則 |
|---|---|
| 第一行 | `%%` 加標題，Title Case |
| `Strategy` | 必要。寫做法與理由，不重複 Workflow 的步驟名稱 |
| `Per MathWorks guidance` | 只在本次對話實際讀過該文件頁時才引用原句並附頁名；否則整段省略，不憑記憶引用 |
| `Sources` / `Assumptions` / `Inputs` / `Outputs` | 依腳本性質選用：參數 preset 寫 Sources，回放與分析寫 Inputs / Outputs，獨立模擬寫 Assumptions |
| `Workflow` | 必要。編號與本文的 `%% Step N:` 一一對應 |
| `Modified` | 時間到秒並標時區；只列本次變更，舊條目刪除（歷史在版本控制裡） |
| `Copyright` | 最後一列；年份與單位名稱照專案既有檔案 |

### 2.2 函式檔

```matlab
function [out1, out2] = <project>_<domain>_<purpose>(in1, in2, options)
%<FUNCTION_NAME> <One-line summary>
%
% Strategy: <only when the method needs explaining>
%
% Syntax:
%   [out1, out2] = <function_name>(in1, in2)
%   [out1, out2] = <function_name>(___, Name=Value)
%
% Inputs:
%   in1    <size and meaning, unit>
%
% Name-Value arguments:
%   Name   <meaning, unit>
%
% Outputs:
%   out1   <size and meaning, unit>
%
% Note: <side effects, e.g. set_param leaves the model unsaved>
%
% See also <related functions>
%
% Model:     <Simulink models used>
% Author:    <name>
% Modified:  YYYY-MM-DD HH:MM:SS (GMT+8)
%   - <this change only>
%
% Copyright <year> <organization>

arguments
    in1 (1, :) cell
    in2 (1, :) double {mustBePositive}
    options.Name (1, 1) double {mustBePositive} = 10
end
```

- H1 行的函式名用大寫；`arguments` 區塊緊接檔頭，選用參數一律走 `options.Name`。
- `arguments` 驗不了的條件（例如各輸入長度要相等）在區塊後用 `error` 檢查。
- 函式會改動外部狀態（已載入的模型、檔案）時，必須寫在 `Note`。

### 2.3 Local function

```matlab
function [v, nPoint] = curveOnGrid(curves, label, qGrid, nMin)
%curveOnGrid Resample one digitized curve on the charge grid.
%
%   Inputs:
%       curves - table with label, mAh, V
%       qGrid  - charge grid, mAh
%
%   Outputs:
%       v      - voltage on qGrid, NaN outside the curve, V
```

H1 行照函式名原樣；三行以內說得完的小函式只留 H1 與一段說明，不列 Inputs / Outputs。

## 3. 分段

| 段落 | 規則 |
|---|---|
| `%% Initialization` | 第一段：檔案路徑、模型名稱、開關（`flag.<name>`）、常數、繪圖預設 |
| `%% Step N: <name>` | 主流程；編號與名稱對應檔頭 Workflow。步驟在迴圈內時也照寫，縮排跟著迴圈 |
| `%% Local Functions` | 最後一段 |

- 需要逐段執行、反覆調整的設計腳本，段名可用描述句代替 `Step N`，但順序仍須對應 Workflow。
- 清除指令只出現在檔頭之後一次；本文中不再 `close all`、`clc`。

## 4. 等號對齊（硬性偏好）

連續的設定成組對齊，組與組之間空一行。

```matlab
% Model variant flags
flag.hil    = 0;
flag.servo  = 0;
flag.motor  = 0;

% Total mass, kg
init.mass = 24.75;
% Center of gravity, body FRD, m
init.cg   = [-0.52829 0.0 -0.02888];
```

- 同一組 = 連續、沒有空行隔開的設定（中間可以夾上一行註解）
- 對齊到該組最長的左值，`=` 前至少空一格
- 結構陣列逐欄寫入、迴圈開頭展開欄位、結果收集都要對齊

## 5. 資料表

### 5.1 Case table

依欄位數量選寫法，兩種都要對齊。欄位定義（名稱、單位、意義）統一寫在表格上方的註解區塊。

**欄位少（一行寫得下且 ≤ 75 字元）**：一行一個 case，欄位之間用 `;` 隔開並縱向對齊。這是「一行一敘述」的唯一例外。

```matlab
cases(1).mode = "hover";   cases(1).VXN = 0;   cases(1).VZN =  0;
cases(2).mode = "climb";   cases(2).VXN = 0;   cases(2).VZN = -3.0;
```

**欄位多**：一欄一行，每個 case 一組，case 之間空一行。

```matlab
cases(1).name  = "ocv_bms";
cases(1).soc0  = soc0Ocv;
cases(1).label = "SOC_0 from OCV, BMS current";

cases(2).name  = "log_bms";
cases(2).soc0  = soc0Log;
cases(2).label = "SOC_0 = log remaining, BMS current";
```

> 待決（b）：欄位少的寫法中，每列 case 的說明要放在哪裡。決定前，放在該列上一行。

### 5.2 數值表與文字表

量測表、規格表直接寫成矩陣，欄位縱向對齊，欄位意義與單位寫在上方註解；寫完立刻拆成具名欄位，後面不用欄號取值。

```matlab
% Columns: commanded voltage V, supply current A, speed rpm
benchData = [ ...
     2.0   0.1   180
    10.0   0.5  1020
    56.0  38.7  5370];
bench.cmdVoltage = benchData(:, 1);
bench.iSupply    = benchData(:, 2);
bench.rpm        = benchData(:, 3);
```

名稱、說明、預設值這類文字表用 string 矩陣，一列一項，再用迴圈取用。

### 5.3 參數 struct

- 以元件型號命名、扁平一層（`<model>.<field>`）；每個欄位上一行註解寫意義、單位、來源。
- 沒有來源、假設或待量測的值，在註解標 `<?>` 並寫明原因，例如
  `% Rotor inertia, kg*m^2 (not in datasheet, <?> to be measured)`。
- 來源資料（規格書表格、量測表）原樣保留在 struct 裡，另存推導後的表；推導完用 `table` 顯示推導誤差。
- 多個 preset 共用一個 `.mat` 時，檔案存在就 `save(file, "<name>", "-append")`。

## 6. 迴圈

### 6.1 Iterator 命名：`index<Meaning>`

```matlab
for indexCase = 1:numel(runCases)
    for indexAxis = 1:nAxis
        ...
    end
end
```

- **不用** `i`、`j`、`k`、`m`、`ir`、`ic`、`idx`
- 迴圈次數用 `n<Things>`，例如 `nAxis`、`nGain`
- 迴圈前要 pre-allocate；巢狀不超過 5 層；不在迴圈內修改 iterator

### 6.2 迴圈開頭展開欄位

```matlab
for indexCase = 1:nCase
    name  = cases(indexCase).name;
    soc0  = cases(indexCase).soc0;
    input = cases(indexCase).input;

    %% Step 4: Run the replay case
    ...
end
```

### 6.3 結果收集

逐欄寫入 struct array，`=` 對齊；先用 `struct("field", cell(1, n), ...)` 建好欄位。

```matlab
results(indexCase).name     = name;
results(indexCase).soc0     = soc0;
results(indexCase).vBus     = yout.get("V_bus").Values.Data;
results(indexCase).datetime = datetime("now", TimeZone=timeZone);
```

## 7. switch

每個 case 都換行縮排，即使只有一行；case 之間空一行；必須有 `otherwise` 並呼叫 `error`。

```matlab
switch reSource
    case "datasheet"
        motor.Re = motor.ReDatasheet;

    case "bench"
        motor.Re = motor.ReBench;

    otherwise
        error("Unknown reSource: %s", reSource)
end
```

## 8. 字串與 Name-Value

- 字串一律用 `"`，**既有檔案也要統一改**；組字串用 `+`，數值會自動轉字串。
- Name-Value 一律用 `Name=Value`，包含 `struct(Ns=14, Np=4)`。
- 例外：API 規定要 char 時（mask 的 Initialization / callback 字串內容、`set_param` 讀回的 cell 陣列、少數舊函式）保留 `'...'` 或 `char(...)`，並在上一行註解說明。
- 多行文字（寫入檔案的報告、mask 程式碼）用 string 陣列一列一行，最後 `strjoin(lines, newline)` 或 `writelines`。

## 9. 單位、常數、座標轉換：能用 Toolbox 函數就一律用

不寫 `57.3`、`9.81`、`0.5144` 這類魔術數字；有 Aerospace Toolbox 時一律優先使用它的函數。

| 需求 | 使用 |
|---|---|
| 角度 | `convang(x, "rad", "deg")` |
| 角速度 / rpm | `convangvel(x, "rad/s", "deg/s")`、`convangvel(x, "rpm", "rad/s")` |
| 加速度（g） | `convacc(x, "G's", "m/s^2")` |
| 速度 | `convvel(x, "kts", "m/s")` |
| 長度 | `convlength(x, "in", "m")` |
| 姿態 / DCM / 四元數 | `angle2dcm`、`dcm2angle`、`angle2quat`、`quat2angle` |
| 座標 | `lla2flat`、`flat2lla`、`ecef2lla` 等 |
| 大氣 / 重力 | `atmoscoesa`、`atmosisa`、`gravitywgs84` |

- 動筆前先確認函數**是否支援該單位**（例如 `convlength` 不支援 mm）。不支援時定義具名常數，上一行註解寫出換算方向、單位與來源：

```matlab
% s to ms
sToMs = 1e3;
% Standard gravity for gram-force to newton (ISO 80000-3), m/s^2
g0    = 9.80665;
```

- 門檻、容差、步長、解析度等調整值同樣定義成具名常數並附單位，不直接寫在式子裡。
- 內部運算維持 SI（rad）；顯示和繪圖用 deg、deg/s、m/s、m/s²。
- 控制與訊號處理同樣優先使用內建函數：`tf`、`ss`、`allmargin`、`bandwidth`、`stepinfo`、`linearize`、`pidtune`、`pwelch`、`designfilt`、`filtfilt` 等。捨棄常用函數改用另一個時（例如用 `allmargin` 取代 `margin`），在上一行註解寫原因。

## 10. 結果輸出：`disp(table)`

```matlab
summary = table(axisName(:), riseTime(:), overshoot(:), gm(:), pm(:), ...
    VariableNames=["Axis", "Rise_s", "OS_pct", "GM_dB", "PM_deg"]);
disp("Design summary: " + mode)
disp(summary)
```

- 欄名帶單位字尾（`_s`、`_pct`、`_N`、`_mOhm`）；列是指標、欄是軸或 case 時用 `RowNames`，單位寫在列名裡。
- 不用 `fprintf` 的 `=== 標題 ===` 區塊和手排欄寬；標題用 `disp` 一行。
- 進度與存檔訊息各一行：`disp("Processing " + key)`、`disp("saved " + outFile)`，或一行 `fprintf`。
- 同一張表要給多支腳本用（設計值與參考值並列）時，拆成共用函式產生，確保列定義只有一份。

## 11. 繪圖

| 項目 | 規則 |
|---|---|
| 樣式預設 | `%% Initialization` 用 `set(groot, Default...)` 設定一次，不在每個軸重複 `set(gca, ...)` |
| figure | `figure(Color="w", Units="centimeters", Position=figPosition)`，全腳本共用 `figPosition` |
| 子圖 | `tiledlayout(..., TileSpacing="compact", Padding="compact")` + `nexttile`，不用 `subplot` |
| 軸標籤 | 含單位：`Time (s)`、`Pitch rate (deg/s)` |
| 線型與顏色 | 顏色取 `lines(n)`；量測或 log 用黑色，模型用色線；同一對象的設計值實線、參考值虛線、同色 |
| legend | `Location="best"`；多通道、多 case 比較疊在同一張圖 |
| 匯出 | `exportgraphics(fig, file, Resolution=figResolution)`，解析度為具名常數 |

```matlab
% Plot defaults for every figure in this script
set(groot, DefaultAxesFontName="Century")
set(groot, DefaultAxesFontSize=12)
set(groot, DefaultAxesXGrid="on")
set(groot, DefaultAxesYGrid="on")
set(groot, DefaultLineLineWidth=1.5)
% Figure position shared by all figures, cm
figPosition = [13.00 3.28 28.00 21.00];
```

> 待決（a）：字體大小階層、標題與圖號的寫法尚未定案；上表其餘項目是現行做法。

## 12. 檔案、路徑、Simulink

| 項目 | 規則 |
|---|---|
| 路徑 | 先開 MATLAB Project。相對專案根目錄：`fullfile(".", "data", ...)` 或 `".\workspace\x.mat"`；要能從任意目錄執行的腳本，用 `fileparts(mfilename("fullpath"))` 往上推出根目錄。所有路徑在 `%% Initialization` 定義成變數 |
| 清除指令 | `clear all; close all; clc`；需要時才加 `clear mex`（Simulink 編譯快取或 S-function 問題），並在上一行註解寫明原因 |
| 存檔 | `save(file, "var1", "var2")` 明列變數；輸出資料夾不存在時先 `mkdir`；大型中間訊號存檔前先 `rmfield` 並註解原因 |
| 模擬 | `Simulink.SimulationInput` + `setVariable` / `setBlockParameter` / `setModelParameter(Name=Value)` / `setExternalInput`，不靠 base workspace 傳參數給新寫的模型 |
| 模型開關 | 載入前記下 `wasLoaded = bdIsLoaded(model)`，結束時只關自己載入的：`close_system(model, 0)`；不用 `bdclose all` |
| 改動模型 | `set_param` 改了已載入的模型而不存檔時，在檔頭 `Note` 寫明；改 library 要先解鎖、存檔後鎖回 |
| 輔助函式 | 只有一支腳本用：放檔尾 `%% Local Functions`；兩支以上共用：拆成獨立檔 |
| 匿名函數 | 不用匿名函數包裝重複呼叫；例外是求解器要的目標函數 handle（`lsqnonlin`、`fzero` 等），本體仍寫成 local function |
| 禁用 | `global`、`eval`、`evalin`、`assignin`、command syntax |
| 浮點比較 | 不用 `==`、`~=`，改用容差 |
| Code Analyzer | 警告要清光，不用行尾 `%#ok` 壓警告，而是改寫程式消除 |

## 13. 命名

| 對象 | 規則 |
|---|---|
| 檔名 / 函式檔 | `<project>_<domain>_<purpose>`，snake_case |
| 區域變數 | lowerCamelCase；物理符號可以用短名（`J`、`Q`、`Kt`、`VXN`、`tauT0`） |
| Iterator | `index<Meaning>`（§6.1） |
| 數量 | `n<Things>` |
| 邏輯變數 | `is` / `has` / `was` 開頭，例如 `isValid`、`hasTemp`、`wasLoaded` |
| 開關 | `flag.<name>`，0 / 1 |
| 檔案與資料夾 | `<what>File`、`<what>Dir` |
| figure / axes handle | `fig<What>`、`ax<What>` |
| Local function | 動詞片語 lowerCamelCase，≤ 32 字元；輸入 ≤ 6、輸出 ≤ 4 |
| 錯誤訊息 | `error("Unknown <thing>: %s", value)`，句首大寫，帶出問題值 |

## 14. 統一既有檔案的流程

1. 依 §0 分類；第 4 類直接跳過
2. 依專案 `CLAUDE.md` 列寫入清單，等使用者確認
3. 只改風格：檔頭、排版、引號、Name=Value、對齊、iterator 改名、註解位置、banner、單位換算函數化、`subplot` 改 `tiledlayout`、逐軸 `set(gca, ...)` 改 `groot` 預設
4. **不改邏輯**；遇到疑似 bug，只回報、不修
5. iterator 改名要確認整個作用域沒有撞名；被呼叫的腳本若以變數名讀取 workspace（例如 tuner 腳本讀 `sys`），那些名稱不能改
6. 魔術數字改成函數時，要確認數值等價（例如 `57.3` 和 `convang` 的差異約 0.004%，`rpm*pi/30` 與 `convangvel` 可能差在最後一位），必須告訴使用者結果會有微小差異
7. 寫完執行 Code Analyzer（`check_matlab_code`），警告不得比原本多
8. 回報版本控制的差異統計

## 待決事項

| # | 項目 |
|---|---|
| a | 繪圖：字體大小階層、標題與圖號的寫法 |
| b | case table 每列說明的位置 |
| c | 黃金範例檔（`golden_example.m`）尚未建立 |
