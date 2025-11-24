## Photoshop Reimagination Plan (Swift + React/Electron)

### 1. Objectives
- Deliver a native-quality macOS experience optimized for Apple Silicon while retaining Photoshop 1.0 functionality.
- Separate the high-performance imaging core (Swift + Metal + Accelerate) from the cross-platform UI shell (React within Electron).
- Provide a pathway for incremental feature parity, automated testing, and future extensibility (plugins, scripting).

### 2. Guiding Principles
- **Native performance first:** pixel operations live in Swift packages using Metal compute kernels or Accelerate for fallback.
- **Modern modularity:** domain modules (documents, layers, tools, formats) exposed via Swift protocols + IPC-friendly APIs.
- **Deterministic undo/redo:** mirror the original command stack with value-based snapshots and diffed masks.
- **Automation-friendly:** headless CLI harness for regression tests and scripted benchmarks.

### 3. High-Level Architecture
- **Core Engine (Swift)**
  - Swift Package Manager workspace targeting macOS 14+; leverages Metal Performance Shaders for GPU pipelines.
  - Subpackages: `ImagingCore`, `Selections`, `Formats`, `UndoRedo`, `Persistence`.
  - Expose APIs via XPC and a thin C-ABI shim for Electron’s native-module bridge.
- **UI Shell (Electron + React)**
  - Electron main process handles windowing, file dialogs, and native menus (bridged to Swift commands).
  - React/TypeScript renderer renders toolbars, panels, canvas proxy; uses `CanvasKit`/WebGL for previews.
  - State lives in Redux Toolkit/Zustand with optimistic updates synced to the Swift engine.
- **Interop Layer**
  - Swift Package producing a Node native addon via `swift build --triple arm64-apple-macosx`.
  - Protobuf/FlatBuffers schemas define command payloads (selection ops, filters, document mutations).

### 4. Migration Strategy
1. **Inventory & Prioritize**
   - Catalog legacy modules (e.g., `USelect`, `UFilters`, `UTIFFormat`) and rank by impact.
   - Define MVP scope: document IO (PICT, TIFF), basic painting, selection tools, undo/redo.
2. **Data Model Port**
   - Translate `TVMArray` concept into Swift structs backed by Metal buffers + pageable storage.
   - Model documents, layers, channels, and masks with Codable structs for persistence tests.
3. **Command System**
   - Implement `Command` protocol mirroring `Do/Undo/Redo`; integrate with Combine for state updates.
   - Build selection + paint commands first (lasso, wand, bucket) using Swift + Metal compute shaders.
4. **File Formats**
   - Reuse legacy parsing knowledge to create Swift decoders; lean on CoreGraphics where possible.
   - Establish golden-file fixtures extracted from the original repo for regression comparisons.
5. **Electron Shell**
   - Scaffold Electron app with Vite + React, TypeScript strict mode, and Storybook for UI components.
   - Implement canvas host component that streams bitmap tiles from the Swift engine via shared textures or memory maps.
6. **Testing & Tooling**
   - Swift unit + performance tests (XCTest), GPU shader tests with Metal validation layer.
   - JS/TS tests via Vitest/Playwright; contract tests for IPC schemas.
7. **Performance Pass**
   - Profile with Instruments (Metal System Trace, Allocations) and optimize hotspots before feature-complete tag.

### 5. Milestones
| Milestone | Scope | Deliverables |
| --- | --- | --- |
| M0: Project Setup | Repos, build scripts, IPC scaffolding | SwiftPM workspace, Electron bootstrap, shared schema repo |
| M1: Core Imaging MVP | Document model, image buffers, undo/redo | Swift engine lib, CLI renderer, XCT regression tests |
| M2: Tooling & Selection | Lasso, marquee, wand, bucket | Metal kernels + React tool UI + round-trip undo |
| M3: File I/O | Import/export PICT, TIFF, PSD subset | Swift decoders, golden tests, Electron dialogs |
| M4: UI Polish | Layer palette, history panel, shortcuts | React components, state sync, theming |
| M5: Performance & Release Preview | Profiling, arm64 packaging, auto-updates | Signed Electron app, TestFlight-style distro |

### 6. Risks & Mitigations
- **Metal expertise gap:** schedule time for shader prototyping; pair with GPU engineer.
- **IPC latency:** use shared memory (IOSurface) for large pixel transfers; batch commands.
- **Electron bundle size:** tree-shake deps, lazy-load panels, enable sandboxing.
- **Legacy parity drift:** capture sample docs + behaviors from original code, automate screenshot diffs.

### 7. Next Actions
1. Stand up mono-repo (Git workspace with `swift/` and `app/` folders) and CI skeleton (GitHub Actions for Swift + JS).
2. Extract reference assets/tests from legacy repo into `/fixtures`.
3. Author initial technical design docs per module (Imaging Core, IPC, UI) before coding sprint kickoff.
