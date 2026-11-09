#!/usr/bin/env node
// npx -y @nguyentan0510/project-os [--tools agents,claude|all] [--global] [--dry-run] [--uninstall] [--dir <thư-mục>]
//
// Mặc định (theo dự án): chép skill vào thư mục hiện tại (hoặc --dir), để commit cùng repo
// (chọn bớt bằng --tools hoặc biến PROJECT_OS_TOOLS):
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
// Công cụ → thư mục skill trong dự án.
const TOOLS = {
  agents: [".agents", "skills", "project-os"], // Codex, Antigravity và các công cụ dùng chuẩn chung
  claude: [".claude", "skills", "project-os"], // Claude Code
};
const VERSION = require(path.join(PKG_ROOT, "package.json")).version;

// Mặc định: cả hai. Đổi mặc định cho riêng bạn bằng biến môi trường PROJECT_OS_TOOLS (ví dụ "agents").
function resolveTools(spec) {
  const names = String(spec).split(",").map((s) => s.trim().toLowerCase()).filter(Boolean);
  const out = new Set();
  for (const n of names) {
    if (n === "all") Object.keys(TOOLS).forEach((k) => out.add(k));
    else if (TOOLS[n]) out.add(n);
    else fail(`--tools không nhận "${n}". Hợp lệ: ${Object.keys(TOOLS).join(", ")}, all`);
  }
  if (!out.size) fail("--tools cần ít nhất một giá trị (agents, claude, all)");
  return [...out];
}

const HELP = `project-os — cài skill Project OS

  npx -y @nguyentan0510/project-os              cài vào dự án hiện tại (mặc định: .agents/ và .claude/)
  npx -y @nguyentan0510/project-os --global     cài vào thư mục home của các công cụ AI

Tuỳ chọn:
  --tools <danh-sách>  chọn nơi cài, cách nhau bằng dấu phẩy: agents (Codex, Antigravity),
                       claude (Claude Code), all. Mặc định: all, hoặc biến PROJECT_OS_TOOLS.
  --dir <thư-mục>   cài vào thư mục này thay vì thư mục hiện tại
  --dry-run         chỉ in việc sẽ làm
  --uninstall       gỡ bản đã cài bằng lệnh này
  --global          cài toàn cục thay vì theo dự án
  -h, --help        trợ giúp`;

function parse(argv) {
  const o = { global: false, dry: false, uninstall: false, dir: process.cwd(), help: false,
    tools: process.env.PROJECT_OS_TOOLS || "all" };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--tools") {
      if (!argv[i + 1]) fail("--tools cần giá trị: agents, claude hoặc all");
      o.tools = argv[++i];
    } else if (a.startsWith("--tools=")) o.tools = a.slice("--tools=".length);
    else if (a === "--global") o.global = true;
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
  for (const loc of resolveTools(o.tools).map((k) => TOOLS[k])) {
    const dst = path.join(o.dir, ...loc);
    const rel = loc.join("/");
    if (o.uninstall) {
      if (installedByUs(dst)) {
        if (!o.dry) {
          fs.rmSync(dst, { recursive: true, force: true });
          // Dọn thư mục cha nếu rỗng (skills/, rồi .agents/ hoặc .claude/); thư mục có file khác thì giữ.
          for (let d = path.dirname(dst), i = 0; i < 2; d = path.dirname(d), i++) {
            try { fs.rmdirSync(d); } catch { break; }
          }
        }
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
