# Adobe Photoshop 1.0.1 Source Code - Guide for Modern Developers

## Overview

This is the **original Adobe Photoshop 1.0.1 source code** (circa 1990), released by the Computer History Museum. It's a complete, working implementation of the first commercial version of Photoshop, written in **Pascal** for **classic Mac OS** (System 6/7 era).

## Historical Context

- **Language**: Pascal (Object Pascal variant)
- **Platform**: Classic Mac OS (pre-OS X)
- **Architecture**: 68k Macintosh (Motorola 68000 series)
- **Year**: 1990
- **License**: Non-commercial use only (Computer History Museum license)

## Architecture Overview

### Entry Point
- **`MPhotoshop.p`**: Main program entry point
  - Initializes the Macintosh Toolbox
  - Creates the `TPhotoshopApplication` object
  - Runs the main event loop

### Core Application Structure
- **`UPhotoshop.p`**: Main application class (`TPhotoshopApplication`)
  - Inherits from `TApplication` (MacApp framework)
  - Handles document management, menus, events
  - Manages the overall application lifecycle

### Key Architectural Patterns

#### 1. **Object-Oriented Pascal**
```pascal
TPhotoshopApplication = OBJECT (TApplication)
  PROCEDURE IPhotoshopApplication;
  PROCEDURE Terminate; OVERRIDE;
  ...
END;
```
- Uses Object Pascal (predecessor to modern OOP)
- Single inheritance via `OBJECT (ParentClass)`
- Method overriding with `OVERRIDE` keyword
- Initialization methods prefixed with `I` (e.g., `IPhotoshopApplication`)

#### 2. **Unit-Based Modularity**
The codebase is organized into **Units** (similar to modules/packages):
- **U** prefix = Unit (e.g., `UPhotoshop`, `UConstants`)
- **M** prefix = Main program (e.g., `MPhotoshop`)
- Units have `INTERFACE` and `IMPLEMENTATION` sections

#### 3. **File Format Abstraction**
- **`URootFormat.p`**: Base class for all file format handlers
- Format-specific implementations:
  - `UTIFFormat.p` - TIFF support
  - `UGIFFormat.p` - GIF support
  - `UEPSFormat.p` - EPS/PostScript support
  - `UInternal.p` - Native Photoshop format
  - `UMacPaint.p`, `UPixelPaint.p`, `UPixar.p`, etc.

#### 4. **Image Processing Pipeline**
- **`UVMemory.p`**: Virtual memory management for large images
- **`UScreen.p`**: Screen rendering and display
- **`USelect.p`**: Selection tools (marquee, lasso, magic wand)
- **`UDraw.p`**: Drawing operations (brush, pencil, airbrush)
- **`UFilters.p`**: Image filters (blur, sharpen, etc.)

## Key Components

### Image Representation
- **Channels**: Up to 16 channels per image (`kMaxChannels = 16`)
- **Color Modes**: 
  - Halftone, Monochrome, Indexed Color
  - RGB Color, CMYK Separations
  - HSL/HSB Separations, Multichannel
- **Bit Depth**: Supports various pixel depths (1, 2, 4, 8 bits)

### Tools & Operations

#### Selection Tools
- Marquee (rectangular/elliptical)
- Lasso (freehand selection)
- Magic Wand (color-based selection)
- Selection operations: grow, similar, inverse, feather

#### Drawing Tools
- Pencil, Brush, Airbrush
- Paint Bucket (fill)
- Line Tool
- Text Tool
- Clone Stamp

#### Image Adjustments
- **`UAdjust.p`**: Levels, brightness/contrast, color balance, hue/saturation
- **`UHistogram.p`**: Histogram analysis
- **`UTable.p`**: Lookup tables for color mapping

#### Filters
- **`UFilters.p`**: Core filter engine
- **`UFilter.p`**: Filter interface and management
- Filters include: Blur, Sharpen, Gaussian, Sobel, Median, Motion Blur, etc.

#### Transformations
- **`URotate.p`**: Rotation operations
- **`UResize.p`**: Resizing and resampling
- **`UCrop.p`**: Cropping
- **`UFloat.p`**: Floating selections and transformations

### Color Management
- **`USeparation.p`**: CMYK color separation
- **`UConvert.p`**: Color space conversions
- **`UDither.a`**: Dithering algorithms
- **`UScreen.p`**: Halftone screen generation

### File I/O
- **`URootFormat.p`**: Abstract base for all formats
- Format handlers implement read/write operations
- Supports multi-disk files (for large images on floppy disks!)
- Resource fork management (classic Mac OS feature)

### User Interface
- **`UBWDialog.p`**: Black & white dialog boxes
- **`UProgress.p`**: Progress indicators
- **`UPick.p`**: Color picker
- **`UCoords.p`**: Coordinate display
- **`UMagnification.p`**: Zoom controls

## Modern Developer Translation Guide

### Language Equivalents

| Classic Pascal | Modern Equivalent |
|----------------|-------------------|
| `UNIT` | Module/Package/Namespace |
| `OBJECT` | Class |
| `OVERRIDE` | `override` keyword |
| `PROCEDURE` | `void` function |
| `FUNCTION` | Function with return value |
| `VAR` | Variable declaration |
| `^` (pointer) | `*` (pointer) or references |
| `RECORD` | Struct/Class |
| `ARRAY [0..255]` | Array with bounds |

