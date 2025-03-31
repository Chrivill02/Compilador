import re
from NodosAST import *
import json

# === Analisis Lexico ===
token_patron = {
    "KEYWORD": r'\b(if|else|while|switch|case|return|print|break|for|int|float|void|double|char)\b',
    "IDENTIFIER": r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    "NUMBER": r'\b\d+(\.\d+)?\b',
    "OPERATOR": r'[\+\-\*\/\=\<\>\!\_]',
    "DELIMITER": r'[(),;{}]',
    "WHITESPACE": r'\s+',
    "STRING": r'"[^"]*"',  
}

def identificar_tokens(texto):
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)
    tokens_encontrados = []
    for match in patron_regex.finditer(texto):
        for token, valor in match.groupdict().items():
            if valor is not None and token != "WHITESPACE":
                tokens_encontrados.append((token, valor))
    return tokens_encontrados


# === Analizador Sintactico ===
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.funciones = []

    def obtener_token_actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == tipo_esperado:
            self.pos += 1
            return token_actual
        else:
            raise SyntaxError(f'Error sintactico: se esperaba {tipo_esperado}, pero se encontro: {token_actual}')

    def parsear(self):
        funciones = []
        while self.pos < len(self.tokens):
            funcion = self.funcion()
            funciones.append(funcion)

        if not any(funcion.nombre == 'main' for funcion in funciones):
            raise SyntaxError("Error sintactico: Debe existir una funcion 'main' en el codigo.")

        if funciones[-1].nombre != 'main':
            raise SyntaxError("Error sintactico: La funcion 'main' debe ser la ultima en el codigo.")

        return NodoPrograma(funciones)
    
    def llamada_funcion(self):
        nombre_funcion = self.coincidir('IDENTIFIER')
        self.coincidir('DELIMITER')  # '('
        argumentos = self.argumentos()
        self.coincidir('DELIMITER')  # ')'
        self.coincidir('DELIMITER')  # ';'
        return NodoLlamadaFuncion(nombre_funcion[1], argumentos)
    
    def argumentos(self):
        argumentos = []
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != ')':
            argumentos.append(self.expresion_ing())
            if self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
                self.coincidir('DELIMITER')
        return argumentos
    
    def funcion(self):
        tipo_retorno = self.coincidir('KEYWORD')
        nombre_funcion = self.coincidir('IDENTIFIER')
        self.coincidir('DELIMITER')  # '('
        parametros = self.parametros()
        self.coincidir('DELIMITER')  # ')'
        self.coincidir('DELIMITER')  # '{'
        cuerpo = self.cuerpo()
        self.coincidir('DELIMITER')  # '}'
        return NodoFuncion(nombre_funcion[1], parametros, cuerpo)

    def parametros(self):
        parametros = []
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != ')':
            tipo = self.coincidir('KEYWORD')
            nombre = self.coincidir('IDENTIFIER')
            parametros.append(NodoParametro(tipo[1], nombre[1]))
            if self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
                self.coincidir('DELIMITER')
        return parametros

    def declaracion(self):
        tipo = self.coincidir('KEYWORD')
        nombre = self.coincidir('IDENTIFIER')

        if self.obtener_token_actual() and self.obtener_token_actual()[1] == '=':
            self.coincidir('OPERATOR')
            expresion = self.expresion_ing()
            nodo = NodoAsignacion(nombre, expresion)
        else:
            nodo = NodoDeclaracion(tipo[1], nombre[1])

        self.coincidir('DELIMITER')
        return nodo

    def asignacion(self):
        # Manejar ambos casos: con y sin tipo
        token_actual = self.obtener_token_actual()
        if token_actual[0] == 'KEYWORD' and token_actual[1] in ['int', 'float', 'double', 'char']:
            tipo = self.coincidir('KEYWORD')
        else:
            tipo = None
        
        nombre = self.coincidir('IDENTIFIER')
        self.coincidir('OPERATOR')  # '='
        expresion = self.expresion_ing()
        self.coincidir('DELIMITER')  # ';'
        
        if tipo:
            return NodoDeclaracion(tipo[1], nombre[1], expresion)
        else:
            return NodoAsignacion(nombre, expresion)
    def retorno(self):
        self.coincidir('KEYWORD')
        expresion = self.expresion_ing()
        self.coincidir('DELIMITER')
        return NodoRetorno(expresion)

    def cuerpo(self):
        instrucciones = []  
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != '}':
            token_actual = self.obtener_token_actual()

            if token_actual[0] == 'DELIMITER' and token_actual[1] == ';':
                self.coincidir('DELIMITER')
                continue

            if token_actual[0] == 'KEYWORD':
                if token_actual[1] == 'if':
                    instrucciones.append(self.bucle_if())
                elif token_actual[1] == 'while':
                    instrucciones.append(self.bucle_while())
                elif token_actual[1] == 'for':
                    instrucciones.append(self.bucle_for())
                elif token_actual[1] == 'print':
                    instrucciones.append(self.printf_llamada())
                elif token_actual[1] == 'return':
                    instrucciones.append(self.retorno())
                elif token_actual[1] in ['int', 'float', 'void', 'double', 'char']:
                    instrucciones.append(self.declaracion())
                else:
                    raise SyntaxError(f'Keyword no reconocido: {token_actual}')

            elif token_actual[0] == 'IDENTIFIER':
                siguiente_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                if siguiente_token and siguiente_token[1] == '(':
                    instrucciones.append(self.llamada_funcion())
                else:
                    instrucciones.append(self.asignacion())

            elif token_actual[0] in ['NUMBER', 'STRING']:
                instrucciones.append(self.expresion_ing())
                self.coincidir('DELIMITER')

            else:
                raise SyntaxError(f'Se esperaba declaración válida: {token_actual}')

        return instrucciones
    def expresion_ing(self):
        izquierda = self.termino()
        while self.obtener_token_actual() and self.obtener_token_actual()[0] == 'OPERATOR':
            operador = self.coincidir('OPERATOR')
            derecha = self.termino()
            izquierda = NodoOperacion(izquierda, operador[1], derecha)
        return izquierda

    def termino(self):
        token = self.obtener_token_actual()
        if token[0] == 'NUMBER':
            return NodoNumero(self.coincidir('NUMBER'))
        elif token[0] == 'IDENTIFIER':
            return NodoIdentificador(self.coincidir('IDENTIFIER'))
        elif token[0] == 'STRING':
            return NodoString(self.coincidir('STRING'))
        else:
            raise SyntaxError(f'Error sintactico: Termino no valido {token}')
            
    def expresion(self):
        if self.obtener_token_actual()[0] in ['IDENTIFIER', 'NUMBER', 'STRING']:
            self.coincidir(self.obtener_token_actual()[0])
        else:
            raise SyntaxError(f"Error sintactico: Se esperaba IDENTIFIER, NUMBER o STRING, pero se encontro {self.obtener_token_actual()}")

        while self.obtener_token_actual() and self.obtener_token_actual()[0] in ['OPERATOR']:
            self.coincidir('OPERATOR')
            if self.obtener_token_actual()[0] in ['IDENTIFIER', 'NUMBER', 'STRING']:
                self.coincidir(self.obtener_token_actual()[0])
            else:
                raise SyntaxError(f"Error sintactico: Se esperaba IDENTIFIER, NUMBER o STRING despues de {self.obtener_token_anterior()}")

    def bucle_if(self):
        self.coincidir('KEYWORD')  # 'if'
        self.coincidir('DELIMITER')  # '('
        
        condicion = self.expresion_logica()
        
        self.coincidir('DELIMITER')  # ')'
        self.coincidir('DELIMITER')  # '{'
        
        cuerpo_if = self.cuerpo()
        
        self.coincidir('DELIMITER')  # '}'
        
        cuerpo_else = []
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == 'else':
            self.coincidir('KEYWORD')  # 'else'
            self.coincidir('DELIMITER')  # '{'
            cuerpo_else = self.cuerpo()
            self.coincidir('DELIMITER')  # '}'
        
        return NodoIf(condicion, cuerpo_if, cuerpo_else)

    def expresion_logica(self):
        izquierda = self.termino()
        
        if self.obtener_token_actual() and self.obtener_token_actual()[0] == 'OPERATOR':
            operador = self.coincidir('OPERATOR')
            
            if operador[1] in ['=', '!', '<', '>']:
                if self.obtener_token_actual() and self.obtener_token_actual()[1] == '=':
                    operador = (operador[0], operador[1] + self.coincidir('OPERATOR')[1])
            
            derecha = self.termino()
            return NodoOperacionLogica(izquierda, operador[1], derecha)
        
        return izquierda

    def printf_llamada(self):
        self.coincidir('KEYWORD')  # 'print'
        self.coincidir('DELIMITER')  # '('
        
        argumentos = []
        # Primer argumento
        if self.obtener_token_actual()[0] in ['STRING', 'IDENTIFIER', 'NUMBER']:
            argumentos.append(self.expresion_ing())
        
        # Argumentos adicionales
        while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
            self.coincidir('DELIMITER')  # ','
            argumentos.append(self.expresion_ing())
        
        self.coincidir('DELIMITER')  # ')'
        self.coincidir('DELIMITER')  # ';'
        
        return NodoPrint(argumentos)
    def bucle_for(self):
        self.coincidir('KEYWORD')  # 'for'
        self.coincidir('DELIMITER')  # '('
        
        # Inicialización (puede ser declaración o asignación)
        token_actual = self.obtener_token_actual()
        if token_actual[0] == 'KEYWORD' and token_actual[1] in ['int', 'float', 'double', 'char']:
            inicializacion = self.declaracion()
        else:
            # Es una asignación sin declaración de tipo
            nombre = self.coincidir('IDENTIFIER')
            self.coincidir('OPERATOR')  # '='
            expresion = self.expresion_ing()
            self.coincidir('DELIMITER')  # ';'
            inicializacion = NodoAsignacion(nombre, expresion)
        
        # Condición
        condicion = self.expresion_logica()
        self.coincidir('DELIMITER')  # ';'
        
        # Incremento
        nombre = self.coincidir('IDENTIFIER')
        self.coincidir('OPERATOR')  # '='
        expresion = self.expresion_ing()
        self.coincidir('DELIMITER')  # ')'
        incremento = NodoAsignacion(nombre, expresion)
        
        self.coincidir('DELIMITER')  # '{'
        cuerpo = self.cuerpo()
        self.coincidir('DELIMITER')  # '}'
        
        return NodoFor(inicializacion, condicion, incremento, cuerpo)
    
    def return_statement(self):
        self.coincidir('KEYWORD')
        self.expresion()
        self.coincidir('DELIMITER')

    def break_statement(self):
        self.coincidir('KEYWORD')
        self.coincidir('DELIMITER')

    def operador_abreviado(self):
        self.coincidir('IDENTIFIER')
        operador_actual1 = self.obtener_token_actual()
        self.coincidir('OPERATOR')
        operador_actual2 = self.obtener_token_actual()
        self.coincidir('OPERATOR')
        if operador_actual1[1] + operador_actual2[1] not in ['++','--', '+=', '-=', '*=', '/=']:
            raise SyntaxError(f'Error sintactico: se esperaba una declaracion valida, pero se encontro: {operador_actual1[1],operador_actual2[1]}')
        self.coincidir('DELIMITER')

    def bucle_while(self):
        self.coincidir('KEYWORD')  # 'while'
        self.coincidir('DELIMITER')  # '('
        
        condicion = self.expresion_logica()
        
        self.coincidir('DELIMITER')  # ')'
        self.coincidir('DELIMITER')  # '{'
        
        cuerpo = self.cuerpo()
        
        self.coincidir('DELIMITER')  # '}'
        
        return NodoWhile(condicion, cuerpo)

