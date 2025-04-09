# ------------------------------Analisis Semántico-----------------------------------------------------
from NodosAST import *

class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = {}
        self.errores = []
        self.palabras_reservadas = {"int", "float", "string", "if", "else", "while", "for", "return", "print"}

    def analizar(self, nodo):
        


        if isinstance(nodo, NodoPrograma):
            for decl in nodo.funciones:  # ← ¡cambio importante aquí!
                self.analizar(decl)

        elif isinstance(nodo, NodoFuncion):
            self.analizar_bloque(nodo.cuerpo)

        if isinstance(nodo, NodoDeclaracion):
            for i, nombre in enumerate(nodo.nombres):
                if nombre in self.palabras_reservadas:
                    self.errores.append(f"Error: '{nombre}' es una palabra reservada y no puede ser una variable")
                elif nombre in self.tabla_simbolos:
                    self.errores.append(f"Error: variable '{nombre}' ya ha sido declarada")
                else:
                    self.tabla_simbolos[nombre] = nodo.tipo
                
                # Si hay una expresión de inicialización, analizarla
                if i < len(nodo.valores):
                    valor = nodo.valores[i]
                    if valor is not None:
                        self.analizar(valor)


        elif isinstance(nodo, NodoAsignacion):
            if nodo.nombre[1] not in self.tabla_simbolos:
                self.errores.append(f"Error: variable '{nodo.nombre[1]}' no declarada")
            self.analizar(nodo.expresion)

        elif isinstance(nodo, NodoOperacion) or isinstance(nodo, NodoOperacionLogica):
            self.analizar(nodo.izquierda)
            self.analizar(nodo.derecha)

        elif isinstance(nodo, NodoIf):
            self.analizar(nodo.condicion)
            self.analizar_bloque(nodo.cuerpo_if)
            self.analizar_bloque(nodo.cuerpo_else)

        elif isinstance(nodo, NodoWhile):
            self.analizar(nodo.condicion)
            self.analizar_bloque(nodo.cuerpo)

        elif isinstance(nodo, NodoFor):
            self.analizar(nodo.inicializacion)
            self.analizar(nodo.condicion)
            self.analizar(nodo.incremento)
            self.analizar_bloque(nodo.cuerpo)

        elif isinstance(nodo, NodoLlamadaFuncion):
            for arg in nodo.argumentos:
                self.analizar(arg)

        elif isinstance(nodo, NodoRetorno):
            self.analizar(nodo.expresion)

        elif isinstance(nodo, NodoIdentificador):
            if nodo.nombre[1] not in self.tabla_simbolos:
                self.errores.append(f"Error: variable '{nodo.nombre[1]}' no declarada")

        # No hace falta analizar NodoNumero ni NodoString, son valores constantes

    def analizar_bloque(self, instrucciones):
        for inst in instrucciones:
            self.analizar(inst)




# ------------------------------Tabla de Símbolos-----------------------------------------------------
class TablaSimbolos:
    def __init__(self):
        self.variables = {}  # Almacena variables {nombre: tipo}
        self.funciones = {}  # Almacena funciones {nombre: {tipo_retorno, parametros}}
        self.reservadas = {'int', 'float', 'if', 'for', 'else', 'return', 'print'}  # Palabras reservadas

    def declarar_variable(self, nombre, tipo):
        if nombre in self.reservadas:
            raise Exception(f"Error: '{nombre}' es una palabra reservada y no puede ser una variable")
        if nombre in self.variables:
            raise Exception(f"Error: Variable {nombre} ya declarada")
        self.variables[nombre] = tipo

    def obtener_tipo_variable(self, nombre):
        if nombre not in self.variables:
            raise Exception(f"Error: Variable {nombre} no declarada")
        return self.variables[nombre]

    def declarar_funcion(self, nombre, tipo_retorno, parametros):
        if nombre in self.reservadas:
            raise Exception(f"Error: '{nombre}' es una palabra reservada y no puede ser una función")
        if nombre in self.funciones:
            raise Exception(f"Error: función {nombre} ya declarada")
        self.funciones[nombre] = {"tipo_retorno": tipo_retorno, "parametros": parametros}

    def obtener_info_funcion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f"Error: Función {nombre} no declarada")
        return self.funciones[nombre]

