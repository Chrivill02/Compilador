SECTION .data
    msg   db   "Hola mundo!", 0Ah

SECTION .text
global _start

_start:
    mov   edx, 12 ;longitud de cadena
    mov   ecx, msg; cadena a imprimir
    mov   ebx, 1 ;  tipo de salida (STDOUT file)
    mov   eax, 4 ; SYS_WRITE (kernel opocode 4)
    int 80h

    mov ebx, 0   ; return 0 status on exit
    mov eax, 1   ;SYS_EXIT (kernel opcode 1)
    int 80h