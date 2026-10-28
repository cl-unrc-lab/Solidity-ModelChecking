"""Esqueleto de la versión B (patrón visitor con traducción diferida).

Idea general:
- Wake llama a los visit_* en un orden no especificado y no devuelve valores.
- Fase 1 (visit_*): solo REGISTRAR los nodos.
- Fase 2 (print): traducir los nodos de MÁS profundo a MENOS profundo, así el
  texto de los hijos ya está listo (en un memo) cuando se traduce el padre.
- Fase 3 (print): ensamblar contratos y funciones en el buffer de cada archivo.
"""
from __future__ import annotations

from collections import defaultdict
from os import error
from pathlib import Path
from typing import Dict, List

import wake.ir as ir
from wake.printers import Printer, printer

INDENT = "  "

# Tipo de Solidity -> tipo de C.
TYPE_MAP = {
    "bool": "bool",
    "uint8": "uint8_t",
    "uint16": "uint16_t",
    "uint32": "uint32_t",
    "uint64": "uint64_t",
    "uint256": "uint64_t",
    "int8": "int8_t",
    "int16": "int16_t",
    "int32": "int32_t",
    "int64": "int64_t",
    "int256": "int64_t",
}


def c_type(sol_type: str) -> str:
    return TYPE_MAP.get(sol_type, f"/* {sol_type} */ int64_t")


def depth_of(node) -> int:
    # Profundidad del nodo en el árbol: cuántos .parent hay hasta llegar a la raíz
    # (parent is None). Sirve para ordenar de más profundo a menos profundo.
    d = 0
    while node.parent is not None:
        node = node.parent
        d += 1 
    return d


