#!/bin/bash
# 277.sh <nrf_elf> <outdir> : BLE-only slice of the discovery policy. Pad connects (AUTO), host sets BT.DISCOVERY.SET mode=2 (OFF),
# drops the link (BLE.DROP 1000 ms), waits: with OFF the central must not scan/reconnect on its own.
exec "$(dirname "$0")/nrf_cdc.sh" "$1" "$2" nrf_ble.yaml 3 '{"cmd":"BT.STATUS"}' '{"cmd":"BT.DISCOVERY.SET","mode":2}' '{"cmd":"BLE.DROP","ms":1000}' 'wait:7.5' '{"cmd":"BT.STATUS"}'
