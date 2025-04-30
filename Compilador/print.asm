; Lectura de datos desde teclado y almacenamiento en memoria
; fecha 20250428

%include 'stdio.asm'

SECTION .data
    msg1 db 'Ingrese Nombre: ', 0
    msg2 db 'Hola ', 0

SECTION .bss
    nombre resb 20

SECTION .text
    global _start

_start:
    mov eax, msg1
    call printstr

    mov edx, 20     ;Espacio total de lectura
    mov ecx, nombre     ;ecx=dir, de memoria para almacenar el dato
    mov ebx, 0      ;lee desde STDIN
    mov eax, 3      ;servicio sys_read
    int 80h

    mov eax, msg2
    call printstr

    mov eax, nombre
    call printstr

    call quit