class SolidityToCPrinter(Printer):
    _code: Dict[Path, List[str]]

    def __init__(self) -> None:
        #  - _code: buffer de líneas por archivo
        #  - _pending: lista de sentencias y expresiones registradas
        #  - _contracts: lista de contratos visitados
        #  - _functions: funciones agrupadas por contrato (clave: id del contrato)
        #  - _memo: resultado de traducir cada nodo, clave id(nodo);
        #           expresiones -> str, sentencias -> List[str]
        self._code = defaultdict(list)
        self._pending : List = []
        self._contracts : List[ir.ContractDefinition] = []
        self._functions : Dict[int, List[ir.FunctionDefinition]] = defaultdict(list)
        self._memo : Dict[int, object] = {}

    # ------------------------------------------------------------------
    # Fase 1: visit_* (solo registran)
    # ------------------------------------------------------------------
    def visit_source_unit(self, node: ir.SourceUnit):
        lines = self._code[node.file]
        lines.append("#include <stdint.h>")
        lines.append("#include <stdbool.h>")
        lines.append("#include <stdio.h>\n")

    def visit_contract_definition(self, node: ir.ContractDefinition):
        # Registra el contrato en _contracts.
        self._contracts.append(node)    

    def visit_function_definition(self, node: ir.FunctionDefinition):
        # Registra la función bajo su contrato (node.parent) si ese padre es un
        # ContractDefinition; ignora las funciones libres por ahora.
        parent = node.parent
        if isinstance(parent, ir.ContractDefinition):
            self._functions[id(parent)].append(node)

    def visit_block(self, node: ir.Block):
        self._pending.append(node)

    def visit_variable_declaration_statement(self, node: ir.VariableDeclarationStatement):
        self._pending.append(node)

    def visit_expression_statement(self, node: ir.ExpressionStatement):
        self._pending.append(node)

    def visit_return(self, node: ir.Return):
        self._pending.append(node)

    def visit_if_statement(self, node: ir.IfStatement):
        self._pending.append(node)

    def visit_while_statement(self, node: ir.WhileStatement):
        self._pending.append(node)

    def visit_do_while_statement(self, node: ir.DoWhileStatement):
        self._pending.append(node)

    def visit_for_statement(self, node: ir.ForStatement):
        self._pending.append(node)

    def visit_break(self, node: ir.Break):
        self._pending.append(node)

    def visit_continue(self, node: ir.Continue):
        self._pending.append(node)

    def visit_literal(self, node: ir.Literal):
        self._pending.append(node)

    def visit_identifier(self, node: ir.Identifier):
        self._pending.append(node)

    def visit_assignment(self, node: ir.Assignment):
        self._pending.append(node)

    def visit_binary_operation(self, node: ir.BinaryOperation):
        self._pending.append(node)

    def visit_unary_operation(self, node: ir.UnaryOperation):
        self._pending.append(node)

    # Funciones auxiliares que manipulan el código ya traducido

    def _txt(self, node) -> str:
        return self._memo.get(id(node), f"/* TODO expr {type(node).__name__}: {node.source} */")

    def _lines(self, node) -> List[str]:
        return self._memo.get(id(node), [f"/* TODO stmt {type(node).__name__}: {node.source} */"])
 
    def _decl(self, v: ir.VariableDeclaration) -> str:
        return f"{c_type(v.type_string)} {v.name}"

    def _return_owner(self, v: ir.VariableDeclaration):
        plist = v.parent
        fn = plist.parent if plist is not None else None
        if isinstance(fn, ir.FunctionDefinition) and plist is fn.return_parameters:
            return fn
        return None

    def _enclosing_function(self, node):
        while node is not None and not isinstance(node, ir.FunctionDefinition):
            node = node.parent
        return node

    def _always_returns(self, node) -> bool:
        if isinstance(node, ir.Return):
            return True
        if isinstance(node, ir.Block):
            return any(self._always_returns(s) for s in node.statements)
        if isinstance(node, ir.IfStatement):
            return (
                node.false_body is not None
                and self._always_returns(node.true_body)
                and self._always_returns(node.false_body)
            )
        return False

    # Traducción de expresiones, sentencias y definiciones
    # Se traduce todo lo que queda pendiente, ya sea en pending, contracts o functions 
    def _tr_Literal(self, node: ir.Literal) -> str:
        if node.value is not None:
            return node.value

    def _tr_Identifier(self, node: ir.Identifier) -> str:
        ref = node.referenced_declaration
        if isinstance(ref, ir.VariableDeclaration):
            if ref.is_state_variable:
                return f"self->{node.name}"
            fn = self._return_owner(ref)
            if fn is not None and len(fn.return_parameters.parameters) >= 2:
                return f"_ret.{node.name}"
        return node.name

    def _tr_Assignment(self, node: ir.Assignment) -> str:
        left = self._txt(node.left_expression)
        right = self._txt(node.right_expression)
        return f"{left} {node.operator.value} {right}"

    def _tr_BinaryOperation(self, node: ir.BinaryOperation) -> str:
        left = self._txt(node.left_expression)
        right = self._txt(node.right_expression)
        if node.operator == ir.enums.BinaryOpOperator.EXP:
            return f"ipow({left}, {right})"
        return f"{left} {node.operator.value} {right}"

    def _tr_UnaryOperation(self, node: ir.UnaryOperation) -> str:
        sub_expr = self._txt(node.sub_expression)
        match node.operator:
            case ir.enums.UnaryOpOperator.DELETE:
                return f"TODO {node.operator.value}"
            case ir.enums.UnaryOpOperator.TILDE:
                return f"TODO {node.operator.value}"
        if not node.prefix:
            return f"{sub_expr}{node.operator.value}"
        return f"{node.operator.value}{sub_expr}"

    def _tr_ExpressionStatement(self, node: ir.ExpressionStatement) -> List[str]:
        return [f"{self._txt(node.expression)};"]

    def _tr_VariableDeclarationStatement(self, node: ir.VariableDeclarationStatement) -> List[str]:
        decls = [d for d in node.declarations if d is not None]
        if len(node.declarations) == 1 and decls:
            line = self._decl(decls[0])
            if node.initial_value is not None:
                line += f" = {self._txt(node.initial_value)}"
            return [line + ";"]
        out = [f"{self._decl(d)};" for d in decls]
        if node.initial_value is not None:
            out.append(f"/* TODO tupla: {node.source} */")
        return out

    def _tr_Return(self, node: ir.Return) -> List[str]:
        fn = self._enclosing_function(node)
        rets = fn.return_parameters.parameters
        ret_type = f"ret_{fn.parent.name}_{fn.name}"

        if len(rets) == 0:
            return ["return;"]

        if node.expression is None:                      # "return;"
            if len(rets) >= 2:
                return ["return _ret;"]
            return [f"return {rets[0].name or '0'};"]

        if len(rets) == 1:                               # "return x;"
            return [f"return {self._txt(node.expression)};"]

        exprs = node.expression.components               # "return (a, b);"
        fields = ", ".join(
            f".{self._ret_name(r, i)} = {self._txt(e)}"
            for i, (r, e) in enumerate(zip(rets, exprs))
        )
        return [f"return ({ret_type}){{ {fields} }};"]

    def _tr_IfStatement(self, node: ir.IfStatement) -> List[str]:
        out: List[str] = [f"if ({self._txt(node.condition)}) {{"]
        out += [INDENT + l for l in self._lines(node.true_body)]
        if node.false_body is not None:
            out.append("} else {")
            out += [INDENT + l for l in self._lines(node.false_body)]
        out.append("}\n")
        return out

    def _tr_WhileStatement(self, node: ir.WhileStatement) -> List[str]:
        out: List[str] = [f"while ({self._txt(node.condition)}) {{"]
        out += [INDENT + l for l in self._lines(node.body)]
        out.append("}\n")
        return out

    def _tr_DoWhileStatement(self, node: ir.DoWhileStatement) -> List[str]:
        out: List[str] = ["do {"]
        out += [INDENT + l for l in self._lines(node.body)]
        out.append(f"}} while ({self._txt(node.condition)});\n")
        return out

    def _inline(self, node) -> str:
        # Sentencia en una línea, sin ';' final (para la cabecera del for).
        if node is None:
            return ""
        return " ".join(self._lines(node)).rstrip(";")

    def _tr_ForStatement(self, node: ir.ForStatement) -> List[str]:
        init = self._inline(node.initialization_expression)
        cond = self._txt(node.condition) if node.condition is not None else ""
        step = self._inline(node.loop_expression)

        out: List[str] = [f"for ({init}; {cond}; {step}) {{"]
        if node.body is not None:
            out += [INDENT + l for l in self._lines(node.body)]
        out.append("}")
        return out

    def _tr_Break(self, node: ir.Break) -> List[str]:
        return ["break;"]

    def _tr_Continue(self, node: ir.Continue) -> List[str]:
        return ["continue;"]

    def _tr_Block(self, node: ir.Block) -> List[str]:
        out: List[str] = []
        for s in node.statements:
            out.extend(self._lines(s))
        return out

    def _tr_ContractDefinition(self, node: ir.ContractDefinition) -> List[str]:
        out = [f"typedef struct {node.name} {{"]
        out += [f"{INDENT}{self._decl(v)};" for v in node.declared_variables]
        out.append(f"}} {node.name};\n")
        return out
 
    def _ret_name(self, r: ir.VariableDeclaration, i: int) -> str:
        return r.name if r.name else f"_{i}"

    def _tr_FunctionDefinition(self, node: ir.FunctionDefinition) -> List[str]:
        contract = node.parent
        if node.kind != ir.enums.FunctionKind.FUNCTION:
            return []
        if not isinstance(contract, ir.ContractDefinition):
            return []

        fname = f"{contract.name}_{node.name}"
        rets = node.return_parameters.parameters
        out: List[str] = []

        if len(rets) == 0:
            ret_type = "void"
        elif len(rets) == 1:
            ret_type = c_type(rets[0].type_string)
        else:
            ret_type = f"ret_{fname}"
            out.append(f"typedef struct {ret_type} {{")
            out += [f"{INDENT}{c_type(r.type_string)} {self._ret_name(r, i)};"
                    for i, r in enumerate(rets)]
            out.append(f"}} {ret_type};\n")

        params = [f"{contract.name} *self"] + [self._decl(p) for p in node.parameters.parameters]
        out.append(f"{ret_type} {fname}({', '.join(params)}) {{")

        # Prólogo: retornos con nombre = locales con valor por defecto
        if len(rets) == 1 and rets[0].name:
            out.append(f"{INDENT}{ret_type} {rets[0].name} = 0;")
        elif len(rets) >= 2:
            out.append(f"{INDENT}{ret_type} _ret = {{0}};")

        if node.implemented and node.body is not None:
            out += [INDENT + l for l in self._lines(node.body)]
            falls_through = not self._always_returns(node.body)
        else:
            falls_through = True 

        # Epílogo: si el cuerpo termina sin return, se devuelve lo acumulado

        if falls_through:
            if len(rets) == 1 and rets[0].name:
                out.append(f"{INDENT}return {rets[0].name};")
            elif len(rets) >= 2:
                out.append(f"{INDENT}return _ret;")

        out.append("}\n")
        return out

    def print(self) -> None:
        # Fase 2: de más profundo a menos profundo
        for node in sorted(self._pending, key=depth_of, reverse=True):
            self._memo[id(node)] = getattr(self, f"_tr_{type(node).__name__}")(node)
 
        for contract in self._contracts:
            lines = self._code[contract.source_unit.file]
            lines.extend(self._tr_ContractDefinition(contract))
            for fn in self._functions[id(contract)]:
                lines.extend(self._tr_FunctionDefinition(fn))
 
        output_dir = Path("output_c")
        output_dir.mkdir(parents=True, exist_ok=True)
        for sol_path, lines in self._code.items():
            c_file_path = output_dir / f"{sol_path.stem}.c"
            c_file_path.write_text("\n".join(lines), encoding="utf-8")
            self.console.print(f"[green]Archivo generado con éxito:[/green] {c_file_path}")

    @printer.command(name="solidity-to-c")
    def cli(self) -> None:
        # Define el nombre del comando: wake print solidity-to-c-visitor
        pass
