#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

const STYLE_DIR = path.join(__dirname, "..", "style", "styles", "ebis");

function fallbackLint(text) {
  const ruleFiles = fs.readdirSync(STYLE_DIR).filter((f) => f.endsWith(".yml"));
  const findings = [];
  for (const file of ruleFiles) {
    const rule = yaml.load(fs.readFileSync(path.join(STYLE_DIR, file), "utf8"));
    for (const token of rule.tokens) {
      const re = new RegExp(token, "gi");
      let m;
      while ((m = re.exec(text)) !== null) {
        findings.push({ rule: file.replace(".yml", ""), level: rule.level, message: rule.message.replace("%s", m[0]) });
      }
    }
  }
  return findings;
}

const targetFile = process.argv[2];
if (!targetFile) { console.error("Usage: node qa_gate.js <file>"); process.exit(2); }
const text = fs.readFileSync(targetFile, "utf8");
const findings = fallbackLint(text);
const errors = findings.filter((f) => f.level === "error");

console.log(`\nEDITORIAL QA GATE\nFile: ${targetFile}  Errors: ${errors.length}\n`);
findings.forEach((f) => console.log(`  [${f.level.toUpperCase()}] (${f.rule}) ${f.message}`));

if (errors.length > 0) {
  console.log("\n❌ QA GATE FAILED\n");
  process.exit(1);
}
console.log("\n✅ QA GATE PASSED\n");
process.exit(0);