// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0 <0.8.0;

// Contrato de prueba para el traductor Solidity -> C.
// Cada función ejercita una forma distinta de declarar o usar retornos.
// Solo usa uint / bool (los tipos del TYPE_MAP).
contract Returns {
    uint total;

    // ------------------------------------------------------------------
    // 0 o 1 retorno  ->  en C: void / tipo directo
    // ------------------------------------------------------------------

    // 1. Sin retorno (void)
    function sinRetorno(uint x) public {
        total = x;
    }

    // 2. Un retorno sin nombre, con return explícito
    function unoSinNombre(uint x) public pure returns (uint) {
        return x + 1;
    }

    // 3. Un retorno con nombre, sin return (se devuelve al llegar al final)
    function unoConNombre(uint base, uint fee) public pure returns (uint suma) {
        suma = base + fee;
    }

    // 4. Un retorno con nombre que nunca se asigna (debe devolver 0)
    function unoPorDefecto() public pure returns (uint r) {
    }

    // 5. Un retorno con nombre y return explícito anticipado
    function unoAnticipado(uint x) public pure returns (bool exito) {
        if (x == 0) {
            return false;
        }
        exito = true;
    }

    // 6. "return;" vacío en una función con retorno con nombre
    function returnVacio(uint x) public pure returns (uint r) {
        r = 5;
        if (x == 0) {
            return r;
        }
        r = x;
    }

    // 7. Varios return en ramas (el return final queda fuera del if)
    function esPar(uint x) public pure returns (bool) {
        if (x % 2 == 0) {
            return true;
        }
        return false;
    }

    // 8. Un solo valor entre paréntesis (puede llegar como tupla de 1 componente)
    function unoEntreParentesis(uint x) public pure returns (uint) {
        return (x);
    }

    // 9. Devuelve una variable de estado
    function leerTotal() public view returns (uint) {
        return total;
    }

    // 10. Modifica estado y devuelve una variable con nombre
    function incrementar(uint x) public returns (uint nuevo) {
        total += x;
        nuevo = total;
    }

    // ------------------------------------------------------------------
    // 2 o más retornos  ->  en C: struct ret_Returns_<funcion>
    // ------------------------------------------------------------------

    // 11. Dos retornos sin nombre (campos _0 y _1)
    function dosSinNombre(uint x) public pure returns (uint, bool) {
        return (x, x > 0);
    }

    // 12. Tres retornos sin nombre
    function tresSinNombre() public pure returns (uint, uint, uint) {
        return (1, 2, 3);
    }

    // 13. Varios con nombre, asignados sin return
    function variosConNombre(uint x) public pure returns (uint a, uint b, bool c) {
        a = x;
        b = x * 2;
        c = x > 10;
    }

    // 14. Varios con nombre y return explícito con tupla
    function variosReturnTupla(uint x) public pure returns (uint a, uint b) {
        return (x, x + 1);
    }

    // 15. Tupla cruzada: return (y, x) con retornos llamados x e y.
    //     Comprueba que se evalúa todo antes de escribir (sin pisar valores).
    function intercambiados(uint a, uint b) public pure returns (uint x, uint y) {
        x = a;
        y = b;
        return (y, x);
    }

    // 16. Varios con nombre, return anticipado con tupla y asignación al final
    function anticipadoVarios(uint x) public pure returns (uint a, bool ok) {
        if (x == 0) {
            return (0, false);
        }
        a = x;
        ok = true;
    }

    // 17. "return;" vacío con varios retornos con nombre (devuelve lo acumulado)
    function returnVacioVarios(uint x) public pure returns (uint a, uint b) {
        a = 1;
        if (x == 0) {
            return (a,b);
        }
        b = x;
    }

    // ------------------------------------------------------------------
    // Del lado del llamador
    // ------------------------------------------------------------------

    // 18. Desestructuración completa con tipos
    function llamadorCompleto() public pure returns (uint) {
        (uint a, uint b, bool c) = variosConNombre(3);
        if (c) {
            return a;
        }
        return b;
    }

    // 19. Desestructuración con huecos
    function llamadorConHuecos() public pure returns (uint) {
        (, uint b, ) = variosConNombre(3);
        return b;
    }

    // 20. Asignación a variables ya declaradas (ExpressionStatement, no declaración)
    function llamadorAsignacion() public pure returns (uint) {
        uint a;
        uint b;
        bool c;
        (a, b, c) = variosConNombre(3);
        if (c) {
            return a;
        }
        return b;
    }

    // 21. Asignación a variables ya declaradas, con un hueco
    function llamadorAsignacionHueco() public pure returns (uint) {
        uint a;
        bool c;
        (a, , c) = variosConNombre(3);
        if (c) {
            return a;
        }
        return 0;
    }

    // 22. Intercambio de variables con tupla (no es una llamada)
    function intercambioLocal(uint x, uint y) public pure returns (uint, uint) {
        (x, y) = (y, x);
        return (x, y);
    }

    // 23. Funciones de un retorno usadas dentro de una expresión y de una condición
    function llamadorExpresion(uint x) public pure returns (uint) {
        if (esPar(x)) {
            return unoSinNombre(x) + unoConNombre(x, 1);
        }
        return 0;
    }
}