### Memory Management
- **Manual memory management**: `NewPtr`, `DisposePtr`
- **Handles**: Mac OS memory management (relocatable blocks)
- **Virtual Memory**: `UVMemory.p` implements custom VM for large images

### Event-Driven Architecture
```pascal
PROCEDURE TPhotoshopApplication.MainEventLoop; OVERRIDE;
```
- Classic Mac OS event model
- Event records contain mouse/keyboard events
- Menu commands dispatched via command numbers

### Build System
- **`Photoshop.make`**: Makefile for building
- Uses MPW (Macintosh Programmer's Workshop) build tools
- Segmented code (for memory-constrained systems)
- Resource files (`.r`) for UI elements

## Notable Implementation Details

### 1. **Segmented Architecture**
Code is organized into segments that can be loaded/unloaded:
- `ARes`, `ARes2`, `ARes3`, `ARes4`: Resource segments
- `AEncoded`: Encoded resources
- `AInit`, `ATerminate`: Initialization/cleanup

### 2. **Assembly Language Optimizations**
Many `.a` files contain assembly code for performance:
- `UAssembly.a`: General assembly routines
- `UDraw.a`, `UResize.a`, `URotate.a`: Optimized image operations
- `USelect.a`: Fast selection operations

### 3. **Plug-in Architecture**
- **`AcquireInterface.p`**: Scanner/input device interface
- **`ExportInterface.p`**: Export module interface
- **`FilterInterface.p`**: Filter plug-in interface

### 4. **Error Handling**
- Custom error codes (negative numbers, e.g., `errBadTIFF = -25210`)
- Error messages via resource strings
- `FailNil` macro for null pointer checks

### 5. **Constants & Configuration**
- **`UConstants.p`**: Centralized constants
  - Command numbers (menu commands)
  - File format codes
  - Error codes
  - Display modes

## File Naming Conventions

- **`.p`**: Pascal source files
- **`.a`**: Assembly source files
- **`.r`**: Resource files (dialogs, menus, strings)
- **`.inc`**: Include files (partial implementations)
- **`.inc1.p`**: First include file for a unit
- **`.make`**: Makefile/build configuration

## Key Algorithms

### Image Processing
- **Convolution**: Used in filters (Gaussian blur, sharpen)
- **Resampling**: Bilinear/bicubic for resize operations
- **Color Conversion**: RGB ↔ CMYK, RGB ↔ HSL
- **Dithering**: Ordered dither, Floyd-Steinberg

### Selection Algorithms
- **Magic Wand**: Flood fill with tolerance
- **Lasso**: Polygon/rasterization
- **Feather**: Gaussian blur on selection mask

## Limitations & Historical Constraints

1. **Memory**: Designed for systems with limited RAM (1-4MB typical)
2. **Storage**: Multi-disk file support for floppy disk era
3. **Display**: 8-bit color (256 colors) was high-end
4. **CPU**: Optimized for 68000/68020 processors
5. **No Layers**: Photoshop 1.0 had no layer support (added in v3.0)

## How to Approach This Codebase

### For Learning
1. Start with `MPhotoshop.p` (entry point)
2. Read `UConstants.p` (understand the vocabulary)
3. Explore `UPhotoshop.p` (main application logic)
4. Pick a feature (e.g., filters) and trace through the code

### For Porting/Modernization
1. **Language**: Would need translation to C++/Rust/Modern language
2. **Platform**: Mac OS APIs → Cross-platform graphics library
3. **Memory**: Manual management → Smart pointers/GC
4. **UI**: Classic Mac Toolbox → Modern UI framework
5. **File Formats**: Update format handlers for modern standards

### For Understanding Image Processing
- Study `UFilters.p` for filter implementations
- Examine `USeparation.p` for color science
- Review `UResize.p` for resampling algorithms
- Check `UDither.a` for dithering techniques

## Dependencies

### Mac OS System Libraries
- **QuickDraw**: 2D graphics API
- **Toolbox**: OS services (files, windows, events)
- **MacApp**: Application framework (predecessor to Cocoa)

### Internal Frameworks
- **UObject, UList, UMacApp**: Object-oriented framework
- **UDialog, UPrinting**: UI components

## Build Requirements (Historical)

- **MPW** (Macintosh Programmer's Workshop)
- **Pascal Compiler** (Apple Pascal or compatible)
- **68k Macintosh** or emulator (System 6/7)
- **Resource Compiler** (Rez)

## Modern Equivalent Stack

If building Photoshop today, you'd likely use:
- **Language**: C++ or Rust
- **Graphics**: Metal/Vulkan/DirectX or OpenGL
- **UI**: Cocoa (macOS), WinUI (Windows), Qt/GTK (Linux)
- **Image Processing**: SIMD-optimized routines
- **File I/O**: Modern format libraries (libpng, libjpeg, etc.)

## Key Takeaways

1. **Modular Design**: Well-organized into units with clear responsibilities
2. **Performance Focus**: Assembly optimizations for critical paths
3. **Extensibility**: Plug-in architecture from day one
4. **Resource Constraints**: Designed for limited hardware
5. **Clean Abstractions**: Format handlers, tools, filters are well-separated

## Further Reading

- [Computer History Museum - Photoshop Source Code](http://computerhistory.org/atchm/adobe-photoshop-source-code/)
- Classic Mac OS Programming documentation
- MacApp framework documentation (if available)
- Pascal/Object Pascal language reference

---

**Note**: This codebase is a historical artifact. While it demonstrates excellent software engineering for its era, modern developers should understand it in context rather than using it as a template for new projects.
