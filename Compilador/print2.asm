;-------calculo de longitud de cadena--------
strlen:
    push ebx
    mov ebx, eax

nextChar:
    cmp byte [eax], 0
    jz finLen
    inc eax
    jmp nextChar

finLen:
    sub eax, ebx
    pop ebx
    ret

;-------Imprimir printstr(msg)---------
printstr:
    ;------guardar en pila--------
    push edx
    push ecx
    push ebx
    push eax

    ;------llamo longitud de cadena------
    call strlen

    mov edx, eax
    pop eax
    mov ecx, eax

    mov ebx, 1
    mov eax, 4
    int 80h

    pop ebx
    pop ecx
    pop edx

    ret

;-------end----------------------------
quit:
    mov ebx, 0
    mov eax, 1
    int 80h