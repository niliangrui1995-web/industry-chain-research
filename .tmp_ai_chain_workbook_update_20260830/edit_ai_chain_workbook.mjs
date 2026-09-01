import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const workbookPath = "D:/vcp_hunter/产业链投研/watchlists/AI产业链.xlsx";
const outputDirectory = "D:/vcp_hunter/产业链投研/outputs/20260830-ai-chain-code-update";
const outputPath = `${outputDirectory}/AI产业链.xlsx`;
const input = await FileBlob.load(workbookPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItem("AI产业链");
const codeCell = sheet.getRange("B241");
const before = codeCell.values;

if (before.length !== 1 || before[0]?.[0] !== "430139") {
  throw new Error(`目标单元格 B241 不是预期旧代码 430139：${JSON.stringify(before)}`);
}

codeCell.values = [["920139"]];
const after = codeCell.values;
if (after.length !== 1 || after[0]?.[0] !== "920139") {
  throw new Error(`工作簿写入后 B241 校验失败：${JSON.stringify(after)}`);
}

const verification = await workbook.inspect({
  kind: "table,computedStyle,match",
  sheetId: "AI产业链",
  range: "A238:E244",
  searchTerm: "430139|920139",
  options: { useRegex: true, maxResults: 20 },
  maxChars: 6000,
  tableMaxRows: 10,
  tableMaxCols: 5,
});
const preview = await workbook.render({
  sheetName: "AI产业链",
  range: "A238:E244",
  scale: 2,
  format: "png",
});

await fs.mkdir(outputDirectory, { recursive: true });
await fs.writeFile(`${outputDirectory}/verification.ndjson`, `${verification.ndjson}\n`, "utf8");
await fs.writeFile(`${outputDirectory}/AI产业链-B241-preview.png`, new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, before: before[0][0], after: after[0][0] }));
