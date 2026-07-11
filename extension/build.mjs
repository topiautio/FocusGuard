import { build } from "esbuild";
import { copyFile, mkdir } from "node:fs/promises";

await mkdir("dist", { recursive: true });
await Promise.all([
  build({ entryPoints: ["src/content.ts"], bundle: true, outfile: "dist/content.js", format: "iife", target: "es2022" }),
  build({ entryPoints: ["src/options/options.ts"], bundle: true, outfile: "dist/options.js", format: "iife", target: "es2022" }),
]);
await Promise.all([
  copyFile("public/manifest.json", "dist/manifest.json"),
  copyFile("src/options/options.html", "dist/options.html"),
]);
