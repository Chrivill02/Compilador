SECTION .data
    msg   db   "Hola mundo!", 0Ah, 0

SECTION .text
global _start
strLen:
    push ebx
    mov ebx, eax

nextChar:
    cmp byte [eax], 0
    jz finlen
    jmp nextChar


finLen:
    sub eax, ebx
    pop ebx
    ret 



printsastr:
    ;guardar registros en pila
    push edx
    push ecx
    push ebx
    push eax

    call strLen 



    mov   edx, eax ;longitud de cadena
    pop eax
    mov   ecx, eax; cadena a imprimir
    mov   ebx, 1 ;  tipo de salida (STDOUT file)
    mov   eax, 4 ; SYS_WRITE (kernel opocode 4)
    int 80h
    

    mov ebx, 0   ; return 0 status on exit
    mov eax, 1   ;SYS_EXIT (kernel opcode 1)
    int 80h

_start:
    mov eax, msg
    call printstr

    call quit
