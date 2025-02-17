#Analisis léxico
#Definir los patrones
import re

token_patron = {
    "KEYWORD": r"\b(if|else|while|return|int|float|void|for|print)\b",
    "IDENTIFIER": r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
    "NUMBER": r"\b\d+(\.\d+)?\b",
    "OPERATOR": r"(==|!=|>=|<=|\+=|-=|\*=|/=|\+\+|--|[+\-*/=<>])",
    "DELIMITER": r"[(),;{}]",
    "WHITESPACE": r"\s+",
}


def identificar(texto):
    #Unir todos los patrones en un único patrón utilizando grupos nombrados
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    #print(patron_general)
    patron_regex = re.compile(patron_general)
    tokens_encontrados = []
    for match in patron_regex.finditer(texto):
        for token, valor in match.groupdict().items():
            if valor is not None and token != "WHITESPACE":
                tokens_encontrados.append((token,valor))
    return tokens_encontrados

#Analizador sintáctico
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def obtener_token_actual(self):
        return self.tokens[self.pos]  if self.pos < len(self.tokens) else None

    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == tipo_esperado:  # Solo para verificar que haya algo, y no sea None
            self.pos += 1
            return token_actual
        raise SyntaxError(f'Error Sintáctico, se esperaba {tipo_esperado}, pero se encontró {token_actual}')

    def parsear(self):
        #Punto de entrada, se espera una función
        self.funcion()

    def funcion(self):
        self.coincidir("KEYWORD")  # Tipo de retorno (ej. int)
        self.coincidir("IDENTIFIER")  # Nombre de la función
        self.coincidir("DELIMITER")  # Se espera '('
        self.parametros()
        self.coincidir("DELIMITER")  # Se espera ')'

        # Asegurar que se consume `{`
        self.coincidir("DELIMITER")  # Consumir `{`, sin necesidad de chequeo adicional

        self.cuerpo()  # Analizar el cuerpo de la función
        self.coincidir("DELIMITER")  # Se espera `}`

    def parametros(self):
        # Si hay al menos un parámetro, procesarlo
        if self.obtener_token_actual() and self.obtener_token_actual()[0] == "KEYWORD":
            self.coincidir("KEYWORD")  # Tipo del parámetro (ej. int)
            self.coincidir("IDENTIFIER")  # Nombre del parámetro (ej. a)

            # Mientras haya una coma, seguir procesando más parámetros
            while self.obtener_token_actual() and self.obtener_token_actual()[1] == ",":
                self.coincidir("DELIMITER")  # Consumir la coma
                self.coincidir("KEYWORD")  # Consumir el tipo del siguiente parámetro
                self.coincidir("IDENTIFIER")  # Consumir el nombre del siguiente parámetro

    def asignacion(self):
        self.coincidir("KEYWORD")  # Tipo de dato (ej. int)
        self.coincidir("IDENTIFIER")  # Nombre de la variable

        # Aceptar operadores compuestos o el '=' simple
        if self.obtener_token_actual()[1] in ("=", "+=", "-=", "*=", "/="):
            self.coincidir("OPERATOR")  # Consumir el operador de asignación
            self.expresion()  # Procesar la expresión de asignación
            self.coincidir("DELIMITER")  # Se espera ";"
        else:
            raise SyntaxError(
                f"Error Sintáctico: Se esperaba un operador de asignación, pero se encontró {self.obtener_token_actual()}")

    def expresion(self):
        self.expresion_aritmetica()
        # Si después de una expresión aritmética hay un operador relacional, procesarlo
        while self.obtener_token_actual() and self.obtener_token_actual()[1] in ('>', '<', '>=', '<=', '==', '!='):
            self.coincidir("OPERATOR")  # Consumir operador relacional
            self.expresion_aritmetica()  # Evaluar la segunda parte de la comparación

    def expresion_relacional(self):
        self.termino()
        while self.obtener_token_actual() and self.obtener_token_actual()[1] in ('>', '<', '>=', '<=', '==', '!='):
            self.coincidir("OPERATOR")  # Consumir operador relacional
            self.termino()

    def expresion_aritmetica(self):
        self.termino()
        while self.obtener_token_actual() and self.obtener_token_actual()[1] in "+-":
            self.coincidir("OPERATOR")  # Consumir '+' o '-'
            self.termino()

    def termino(self):
        self.factor()
        while self.obtener_token_actual() and self.obtener_token_actual()[1] in "*/":
            self.coincidir("OPERATOR")  # Consumir `*` o `/`
            self.factor()

    def factor(self):
        if self.obtener_token_actual()[0] == "IDENTIFIER" or self.obtener_token_actual()[0] == "NUMBER":
            self.coincidir(self.obtener_token_actual()[0])  # Consumir número o variable
        elif self.obtener_token_actual()[1] == "(":
            self.coincidir("DELIMITER")  # Consumir "("
            self.expresion()
            self.coincidir("DELIMITER")  # Consumir ")"
        else:
            raise SyntaxError(
                f"Error Sintáctico: Se esperaba un número, variable o paréntesis, pero se encontró {self.obtener_token_actual()}")

    def retorno(self):
        self.coincidir("KEYWORD")  # Consumir `return`
        self.expresion()  # Procesar la expresión de retorno
        self.coincidir("DELIMITER")  # Consumir `;`

    def cuerpo(self):
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != "}":
            token_actual = self.obtener_token_actual()

            if token_actual[0] == "KEYWORD":
                if token_actual[1] == "return":
                    self.retorno()
                elif token_actual[1] == "print":
                    self.print_stmt()
                elif token_actual[1] == "for":
                    self.for_stmt()
                elif token_actual[1] == "if":
                    self.if_stmt()
                elif token_actual[1] == "while":
                    self.while_stmt()
                else:
                    self.asignacion()  # Declaración de variables
            elif token_actual[0] == "IDENTIFIER":
                self.asignacion_simple()  # Asignación o incremento simple
            else:
                raise Exception(f"Error Sintáctico inesperado: {token_actual}")

    def asignacion_simple(self):
        self.coincidir("IDENTIFIER")  # Consumir la variable

        if self.obtener_token_actual()[0] == "OPERATOR":
            if self.obtener_token_actual()[1] in ("++", "--"):
                self.coincidir("OPERATOR")  # Consumir incremento o decremento
                self.coincidir("DELIMITER")  # Consumir ';'
            elif self.obtener_token_actual()[1] == "=":
                self.coincidir("OPERATOR")  # Consumir '='
                self.expresion()  # Evaluar la expresión de asignación
                self.coincidir("DELIMITER")  # Consumir ';'
            else:
                raise SyntaxError(
                    f"Error Sintáctico: Se esperaba operador de asignación o incremento, pero se encontró {self.obtener_token_actual()}")
        else:
            raise SyntaxError(
                f"Error Sintáctico: Se esperaba operador después de la variable, pero se encontró {self.obtener_token_actual()}")

    def print_stmt(self):
        self.coincidir("KEYWORD")  # Consumir 'print'
        self.coincidir("DELIMITER")  # Consumir '('
        self.expresion()  # Evaluar la expresión dentro del print
        self.coincidir("DELIMITER")  # Consumir ')'
        self.coincidir("DELIMITER")  # Consumir ';'

    def for_stmt(self):
        self.coincidir("KEYWORD")  # Consumir 'for'
        self.coincidir("DELIMITER")  # Consumir '('

        self.asignacion()  # Inicialización
        self.expresion()  # Condición
        self.coincidir("DELIMITER")  # Consumir ';'

        self.actualizacion()  # Actualización
        self.coincidir("DELIMITER")  # Consumir ')'

        self.coincidir("DELIMITER")  # Consumir '{'
        self.cuerpo()  # Procesar el cuerpo del bucle
        self.coincidir("DELIMITER")  # Consumir '}'

    def actualizacion(self):
        if self.obtener_token_actual()[0] == "IDENTIFIER":
            self.coincidir("IDENTIFIER")  # Variable (ej. i)
            if self.obtener_token_actual()[1] in ("++", "--"):
                self.coincidir("OPERATOR")  # Consumir ++ o --
            else:
                self.coincidir("OPERATOR")  # Podría ser una asignación (ej. i = i + 1)
                self.expresion()
        else:
            raise SyntaxError(
                f"Error Sintáctico en la actualización del for: se esperaba una variable, pero se encontró {self.obtener_token_actual()}")

    def if_stmt(self):
        self.coincidir("KEYWORD")  # Consumir 'if'

        if not self.obtener_token_actual() or self.obtener_token_actual()[1] != '(':
            raise Exception(
                f"Error Sintáctico, se esperaba '(' después de 'if', pero se encontró {self.obtener_token_actual()}")

        self.coincidir("DELIMITER")  # Consumir '('
        self.expresion()  # Evaluar la condición

        if not self.obtener_token_actual() or self.obtener_token_actual()[1] != ')':
            raise Exception(
                f"Error Sintáctico, se esperaba ')' después de la condición, pero se encontró {self.obtener_token_actual()}")

        self.coincidir("DELIMITER")  # Consumir ')'

        if not self.obtener_token_actual() or self.obtener_token_actual()[1] != '{':
            raise Exception(
                f"Error Sintáctico, se esperaba '{{' para iniciar el bloque 'if', pero se encontró {self.obtener_token_actual()}")

        self.coincidir("DELIMITER")  # Consumir '{'
        self.cuerpo()  # Procesar el cuerpo del if

        if not self.obtener_token_actual() or self.obtener_token_actual()[1] != '}':
            raise Exception(
                f"Error Sintáctico, se esperaba '}}' para cerrar el bloque 'if', pero se encontró {self.obtener_token_actual()}")

        self.coincidir("DELIMITER")  # Consumir '}'

        # Revisar si hay un bloque 'else'
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == "else":
            self.coincidir("KEYWORD")  # Consumir 'else'

            if self.obtener_token_actual() and self.obtener_token_actual()[1] == "if":
                self.if_stmt()  # Soporte para 'else if'
            else:
                self.coincidir("DELIMITER")  # Consumir '{'
                self.cuerpo()  # Procesar el cuerpo del else

                if not self.obtener_token_actual() or self.obtener_token_actual()[1] != '}':
                    raise Exception(
                        f"Error Sintáctico, se esperaba '}}' para cerrar el bloque 'else', pero se encontró {self.obtener_token_actual()}")

                self.coincidir("DELIMITER")  # Consumir '}'

    def while_stmt(self):
        self.coincidir("KEYWORD")  # Consumir 'while'
        self.coincidir("DELIMITER")  # Consumir '('
        self.expresion()  # Evaluar la condición del bucle
        self.coincidir("DELIMITER")  # Consumir ')'

        self.coincidir("DELIMITER")  # Consumir '{'
        self.cuerpo()  # Procesar el cuerpo del bucle
        self.coincidir("DELIMITER")  # Consumir '}'







