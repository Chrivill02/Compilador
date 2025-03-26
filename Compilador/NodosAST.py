class NodoAST:
    def traducir(self):
        raise NotImplementedError("Metodo traducir() no implementado")
    def generar_codigo(self):
        raise NotImplementedError("Metodo generar_codigo() no implementado")

class NodoPrograma(NodoAST):
    def __init__(self, funciones):
        self.funciones = funciones
        
    def traducir(self):
        return [f.traducir() for f in self.funciones]
    
    def generar_codigo(self):
        codigo = "section .text\n"
        codigo += "global _start\n\n"
        codigo += "\n".join(f.generar_codigo() for f in self.funciones)
        
        # Añadir sección de datos para buffers de impresión
        codigo += "\n\nsection .data\n"
        codigo += "    newline db 10, 0\n"
        codigo += "section .bss\n"
        codigo += "    num_buffer resb 12\n"
        
        return codigo
class NodoFuncion(NodoAST):
    def __init__(self, nombre, parametros, cuerpo):
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo
        
    def traducir(self):
        params = ", ".join(p.traducir() for p in self.parametros)
        cuerpo = "\n    ".join(c.traducir() for c in self.cuerpo)
        return f"def {self.nombre}({params}):\n    {cuerpo}"
    
    def generar_codigo(self):
        codigo = f"{self.nombre}:\n"
        codigo += "    push ebp\n"
        codigo += "    mov ebp, esp\n"
        
        # Reservar espacio para variables locales
        stack_space = 4 * sum(1 for inst in self.cuerpo if isinstance(inst, NodoDeclaracion))
        if stack_space > 0:
            codigo += f"    sub esp, {stack_space}\n"
        
        codigo += "\n".join(c.generar_codigo() for c in self.cuerpo)
        
        if self.nombre != 'main':
            codigo += "\n    mov esp, ebp\n"
            codigo += "    pop ebp\n"
            codigo += "    ret\n"
        else:
            codigo += "\n    mov eax, 1    ; sys_exit\n"
            codigo += "    mov ebx, 0    ; status 0\n"
            codigo += "    int 0x80\n"
        
        return codigo

class NodoParametro(NodoAST):
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre
        
    def traducir(self):
        return f"{self.tipo} {self.nombre}"
    
    def generar_codigo(self):
        return f"; Parametro: {self.tipo} {self.nombre}"

class NodoAsignacion(NodoAST):
    def __init__(self, nombre, expresion):
        self.nombre = nombre 
        self.expresion = expresion
        
    def traducir(self):
        return f"{self.nombre[1]} = {self.expresion.traducir()}"
    
    def generar_codigo(self):
        codigo = self.expresion.generar_codigo()
        codigo += f"\n    mov [{self.nombre[1]}], eax ; asignar a {self.nombre[1]}"
        return codigo

class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
        
    def traducir(self):
        return f"{self.izquierda.traducir()} {self.operador} {self.derecha.traducir()}"

    def generar_codigo(self):
        codigo = []
        codigo.append(self.izquierda.generar_codigo())
        codigo.append('    push eax')
        
        codigo.append(self.derecha.generar_codigo())
        codigo.append('    pop ebx')
        
        if self.operador == '+':
            codigo.append('    add eax, ebx')
        elif self.operador == '-':
            codigo.append('    sub ebx, eax')
            codigo.append('    mov eax, ebx')
        elif self.operador == '*':
            codigo.append('    imul ebx')
        elif self.operador == '/':
            codigo.append('    xchg eax, ebx')
            codigo.append('    cdq')
            codigo.append('    idiv ebx')
        
        return '\n'.join(codigo)

