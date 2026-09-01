import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const originalPath = "D:/vcp_hunter/产业链投研/watchlists/AI产业链.xlsx";
const exportedPath = "D:/vcp_hunter/产业链投研/outputs/20260830-ai-chain-code-update/AI产业链.xlsx";

async function readWorkbook(path) {
  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
  const sheet = workbook.worksheets.getItem("AI产业链");
  const usedRange = sheet.getUsedRange();
  return {
    workbook,
    values: usedRange.values,
    formulas: usedRange.formulas,
    rangeAddress: usedRange.address,
  };
}

const original = await readWorkbook(originalPath);
const exported = await readWorkbook(exportedPath);
if (original.rangeAddress !== "A1:E394" || exported.rangeAddress !== "A1:E394") {
  throw new Error(`导出后工作表已用范围不一致：${original.rangeAddress} -> ${exported.rangeAddress}`);
}
const differences = [];
for (let row = 0; row < original.values.length; row += 1) {
  for (let column = 0; column < original.values[row].length; column += 1) {
    const before = original.values[row][column];
    const after = exported.values[row][column];
    const beforeFormula = original.formulas[row][column];
    const afterFormula = exported.formulas[row][column];
    if (JSON.stringify(before) !== JSON.stringify(after) || beforeFormula !== afterFormula) {
      differences.push({ cell: `${String.fromCharCode(65 + column)}${row + 1}`, before, after, beforeFormula, afterFormula });
    }
  }
}
if (differences.length !== 1 || differences[0]?.cell !== "B241" || differences[0]?.before !== "430139" || differences[0]?.after !== "920139") {
  throw new Error(`导出语义差异不止目标代码：${JSON.stringify(differences.slice(0, 10))}`);
}
console.log(JSON.stringify({ range: exported.rangeAddress, differences }));
