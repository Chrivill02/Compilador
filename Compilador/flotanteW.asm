;Manejo de valores de coma flotante
;compilar: nasm -f win64 flotante.asm -l flotante.lst
;link: gcc flotante.obj -o flotante.exe

extern printf

section .data
    pi        dq 3.14159
    diametro  dq 5.0
    format    db "C = π*d = %f + %f = %f", 10, 0   ; formato correcto

section .bss
    c         resq 1

section .text
    global main

main:
    push rbp

    ; Calcular c = pi * diametro
    fld     qword [diametro]
    fmul    qword [pi]
    fstp    qword [c
    