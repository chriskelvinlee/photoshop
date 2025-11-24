#!/usr/bin/env python3
"""Generate Markdown documentation for Photoshop 1.0.1 public APIs."""
from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent.parent
UNIT_PATTERN = re.compile(r"\bUNIT\s+([A-Za-z0-9_]+)\s*;", re.IGNORECASE)
INTERFACE_PATTERN = re.compile(r"\bINTERFACE\b(.*?)(\bIMPLEMENTATION\b|\bEND\.)", re.IGNORECASE | re.DOTALL)
COMMENT_PAREN = re.compile(r"\(\*.*?\*\)", re.DOTALL)
COMMENT_BRACE = re.compile(r"\{(?!\$).*?\}", re.DOTALL)
USES_PATTERN = re.compile(r"\bUSES\b(.*?);", re.IGNORECASE | re.DOTALL)

@dataclass
class TypeInfo:
    name: str
    kind: str
    definition: str
    parent: Optional[str] = None
    fields: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    enum_members: List[str] = field(default_factory=list)

@dataclass
class UnitDoc:
    name: str
    path: Path
    uses: List[str]
    consts: List[str]
    vars: List[str]
    types: List[TypeInfo]
    routines: List[str]


def strip_comments(text: str) -> str:
    text = COMMENT_PAREN.sub("", text)
    text = COMMENT_BRACE.sub("", text)
    return text


