#------------------------------Analisis Semántico-----------------------------------------------------
from NodosAST import *

class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()
    
    def analizar(self, nodo):
        if isinstance(nodo, NodoAsignacion):
            tipo_expr = self.analizar(nodo.expresion)
            self.tabla_simbolos.declarar_variable(nodo.nombre,tipo_expr)
        elif isinstance(nodo,NodoIdentificador):
            return self.tabla_simbolos.obtener_tipo_variable(nodo.nombre)

        elif isinstance(nodo, NodoNumero):
            return "int"
        
        elif isinstance(nodo, NodoOperacion):
            tipo_izq = self.analizar(nodo.izquierda)
            tipo_der = self.analizar(nodo.derecha)
            if tipo_izq != tipo_der:
                raise Exception(f"Error: tipos incompatibles en operacion {tipo_izq} {nodo.operador}")

            return tipo_izq

        if isinstance(nodo, NodoFuncion):
            self.tabla_simbolos.declarar_funcion(nodo.nombre, nodo.tipo_retorno, nodo.parametros)
            for instruccion in nodo.cuerpo:
                self.analizar(instruccion)

        if isinstance(nodo, NodoLlamadaFuncion):
            tipo_retorno, parametros = self.tabla_simbolos.obtener_info_funcion(nodo.nombre)
            if len(nodo.argumentos) != len(parametros):
                raise Exception(f"Error: la funcion {nodo.nombre} espera {len(parametros)} argumentos")
            return tipo_retorno
    
        if isinstance(nodo, NodoPrograma):
            for funcion in nodo.funciones:
                self.analizar(funcion)
            self.analizar(nodo.main)
        
    def visitar_NodoFuncion(self,nodo):
        if nodo.nombre[1] in self.tabla_simbolos:
            raise Exception(f"Error semántico: la función {nodo.nombre[1]} ya está definida")
        
        self.tabla_simbolos[nodo.nombre[1]] = {"tipo": nodo.parametros[0].tipo[1], "parametros":nodo.parametros}
        for param in nodo.parametros:
            self.tabla_simbolos[param.nombre[1]] = {"tipo": param.tipo[1]} 
        
        for instruccion in nodo.cuerpo:
            self.analizar(instruccion)

    def visitar_NodoAsignacion(self, nodo):
        tipo_expresion = self.analizar(nodo.expresion)
        self.tabla_simbolos[nodo.nombre[1]] = {"tipo": tipo_expresion}

    def visitar_NodoOperacion(self,nodo):
        tipo_izquierda = self.analizar(nodo.izquierda)
        tipo_derecha = self.analizar(nodo.derecha)

        if tipo_izquierda != tipo_derecha:
            raise Exception(f"Error semántico: Operacion entre tipos incompatibles")

        return tipo_izquierda

    def visitar_NodoNumero(self, nodo):
        return "int" if "." not in nodo.valor[1] else "float"
    
    def visitar_NodoIdentificador(self, nodo):
        if nodo.nombre[1] not in self.tabla_simbolos:
            raise Exception(f"Error semántico: La variable {nodo.nombre[1]} no es igual")
        
        return self.tabla_simbolos[nodo.nombre[1]]["Tipo"]
    
    def visitar_NodoRetorno(self, nodo):
        return self.analizar(nodo.expresion)

class TablaSimbolos:
    def __init__(self):
        self.variables = {} #Almacena variables {nombre: tipo}
        self.funciones = {} #Almacena funciones {nombre: {tipo_retorno {parametros}}}

    def declarar_variable(self, nombre, tipo):
        if nombre in self.variables:
            raise Exception(f"Error: Variable {nombre} ya declarada")
        self.variables[nombre] = tipo

    def obtener_tipo_variable(self, nombre):
        if nombre not in self.variables:
            raise Exception(f"Error variable {nombre} no declarado")
        return self.variables[nombre]

    def declarar_funcion(self, nombre, tipo_retorno, parametros):
        if nombre in self.funciones:
            raise Exception(f"Error: función {nombre} ya declarada")
        self.funciones[nombre] = {tipo_retorno, parametros}

    def obtener_info_funcion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f"Error: {nombre} no declarada")
        return self.funciones[nombre]
    



