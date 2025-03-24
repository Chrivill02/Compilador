class NodoCondicion(NodoAST):
    def __init__(self, condicion, cuerpo_if, cuerpo_else=None):
        hijos = [condicion, cuerpo_if]
        if cuerpo_else:
            hijos.append(cuerpo_else)
        super().__init__('CONDICION', 'if', hijos)
        self.etiqueta_else = f"else_{id(self)}"
        self.etiqueta_fin = f"fin_if_{id(self)}"
    
    def traducir(self):
        cond = self.hijos[0].traducir()
        cuerpo_if = self.hijos[1].traducir()
        if len(self.hijos) > 2:
            cuerpo_else = self.hijos[2].traducir()
            return f"if ({cond}) {{\n{cuerpo_if}\n}} else {{\n{cuerpo_else}\n}}"
        return f"if ({cond}) {{\n{cuerpo_if}\n}}"
    
    def generar_codigo(self):
        codigo_cond = self.hijos[0].generar_codigo()
        
        # Generar código para el cuerpo del if
        codigo_if = ""
        if isinstance(self.hijos[1], list):
            for nodo in self.hijos[1]:
                codigo_if += nodo.generar_codigo() + "\n"
        else:
            codigo_if = self.hijos[1].generar_codigo()
        
        # Generar código para el else si existe
        codigo_else = ""
        if len(self.hijos) > 2:
            if isinstance(self.hijos[2], list):
                for nodo in self.hijos[2]:
                    codigo_else += nodo.generar_codigo() + "\n"
            else:
                codigo_else = self.hijos[2].generar_codigo()
        
        # Ensamblar todo el código
        codigo = (
            f"; Condicional if\n"
            f"{codigo_cond}\n"
            f"TEST EAX, EAX\n"
            f"JZ {self.etiqueta_else if len(self.hijos) > 2 else self.etiqueta_fin}\n"
            f"; Cuerpo if\n"
            f"{codigo_if}\n"
            f"JMP {self.etiqueta_fin}\n"
        )
        
        if len(self.hijos) > 2:
            codigo += (
                f"{self.etiqueta_else}:\n"
                f"; Cuerpo else\n"
                f"{codigo_else}\n"
            )
        
        codigo += f"{self.etiqueta_fin}:\n"
        return codigo


class NodoComparacion(NodoAST):
    def __init__(self, operador, izquierdo, derecho):
        super().__init__('COMPARACION', operador, [izquierdo, derecho])
    
    def traducir(self):
        izq = self.hijos[0].traducir()
        der = self.hijos[1].traducir()
        return f"{izq} {self.valor} {der}"
    
    def generar_codigo(self):
        codigo_izq = self.hijos[0].generar_codigo()
        codigo_der = self.hijos[1].generar_codigo()
        
        return (
            f"; Comparación {self.valor}\n"
            f"{codigo_izq}\n"
            f"PUSH EAX\n"
            f"{codigo_der}\n"
            f"POP EBX\n"
            f"CMP EBX, EAX\n"
            f"MOV EAX, 0\n"  # Por defecto, false
            f"{self._generar_salto()}\n"
            f"MOV EAX, 1\n"  # True si se cumple la condición
            f"{self.etiqueta_fin}:\n"
        )
    
    def _generar_salto(self):
        saltos = {
            '==': 'JNE',
            '!=': 'JE',
            '<': 'JGE',
            '<=': 'JG',
            '>': 'JLE',
            '>=': 'JL'
        }
        return f"{saltos[self.valor]} {self.etiqueta_fin}"


# Ejemplo de uso extendido
if __name__ == "__main__":
    # if (a > b) { return a; } else { return b; }
    condicion_if = NodoCondicion(
        condicion=NodoComparacion('>', NodoVariable('a'), NodoVariable('b')),
        cuerpo_if=NodoRetorno(NodoVariable('a')),
        cuerpo_else=NodoRetorno(NodoVariable('b'))
    )
    
    # int max(int a, int b) { ... }
    funcion_max = NodoFuncion(
        'max',
        [
            NodoParametro('a'),
            NodoParametro('b')
        ],
        [condicion_if]
    )
    
    # int main() { int m = max(5, 3); }
    main_func = NodoFuncion(
        'main',
        [],
        [
            NodoDeclaracion('m'),
            NodoAsignacion(
                'm',
                NodoLlamadaFuncion(
                    'max',
                    [
                        NodoNumero(5),
                        NodoNumero(3)
                    ]
                )
            )
        ]
    )
    
    print("// Código C traducido:")
    print(funcion_max.traducir())
    print(main_func.traducir())
    
    print("\n; Código Assembly generado:")
    print("section .data")
    print("m DD 0")
    print("\nsection .text")
    print("global _start")
    print("_start:")
    print(main_func.generar_codigo())
    print("\n" + funcion_max.generar_codigo())
    print("\n; Terminar programa")
    print("MOV EAX, 1\nINT 0x80")