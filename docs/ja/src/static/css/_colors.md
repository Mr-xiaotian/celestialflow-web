# src/celestialflow_web/static/css/_colors.css

> 📅 最終更新日: 2026/09/24

Web UI が使用するグローバルな色彩システム変数を定義します。CSS Variables (`:root`) に基づいて実装され、一元的な管理とテーマ切り替えを容易にします。

## 色彩体系

プロジェクトはマルチカラースケール設計を採用しており、各色系統には 50 から 900 までの複数の色階が含まれます。

### コア色系統

- **霜白 (Frost)**: `--frost-0` (#ffffff)。背景および純白の要素に使用します。
- **カーボンブラック (Carbon)**: `--carbon-50` ~ `--carbon-900`。文字、枠線、影、ダークモードの背景に使用します。
- **翡翠緑 (Jade)**: `--jade-50` ~ `--jade-900`。成功状態、プログレスバー、ポジティブなフィードバックに使用します。
- **深紅 (Crimson)**: `--crimson-50` ~ `--crimson-900`。エラー状態、異常アラート、ネガティブなフィードバックに使用します。
- **マリーゴールド黄 (Marigold)**: `--marigold-50` ~ `--marigold-900`。重複タスク、警告、中性状態に使用します。
- **ヤグルマギク青 (Cornflower)**: `--cornflower-50` ~ `--cornflower-900`。実行中状態、リンク、主要な操作ボタンに使用します。

### 補助色系統

- **アンバー橙 (Amber)**: `--amber-50` ~ `--amber-900`。
- **ローズ赤 (Rose)**: `--rose-50` ~ `--rose-900`。
- **バイオレット (Violet)**: `--violet-50` ~ `--violet-900`。
- **スカイブルー (Sky)**: `--sky-50` ~ `--sky-900`。

## 使用方法

他の CSS ファイルから `var()` 関数で参照します:

```css
.example {
  color: var(--carbon-900);
  background-color: var(--jade-50);
  border: 1px solid var(--cornflower-500);
}
```

## 設計規範

- **文字色**: デフォルトでは `--carbon-900` (ライトモード) または `--carbon-200` (ダークモード) を使用します。
- **枠線色**: 一般的に `--carbon-200` または `--carbon-300` を使用します。
- **状態色**:
  - 成功: `Jade`
  - エラー: `Crimson`
  - 重複: `Marigold`
  - 実行: `Cornflower`
  - 待機/停止: `Carbon`