def normalize(text: str) -> List[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = strip_comments(text)
    lines = [line.replace("\t", "    ") for line in text.splitlines()]
    return lines


def extract_interface(full_text: str) -> Optional[str]:
    match = INTERFACE_PATTERN.search(full_text)
    if not match:
        return None
    return match.group(1)


def parse_uses(interface_text: str) -> List[str]:
    uses: List[str] = []
    for block in USES_PATTERN.findall(interface_text):
        section = re.sub(r"\{\$.*?\}", "", block, flags=re.DOTALL)
        section = section.replace("\n", " ")
        tokens = [token.strip() for token in section.split(',')]
        for token in tokens:
            if not token:
                continue
            if token.upper().startswith("USES "):
                token = token[5:].strip()
            if not token:
                continue
            if token not in uses:
                uses.append(token)
    return uses


def collect_statement(lines: List[str], start_idx: int, initial: Optional[str] = None) -> tuple[str, int]:
    if initial is None:
        current = lines[start_idx].strip()
    else:
        current = initial.strip()
    buffer = [current]
    paren = current.count('(') - current.count(')')
    bracket = current.count('[') - current.count(']')
    record_depth = current.upper().count('RECORD') - current.upper().count('END')
    while True:
        trimmed = buffer[-1].strip()
        if paren <= 0 and bracket <= 0 and record_depth <= 0 and trimmed.endswith(';'):
            break
        start_idx += 1
        if start_idx >= len(lines):
            break
        next_line = lines[start_idx].strip()
        if not next_line or next_line.startswith('{$'):
            continue
        buffer.append(next_line)
        paren += next_line.count('(') - next_line.count(')')
        bracket += next_line.count('[') - next_line.count(']')
        record_depth += next_line.upper().count('RECORD') - next_line.upper().count('END')
    statement = ' '.join(part for part in buffer if part)
    statement = re.sub(r"\s+", " ", statement)
    return statement, start_idx


def collect_object_block(rest: str, lines: List[str], start_idx: int) -> tuple[str, int]:
    buffer = [rest.strip()]
    while True:
        start_idx += 1
        if start_idx >= len(lines):
            break
        segment = lines[start_idx].strip()
        if not segment or segment.startswith('{$'):
            continue
        buffer.append(segment)
        if segment.upper().startswith('END'):
            break
    return '\n'.join(buffer), start_idx


def detect_kind(body: str) -> str:
    stripped = body.strip().rstrip(';').strip()
    upper = stripped.upper()
    if stripped.startswith('('):
        return 'enum'
    if upper.startswith('PACKED ARRAY') or upper.startswith('ARRAY'):
        return 'array'
    if upper.startswith('PACKED SET') or upper.startswith('SET'):
        return 'set'
    if upper.startswith('RECORD'):
        return 'record'
    if stripped.startswith('^'):
        return 'pointer'
    if upper.startswith('PROCEDURE') or upper.startswith('FUNCTION'):
        return 'callback'
    return 'alias'


def parse_plain_type(name: str, body: str) -> TypeInfo:
    kind = detect_kind(body)
    enum_members: List[str] = []
    if kind == 'enum':
        contents = body.strip().rstrip(';').strip()
        contents = contents[1:-1] if contents.startswith('(') and contents.endswith(')') else contents
        enum_members = [member.strip() for member in contents.split(',') if member.strip()]
    return TypeInfo(name=name, kind=kind, definition=body, enum_members=enum_members)


def parse_object(name: str, block: str) -> TypeInfo:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    header = lines[0]
    parent = None
    match = re.search(r'OBJECT\s*\((.*?)\)', header, re.IGNORECASE)
    if match:
        parent = match.group(1).strip()
    fields: List[str] = []
    methods: List[str] = []
    idx = 1
    while idx < len(lines):
        line = lines[idx]
        upper = line.upper()
        if upper in {'PUBLIC', 'PRIVATE', 'PROTECTED'}:
            idx += 1
            continue
        if upper.startswith('PROCEDURE') or upper.startswith('FUNCTION'):
            statement, idx = collect_statement(lines, idx)
            statement = statement.replace(f'{name}.', '')
            methods.append(statement)
            idx += 1
            continue
        if upper.startswith('END'):
            break
        statement, idx = collect_statement(lines, idx)
        fields.append(statement)
        idx += 1
    return TypeInfo(name=name, kind='object', parent=parent, definition='OBJECT', fields=fields, methods=methods)


def parse_unit(path: Path, text: str) -> Optional[UnitDoc]:
    interface_text = extract_interface(text)
    if not interface_text:
        return None
    uses = parse_uses(interface_text)
    lines = normalize(interface_text)
    consts: List[str] = []
    vars_: List[str] = []
    types: List[TypeInfo] = []
    routines: List[str] = []

    state: Optional[str] = None
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if not line or line.startswith('{$'):
            idx += 1
            continue
        upper = line.upper()
        if upper.startswith('USES'):
            while idx < len(lines) and ';' not in lines[idx]:
                idx += 1
            idx += 1
            continue
        if upper.startswith('TYPE'):
            state = 'type'
            idx += 1
            continue
        if upper.startswith('CONST'):
            state = 'const'
            idx += 1
            continue
        if upper.startswith('VAR'):
            state = 'var'
            idx += 1
            continue
        if upper.startswith('IMPLEMENTATION') or upper.startswith('END.'):
            break

        if state == 'type':
            if upper.startswith(('CONST', 'VAR', 'PROCEDURE', 'FUNCTION')):
                state = None
                continue
            if '=' in line:
                left, right = line.split('=', 1)
                type_name = left.strip()
                body = right.strip()
                if not body:
                    idx += 1
                    continue
                if body.upper().startswith('OBJECT'):
                    block, idx = collect_object_block(body, lines, idx)
                    types.append(parse_object(type_name, block))
                    idx += 1
                    continue
                statement, idx = collect_statement(lines, idx, body)
                types.append(parse_plain_type(type_name, statement))
                idx += 1
                continue
            idx += 1
            continue

        if state == 'const':
            if upper.startswith(('TYPE', 'VAR', 'PROCEDURE', 'FUNCTION')):
                state = None
                continue
            statement, idx = collect_statement(lines, idx)
            consts.append(statement)
            idx += 1
            continue

        if state == 'var':
            if upper.startswith(('TYPE', 'CONST', 'PROCEDURE', 'FUNCTION')):
                state = None
                continue
            statement, idx = collect_statement(lines, idx)
            vars_.append(statement)
            idx += 1
            continue

        if upper.startswith(('PROCEDURE', 'FUNCTION')):
            statement, idx = collect_statement(lines, idx)
            tokens = statement.split()
            name_token = tokens[1] if len(tokens) > 1 else ''
            if '.' not in name_token:
                routines.append(statement)
            idx += 1
            continue

        idx += 1

    return UnitDoc(name=UNIT_PATTERN.search(text).group(1), path=path, uses=uses,
                   consts=consts, vars=vars_, types=types, routines=routines)


def humanize(identifier: str) -> str:
    cleaned = identifier
    if cleaned.startswith('U') and cleaned[1:2].isupper():
        cleaned = cleaned[1:]
    tokens = re.findall(r'[A-Z]+(?=[A-Z][a-z]|[0-9])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+', cleaned)
    if not tokens:
        return identifier
    return ' '.join(tokens)


def describe_unit(name: str) -> str:
    base = humanize(name)
    lowered = base.lower()
    if 'format' in lowered:
        return f"{base} file format handler"
    if 'filter' in lowered:
        return f"{base} filter or effect module"
    if 'dialog' in lowered or 'window' in lowered:
        return f"{base} dialog/UI helpers"
    if 'command' in lowered or 'select' in lowered or 'draw' in lowered:
        return f"{base} editing commands"
    if 'channel' in lowered or 'color' in lowered:
        return f"{base} channel/color management"
    if 'print' in lowered or 'post script' in lowered:
        return f"{base} printing pipeline"
    if 'memory' in lowered or 'progress' in lowered:
        return f"{base} infrastructure"
    return f"{base} module"


def format_list(items: List[str]) -> str:
    return ', '.join(f"`{item}`" for item in items)


def build_usage_section() -> str:
    examples = textwrap.dedent(
        """
        ## Usage Patterns & Examples

        ### Command Execution and History
        ```pascal
        procedure ApplyResize(view: TImageView);
        var
          command: TCommand;
        begin
          InitResize;
          command := DoResizeImage(view);
          if command <> NIL then
          begin
            command.DoIt;
            gHistory.Append(command);
          end;
        end;
        ```

        ### Filter Dispatch
        ```pascal
        procedure RunGaussian(view: TImageView; radius: INTEGER);
        var
          r: Rect;
        begin
          r := view^.VisibleRect;
          GaussianFilter(view^.PrimaryArray, r, radius, FALSE, TRUE);
          view^.Invalidate(r);
        end;
        ```

        ### File Format Registration
        ```pascal
        procedure BootstrapFormats;
        begin
          InitFormats; { allocates and registers URawFormat, UPICTFile, UTarga, etc. }
        end;
        ```

        ### Plug-in Acquisition Modules
        ```pascal
        procedure AcquireDocument(record: AcquireRecordPtr);
        begin
          record^.imageMode := acquireModeRGBColor;
          record^.abortProc := @CheckUserAbort;
          record^.progressProc := @ReportProgress;
          { supply image data via acquireSelectorStart/Continue callbacks }
        end;
        ```

        ### PostScript Export
        ```pascal
        procedure PrintPostScript(doc: TImageDocument; channel: INTEGER);
        var
          imageBounds: Rect;
        begin
          imageBounds := doc^.Bounds;
          BeginPostScript(FALSE, gPrintRefNum);
          GeneratePostScript(doc, channel, imageBounds, imageBounds, TRUE, TRUE, TRUE, FALSE, TRUE, TRUE);
          EndPostScript;
        end;
        ```
        """
    ).strip()
    return examples + "\n"


def render_type(type_info: TypeInfo) -> List[str]:
    lines: List[str] = []
    if type_info.kind == 'object':
        headline = f"- `{type_info.name}` object"
        if type_info.parent:
            headline += f" (extends `{type_info.parent}`)"
        lines.append(headline)
        if type_info.fields:
            field_lines = '\n'.join(f"  - field: `{field}`" for field in type_info.fields)
            lines.append(field_lines)
        if type_info.methods:
            method_lines = '\n'.join(f"  - method: `{method}`" for method in type_info.methods)
            lines.append(method_lines)
    elif type_info.kind == 'enum' and type_info.enum_members:
        members = ', '.join(f"`{member}`" for member in type_info.enum_members)
        lines.append(f"- `{type_info.name}` enum → {members}")
    else:
        lines.append(f"- `{type_info.name}` {type_info.kind}: `{type_info.definition}`")
    return lines


def render_unit(unit: UnitDoc) -> str:
    parts: List[str] = []
    parts.append(f"### {unit.name} (`{unit.path.name}`)")
    parts.append("")
    parts.append(f"**Purpose**: {describe_unit(unit.name)}")
    if unit.uses:
        parts.append(f"**Depends on**: {format_list(unit.uses)}")
    if unit.consts:
        parts.append("**Constants**:")
        for const in unit.consts:
            parts.append(f"- `{const}`")
    if unit.vars:
        parts.append("**Variables**:")
        for var in unit.vars:
            parts.append(f"- `{var}`")
    if unit.types:
        parts.append("**Types & Objects**:")
        for type_info in unit.types:
            parts.extend(render_type(type_info))
    if unit.routines:
        parts.append("**Routines**:")
        for routine in unit.routines:
            parts.append(f"- `{routine}`")
    parts.append("")
    return '\n'.join(parts)


def build_doc(units: List[UnitDoc]) -> str:
    header = textwrap.dedent(
        """
        # Photoshop 1.0.1 Public API Documentation

        Comprehensive reference of every Pascal unit that exposes a public interface in the original
        Photoshop 1.0.1 source tree. Each section lists the unit dependencies, exported constants,
        variables, types, objects, and callable routines. Use this alongside the implementation
        (`*.inc1.p` and related files) for behavioural details.
        """
    ).strip()

    architecture = textwrap.dedent(
        """
        ## Architecture Overview
        - `UPhotoshop`, `UCommands`, and `UProgress` provide the MacApp-based shell, command stack, and progress services.
        - Image manipulation is organised into command objects (`UResize`, `URotate`, `USelect`, `UDraw`, `UAdjust`, etc.). Each command exposes `DoIt/UndoIt/RedoIt` for history integration.
        - File formats live in dedicated units (`URawFormat`, `UPICTFile`, `UTarga`, `UPixelPaint`, `UTIFFormat`, etc.) and are registered via `UInitFormats.InitFormats`.
        - Filters bridge built-in kernels (`UFilter`, `UFilters`) and plug-in interfaces (`FilterInterface`).
        - Memory, virtual arrays, and scratch buffers are abstracted by `UVMemory`, `UFloat`, `UScreen`, and friends.
        - User interaction relies on dialog helpers (`UBWDialog`, `UDialog`, `UPasteControls`, `UPreferences`) plus acquisition/export plug-in contracts (`AcquireInterface`, `ExportInterface`).
        """
    ).strip()

    usage = build_usage_section()
    reference_sections = ['## Public API Reference']
    for unit in units:
        reference_sections.append(render_unit(unit))
    body = '\n\n'.join([header, architecture, usage, '\n'.join(reference_sections)])
    return body + '\n'


def main() -> None:
    units: List[UnitDoc] = []
    for path in sorted(ROOT.glob('*.p')):
        lower = path.name.lower()
        if '.inc' in lower:
            continue
        text = path.read_text(encoding='latin-1')
        if not UNIT_PATTERN.search(text):
            continue
        unit = parse_unit(path, text)
        if unit:
            units.append(unit)
    units.sort(key=lambda item: item.name.lower())
    docs_dir = ROOT / 'docs'
    docs_dir.mkdir(exist_ok=True)
    output = docs_dir / 'API_REFERENCE.md'
    output.write_text(build_doc(units), encoding='utf-8')
    print(f"Wrote {output.relative_to(ROOT)} with {len(units)} units")


if __name__ == '__main__':
    main()
