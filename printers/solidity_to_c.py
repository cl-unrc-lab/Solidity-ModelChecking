from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import networkx as nx
import rich_click as click
import wake.ir as ir
import wake.ir.types as types
from rich import print
from wake.cli import SolidityName
from wake.printers import Printer, printer

TYPE_MAP = {
    "uint8" : "uint8_t",
    "uint16" : "uint16_t",
    "uint32" : "uint32_t",
    "uint64" : "uint64_t",
    "int8" : "int8_t",
    "int16" : "int16_t",
    "int32" : "int32_t",
    "int64" : "int64_t",
    "int256" : "int64_t"
}

def c_type(sol_type: str) -> str:
    return TYPE_MAP[sol_type]

class SolidityToCPrinter(Printer):
    _code: Dict[Path, List[str]]

    def __init__(self) -> None:
        self._code = defaultdict(list)

    def visit_source_unit(self, node: ir.SourceUnit):
        lines = self._code[node.file]
        lines.append("#include <stdint.h>")
        lines.append("#include <stdbool.h>")
        lines.append("#include <stdio.h>\n")

    #TODO: Constructor del contrato.
    def visit_contract_definition(self, node: ir.ContractDefinition):
        lines = self._code[node.source_unit.file]
        lines.append(f"typedef struct {node.name} {{")
        
        # TODO: Variables declaradas con valor inicial
        for variable in node.declared_variables:
            lines.append(f"\t{c_type(variable.type_string)} {variable.name};")

        lines.append(f"}}{node.name};\n")

    def visit_function_definition(self, node: ir.FunctionDefinition):
        lines = self._code[node.source_unit.file]

        #TODO: Terminar con el resto de tipos de funciones
        match node.kind:
            case ir.enums.FunctionKind.FALLBACK:
                pass
            case ir.enums.FunctionKind.FUNCTION:
                return_type = ""
                return_variables = node.return_parameters.parameters

                if len(return_variables) == 1:
                    return_type = c_type(return_variables[0].type_string)
                elif len(return_variables) == 0:
                    return_type = "void"
                else:
                    lines.append(f"typedef struct ret_{node.name} {{")
                    for variable in return_variables:
                        lines.append(f"\t{c_type(variable.type_string)} {variable.name};")
                    lines.append(f"}}ret_{node.name};\n")
                    return_type = f"ret_{node.name}"

                lines.append(f"{return_type} {node.name}(")

                function_parameters = node.parameters.parameters
                for param in function_parameters:
                    if param != function_parameters[-1]:
                        lines[-1] += f"{param.type_string} {param.name},"
                    else:
                        lines[-1] += f"{param.type_string} {param.name}"
                lines[-1] += ")\n{\n"
                #TODO: Crear función para la traducción de un block
                if node.implemented:
                    pass

                lines.append("}\n")


            case ir.enums.FunctionKind.FREE_FUNCTION:
                pass
            case ir.enums.FunctionKind.RECEIVE:
                pass 

    def print(self) -> None:
        output_dir = Path("output_c")
        output_dir.mkdir(parents=True, exist_ok=True)

        for sol_path, lines in self._code.items():
            c_file_path = output_dir / f"{sol_path.stem}.c"
            c_file_path.write_text("\n".join(lines), encoding="utf-8")
            self.console.print(f"[green]Archivo generado con éxito:[/green] {c_file_path}")

    @printer.command(name="solidity-to-c")
    def cli(self) -> None:
        pass
