# Photoshop 1.0 Refactoring & Modernization Plan

## 1. Executive Summary

This plan outlines the strategy to refactor and rewrite the Adobe Photoshop 1.0 codebase (written in Object Pascal and 68k Assembly) into a modern systems programming language (Rust or C++20). The goal is to preserve the original algorithmic intent and "feel" while leveraging modern hardware (GPU, Multi-threading, SIMD) and safety paradigms.

**Target Stack:**
*   **Language:** Rust (Recommended for safety/concurrency) or C++20 (Industry standard).
*   **Graphics API:** WGPU (WebGPU native) or Vulkan.
*   **GUI Framework:** Egui (Rust) or Dear ImGui (C++) for a tool-based UI, or Qt for a full native app.
*   **Build System:** Cargo (Rust) or CMake (C++).

---

## 2. Codebase Archeology (Current State)

The current codebase is a product of 1990 Macintosh constraints:
*   **`MPhotoshop.p` / `UPhotoshop.p`**: The Application Shell, tightly coupled to **MacApp** (Apple's legacy object-oriented framework) and the **Macintosh Toolbox** (QuickDraw, OSIntf).
*   **`UVMemory.p`**: A custom software virtual memory implementation. It manually pages 30KB blocks of image data to/from a temporary disk file because Macs back then had 4MB-8MB of RAM.
*   **`TImageView`**: Handles rendering using QuickDraw (2D raster API). It manages dithering (converting 24-bit color to 1-bit or 8-bit screens).
*   **`UFilters.p`**: Contains image processing algorithms (Gaussian Blur, Sharpen) often implemented in assembly for performance.

---

## 3. Modernization Strategy

### Phase 1: The Core Engine (LibPhotoshop)
*Goal: Decouple image logic from the UI and OS.*

1.  **Replace `UVMemory` with Modern Allocators**:
    *   **Legacy:** `TVMArray` manages manual paging.
    *   **Modern:** Use 64-bit address space. Map files directly to memory (`mmap`) or simply allocate `Vec<u8>` / `std::vector<uint8_t>`.
    *   *Action:* Create a `PixelBuffer` struct that holds raw image data (R, G, B, A).

2.  **Abstract the Image Model**:
    *   Port `TImageDocument` to a struct `ImageDocument`.
    *   Remove all dependencies on `TDocument` (MacApp).
    *   Implement Channels as separate planes or interleaved buffers (modern GPUs prefer interleaved RGBA, but image processing often prefers planar).

### Phase 2: The Rendering Pipeline
*Goal: Replace QuickDraw with a GPU-accelerated pipeline.*

1.  **Pipeline Setup**:
    *   Create a WGPU/Vulkan context.
    *   Upload `PixelBuffer` data to GPU Textures.

2.  **View Transformation**:
    *   Port `TImageView` logic (Zoom, Pan).
    *   Instead of software scaling (slow), use GPU texture sampling (bilinear/nearest).

3.  **Dithering (Optional but Retro)**:
    *   The original heavily relied on `TDitherTables`.
    *   Implement dithering as a **Fragment Shader** to emulate the retro look, or discard it for true 24-bit color.

### Phase 3: Tools & Input
*Goal: Reimplement the "Tool" metaphor.*

1.  **Tool State Machine**:
    *   Port the `ObeyMouseDown` logic.
    *   Create a generic `Tool` trait/interface (Brush, Marquee, Lasso).
    *   Implement `BrushTool`:
        *   **Legacy:** Modified pixels directly in `TVMArray` using CPU loops.
        *   **Modern:** Render brush stamps to a "Command Buffer" or compute shader, then blend into the image.

### Phase 4: Image Processing (Filters)
*Goal: Port algorithms from Pascal/Assembly to Compute Shaders.*

1.  **Convolution Engine**:
    *   Port `Do3by3Filter` (generic kernel) to a Compute Shader.
    *   This allows filters like Sharpen/Blur to run instantly on the GPU.

2.  **Port Specific Filters**:
    *   Gaussian Blur: Implement as a two-pass separable shader.
    *   Levels/Curves: Implement as a LUT (Look-Up Table) operation on the GPU.

---

## 4. Implementation Roadmap (Rust Example)

### Step 1: Project Setup
```rust
// Cargo.toml
[dependencies]
winit = "0.29"      // Window handling
wgpu = "0.19"       // Graphics
image = "0.24"      // File formats (PNG/JPG)
bytemuck = "1.14"   // Byte manipulation
```

### Step 2: The Pixel Buffer (Replacing UVMemory)
```rust
pub struct PixelBuffer {
    width: u32,
    height: u32,
    channels: u8,
    data: Vec<u8>, // The "Memory" - no more manual paging!
}

impl PixelBuffer {
    pub fn new(width: u32, height: u32) -> Self {
        // ... allocation ...
    }
    
    pub fn get_pixel(&self, x: u32, y: u32) -> [u8; 4] {
        // ... efficient access ...
    }
}
```

### Step 3: The Document Model
```rust
pub struct ImageDocument {
    layers: Vec<Layer>,
    active_layer_index: usize,
    selection: SelectionMask,
}
```

---

## 5. Challenges & Considerations

1.  **Legacy Formats**:
    *   Photoshop 1.0 had specific handling for PICT, MacPaint, and early TIFF.
    *   *Solution:* Use a modern library (like Rust's `image` crate) for I/O, but write a custom parser if opening original PS 1.0 raw files is required.

2.  **The "Feel"**:
    *   Modern GPUs are "too smooth". To replicate 1.0 exactly, we must disable anti-aliasing and use Nearest Neighbor interpolation.

3.  **Assembly Blocks**:
    *   The `.a` files contain hand-optimized loops.
    *   *Action:* Do not port assembly line-by-line. Understand the *math* (e.g., "Add value X to every pixel"), then write that in high-level Rust/C++. The compiler or GPU will optimize it better than 1990s assembly.
