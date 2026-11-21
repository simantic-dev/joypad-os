# PR 291 targeted: PS3 mode square stick range
Verdict: FEATURE DEMONSTRATED.

Scenario: scenarios/run_a.sh ps3 sticks <A elf>: remapper A built with USBD_DEFAULT_MODE=USB_OUTPUT_MODE_PS3 (scenarios/ps3default.cmake),
enumerates as 054c:0268; a_peer.py feeds uart_peer EVENT frames (left stick full circle diagonal 218/38, cardinal 255/128, right stick
38/218, half diagonal 192/64) and decodes the PS3 input report (lx at byte 6, ly 7, rx 8, ry 9).
main (9fa79f45): L=(218,38) | L=(255,128) | R=(38,218) | L=(192,64)   (circle passed through)
PR (cf2e6df8):  L=(255,1)   | L=(255,128) | R=(1,255)   | L=(218,38)   (diagonals stretched to the square, cardinals and centre unchanged)
Not covered: DS3/DS2 sources with pressure data (left untouched by the PR); inputs here carry no pressure data.
Evidence: results/291/targeted/sticks.{main,pr}.reports.txt
