#!/usr/bin/env python3
"""Extract named MANIFOLD_SOLID_BREP entities into standalone STEP files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REFERENCE_RE = re.compile(r"#(\d+)")
SOLID_NAME_RE = re.compile(r"^MANIFOLD_SOLID_BREP\('((?:''|[^'])*)'", re.DOTALL)
ENTITY_START_RE = re.compile(r"(?m)^\s*#(\d+)\s*=")


def parse_entities(data_section: str) -> dict[int, str]:
    entities: dict[int, str] = {}
    cursor = 0
    length = len(data_section)

    while cursor < length:
        match = ENTITY_START_RE.search(data_section, cursor)
        if not match:
            break
        entity_id = int(match.group(1))
        start = match.start()
        scan = match.end()
        in_string = False

        while scan < length:
            char = data_section[scan]
            if char == "'":
                if in_string and scan + 1 < length and data_section[scan + 1] == "'":
                    scan += 2
                    continue
                in_string = not in_string
            elif char == ";" and not in_string:
                scan += 1
                break
            scan += 1

        statement = data_section[start:scan].strip()
        entities[entity_id] = statement
        cursor = scan

    return entities


def dependency_closure(entities: dict[int, str], roots: set[int]) -> set[int]:
    selected: set[int] = set()
    pending = list(roots)
    while pending:
        entity_id = pending.pop()
        if entity_id in selected:
            continue
        if entity_id not in entities:
            raise ValueError(f"STEP reference #{entity_id} is missing from the source file")
        selected.add(entity_id)
        for reference in REFERENCE_RE.findall(entities[entity_id]):
            referenced_id = int(reference)
            if referenced_id != entity_id and referenced_id not in selected:
                pending.append(referenced_id)
    return selected


def escaped_step_string(value: str) -> str:
    return value.replace("'", "''")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("names", nargs="+")
    args = parser.parse_args()

    source_text = args.source.read_text(encoding="utf-8", errors="strict")
    header_match = re.search(r"\A(ISO-10303-21;\s*HEADER;.*?ENDSEC;)\s*DATA;", source_text, re.DOTALL)
    data_match = re.search(r"\bDATA;(.*)ENDSEC;\s*END-ISO-10303-21;\s*\Z", source_text, re.DOTALL)
    if not header_match or not data_match:
        raise ValueError("Source is not a supported ISO-10303-21 STEP exchange file")

    entities = parse_entities(data_match.group(1))
    solids: dict[str, int] = {}
    for entity_id, statement in entities.items():
        rhs = statement.split("=", 1)[1].lstrip()
        name_match = SOLID_NAME_RE.match(rhs)
        if name_match:
            solids[name_match.group(1).replace("''", "'")] = entity_id

    # The source assembly uses this geometric context for the four enclosure bodies.
    context_id = 441117
    if context_id not in entities:
        raise ValueError(f"Expected source geometric context #{context_id} was not found")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    wrapper_start = max(entities) + 100

    for offset, name in enumerate(args.names):
        if name not in solids:
            raise ValueError(f"Named solid {name!r} was not found")

        solid_id = solids[name]
        selected = dependency_closure(entities, {solid_id, context_id})
        base = wrapper_start + offset * 20
        safe_name = escaped_step_string(name)
        wrappers = {
            base + 0: f"#{base + 0}=APPLICATION_CONTEXT('automotive design');",
            base + 1: (
                f"#{base + 1}=APPLICATION_PROTOCOL_DEFINITION('international standard',"
                f"'automotive_design',2000,#{base + 0});"
            ),
            base + 2: f"#{base + 2}=PRODUCT_CONTEXT('',#{base + 0},'mechanical');",
            base + 3: f"#{base + 3}=PRODUCT('{safe_name}','{safe_name}','',(#{base + 2}));",
            base + 4: f"#{base + 4}=PRODUCT_DEFINITION_FORMATION('','',#{base + 3});",
            base + 5: f"#{base + 5}=PRODUCT_DEFINITION_CONTEXT('part definition',#{base + 0},'design');",
            base + 6: f"#{base + 6}=PRODUCT_DEFINITION('design','',#{base + 4},#{base + 5});",
            base + 7: f"#{base + 7}=PRODUCT_DEFINITION_SHAPE('','',#{base + 6});",
            base + 8: (
                f"#{base + 8}=ADVANCED_BREP_SHAPE_REPRESENTATION('',"
                f"(#{solid_id}),#{context_id});"
            ),
            base + 9: f"#{base + 9}=SHAPE_DEFINITION_REPRESENTATION(#{base + 7},#{base + 8});",
            base + 10: f"#{base + 10}=PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(#{base + 3}));",
        }

        output_header = re.sub(
            r"(?s)FILE_NAME\(.*?\);",
            (
                "FILE_NAME(\n"
                f"/* name */ '{safe_name}.step',\n"
                "/* time_stamp */ '2026-08-29T00:00:00-04:00',\n"
                "/* author */ (''),\n"
                "/* organization */ (''),\n"
                "/* preprocessor_version */ 'Named STEP solid extractor',\n"
                "/* originating_system */ 'ESP32-Walkie-Talkie-V2',\n"
                "/* authorisation */ '');"
            ),
            header_match.group(1),
            count=1,
        )

        output_entities = [entities[entity_id] for entity_id in sorted(selected)]
        output_entities.extend(wrappers[entity_id] for entity_id in sorted(wrappers))
        output_text = (
            output_header
            + "\n\nDATA;\n"
            + "\n".join(output_entities)
            + "\nENDSEC;\nEND-ISO-10303-21;\n"
        )

        output_path = args.output_dir / f"{name}.step"
        output_path.write_text(output_text, encoding="utf-8", newline="\n")

        written_entities = parse_entities(re.search(r"\bDATA;(.*)ENDSEC;", output_text, re.DOTALL).group(1))
        dangling = {
            int(reference)
            for statement in written_entities.values()
            for reference in REFERENCE_RE.findall(statement)
            if int(reference) not in written_entities
        }
        if dangling:
            raise ValueError(f"{output_path.name} has dangling STEP references: {sorted(dangling)[:10]}")
        print(f"{output_path}: {len(written_entities)} entities, solid #{solid_id}")


if __name__ == "__main__":
    main()
