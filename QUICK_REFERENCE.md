# Photoshop 1.0.1 Codebase - Quick Reference

## File Organization Map

```
MPhotoshop.p                    # Main entry point
├── UPhotoshop.p                # Application class (TPhotoshopApplication)
│   ├── UConstants.p            # Constants, command IDs, error codes
│   ├── UVMemory.p              # Virtual memory management
│   ├── UInternal.p             # Native Photoshop file format
│   │
│   ├── UI Components
│   │   ├── UBWDialog.p         # Dialog boxes
│   │   ├── UProgress.p         # Progress indicators
│   │   ├── UPick.p             # Color picker
│   │   ├── UCoords.p           # Coordinate display
│   │   ├── UMagnification.p    # Zoom controls
│   │   └── UPreferences.p      # Settings/preferences
│   │
│   ├── File Formats
│   │   ├── URootFormat.p       # Base format class
│   │   ├── UTIFFormat.p        # TIFF support
│   │   ├── UGIFFormat.p        # GIF support
│   │   ├── UEPSFormat.p        # EPS/PostScript
│   │   ├── UMacPaint.p         # MacPaint format
│   │   ├── UPixelPaint.p       # PixelPaint format
│   │   ├── UPixar.p            # Pixar format
│   │   ├── UIFFFormat.p        # IFF/Amiga format
│   │   ├── UTarga.p            # Targa format
│   │   ├── UScitexFormat.p     # Scitex format
│   │   ├── UThunderScan.p      # ThunderScan format
│   │   ├── URawFormat.p        # Raw format
│   │   ├── UPICTFile.p         # PICT file
│   │   └── UPICTResource.p     # PICT resource
│   │
│   ├── Image Operations
│   │   ├── UScreen.p           # Display/rendering
│   │   ├── USelect.p           # Selection tools
│   │   ├── UDraw.p             # Drawing tools
│   │   ├── UResize.p           # Resize/resample
│   │   ├── URotate.p           # Rotation
│   │   ├── UCrop.p             # Cropping
│   │   └── UFloat.p            # Floating selections
│   │
│   ├── Color & Adjustment
│   │   ├── UAdjust.p           # Levels, brightness, etc.
│   │   ├── UConvert.p          # Color space conversion
│   │   ├── USeparation.p       # CMYK separation
│   │   ├── UTable.p            # Lookup tables
│   │   ├── UHistogram.p        # Histogram analysis
│   │   ├── UDither.a           # Dithering (assembly)
│   │   └── UTransfer.p         # Transfer functions
│   │
│   ├── Filters
│   │   ├── UFilter.p           # Filter interface
│   │   └── UFilters.p          # Filter implementations
│   │
│   ├── Tools
│   │   ├── ULine.p             # Line tool
│   │   ├── UText.p             # Text tool
│   │   ├── UPasteControls.p    # Paste controls
│   │   └── UPressure.p         # Pressure sensitivity
│   │
│   ├── Printing & Output
│   │   ├── UPrint.p            # Printing
│   │   └── UPostScript.p      # PostScript generation
│   │
│   ├── Advanced Features
│   │   ├── UCalculate.p        # Channel calculations
│   │   ├── UChannel.p          # Channel management
│   │   ├── UTrap.p             # Trapping
│   │   └── UScan.p             # Scanner interface
│   │
│   └── Utilities
│       ├── UCommands.p        # Command handling
│       ├── UAbout.p            # About dialog
│       ├── UGhost.p            # Ghost window support
│       └── UInitFormats.p      # Format registration
│
└── Assembly Optimizations (.a files)
    ├── UAssembly.a            # General assembly
    ├── UDraw.a                # Drawing optimizations
    ├── UResize.a              # Resize optimizations
    ├── URotate.a              # Rotation optimizations
    ├── USelect.a              # Selection optimizations
    ├── UScreen.a              # Screen optimizations
    ├── UConvert.a             # Conversion optimizations
    ├── ULine.a                # Line tool optimizations
    ├── UDither.a              # Dithering optimizations
    ├── UFloat.a               # Float operations
    ├── UPostScript.a          # PostScript optimizations
    ├── USeparation.a          # Separation optimizations
    ├── UTrap.a                # Trapping optimizations
    ├── UTarga.a               # Targa format optimizations
    ├── UGIFFormat.a           # GIF format optimizations
    ├── UTIFFormat.a           # TIFF format optimizations
    └── UIFFFormat.a           # IFF format optimizations
```

## Command Number Ranges

| Range | Category | Examples |
|-------|----------|----------|
| 1000-1099 | General Commands | Preferences, Zoom, Feather, Crop |
| 1100-1199 | Channels | Channel operations, Color tables |
| 1200-1299 | Transformations | Flip, Rotate |
| 1300-1399 | Effects | Resize, Skew, Perspective, Distort |
| 1400-1499 | Color Mapping | Invert, Equalize, Threshold, Posterize |
| 1450-1499 | Adjustments | Levels, Brightness/Contrast, Color Balance |
| 1500-1549 | Calculations | Channel math operations |
| 1550-1599 | Filters | Filter operations |
| 1600-1699 | Acquire | Scanner/input operations |
| 1700-1799 | Export | Export operations |
| 2000-2099 | Undo Operations | Move, Draw, Paint, Filter, etc. |
| 3000-3099 | UI Wording | Menu item text |
| 4000-4099 | Filter IDs | Convolve, Gaussian, Blur, Sharpen, etc. |

## File Format Codes

