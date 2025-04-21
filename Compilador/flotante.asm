;Manejo de valores de coma flotante
;creador:
;fecha: 21 abr 2025
;compilar: nasm -f elf64 flotante.asm -l flotante.lst
;link gcc -m64 flotante.o -o flotante -no-pie

extern printf

SECTION .data
   pi:        dq   3.14159
   diametro   dq   5.0
   format     dq   "C = ¶*d = %f + % f = %f", 10,0

SECTION .bss
    c:      resq   1

SECTION .text
    global main


main:
    push    rbp
    fld     qword [diametro]        ;Carga el radio al registro ST0
    fmul    qword [pi]              ; diametro * pi
    fstp    qword [c]               ; guarda el resultado de ST0 en c

;------------------------------------- llamada a printf --------------------------------------------------

    mov     rdi, format             ; cargar la cadena formateada
    movq    xmm0, qword [pi]
    movq    xmm1, qword [diamtetro]
    movq    xmm2, qword [c]
    mov     rax, 3
    call printf 