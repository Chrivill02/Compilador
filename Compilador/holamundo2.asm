%include "stdio.asm"

SECTION .data
    msg   db   "Hola mundo!", 0Ah

SECTION .text
global _start

_start:
    mov eax, msg
    call printstr

    call quit
