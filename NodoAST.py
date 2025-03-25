import json

class NodoAST:
    pass

    def traducir(self):
        raise NotImplementedError("Metodo traducir() no implementado en este nodo")
    def generar_codigo(self):
        raise NotImplementedError("Metodo generar_codigo() no implementado en este nodo")
    

class NodoPrograma(NodoAST):
    """ Nodo raíz que contiene múltiples funciones """
    def __init__(self, funciones):
        self.funciones = funciones  # Lista de funciones

    def generar_codigo(self):
        return "\n".join(funcion.generar_codigo() for funcion in self.funciones)

class NodoFuncion(NodoAST):
    def __init__(self, nombre, parametros, cuerpo):
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo  # Ahora el cuerpo es una lista de instrucciones

    def traducir(self):
        params = ",".join(p.tradurcir() for p in self.parametros)
        cuerpo = "\n      ".join(c.traducir() for c in self.cuerpo)
        return f"def {self.nombre[1]} ({params}):\n   {cuerpo}"
    
    def generar_codigo(self):

        codigo = f"{self.nombre[1]}: \n"
        codigo += "\n".join(c.generar_codigo() for c in self.cuerpo)
        return codigo

class NodoParametro(NodoAST):
        
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre
    
    def traducir(self):
        return self.nombre[1]

class NodoAsignacion(NodoAST):
    def __init__(self, nombre, expresion):
        self.nombre = nombre
        self.expresion = expresion
    
    def traducir(self):
        return f"{self.nombre} = {self.expresion.traducir()}"

    def generar_codigo(self):
        codigo = self.expresion.generar_codigo()
    
        codigo += f"\n    mov [{self.nombre[1]}], eax; guardar resultado en {self.nombre[1]}"
        return codigo 

class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
    
    def generar_codigo(self):
        codigo = []
        codigo.append(self.izquierda.generar_codigo())
        codigo.append("    push eax; guardar en la pila ")

        codigo.append(self.derecha.generar_codigo())
        codigo.append("    pop ebx; recuperar el primer operando ")

        if self.operador[1] == "+":
            codigo.append("         add eax, ebx; eax + ebx")
        elif self.operador[1] == "-":
            codigo.append("    sub ebx, eax; eax - ebx")
        
        return

    def traducir(self):
        return f"{self.izquierda.traducir()[1]} {self.operador[1]} {self.derecha.traducir()[1]}"
    

    def optimimzar(self):
        if isinstance(self.izquierda, NodoOperacion):
            izquierda = self.izquierda.optimizar()
        else:
            izquierda = self.izquierda
        if isinstance(self.derecha, NodoOperacion):
            derecha = self.derecha.optimizar()
        else:
            derecha = self.derecha

        if isinstance(izquierda,NodoNumero) and isinstance(derecha, NodoNumero):
            if self.operador == "+":
                return NodoNumero(izquierda.valor + derecha.valor)
            elif self.operador == "-":
                return NodoNumero(izquierda.valor - derecha.valor)
            elif self.operador == "*":
                return NodoNumero(izquierda.valor * derecha.valor)
            elif self.operador == "/" and derecha.valor != 0:
                return NodoNumero(izquierda.valor / derecha.valor)
            
            #Simplificacion algebraica
        if self.operador == "*" and isinstance(derecha, NodoNumero) and derecha.valor == 1:
            return izquierda
        if self.operador == "*" and isinstance(izquierda, NodoNumero) and izquierda.valor == 1:
            return derecha
        if self.operador == "+" and isinstance(derecha, NodoNumero) and derecha.valor == 0:
            return izquierda
        if self.operador == "+" and isinstance(izquierda, NodoNumero) and izquierda.valor == 0:
            return derecha
        
        return NodoOperacion(izquierda, self.operador, derecha)
    
            
    
class NodoRetorno(NodoAST):
    def __init__(self, expresion):
        self.expresion = expresion
    
    def traducir(self):
        return f"return {self.expresion.traducir()}"

class NodoIdentificador(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre
    
    def traducir(self):
        return self.nombre[1]

    def generar_codigo(self):
        if self.nombre is None or not isinstance(self.nombre, str):
            raise ValueError("Error: self.nombre debe ser una cadena válida")
        if len(self.nombre) > 1:
            return f"         mov eax, {self.nombre[1]}; cargar variable {self.nombre[1]} en eax"
        else:
            return f"         mov eax, {self.nombre}; cargar variable {self.} en eax"
        
      

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor
    
    def traducir(self):
        return str(self.valor[1])
    def generar_codigo():
        return f"         mov eax, {self.valor[1]}; cargar numero {self.valor[1]} en eax" 

class NodoWhile(NodoAST):
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion  # Expresión booleana
        self.cuerpo = cuerpo  # Lista de instrucciones dentro del while


def imprimir_ast(nodo):
    if isinstance(nodo, NodoPrograma):
        return {'Programa': [imprimir_ast(func) for func in nodo.funciones]}
    elif isinstance(nodo, NodoFuncion):
        return {'Funcion': nodo.nombre,
                'Parametros': [imprimir_ast(p) for p in nodo.parametros],
                'Cuerpo': [imprimir_ast(c) for c in nodo.cuerpo]}
    elif isinstance(nodo, NodoParametro):
        return {'Parametro': nodo.nombre, 'Tipo': nodo.tipo}
    elif isinstance(nodo, NodoAsignacion):
        return {'Asignacion': nodo.nombre,
                'Expresion': imprimir_ast(nodo.expresion)}
    elif isinstance(nodo, NodoOperacion):
        return {'Operacion': nodo.operador,
                'Izquierda': imprimir_ast(nodo.izquierda),
                'Derecha': imprimir_ast(nodo.derecha)}
    elif isinstance(nodo, NodoRetorno):
        return {'Return': imprimir_ast(nodo.expresion)}
    elif isinstance(nodo, NodoIdentificador):
        return {'Identificador': nodo.nombre}
    elif isinstance(nodo, NodoNumero):
        return {'Numero': nodo.valor}
    elif isinstance(nodo, NodoWhile):
        return {'While': imprimir_ast(nodo.condicion),
                'Cuerpo': [imprimir_ast(c) for c in nodo.cuerpo]}
    return {}

funcionC = """ int suma(int a, int b) {
    
    int x = a + b * 2;
    int y = x - 5;
    
    if (x > 2){
        print(x);
    }       
    else if (x<2) {
        print(1);
    }   
 }
"""


#programa = NodoPrograma([funcionmain, funcion2, funcion3, funcion4])  # Nodo raíz con múltiples funciones

programa = NodoPrograma(funcionC)
# Imprimir el AST
#print(json.dumps(imprimir_ast(programa), indent=2))
"""

nodo_exp = NodoOperacion(NodoNumero(5), "+", NodoNumero(8))
print(json.dumps(imprimir_ast(nodo_exp), indent=1))
"""

codigo_asm = programa.generar_codigo()
print(codigo_asm)