# joypad-mcp driving Joypad OS in simulation

The stock `tools/joypad-mcp` server, unmodified, sends `UART_PKT_INPUT_EVENT` frames to stock Joypad firmware running on a simulated RP2040.
A simulated USB console sees the result. No hardware is involved.

```
mcp_drive.mjs ─MCP stdio─► joypad-mcp ─serial─► sim --uart-pty uart0 ─► usb2usb (Feather RP2040 USB host build, CONFIG_UART_HOST)
                                                                              │ USB device (Switch mode)
                                                                 switch_host.py ◄─ sim --usb-raw usb:<port>
```

```sh
(cd tools/joypad-mcp && npm ci && npm run build)
SIM=<sim binary> ELF=sim/elf/usb2usb_feather_usb_host_9fa79f45.elf MCP=$PWD/tools/joypad-mcp sh sim/mcp/run_mcp.sh
```

`mcp_drive.mjs` makes the same tool calls Claude Code would make: `connect`, `tap`, `axis`, `release_all`, `combo` and `read_log`.
To drive the sim by hand instead, register joypad-mcp in your MCP client and pass the `/dev/ttys…` path printed by `run_mcp.sh` to `connect`.
`example_console.txt` is one run; the Konami-code combo comes out in order.

joypad-mcp times presses by the wall clock, so `--uart-pty` makes the sim run in real time. On a loaded machine the sim runs below real time, and a 300 ms tap then shows up as less simulated time.
