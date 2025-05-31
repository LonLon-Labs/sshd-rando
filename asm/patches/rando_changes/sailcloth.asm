; Deactivate air vents if the player doesn't have the sailcloth
.offset 0x71009f6e3c
mov w8, #98
b additions_jumptable


.offset 0x7100d88730
mov w8, #99
bl additions_jumptable
nop
