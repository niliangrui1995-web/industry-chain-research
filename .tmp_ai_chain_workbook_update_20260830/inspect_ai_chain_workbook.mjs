import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const workbookPath = "D:/vcp_hunter/产业链投研/watchlists/AI产业链.xlsx";
const outputDirectory = "D:/vcp_hunter/产业链投研/.tmp_ai_chain_workbook_update_20260830";
const input = await FileBlob.load(workbookPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const summary = await workbook.inspect({
  kind: "workbook,sheet,table,computedStyle",
  sheetId: "AI产业链",
  range: "A1:F20",
  maxChars: 8000,
  tableMaxRows: 20,
  tableMaxCols: 6,
});
const matches = await workbook.inspect({
  kind: "match",
  searchTerm: "430139|920139",
  options: { useRegex: true, maxResults: 20 },
  maxChars: 4000,
});
const preview = await workbook.render({
  sheetName: "AI产业链",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDirectory}/workbook-inspect.ndjson`, `${summary.ndjson}\n${matches.ndjson}\n`, "utf8");
await fs.writeFile(`${outputDirectory}/workbook-preview.png`, new Uint8Array(await preview.arrayBuffer()));
