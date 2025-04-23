;Hola mundo version 64 bits
;nasm -f elf64 hola64.asm -o hola64.o
;ld -o hola64 hola64.0
;./hola64

SECTION .data
    msg db  "Hola mundo!", 10

SECTION .text
    global _start

_start:
    mov     rdx, 12; Longitud de cadena
    mov     rsi, msg; Apunta a la direccion base de la cadena
    mov     rdi, 1 ; stdout
    mov     rax, 1 ; 
    syscall

    mov     rax, 60
    xor     rdi, rdi
    syscall


    