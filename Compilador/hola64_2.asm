;Hola mundo version 64 bits
;nasm -f elf64 hola64.asm -o hola64.o
;ld -o hola64 hola64.0
;./hola64

%include    "stdio64.asm"


SECTION .data
    msg db  "Hola mundo!", 10

SECTION .text
    global _start

_start:
    mov     rax, msg;
    call    printStr
    
    call salir

    