class NodoOperacionLogica(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
        
    def traducir(self):
        return f"{self.izquierda.traducir()} {self.operador} {self.derecha.traducir()}"
    
    def generar_codigo(self):
        codigo = []
        codigo.append(self.izquierda.generar_codigo())
        codigo.append("    push eax")
        
        codigo.append(self.derecha.generar_codigo())
        codigo.append("    pop ebx")
        
        codigo.append("    cmp ebx, eax")
        
        if self.operador == '==':
            codigo.append("    sete al")
        elif self.operador == '!=':
            codigo.append("    setne al")
        elif self.operador == '<':
            codigo.append("    setl al")
        elif self.operador == '<=':
            codigo.append("    setle al")
        elif self.operador == '>':
            codigo.append("    setg al")
        elif self.operador == '>=':
            codigo.append("    setge al")
        elif self.operador == '&&':
            codigo.append("    and eax, ebx")
        elif self.operador == '||':
            codigo.append("    or eax, ebx")
        
        codigo.append("    movzx eax, al")
        
        return "\n".join(codigo)

class NodoRetorno(NodoAST):
    def __init__(self, expresion):
        self.expresion = expresion
        
    def traducir(self):
        return f"return {self.expresion.traducir()}"
    
    def generar_codigo(self):
        return self.expresion.generar_codigo() + '\n    ret'

class NodoIdentificador(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre
        
    def traducir(self):
        return self.nombre[1]

    def generar_codigo(self):
        return f"    mov eax, [{self.nombre[1]}] ; cargar variable {self.nombre[1]}"

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor
        
    def traducir(self):
        return str(self.valor[1])
        
    def generar_codigo(self):
        return f"    mov eax, {self.valor[1]} ; cargar constante {self.valor[1]}"

class NodoLlamadaFuncion(NodoAST):
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos
        
    def traducir(self):
        params = ", ".join(p.traducir() for p in self.argumentos)
        return f"{self.nombre}({params})"
    
    def generar_codigo(self):
        codigo = []
        for arg in reversed(self.argumentos):
            codigo.append(arg.generar_codigo())
            codigo.append("    push eax")
        
        codigo.append(f"    call {self.nombre}")
        
        if self.argumentos:
            codigo.append(f"    add esp, {4*len(self.argumentos)}")
        
        return "\n".join(codigo)

class NodoString(NodoAST):
    def __init__(self, valor):
        self.valor = valor
        
    def traducir(self):
        return self.valor[1]
        
    def generar_codigo(self):
        return f'    mov eax, {self.valor[1]} ; cargar string'

class NodoDeclaracion(NodoAST):
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre
        
    def traducir(self):
        return f"{self.tipo} {self.nombre};"
        
    def generar_codigo(self):
        return f"; Declaración de variable: {self.tipo} {self.nombre}"

class NodoIf(NodoAST):
    def __init__(self, condicion, cuerpo_if, cuerpo_else=None):
        self.condicion = condicion
        self.cuerpo_if = cuerpo_if
        self.cuerpo_else = cuerpo_else if cuerpo_else else []
        
    def traducir(self):
        if_part = f"if {self.condicion.traducir()}:\n"
        if_part += "\n".join(f"    {inst.traducir()}" for inst in self.cuerpo_if)
        
        if not self.cuerpo_else:
            return if_part
            
        else_part = "else:\n"
        else_part += "\n".join(f"    {inst.traducir()}" for inst in self.cuerpo_else)
        
        return f"{if_part}\n{else_part}"
    
    def generar_codigo(self):
        label_else = f"else_{id(self)}"
        label_end = f"endif_{id(self)}"
        
        codigo = []
        codigo.append(self.condicion.generar_codigo())
        codigo.append(f"    cmp eax, 0")
        codigo.append(f"    je {label_else}")
        
        for instruccion in self.cuerpo_if:
            codigo.append(instruccion.generar_codigo())
        
        codigo.append(f"    jmp {label_end}")
        codigo.append(f"{label_else}:")
        
        for instruccion in self.cuerpo_else:
            codigo.append(instruccion.generar_codigo())
        
        codigo.append(f"{label_end}:")
        
        return "\n".join(codigo)

class NodoWhile(NodoAST):
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo
        
    def traducir(self):
        cuerpo = "\n    ".join(inst.traducir() for inst in self.cuerpo)
        return f"while {self.condicion.traducir()}:\n    {cuerpo}"
    
    def generar_codigo(self):
        label_start = f"while_start_{id(self)}"
        label_end = f"while_end_{id(self)}"
        
        codigo = []
        codigo.append(f"{label_start}:")
        
        # Generar código para la condición
        codigo.append(self.condicion.generar_codigo())
        codigo.append("    cmp eax, 0")
        codigo.append(f"    je {label_end}")
        
        # Generar código para el cuerpo
        for instruccion in self.cuerpo:
            codigo.append(instruccion.generar_codigo())
        
        # Volver al inicio del while
        codigo.append(f"    jmp {label_start}")
        codigo.append(f"{label_end}:")
        
        return "\n".join(codigo)
class NodoFor(NodoAST):
    def __init__(self, inicializacion, condicion, incremento, cuerpo):
        self.inicializacion = inicializacion
        self.condicion = condicion
        self.incremento = incremento
        self.cuerpo = cuerpo
        
    def traducir(self):
        init = self.inicializacion.traducir()
        cond = self.condicion.traducir()
        incr = self.incremento.traducir().rstrip(';')
        cuerpo = "\n    ".join(inst.traducir() for inst in self.cuerpo)
        return f"for ({init} {cond}; {incr}):\n    {cuerpo}"
    
    def generar_codigo(self):
        label_start = f"for_start_{id(self)}"
        label_end = f"for_end_{id(self)}"
        
        codigo = []
        
        # Inicialización
        codigo.append(self.inicializacion.generar_codigo())
        
        # Inicio del bucle
        codigo.append(f"{label_start}:")
        
        # Condición
        codigo.append(self.condicion.generar_codigo())
        codigo.append("    cmp eax, 0")
        codigo.append(f"    je {label_end}")
        
        # Cuerpo del for
        for instruccion in self.cuerpo:
            codigo.append(instruccion.generar_codigo())
        
        # Incremento
        codigo.append(self.incremento.generar_codigo())
        
        # Volver a evaluar condición
        codigo.append(f"    jmp {label_start}")
        codigo.append(f"{label_end}:")
        
        return "\n".join(codigo)

class NodoPrint(NodoAST):
    def __init__(self, argumentos):
        self.argumentos = argumentos
        
    def traducir(self):
        args = ", ".join(arg.traducir() for arg in self.argumentos)
        return f"print({args})"
    
    def generar_codigo(self):
        codigo = []
        codigo.append("    ; Preparación para imprimir")
        
        for arg in self.argumentos:
            codigo.append(arg.generar_codigo())
            
            if isinstance(arg, NodoString):
                # Para strings
                codigo.append("    mov ecx, eax  ; dirección del string")
                codigo.append("    mov edx, 0    ; contador de longitud")
                codigo.append("    .strlen_loop:")
                codigo.append("    cmp byte [ecx+edx], 0")
                codigo.append("    je .strlen_done")
                codigo.append("    inc edx")
                codigo.append("    jmp .strlen_loop")
                codigo.append("    .strlen_done:")
            else:
                # Para números (convertir a string)
                codigo.append("    ; Conversión de número a string")
                codigo.append("    mov ecx, num_buffer")
                codigo.append("    mov ebx, 10")
                codigo.append("    mov edi, 0")
                codigo.append("    .convert_loop:")
                codigo.append("    xor edx, edx")
                codigo.append("    div ebx")
                codigo.append("    add dl, '0'")
                codigo.append("    mov [ecx+edi], dl")
                codigo.append("    inc edi")
                codigo.append("    test eax, eax")
                codigo.append("    jnz .convert_loop")
                codigo.append("    mov edx, edi  ; longitud")
                
                # Invertir el string
                codigo.append("    mov esi, 0")
                codigo.append("    dec edi")
                codigo.append("    .reverse_loop:")
                codigo.append("    cmp esi, edi")
                codigo.append("    jge .reverse_done")
                codigo.append("    mov al, [ecx+esi]")
                codigo.append("    mov bl, [ecx+edi]")
                codigo.append("    mov [ecx+esi], bl")
                codigo.append("    mov [ecx+edi], al")
                codigo.append("    inc esi")
                codigo.append("    dec edi")
                codigo.append("    jmp .reverse_loop")
                codigo.append("    .reverse_done:")
                codigo.append("    mov ecx, num_buffer")
            
            # Llamada al sistema para escribir
            codigo.append("    mov eax, 4      ; sys_write")
            codigo.append("    mov ebx, 1      ; stdout")
            codigo.append("    int 0x80")
        
        return "\n".join(codigo)    
class NodoDeclaracion(NodoAST):
    def __init__(self, tipo, nombre, expresion=None):
        self.tipo = tipo
        self.nombre = nombre
        self.expresion = expresion
        
    def traducir(self):
        if self.expresion:
            return f"{self.tipo} {self.nombre} = {self.expresion.traducir()};"
        return f"{self.tipo} {self.nombre};"
        
    def generar_codigo(self):
        codigo = f"; Declaración de {self.tipo} {self.nombre}"
        if self.expresion:
            codigo += "\n" + self.expresion.generar_codigo()
            codigo += f"\n    mov [{self.nombre}], eax"
        return codigo