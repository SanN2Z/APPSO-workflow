"use strict";

const fs = require("fs");
const vm = require("vm");

const [rendererPath, inputPath, outputPath, htmlPath] = process.argv.slice(2);
if (!rendererPath || !inputPath || !outputPath || !htmlPath) {
  throw new Error("usage: node render_with_extension.js <renderer> <input.json> <output.json> <output.html>");
}

const rendererSource = fs.readFileSync(rendererPath, "utf8");
vm.runInThisContext(rendererSource, { filename: rendererPath });

const reader = globalThis.IFANR_FEISHU_PAGE_READER;
if (!reader || typeof reader.buildFixture !== "function") {
  throw new Error("locked extension renderer did not expose buildFixture");
}

const input = JSON.parse(fs.readFileSync(inputPath, "utf8"));
const result = reader.buildFixture(input);
const html = String(result.html || "");
delete result.html;
fs.writeFileSync(htmlPath, html, "utf8");
fs.writeFileSync(outputPath, JSON.stringify(result), "utf8");
