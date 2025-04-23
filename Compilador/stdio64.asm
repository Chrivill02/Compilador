
strlen:
    push rsi
    mov rsi, rax
sigChar:
    cmp byte[rax], 0
    jz  finStrlen
    inc rax
    jmp     sigChar

finStrlen:
    sub     rax,rsi
    pop     rsi
    ret     

 ;----------- printStr(cadena) ------------------
printStr:
    push rdx
    push rsi
    push rdi
    push rax
    ;-------------------llamada a longitud de cadena (cadena en rax)
    call strlen

    mov rdx, rax
    pop rax
    
    mov     rsi, rax; Apunta a la direccion base de la cadena
    mov     rdi, 1 ; stdout
    mov     rax, 1 ; 
    syscall

    ;--------------------devolver el contenido a los registros

    pop rdi
    pop rsi
    pop rdx
    ret


    mov     rax, 60
    xor     rdi, rdi
    syscall
