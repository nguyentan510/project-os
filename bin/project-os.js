#!/usr/bin/env node
// npx -y @nguyentan0510/project-os [--global] [--dry-run] [--uninstall] [--dir <thư-mục>]
//
// Mặc định (theo dự án): chép skill vào thư mục hiện tại (hoặc --dir), để commit cùng repo:
//   <dự-án>/.agents/skills/project-os   Codex, Antigravity và các công cụ dùng chuẩn chung
//   <dự-án>/.claude/skills/project-os   Claude Code
// --global: cài vào thư mục home của các công cụ (ủy quyền cho install.sh / install.ps1).
"use strict";
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const PKG_ROOT = path.resolve(__dirname, "..");
const SRC = path.join(PKG_ROOT, ".agents", "skills", "project-os");
const MARKER = ".project-os-install";
const LOCATIONS = [
  [".agents", "skills", "project-os"],
  [".claude", "skills", "project-os"],
];
const VERSION = require(path.join(PKG_ROOT, "package.json")).version;

const HELP = `project-os — cài skill Project OS

  npx -y @nguyentan0510/project-os              cài vào dự án hiện tại (.agents/ và .claude/)
  npx -y @nguyentan0510/project-os --global     cài vào thư mục home của các công cụ AI

Tuỳ chọn:
  --dir <thư-mục>   cài vào thư mục này thay vì thư mục hiện tại
  --dry-run         chỉ in việc sẽ làm
  --uninstall       gỡ bản đã cài bằng lệnh này
  --global          cài toàn cục thay vì theo dự án
  -h, --help        trợ giúp`;

function parse(argv) {
  const o = { global: false, dry: false, uninstall: false, dir: process.cwd(), help: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--global") o.global = true;
    else if (a === "--dry-run") o.dry = true;
    else if (a === "--uninstall") o.uninstall = true;
    else if (a === "--dir") {
      if (!argv[i + 1]) fail("--dir cần đường dẫn");
      o.dir = path.resolve(argv[++i]);
    } else if (a === "-h" || a === "--help") o.help = true;
    else fail(`Tham số lạ: ${a}\n\n${HELP}`);
  }
  return o;
}

function fail(msg) {
  console.error(msg);
  process.exit(2);
}

function installedByUs(dst) {
  try {
    return fs.lstatSync(dst).isDirectory() && fs.existsSync(path.join(dst, MARKER));
  } catch {
    return false;
  }
}

function exists(p) {
  try {
    fs.lstatSync(p);
    return true;
  } catch {
    return false;
  }
}

function projectMode(o) {
  if (!fs.existsSync(path.join(SRC, "SKILL.md"))) {
    console.error(`Gói thiếu skill (${SRC}). Cài lại gói hoặc dùng --global.`);
    process.exit(1);
  }
  if (!fs.existsSync(o.dir) || !fs.statSync(o.dir).isDirectory()) fail(`Không có thư mục: ${o.dir}`);
  console.log(`Project OS · ${o.uninstall ? "gỡ" : "cài"} skill theo dự án · ${o.dir}`);

  let skipped = 0;
  for (const loc of LOCATIONS) {
    const dst = path.join(o.dir, ...loc);
    const rel = loc.join("/");
    if (o.uninstall) {
      if (installedByUs(dst)) {
        if (!o.dry) fs.rmSync(dst, { recursive: true, force: true });
        console.log(`  ${o.dry ? "[dry-run] sẽ gỡ" : "đã gỡ"}  ${rel}`);
      } else console.log(`  bỏ qua  ${rel} (không có, hoặc không phải do lệnh này tạo)`);
      continue;
    }
    const had = exists(dst);
    if (had && !installedByUs(dst)) {
      console.log(`  BỎ QUA  ${rel}: đã có thứ khác ở đó, không ghi đè. Xoá hoặc đổi tên nó rồi chạy lại.`);
      skipped++;
      continue;
    }
    if (o.dry) {
      console.log(`  [dry-run] sẽ ${had ? "làm mới" : "tạo"}  ${rel}`);
      continue;
    }
    if (had) fs.rmSync(dst, { recursive: true, force: true });
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    fs.cpSync(SRC, dst, { recursive: true });
    fs.writeFileSync(path.join(dst, MARKER), `${VERSION}\n`);
    console.log(`  ${had ? "làm mới" : "tạo"}  ${rel}`);
  }

  if (o.uninstall) return;
  console.log("\nXong. Khởi động lại công cụ AI nếu nó không thấy skill.");
  console.log("Gọi: Claude Code /project-os · Codex $project-os · Antigravity tự nhận.");
  console.log("Commit .agents/ và .claude/ để cả nhóm (và AI khác) cùng có skill; chạy lại lệnh này để cập nhật.");
  console.log("Bắt đầu: nói với AI \"Dùng skill project-os để bắt đầu dự án này\".");
  if (skipped) process.exitCode = 1;
}

function globalMode(o) {
  const env = { ...process.env, PROJECT_OS_CLONE: "1" }; // luôn cài từ bản clone ~/project-os
  let cmd, args;
  if (process.platform === "win32") {
    // Đọc UTF-8 rồi chạy như scriptblock: -File trên PowerShell 5.1 đọc file không BOM theo ANSI.
    const q = (s) => `'${String(s).replace(/'/g, "''")}'`;
    const flags = [o.dry && "-DryRun", o.uninstall && "-Uninstall"].filter(Boolean).join(" ");
    const script = path.join(PKG_ROOT, "install.ps1");
    cmd = "powershell.exe";
    args = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
      `& ([scriptblock]::Create([IO.File]::ReadAllText(${q(script)}, [Text.Encoding]::UTF8))) ${flags}`];
  } else {
    cmd = "bash";
    args = [path.join(PKG_ROOT, "install.sh"), ...[o.dry && "--dry-run", o.uninstall && "--uninstall"].filter(Boolean)];
  }
  const r = spawnSync(cmd, args, { stdio: "inherit", env });
  if (r.error) {
    console.error(`Không chạy được ${cmd}: ${r.error.message}`);
    process.exit(1);
  }
  process.exit(r.status === null ? 1 : r.status);
}

const opts = parse(process.argv.slice(2));
if (opts.help) {
  console.log(HELP);
  process.exit(0);
}
opts.global ? globalMode(opts) : projectMode(opts);
