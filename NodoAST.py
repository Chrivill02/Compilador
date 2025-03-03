class NodoAST:
    #Clase base para todos los nodos del AST
    pass
class NodoFuncion(NodoAST):
    #Nodo que representa una funcion
    def __init__(self, nombre, parametros,cuerpo):
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo

class NodeParametro(NodoAST):
    #Nodo que representa un parámetro de función
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre

class NodoAsignacion(NodoAST):
    def __init__(self, nombre, expresion):
        self.nombre = nombre
        self.expresion = expresion

class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

class NodoRetorno(NodoAST):
    #Nodo que representa a la sentencia return
    def __init__(self, expresion):
        self.expresion = expresion
class NodoIdentificador(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor



