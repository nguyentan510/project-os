#!/usr/bin/env node
// npx -y project-os [--all] [--dry-run] [--uninstall] [--dir <chỗ>]
// Lớp mỏng: chọn install.ps1 (Windows) hoặc install.sh (còn lại) và chuyển tham số.
// Luôn cài từ bản clone ở ~/project-os (PROJECT_OS_CLONE=1), không từ thư mục tạm của npx.
"use strict";
const { spawnSync } = require("child_process");
const path = require("path");

const root = path.resolve(__dirname, "..");
const args = process.argv.slice(2);
const env = { ...process.env, PROJECT_OS_CLONE: "1" };

if (args.includes("-h") || args.includes("--help")) {
  console.log("project-os [--all] [--dry-run] [--uninstall] [--dir <thư-mục-clone>]");
  process.exit(0);
}

let cmd, cmdArgs;
if (process.platform === "win32") {
  const map = { "--all": "-All", "--dry-run": "-DryRun", "--uninstall": "-Uninstall", "--dir": "-Dir" };
  // Đọc file theo UTF-8 rồi chạy như scriptblock: -File trên PowerShell 5.1 đọc file không BOM theo ANSI,
  // làm hỏng dấu tiếng Việt và cú pháp.
  const q = (s) => `'${String(s).replace(/'/g, "''")}'`;
  const psArgs = args.map((a) => (map[a] ? map[a] : q(a))).join(" ");
  const script = path.join(root, "install.ps1");
  cmd = "powershell.exe";
  cmdArgs = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
    `& ([scriptblock]::Create([IO.File]::ReadAllText(${q(script)}, [Text.Encoding]::UTF8))) ${psArgs}`];
} else {
  cmd = "bash";
  cmdArgs = [path.join(root, "install.sh"), ...args];
}

const r = spawnSync(cmd, cmdArgs, { stdio: "inherit", env });
if (r.error) {
  console.error(`Không chạy được ${cmd}: ${r.error.message}`);
  process.exit(1);
}
process.exit(r.status === null ? 1 : r.status);