# === Ejemplo de Uso ===
codigo_fuente = """
void main() {
    int i;
    for(i = 0; i < 10; i = i + 1) {
        print("Contador: ", i, "\n");
    }
    
    int n = 5;
    while(n > 0) {
        print(n, "\n");
        n = n - 1;
    }
    
    return 0;
}
"""

tokens = identificar_tokens(codigo_fuente)
print("Tokens encontrados:")
for tipo, valor in tokens:
    print(f'{tipo}: {valor}')

try:
    print('\nIniciando analisis sintactico...')
    parser = Parser(tokens)
    arbol_ast = parser.parsear()
    print('Analisis sintactico completado sin errores')

except SyntaxError as e:
    print(e)
    
def imprimir_ast(nodo):
    if isinstance(nodo, NodoPrograma):
        return {
            "Programa": [imprimir_ast(f) for f in nodo.funciones] 
        }
    elif isinstance(nodo, NodoFuncion):
        return {
            "Funcion": nodo.nombre,
            "Parametros": [imprimir_ast(p) for p in nodo.parametros],
            "Cuerpo": [imprimir_ast(c) for c in nodo.cuerpo]
        }
    elif isinstance(nodo, NodoParametro):
        return {
            "Parametro": nodo.nombre,
            "Tipo": nodo.tipo
        }
    elif isinstance(nodo, NodoAsignacion):
        return {
            "Asignacion": nodo.nombre,
            "Expresion": imprimir_ast(nodo.expresion)
        }
    elif isinstance(nodo, NodoOperacion):
        return {
            "Operacion": nodo.operador,
            "Izquierda": imprimir_ast(nodo.izquierda),
            "Derecha": imprimir_ast(nodo.derecha)
        }
    elif isinstance(nodo, NodoOperacionLogica):
        return {
            "OperacionLogica": nodo.operador,
            "Izquierda": imprimir_ast(nodo.izquierda),
            "Derecha": imprimir_ast(nodo.derecha)
        }
    elif isinstance(nodo, NodoRetorno):
        return {
            "Retorno": imprimir_ast(nodo.expresion)
        }
    elif isinstance(nodo, NodoIdentificador):
        return {
            "Identificador": nodo.nombre
        }
    elif isinstance(nodo, NodoNumero):
        return {
            "Numero": nodo.valor
        }
    elif isinstance(nodo, NodoLlamadaFuncion):
        return {
            "LlamadaFuncion": nodo.nombre,
            "Argumentos": [imprimir_ast(arg) for arg in nodo.argumentos]
        }
    elif isinstance(nodo, NodoIf):
        return {
            "If": {
                "Condicion": imprimir_ast(nodo.condicion),
                "CuerpoIf": [imprimir_ast(i) for i in nodo.cuerpo_if],
                "CuerpoElse": [imprimir_ast(e) for e in nodo.cuerpo_else]
            }
        }
    return {}

parser = Parser(tokens)
arbol_ast = parser.parsear()    
print(json.dumps(imprimir_ast(arbol_ast), indent=1))

codigo_asm = arbol_ast.generar_codigo()
print("\nCódigo Ensamblador Generado:")
print(codigo_asm)



#------------------------------Analisis Semántico-----------------------------------------------------
class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = {}
    
    def analizar(self, nodo):
        metodo = f"Visitar:{type(nodo).__name__}"
        if hasattr(self,metodo)(nodo):
            return getattr(self, metodo)(nodo)
        else:
            raise Exception(f"No se ha implementado el análisis semántico para {type(nodo)}.__name__")

    def visitar_NodoFuncion(self,nodo):
        if nodo.nombre[1] in self.tabla_simbolos:
            raise Exception(f"Error semántico: la función {nodo.nombre[1]} ya está definida")
        
        self.tabla_simbolos[nodo.nombre[1]] = {"tipo": nodo.parametros[0].tipo[1], "parametros":nodo.parametros}
        for param in nodo.parametros:
            self.tabla_simbolos[param.nombre[1]] = {"tipo": param.tipo[1]} 
        
        for instruccion in nodo.cuerpo:
            self.analizar(instruccion)