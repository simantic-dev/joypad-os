// Drives the stock joypad-mcp server over MCP stdio, exactly as an MCP client (Claude Code) would.
// usage: node mcp_drive.mjs <server.js> <serial port>
import { spawn } from "node:child_process";
const [server, port] = process.argv.slice(2);
const p = spawn("node", [server], { stdio: ["pipe", "pipe", "inherit"] });
let id = 0, buf = ""; const waiting = new Map();
p.stdout.on("data", (d) => { buf += d; let i; while ((i = buf.indexOf("\n")) >= 0) { const m = JSON.parse(buf.slice(0, i)); buf = buf.slice(i + 1); waiting.get(m.id)?.(m); } });
const rpc = (method, params) => new Promise((r) => { const n = ++id; waiting.set(n, r); p.stdin.write(JSON.stringify({ jsonrpc: "2.0", id: n, method, params }) + "\n"); });
const call = async (name, args = {}) => { const r = await rpc("tools/call", { name, arguments: args }); const t = r.result?.content?.[0]?.text ?? JSON.stringify(r.error); console.log(`mcp ${name} ${JSON.stringify(args)} -> ${t.slice(0, 160)}`); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
await rpc("initialize", { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "sim-demo", version: "0" } });
p.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n");
await call("connect", { port });
await sleep(1500);
await call("tap", { buttons: "B1", duration_ms: 300 }); await sleep(600);
await call("tap", { buttons: "B2+DR", duration_ms: 300 }); await sleep(600);
await call("axis", { axis: "LX", value: 255 }); await sleep(600);
await call("release_all"); await sleep(600);
await call("combo", { steps: [{buttons:"DU",duration_ms:120,gap_ms:80},{buttons:"DU",duration_ms:120,gap_ms:80},{buttons:"DD",duration_ms:120,gap_ms:80},{buttons:"DD",duration_ms:120,gap_ms:80},{buttons:"DL",duration_ms:120,gap_ms:80},{buttons:"DR",duration_ms:120,gap_ms:80},{buttons:"DL",duration_ms:120,gap_ms:80},{buttons:"DR",duration_ms:120,gap_ms:80},{buttons:"B2",duration_ms:120,gap_ms:80},{buttons:"B1",duration_ms:120,gap_ms:80}] }); await sleep(2500);
await call("read_log"); await call("disconnect"); p.kill();
