# Compilador CalcLang 2.0

Mini compilador para a linguagem fictícia **CalcLang 2.0**, desenvolvido em Python. O projeto implementa as três fases fundamentais de um compilador (análise léxica, sintática e semântica) e gera código equivalente em Python como saída.

### Membros do Grupo

- João Victor Lima Almeida Puglies
- Thayná Carnaúba Dantas
- José Lucas da Silva Cardoso

---

## Sumário

- [Arquitetura da Solução](#arquitetura-da-solução)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Decisões de Implementação](#decisões-de-implementação)
- [Estruturas de Dados Utilizadas](#estruturas-de-dados-utilizadas)
- [Fases do Compilador](#fases-do-compilador)
  - [Fase 1 — Análise Léxica (Lexer)](#fase-1--análise-léxica-lexer)
  - [Fase 2 — Análise Sintática (Parser)](#fase-2--análise-sintática-parser)
  - [Fase 3 — Análise Semântica](#fase-3--análise-semântica)
  - [Fase 4 — Geração de Código Python](#fase-4--geração-de-código-python)
- [Como Executar](#como-executar)
- [Exemplo de Execução](#exemplo-de-execução)
- [Perguntas Conceituais](#perguntas-conceituais)

---

## Arquitetura da Solução

O compilador segue uma arquitetura de **pipeline sequencial**, onde a saída de cada fase é a entrada da próxima. O fluxo completo é:

```
entrada.calc → Lexer → Parser → Analisador Semântico → Gerador de Código → saida.py
```

Cada fase é implementada em um módulo Python separado, garantindo coesão e baixo acoplamento. O módulo `main.py` atua como **orquestrador**, invocando cada fase em sequência e interrompendo a compilação caso erros sejam encontrados em qualquer etapa.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Lexer     │────▶│   Parser    │────▶│  Semântico   │────▶│  Tradutor   │
│ (lexer.py)  │     │ (parser.py) │     │(semantic.py) │     │(translator) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
  Código fonte        Lista de           Instruções          Tabela de        Código
  → Tokens            Tokens →           válidas +           símbolos +       Python
                      Instruções         Tabela de           Instruções →
                                         Símbolos            saida.py
```

---

## Estrutura do Projeto

```
Mini Compilador/
├── main.py           # Orquestrador principal do compilador
├── lexer.py          # Análise léxica — transforma código fonte em tokens
├── parser.py         # Análise sintática — valida a gramática e gera instruções
├── semantic.py       # Análise semântica — verifica regras e mantém tabela de símbolos
├── translator.py     # Geração de código Python equivalente
├── entrada.calc      # Arquivo de entrada de teste (código CalcLang)
├── entrada.py        # Arquivo de saída esperado (referência)
└── saida.py          # Arquivo de saída gerado pelo compilador
```

---

## Decisões de Implementação

1. **Separação em módulos**: Cada fase do compilador vive em seu próprio arquivo (`lexer.py`, `parser.py`, `semantic.py`, `translator.py`), espelhando a separação conceitual clássica de compiladores e facilitando manutenção e testes independentes.

2. **Uso de `dataclass` e `Enum`**: Os tokens são modelados com `@dataclass` (classe `Token`) e seus tipos com `Enum` (`TokenType`). Isso garante tipagem clara, legibilidade e comparações seguras por tipo em vez de strings.

3. **Processamento caractere por caractere no Lexer**: O lexer percorre o código fonte caractere por caractere usando os métodos `peek()` e `advance()`, simulando o comportamento de um autômato finito. Essa abordagem é mais fiel ao funcionamento de lexers reais do que simplesmente usar `split()`.

4. **Parser por descida recursiva**: O parser implementa um analisador de **descida recursiva** (recursive descent) com funções específicas para cada tipo de instrução (`parse_set_instruction`, `parse_arithmetic_instruction`, `parse_print_instruction`). O método `parse_instruction()` despacha para a função correta conforme o token atual.

5. **Tratamento de erros por fase**: Cada fase coleta seus próprios erros em listas tipadas (`Token` de tipo `ERROR`, `SyntaxError`, `SemanticError`). O compilador interrompe a execução na primeira fase com erros, evitando cascata de falsos positivos.

6. **Divisão inteira**: A operação `DIV` gera o operador `//` em Python (divisão inteira), mantendo coerência com a linguagem CalcLang que trabalha apenas com números inteiros.

7. **Validação de divisão por zero**: O analisador semântico verifica divisão por zero em tempo de compilação, reportando erro semântico antes da geração de código.

---

## Estruturas de Dados Utilizadas

### Token (`lexer.py`)

```python
@dataclass
class Token:
    type: TokenType   # Tipo do token (SET, ADD, IDENTIFIER, NUMBER, etc.)
    value: str        # Valor literal extraído do código fonte
    line: int         # Número da linha onde o token aparece
    column: int       # Coluna onde o token começa
```

Representa a menor unidade léxica da linguagem. O enum `TokenType` define os tipos possíveis: `SET`, `ADD`, `SUB`, `MUL`, `DIV`, `PRINT`, `IDENTIFIER`, `NUMBER`, `EOF` e `ERROR`.

### Instruction (`parser.py`)

```python
@dataclass
class Instruction:
    type: str         # Tipo da instrução ("SET", "ADD", "PRINT", etc.)
    operands: List    # Lista de operandos (strings ou tuplas (tipo, valor))
    line: int         # Linha da instrução no código fonte
```

Representa uma instrução sintaticamente válida. Os operandos de operações aritméticas são armazenados como tuplas `('IDENTIFIER', nome)` ou `('NUMBER', valor)`, preservando a informação de tipo para uso na análise semântica.

### Symbol (`semantic.py`)

```python
@dataclass
class Symbol:
    name: str                  # Nome da variável
    value: Optional[int]       # Valor atribuído
    declared_at_line: int      # Linha em que foi declarada
    is_declared: bool          # Se foi formalmente declarada com SET
```

Representa uma entrada na tabela de símbolos.

### SymbolTable (`semantic.py`)

```python
class SymbolTable:
    symbols: Dict[str, Symbol]   # Dicionário nome → Symbol
```

A **tabela de símbolos** é implementada como um dicionário Python (`dict`). Oferece operações de:
- `declare_variable(name, value, line)` — registrar nova variável
- `is_declared(name)` — verificar se variável existe
- `get_variable(name)` — obter símbolo pelo nome
- `update_variable(name, value)` — atualizar valor
- `get_all_variables()` — listar todas as variáveis declaradas

A escolha por `dict` garante acesso O(1) por nome, eficiente para lookups frequentes durante a análise semântica.

---

## Fases do Compilador

### Fase 1 — Análise Léxica (Lexer)

**Arquivo:** `lexer.py`

O lexer recebe o código fonte como string e o percorre **caractere por caractere**, produzindo uma lista de tokens. Ele reconhece:

| Elemento             | Exemplo         | TokenType      |
|----------------------|-----------------|----------------|
| Palavras reservadas  | `SET`, `ADD`    | `SET`, `ADD`…  |
| Identificadores      | `a`, `total`    | `IDENTIFIER`   |
| Números inteiros     | `10`, `42`      | `NUMBER`       |
| Comentários          | `# comentário`  | (ignorados)    |
| Fim de arquivo       | —               | `EOF`          |

**Funcionamento:**
1. Pula espaços e tabulações (`skip_whitespace`)
2. Ignora quebras de linha e comentários (`#`)
3. Se encontra letra → lê identificador completo → verifica se é palavra reservada
4. Se encontra dígito → lê número completo
5. Se encontra caractere desconhecido → gera token de erro

**Exemplo:**

Entrada:
```
SET a 10
ADD a 5
```

Tokens gerados:
```
Token(SET, 'SET', linha=1, col=1)
Token(IDENTIFIER, 'a', linha=1, col=5)
Token(NUMBER, '10', linha=1, col=7)
Token(ADD, 'ADD', linha=2, col=1)
Token(IDENTIFIER, 'a', linha=2, col=5)
Token(NUMBER, '5', linha=2, col=7)
Token(EOF, '', linha=3, col=1)
```

---

### Fase 2 — Análise Sintática (Parser)

**Arquivo:** `parser.py`

O parser recebe a lista de tokens e verifica se as instruções seguem a **gramática** da linguagem CalcLang 2.0. A gramática aceita é:

```
programa     → instrução*
instrução    → set_instr | arith_instr | print_instr
set_instr    → SET IDENTIFIER NUMBER
arith_instr  → (ADD | SUB | MUL | DIV) operando operando
print_instr  → PRINT IDENTIFIER
operando     → IDENTIFIER | NUMBER
```

**Funcionamento:**
- Implementa **descida recursiva**: o método `parse_instruction()` verifica o token atual e despacha para `parse_set_instruction()`, `parse_arithmetic_instruction()` ou `parse_print_instruction()`.
- Cada função consome os tokens esperados em sequência, reportando erro sintático com linha e coluna quando a estrutura não é válida.
- Gera uma lista de objetos `Instruction` para instruções válidas.

**Exemplo de erro sintático:**
```
SET 10 a
→ Erro sintático na linha 1, coluna 5: Esperado identificador após SET
```

---

### Fase 3 — Análise Semântica

**Arquivo:** `semantic.py`

Após a validação sintática, o analisador semântico verifica o **significado** das instruções usando a **tabela de símbolos**. Verificações realizadas:

| Regra                                                      | Exemplo de violação             |
|------------------------------------------------------------|---------------------------------|
| Variável deve ser declarada com `SET` antes do uso         | `ADD a 5` (sem `SET a` antes)  |
| Nome de variável não pode ser palavra reservada            | `SET ADD 10`                    |
| Variável não pode ser declarada duas vezes                 | `SET a 10` seguido de `SET a 5`|
| `PRINT` aceita apenas variáveis declaradas                 | `PRINT x` (sem `SET x` antes)  |
| Divisão por zero é proibida                                | `DIV a 0`                       |

**Funcionamento:**
1. Percorre a lista de instruções na ordem
2. Para `SET`: verifica nome válido, registra na tabela de símbolos
3. Para `ADD/SUB/MUL/DIV`: verifica se operandos-identificador estão declarados, calcula resultado
4. Para `PRINT`: verifica se a variável está declarada
5. Instruções válidas são adicionadas à lista `valid_instructions`

**Exemplo de erro semântico:**
```
ADD a 10
→ Erro semântico na linha 1: variável 'a' não declarada
```

---

### Fase 4 — Geração de Código Python

**Arquivo:** `translator.py`

O gerador de código recebe as instruções validadas e a tabela de símbolos, produzindo código Python equivalente:

| CalcLang          | Python gerado       |
|-------------------|---------------------|
| `SET a 10`        | `a = 10`            |
| `ADD a b`         | `a + b`             |
| `SUB a 5`         | `a - 5`             |
| `MUL a b`         | `a * b`             |
| `DIV a 2`         | `a // 2`            |
| `PRINT a`         | `print(a)`          |

O código gerado é escrito no arquivo de saída (por padrão `saida.py`).

---

## Como Executar

**Pré-requisito:** Python 3.7 ou superior.

```bash
# Compilar o arquivo de entrada padrão
python main.py entrada.calc

# Compilar especificando arquivo de saída
python main.py entrada.calc saida.py
```

---

## Exemplo de Execução

**Arquivo de entrada (`entrada.calc`):**
```
SET a 10
SET b 5
ADD a b
PRINT a
```

**Saída no terminal:**
```
============================================================
COMPILADOR CALCLANG 2.0
============================================================

[1] Lendo arquivo: entrada.calc
    ✓ Arquivo lido com sucesso

[2] ANÁLISE LÉXICA (Lexer)
------------------------------------------------------------
    ✓ 9 tokens gerados
      Token(SET, 'SET', linha=1, col=1)
      Token(IDENTIFIER, 'a', linha=1, col=5)
      Token(NUMBER, '10', linha=1, col=7)
      Token(SET, 'SET', linha=2, col=1)
      Token(IDENTIFIER, 'b', linha=2, col=5)
      Token(NUMBER, '5', linha=2, col=7)
      Token(ADD, 'ADD', linha=3, col=1)
      Token(IDENTIFIER, 'a', linha=3, col=5)
      Token(IDENTIFIER, 'b', linha=3, col=7)

[3] ANÁLISE SINTÁTICA (Parser)
------------------------------------------------------------
    ✓ 4 instruções parsidas

[4] ANÁLISE SEMÂNTICA e TABELA DE SÍMBOLOS
------------------------------------------------------------
    ✓ Análise semântica concluída

[5] TABELA DE SÍMBOLOS (Symbol Table)
------------------------------------------------------------
    Variáveis declaradas: 2
      a = 10 (declarada na linha 1)
      b = 5 (declarada na linha 2)

[6] GERAÇÃO DE CÓDIGO PYTHON
------------------------------------------------------------
    Código Python gerado:
      a = 10
      b = 5
      a + b
      print(a)

============================================================
✓ COMPILAÇÃO BEM-SUCEDIDA!
============================================================
```

**Arquivo de saída gerado (`saida.py`):**
```python
a = 10
b = 5
a + b
print(a)
```

---

## Perguntas Conceituais

### a) Em qual fase do compilador ocorre a verificação de variável não declarada?

A verificação de variável não declarada ocorre na **Análise Semântica** (fase 3), implementada no arquivo `semantic.py`. Essa verificação depende da **tabela de símbolos**: ao encontrar um identificador em uma operação aritmética (`ADD`, `SUB`, `MUL`, `DIV`) ou em um comando `PRINT`, o analisador semântico consulta a tabela de símbolos (método `is_declared()`) para garantir que a variável foi previamente declarada com `SET`. Caso não tenha sido, um `SemanticError` é gerado indicando a linha do erro. Essa verificação não pode ser feita na análise léxica (que apenas identifica tokens) nem na análise sintática (que apenas valida a estrutura gramatical), pois requer conhecimento sobre o **contexto** do programa — quais variáveis existem naquele ponto da execução.

### b) Qual a diferença entre erro sintático e erro semântico neste contexto?

- **Erro sintático**: ocorre quando a **estrutura** de uma instrução não segue a gramática da linguagem. É detectado pelo **Parser**. Exemplo: `SET 10 a` — a gramática exige `SET IDENTIFIER NUMBER`, mas foi encontrado `SET NUMBER IDENTIFIER`. A ordem dos elementos está errada.

- **Erro semântico**: ocorre quando a estrutura está correta, mas o **significado** é inválido. É detectado pelo **Analisador Semântico**. Exemplo: `ADD x 5` — sintaticamente é válido (`ADD OPERAND OPERAND`), mas semanticamente é inválido se a variável `x` nunca foi declarada com `SET`.

Resumindo: o erro sintático é sobre **forma** (a instrução está mal formada), enquanto o erro semântico é sobre **sentido** (a instrução está bem formada, mas não faz sentido no contexto do programa).

### c) Qual o papel da tabela de símbolos em compiladores reais?

A tabela de símbolos é uma **estrutura de dados central** em compiladores reais, responsável por armazenar informações sobre todos os identificadores (variáveis, funções, classes, etc.) encontrados no programa. Seu papel inclui:

- **Registro de declarações**: armazena nome, tipo, escopo e localização de cada identificador.
- **Verificação de uso**: permite conferir se uma variável foi declarada antes de ser usada.
- **Resolução de tipos**: em linguagens tipadas, auxilia na verificação de compatibilidade de tipos em expressões e atribuições.
- **Gerenciamento de escopo**: em compiladores mais completos, mantém escopos aninhados (global, local, bloco) para resolver corretamente referências a variáveis.
- **Geração de código**: fornece informações necessárias para alocar memória e gerar referências corretas no código alvo (endereços de memória, registradores, offsets na pilha).

Neste projeto, a tabela de símbolos (`SymbolTable` em `semantic.py`) é implementada como um dicionário que mapeia nomes de variáveis para objetos `Symbol`, contendo valor e linha de declaração.

### d) Como o projeto precisaria evoluir para suportar escopo (ex.: blocos ou funções)?

Para suportar escopo, as seguintes modificações seriam necessárias:

1. **Tabela de símbolos com pilha de escopos**: em vez de um único dicionário, a tabela de símbolos passaria a manter uma **pilha (stack) de escopos**. Cada escopo seria um dicionário independente. Ao entrar em um bloco ou função, um novo escopo é empilhado; ao sair, ele é desempilhado. A busca por variáveis percorre a pilha do topo (escopo mais interno) até a base (escopo global).

2. **Novos comandos na linguagem**: seria necessário adicionar tokens e regras gramaticais para delimitar blocos (`BEGIN`/`END`, `{}`/`}`, ou indentação) e declarar funções (`FUNC nome ... END`).

3. **Atualização do Lexer**: reconhecer novos tokens como `FUNC`, `BEGIN`, `END`, `RETURN`, etc.

4. **Atualização do Parser**: implementar novas regras de gramática para blocos aninhados e definições de função, possivelmente migrando para uma estrutura de **árvore sintática abstrata (AST)** em vez de uma lista linear de instruções.

5. **Atualização da análise semântica**: ao analisar uma referência a variável, o analisador precisaria percorrer a pilha de escopos para resolver o identificador. Também seria necessário verificar regras como: variável local sobrepõe global, variável não pode ser usada fora de seu escopo, parâmetros de função são locais ao escopo da função.

6. **Atualização do gerador de código**: gerar indentação correta para blocos e funções em Python, além de lidar com `def`, `return` e chamadas de função.

---

## Documento de Apresentação

### Estrutura da Tabela de Símbolos

A tabela de símbolos é um **dicionário** (`Dict[str, Symbol]`) onde:
- **Chave**: nome da variável (string)
- **Valor**: objeto `Symbol` contendo `name`, `value`, `declared_at_line` e `is_declared`

Operações suportadas: declaração, consulta, atualização e listagem de variáveis. Acesso em tempo O(1).

### Estratégia de Verificação Semântica

O analisador semântico percorre as instruções **em ordem sequencial**, simulando a execução do programa:
- `SET`: valida que o nome não é palavra reservada nem duplicado, e registra na tabela de símbolos.
- `ADD/SUB/MUL/DIV`: verifica que todos os operandos identificadores estão declarados; verifica divisão por zero.
- `PRINT`: verifica que a variável está declarada.

Erros são coletados com indicação de linha. Apenas instruções válidas são passadas ao gerador de código.

### Organização das Fases do Compilador

| Fase                  | Módulo          | Entrada                 | Saída                              |
|-----------------------|-----------------|-------------------------|------------------------------------|
| Leitura               | `main.py`       | `entrada.calc`          | Código fonte (string)              |
| Análise Léxica        | `lexer.py`      | Código fonte            | Lista de tokens                    |
| Análise Sintática     | `parser.py`     | Lista de tokens         | Lista de instruções                |
| Análise Semântica     | `semantic.py`   | Lista de instruções     | Instruções válidas + tabela de símbolos |
| Geração de Código     | `translator.py` | Instruções + tabela     | Código Python (string)             |
| Escrita               | `main.py`       | Código Python           | `saida.py`                         |