```pascal
kFmtCodeInternal      = 0;   // Native Photoshop format
kFmtCodeIFF          = 1;   // IFF/Amiga
kFmtCodeGIF          = 2;   // GIF
kFmtCodeEPS          = 3;   // Encapsulated PostScript
kFmtCodeMacPaint     = 4;   // MacPaint
kFmtCodePICTFile     = 5;   // PICT file
kFmtCodePICTResource = 6;   // PICT resource
kFmtCodePixar        = 7;   // Pixar format
kFmtCodePixelPaint   = 8;   // PixelPaint
kFmtCodeRaw          = 9;   // Raw format
kFmtCodeTarga        = 10;  // Targa
kFmtCodeThunderScan  = 11;  // ThunderScan
kFmtCodeTIFF         = 12;  // TIFF
kFmtCodeScitex       = 10;  // Scitex (alternative)
```

## Display Modes

```pascal
TDisplayMode = (
    HalftoneMode,        // Halftone
    MonochromeMode,      // 1-bit black & white
    IndexedColorMode,    // 8-bit indexed color
    RGBColorMode,        // 24-bit RGB
    SeparationsCMYK,     // CMYK separations
    SeparationsHSL,      // HSL separations
    SeparationsHSB,      // HSB separations
    MultichannelMode     // Multichannel
);
```

## Key Data Structures

### Image Document
- Managed by `TImageDocument` (in UPhotoshop.p)
- Contains channels, dimensions, color mode
- Handles undo/redo operations

### Channels
- Up to 16 channels per image
- Special channels:
  - `kRGBChannels = -1` (all RGB)
  - `kMaskChannel = -2` (selection mask)
  - `kCMYKChannels = -4` (all CMYK)

### Selection
- Stored as a region (Mac OS Region data structure)
- Can be feathered, inverted, grown
- Managed by `USelect.p`

## Common Patterns

### Unit Structure
```pascal
UNIT UnitName;

INTERFACE
  USES ...;
  TYPE ...;
  CONST ...;
  PROCEDURE/FUNCTION declarations;

IMPLEMENTATION
  PROCEDURE/FUNCTION implementations;
END.
```

### Object-Oriented Pattern
```pascal
TClassName = OBJECT (TParentClass)
  PROCEDURE IClassName;  // Initialization
  PROCEDURE MethodName; OVERRIDE;
END;
```

### Error Handling
```pascal
FailNil(pointer);  // Fails if pointer is nil
gResult := errorCode;  // Set global result
```

## Build Segments

The code is organized into segments for memory management:
- **ARes, ARes2, ARes3, ARes4**: Resource segments
- **AEncoded**: Encoded resources
- **AInit**: Initialization code
- **ATerminate**: Cleanup code
- **Main**: Main program code

## Resource Files (.r)

- `About.r`: About dialog resources
- `Black.r`: Black & white resources
- `Huffman1.r`, `Huffman2.r`: Compression resources
- `PixelPaint.r`: PixelPaint format resources
- `Tables.r`: Table resources
- `Tips.r`: Tip dialog resources
- `Photoshop.r`: Main application resources

## Interface Files

- `AcquireInterface.p`: Scanner/input device interface
- `ExportInterface.p`: Export module interface
- `FilterInterface.p`: Filter plug-in interface

## Assembly Files (.a)

Assembly files contain optimized routines:
- File naming: `U[Feature].a`
- Include files: `U[Feature].a.inc`
- Used for performance-critical operations

## Include Files (.inc, .inc1.p)

- Partial implementations split across files
- `.inc1.p`: First include file
- `.p.inc`: Additional includes for a unit
- `.a.inc`: Assembly include files

## Key Global Variables

(From UPhotoshop.p and other units)
- `gPhotoshopApplication`: Main application instance
- `gBuffer`: Global buffer (32KB)
- `gConfiguration`: System configuration
- `gResult`: Last operation result/error

## Memory Management

- **Handles**: Mac OS relocatable memory blocks
- **Pointers**: Fixed memory blocks
- **Virtual Memory**: Custom implementation in `UVMemory.p`
- **Segments**: Code segments loaded on demand

## Event Handling

```pascal
PROCEDURE TPhotoshopApplication.MainEventLoop; OVERRIDE;
  // Main event loop
  // Handles mouse, keyboard, menu events
  // Dispatches to appropriate handlers
```

## Tool System

Tools are implemented as command handlers:
- Each tool has a command number
- Tools can be modal (active until deselected)
- Tools interact with selection and image data

## Filter System

Filters follow a plug-in architecture:
- Base interface in `FilterInterface.p`
- Filter implementations in `UFilters.p`
- Each filter has a unique ID (4000+ range)
- Filters can be chained/repeated

## File Format System

All formats inherit from `TRootFormat`:
```pascal
TFormatClass = OBJECT (TRootFormat)
  FUNCTION CanRead(...): BOOLEAN;
  FUNCTION CanWrite(...): BOOLEAN;
  PROCEDURE DoRead(...);
  PROCEDURE DoWrite(...);
END;
```

## Color Separation

CMYK separation in `USeparation.p`:
- Under Color Removal (UCR)
- Gray Component Replacement (GCR)
- Total Ink Limit
- Transfer functions
- Halftone screens

## Undo System

- Each operation creates an undo record
- Undo records stored in document
- Command numbers in 2000+ range identify undo types
- Limited by available memory

---

**Quick Tips for Navigation:**

1. **Find a feature**: Look for `U[FeatureName].p`
2. **Find constants**: Check `UConstants.p`
3. **Find format handler**: Look in `U[Format]Format.p`
4. **Find assembly code**: Check `U[Feature].a`
5. **Find UI code**: Look for `UBWDialog.p`, `UProgress.p`, etc.
