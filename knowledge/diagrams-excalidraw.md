# Skill: Create Excalidraw Diagrams

## What this covers
Creating visual structure artifacts — architecture diagrams, flowcharts, data model schemas,
and process flows — as `.excalidraw` files that can be opened in Excalidraw or VS Code.

## When to use
When a task requires a diagram: system architecture, data flow, agent pipeline, process flow,
data model schema, or any visual that would otherwise be described in prose.

## How to do it

1. **Identify diagram type and entities** — what needs to be shown and how they relate
2. **Plan layout**: group related elements, left-to-right or top-to-bottom flow
3. **For complex diagrams**: describe the planned layout first (`STATUS: NEEDS_APPROVAL`);
   wait for confirmation before generating JSON
4. **Generate Excalidraw JSON** following the schema in `~/.claude/skills/excalidraw.md`
5. **Save .excalidraw file** to `~/.claude/data/Output/`
6. **Report file path** to Maarten

### Execution tool
The full Excalidraw element schema, Picnic color system, and JSON rules are in:
`~/.claude/skills/excalidraw.md`

Read that file before generating any diagram. It contains the complete schema.

Output directory: `~/.claude/data/Output/`
File naming: `<task-id>-<diagram-name>.excalidraw`

---

## Reference: Conventions & Patterns

### Core rules
- **Plan coordinates before writing JSON** — sketch the layout mentally first
- **Apply the Picnic color system** as defined in `excalidraw.md`
- **No free-floating text** — labels attach to shapes; arrows have clear source and target
- **Approval optional for simple diagrams** — generate directly; describe first for complex ones

### Diagram types and conventions

| Type | Layout direction | Key pattern |
|------|-----------------|-------------|
| Architecture | Left → Right | Layers as swimlanes |
| Data model | Top → Bottom | Tables as boxes, FK arrows |
| Process flow | Left → Right or Top → Down | Decision diamonds, parallelograms for I/O |
| Agent system | Top → Bottom | Orchestrator at top, agents below |
