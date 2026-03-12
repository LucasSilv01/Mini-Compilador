import sys
from pathlib import Path
from typing import Optional
from lexer import analyze_lexical
from parser import analyze_syntax
from semantic import analyze_semantic
from translator import generate_code

class CompilerError(Exception):
    pass

class CalcLangCompiler:
    def __init__(self, source_file: str, output_file: Optional[str] = None):
        self.source_file = source_file
        if output_file is None:
            self.output_file = str(Path(source_file).with_suffix('.py'))
        else:
            self.output_file = output_file
        self.source_code = None
        self.errors = []
        self.warnings = []
    def read_source(self) -> bool:
        try:
            with open(self.source_file, 'r', encoding='utf-8') as f:
                self.source_code = f.read()
            return True
        except FileNotFoundError:
            self.errors.append(f"Arquivo não encontrado: {self.source_file}")
            return False
        except Exception as e:
            self.errors.append(f"Erro ao ler arquivo: {e}")
            return False
    def compile(self) -> bool:
        print("=" * 60)
        print("COMPILADOR CALCLANG 2.0")
        print("=" * 60)
        print()
        print(f"[1] Lendo arquivo: {self.source_file}")
        if not self.read_source():
            self.print_errors()
            return False
        print("    ✓ Arquivo lido com sucesso")
        print()
        print("[2] ANÁLISE LÉXICA (Lexer)")
        print("-" * 60)
        if self.source_code is None:
            self.errors.append("Código fonte não foi carregado")
            self.print_errors()
            return False
        tokens, lex_errors = analyze_lexical(self.source_code)
        if lex_errors:
            self.errors.extend([str(e) for e in lex_errors])
            self.print_errors()
            return False
        print(f"    ✓ {len(tokens) - 1} tokens gerados")
        for token in tokens[:-1]:
            print(f"      {token}")
        print()
        print("[3] ANÁLISE SINTÁTICA (Parser)")
        print("-" * 60)
        instructions, syn_errors = analyze_syntax(tokens)
        if syn_errors:
            self.errors.extend([str(e) for e in syn_errors])
            print(f"    ✗ {len(syn_errors)} erros sintáticos encontrados:")
            for error in syn_errors:
                print(f"      {error}")
            print()
            return False
        print(f"    ✓ {len(instructions)} instruções parsidas")
        for inst in instructions:
            print(f"      {inst.type} {inst.operands} (linha {inst.line})")
        print()
        print("[4] ANÁLISE SEMÂNTICA e TABELA DE SÍMBOLOS")
        print("-" * 60)
        valid_instructions, symbol_table, sem_errors = analyze_semantic(instructions)
        if sem_errors:
            self.errors.extend([str(e) for e in sem_errors])
            print(f"    ✗ {len(sem_errors)} erros semânticos encontrados:")
            for error in sem_errors:
                print(f"      {error}")
            print()
            return False
        print(f"    ✓ Análise semântica concluída")
        print()
        print("[5] TABELA DE SÍMBOLOS (Symbol Table)")
        print("-" * 60)
        symbols = symbol_table.get_all_variables()
        if symbols:
            print(f"    Variáveis declaradas: {len(symbols)}")
            for name, symbol in symbols.items():
                print(f"      {name} = {symbol.value} (declarada na linha {symbol.declared_at_line})")
        else:
            print("    Sem variáveis declaradas")
        print()
        print("[6] GERAÇÃO DE CÓDIGO PYTHON")
        print("-" * 60)
        generated_code = generate_code(valid_instructions, symbol_table)
        print("    Código Python gerado:")
        for line in generated_code.split('\n'):
            if line.strip():
                print(f"      {line}")
        print()
        print(f"[7] Escrevendo arquivo de saída: {self.output_file}")
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(generated_code)
            print("    ✓ Arquivo gerado com sucesso!")
            print()
        except Exception as e:
            self.errors.append(f"Erro ao escrever arquivo: {e}")
            self.print_errors()
            return False
        print("=" * 60)
        print("✓ COMPILAÇÃO BEM-SUCEDIDA!")
        print("=" * 60)
        return True
    def print_errors(self):
        if self.errors:
            print()
            print("ERROS ENCONTRADOS:")
            print("-" * 60)
            for error in self.errors:
                print(f"  ✗ {error}")
            print()

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_entrada.calc> [arquivo_saida.py]")
        print()
        print("Exemplo:")
        print("  python main.py entrada.calc")
        print("  python main.py entrada.calc saida.py")
        sys.exit(1)
    source_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    compiler = CalcLangCompiler(source_file, output_file)
    success = compiler.compile()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
