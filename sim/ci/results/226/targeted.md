# PR 226 targeted: usb2wiiext (USB pad -> Wii extension port)
Verdict: DEMONSTRATED (Pico target, unencrypted). Built joypad_usb2wiiext_pico from the PR and ran it with a DS4 on the native USB host and a Python Wii console (I2C master bit-banged on GP4/GP5, wiibrew protocol) on the review simulator. Details, citations and caveats: review.md.
ID 0100a4200101 (Classic Pro), calibration checksum ok; Cross -> B, sticks and triggers decode in format 0x01 and 0x03. Finding: format 0x03 X axes run opposite to format 0x01 (existing shared code). Not covered: KB2040 target, encryption, real Wii, 5 V.
Evidence: results/226/review/ (scenarios/226.sh).
