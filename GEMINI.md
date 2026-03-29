# Workspace Mandates

所有生成或修改的 Markdown 檔案必須嚴格遵循 **Obsidian Flavored Markdown (OFM)** 語法。

## 核心規範

1.  **自動啟用技能**：處理任何 `.md` 檔案時，必須先執行 `activate_skill(name="obsidian-markdown")` 以獲取完整規範。
2.  **內部連結**：
    -   必須使用 Wikilinks 格式：`[[檔案名稱]]` 或 `[[檔案名稱|顯示文字]]`。
    -   禁止對內部檔案使用標準 Markdown 連結 `[text](file.md)`。
3.  **屬性 (Frontmatter)**：
    -   所有新檔案必須包含 YAML frontmatter，包含 `tags`、`aliases` 及相關 metadata。
4.  **標註與嵌入**：
    -   使用 Obsidian Callouts 語法：`> [!type] Title`。
    -   使用 `![[檔案名稱]]` 進行內容或圖片嵌入。
5.  **特殊格式**：
    -   使用 `==文字==` 進行螢光筆標記。
    -   支援 LaTeX 數學公式：`$inline$` 或 `$$block$$`。
    -   支援 Mermaid 圖表。

## 寫作風格

-   優先考慮雙向連結 (Backlinks) 的結構化。
-   確保筆記在 Obsidian 閱讀模式下渲染正確。
