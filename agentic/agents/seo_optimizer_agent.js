#!/usr/bin/env node
const fs = require("fs");
const matter = require("gray-matter");

const [briefPath, draftPath] = process.argv.slice(2);
if (!briefPath || !draftPath) {
  console.error("Usage: node seo_optimizer_agent.js <brief.json> <page.md>");
  process.exit(2);
}

const brief = JSON.parse(fs.readFileSync(briefPath, "utf8"));
const raw = fs.readFileSync(draftPath, "utf8");
const { data: frontMatter, content } = matter(raw);
const findings = [];

const h1Match = content.match(/^#\s+(.+)$/m);
if (!h1Match || h1Match[1].trim() !== brief.required_h1) {
  findings.push({ level: "error", check: "H1", detail: `Expected "${brief.required_h1}", found "${h1Match ? h1Match[1].trim() : "(none)"}"` });
} else {
  findings.push({ level: "pass", check: "H1", detail: "Matches brief." });
}

const desc = frontMatter["meta-description"] || frontMatter["description"] || "";
if (!desc) {
  findings.push({ level: "error", check: "meta-description", detail: "Missing meta-description." });
} else if (desc.length > brief.meta_description_max_chars) {
  findings.push({ level: "error", check: "meta-description", detail: `${desc.length} chars, over ${brief.meta_description_max_chars} limit.` });
} else {
  findings.push({ level: "pass", check: "meta-description", detail: `${desc.length} chars — within limit.` });
}

const first100 = content.split(/\s+/).slice(0, 100).join(" ").toLowerCase();
const kwWords = brief.target_keyword.toLowerCase().split(" ");
const kwPresent = kwWords.every((w) => first100.includes(w));
findings.push({ level: kwPresent ? "pass" : "warning", check: "target keyword", detail: kwPresent ? `"${brief.target_keyword}" present early.` : `"${brief.target_keyword}" not clearly present early on.` });

const proofPresent = content.includes(brief.proof_anchor.slice(0, 30));
findings.push({ level: proofPresent ? "pass" : "error", check: "proof anchor", detail: proofPresent ? "Present." : "Required proof anchor from the brief is missing." });

const errors = findings.filter((f) => f.level === "error");
console.log(`\nSEO OPTIMIZER — ${draftPath}`);
findings.forEach((f) => console.log(`  [${f.level.toUpperCase()}] ${f.check}: ${f.detail}`));

if (errors.length > 0) {
  console.log(`\n❌ SEO CHECK FAILED — ${errors.length} issue(s)\n`);
  process.exit(1);
}
console.log(`\n✅ SEO CHECK PASSED\n`);
process.exit(0);