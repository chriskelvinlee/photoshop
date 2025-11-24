# Photoshop 1.0.1 Public API Documentation

Comprehensive reference of every Pascal unit that exposes a public interface in the original
Photoshop 1.0.1 source tree. Each section lists the unit dependencies, exported constants,
variables, types, objects, and callable routines. Use this alongside the implementation
(`*.inc1.p` and related files) for behavioural details.

## Architecture Overview
- `UPhotoshop`, `UCommands`, and `UProgress` provide the MacApp-based shell, command stack, and progress services.
- Image manipulation is organised into command objects (`UResize`, `URotate`, `USelect`, `UDraw`, `UAdjust`, etc.). Each command exposes `DoIt/UndoIt/RedoIt` for history integration.
- File formats live in dedicated units (`URawFormat`, `UPICTFile`, `UTarga`, `UPixelPaint`, `UTIFFormat`, etc.) and are registered via `UInitFormats.InitFormats`.
- Filters bridge built-in kernels (`UFilter`, `UFilters`) and plug-in interfaces (`FilterInterface`).
- Memory, virtual arrays, and scratch buffers are abstracted by `UVMemory`, `UFloat`, `UScreen`, and friends.
- User interaction relies on dialog helpers (`UBWDialog`, `UDialog`, `UPasteControls`, `UPreferences`) plus acquisition/export plug-in contracts (`AcquireInterface`, `ExportInterface`).

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


## Public API Reference
### AcquireInterface (`AcquireInterface.p`)

**Purpose**: Acquire Interface module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`
**Constants**:
- `acquireSelectorAbout = 0;`
- `acquireSelectorStart = 1;`
- `acquireSelectorContinue = 2;`
- `acquireSelectorFinish = 3;`
- `acquireSelectorPrepare = 4;`
- `acquireModeBitmap = 0;`
- `acquireModeGrayScale = 1;`
- `acquireModeIndexedColor = 2;`
- `acquireModeRGBColor = 3;`
- `acquireModeCMYKColor = 4;`
- `acquireModeHSLColor = 5;`
- `acquireModeHSBColor = 6;`
- `acquireModeMultichannel = 7;`
- `acquireBadParameters = -30000;`
- `acquireNoScanner = -30001;`
- `acquireScannerProblem = -30002;`
**Types & Objects**:
- `AcquireLUT` array: `PACKED ARRAY [0..255] OF CHAR;`
- `AcquireRecord` record: `RECORD serialNumber: LONGINT; abortProc: ProcPtr; progressProc: ProcPtr; maxData: LONGINT; imageMode: INTEGER; imageSize: Point; depth: INTEGER; planes: INTEGER; imageHRes: Fixed; imageVRes: Fixed; redLUT: AcquireLUT; greenLUT: AcquireLUT; blueLUT: AcquireLUT; data: Ptr; theRect: Rect; loPlane: INTEGER; hiPlane: INTEGER; colBytes: INTEGER; rowBytes: LONGINT; planeBytes: LONGINT; filename: Str255; vRefNum: INTEGER; dirty: BOOLEAN; END;`
- `AcquireRecordPtr` pointer: `^AcquireRecord;`

### ExportInterface (`ExportInterface.p`)

**Purpose**: Export Interface module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`
**Constants**:
- `exportSelectorAbout = 0;`
- `exportSelectorStart = 1;`
- `exportSelectorContinue = 2;`
- `exportSelectorFinish = 3;`
- `exportSelectorPrepare = 4;`
- `exportModeBitmap = 0;`
- `exportModeGrayScale = 1;`
- `exportModeIndexedColor = 2;`
- `exportModeRGBColor = 3;`
- `exportModeCMYKColor = 4;`
- `exportModeHSLColor = 5;`
- `exportModeHSBColor = 6;`
- `exportModeMultichannel = 7;`
- `exportBadParameters = -30200;`
- `exportBadMode = -30201;`
**Types & Objects**:
- `ExportLUT` array: `PACKED ARRAY [0..255] OF CHAR;`
- `ExportRecord` record: `RECORD serialNumber: LONGINT; abortProc: ProcPtr; progressProc: ProcPtr; maxData: LONGINT; imageMode: INTEGER; imageSize: Point; depth: INTEGER; planes: INTEGER; imageHRes: Fixed; imageVRes: Fixed; redLUT: ExportLUT; greenLUT: ExportLUT; blueLUT: ExportLUT; theRect: Rect; loPlane: INTEGER; hiPlane: INTEGER; data: Ptr; rowBytes: LONGINT; filename: Str255; vRefNum: INTEGER; dirty: BOOLEAN; selectBBox: Rect; END;`
- `ExportRecordPtr` pointer: `^ExportRecord;`

### FilterInterface (`FilterInterface.p`)

**Purpose**: Filter Interface filter or effect module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`
**Constants**:
- `filterSelectorAbout = 0;`
- `filterSelectorParameters = 1;`
- `filterSelectorPrepare = 2;`
- `filterSelectorStart = 3;`
- `filterSelectorContinue = 4;`
- `filterSelectorFinish = 5;`
- `filterBadParameters = -30100;`
**Types & Objects**:
- `FilterRecord` record: `RECORD serialNumber: LONGINT; abortProc: ProcPtr; progressProc: ProcPtr; parameters: Handle; imageSize: Point; planes: INTEGER; filterRect: Rect; background: RGBColor; foreground: RGBColor; maxSpace: LONGINT; bufferSpace: LONGINT; inRect: Rect; inLoPlane: INTEGER; inHiPlane: INTEGER; outRect: Rect; outLoPlane: INTEGER; outHiPlane: INTEGER; inData: Ptr; inRowBytes: LONGINT; outData: Ptr; outRowBytes: LONGINT; isFloating: BOOLEAN; haveMask: BOOLEAN; autoMask: BOOLEAN; maskRect: Rect; maskData: Ptr; maskRowBytes: LONGINT; END;`
- `FilterRecordPtr` pointer: `^FilterRecord;`

### UAbout (`UAbout.p`)

**Purpose**: About module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`
**Types & Objects**:
- `TSerialText` object (extends `TKeyHandler`)
  - field: `fCode: Str255;`
  - field: `fValue: LONGINT;`
  - method: `PROCEDURE Validate (VAR succeeded: BOOLEAN); OVERRIDE;`
- `TRegisterDialog` object (extends `TBWDialog`)
  - method: `PROCEDURE DoFilterEvent (VAR anEvent: EventRecord; VAR itemHit: INTEGER; VAR handledIt: BOOLEAN; VAR doReturn: BOOLEAN); OVERRIDE; END;`
**Routines**:
- `PROCEDURE RegisterCopy;`
- `PROCEDURE ShowSplashScreen;`
- `PROCEDURE KillSplashScreen;`
- `PROCEDURE DoAboutPhotoshop;`
- `PROCEDURE MakeSizeString (doc: TImageDocument; across: BOOLEAN; VAR s: Str255);`
- `PROCEDURE MakeResString (doc: TImageDocument; align: BOOLEAN; VAR s: Str255);`
- `PROCEDURE DoSizeBoxPopUp (doc: TImageDocument; r: Rect; info: EventInfo);`
- `PROCEDURE VerifyEvE;`

### UAdjust (`UAdjust.p`)

**Purpose**: Adjust module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `VideoIntf`, `UDialog`, `UBWDialog`, `UCommands`, `UProgress`
**Constants**:
- `kMaxSliders = 6;`
**Variables**:
- `gBPointer: BitMap;`
- `gGPointer: BitMap;`
- `gWPointer: BitMap;`
- `gPtrWidth: INTEGER;`
- `gAdjustCommand: TAdjustmentCommand;`
**Types & Objects**:
- `TAdjustmentCommand` object (extends `TFloatCommand`)
  - field: `fChannel: INTEGER;`
  - field: `fWholeImage: BOOLEAN;`
  - field: `fAllocated: BOOLEAN;`
  - field: `fPreviewed: BOOLEAN;`
  - field: `fUsingBuffers: BOOLEAN;`
  - field: `fMonochromeLUT: TLookUpTable;`
  - field: `fIndexedColorTable: TRGBLookUpTable;`
  - method: `PROCEDURE IAdjustmentCommand (itsCommand: INTEGER; view: TImageView);`
  - method: `PROCEDURE GetParameters;`
  - method: `PROCEDURE MapMonochrome (dataPtr: Ptr; count: INTEGER);`
  - method: `PROCEDURE MapRGB (rPtr, gPtr, bPtr: Ptr; count: INTEGER);`
  - method: `PROCEDURE MakeMonochromeLUT;`
  - method: `PROCEDURE AllocateBuffers;`
  - method: `PROCEDURE MapBuffers;`
  - method: `PROCEDURE ExchangeBuffers;`
  - method: `PROCEDURE ShowBuffers (checkSelection: BOOLEAN);`
  - method: `PROCEDURE SaveState;`
  - method: `FUNCTION SameState: BOOLEAN;`
  - method: `PROCEDURE DoPreview;`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TInvertCommand` object (extends `TAdjustmentCommand`)
  - method: `PROCEDURE MapMonochrome (dataPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TEqualizeCommand` object (extends `TAdjustmentCommand`)
  - field: `fLUT: TLookUpTable;`
  - method: `PROCEDURE GetParameters; OVERRIDE;`
  - method: `PROCEDURE MapMonochrome (dataPtr: Ptr; count: INTEGER); OVERRIDE;`
- `PPoint` pointer: `^Point;`
- `TFeedbackDialog` object (extends `TBWDialog`)
  - field: `fView: TImageView;`
  - field: `fCommand: TAdjustmentCommand;`
  - field: `fLocation: PPoint;`
  - field: `fPreviewButton: INTEGER;`
  - field: `fFeedbackDevice: GDHandle;`
  - field: `fSaveDevice: GDHandle;`
  - field: `fFeedbackDepth: INTEGER;`
  - field: `fLastPoint: BOOLEAN;`
  - field: `fShiftDown: BOOLEAN;`
  - field: `fOptionDown: BOOLEAN;`
  - field: `fUsingNewColors: BOOLEAN;`
  - field: `fOldColors: cSpecArray;`
  - field: `fPad1 : ARRAY [1..255] OF ColorSpec;`
  - field: `fNewColors: cSpecArray;`
  - field: `fPad2 : ARRAY [1..255] OF ColorSpec;`
  - method: `PROCEDURE IFeedbackDialog (view: TImageView; command: TAdjustmentCommand; location: PPoint; itsRsrcID: INTEGER; itsHookItem: INTEGER; itsDfltButton: INTEGER; itsPreviewButton: INTEGER);`
  - method: `PROCEDURE NextMousePoint (VAR pt: Point);`
  - method: `FUNCTION DownInDialog (mousePt: Point): BOOLEAN;`
  - method: `PROCEDURE PrepareMap (forFeedback: BOOLEAN);`
  - method: `PROCEDURE GetOldColors;`
  - method: `PROCEDURE GetNewColors;`
  - method: `PROCEDURE SetScreenColors (VAR colors: cSpecArray);`
  - method: `PROCEDURE SetNewColors;`
  - method: `PROCEDURE SetOldColors;`
  - method: `FUNCTION DoSetCursor (localPoint: Point): BOOLEAN; OVERRIDE;`
  - method: `FUNCTION IsSafeButton (item: INTEGER): BOOLEAN;`
  - method: `PROCEDURE DoFilterEvent (VAR anEvent: EventRecord; VAR itemHit: INTEGER; VAR handledIt: BOOLEAN; VAR doReturn: BOOLEAN); OVERRIDE; PROCEDURE DoFeedback; PROCEDURE DoTalkToUser (PROCEDURE HandleSelectedItem (anItem: INTEGER; VAR done: BOOLEAN)); END;`
- `THistDialog` object (extends `TFeedbackDialog`)
  - field: `fHistRect: Rect;`
  - field: `fHist: THistogram;`
  - method: `PROCEDURE IHistDialog (command: TAdjustmentCommand; location: PPoint; hist: THistogram; itsRsrcID: INTEGER; itsHookItem: INTEGER; itsHistItem: INTEGER; itsDfltButton: INTEGER; itsPreviewButton: INTEGER);`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
- `TThresholdDialog` object (extends `THistDialog`)
  - field: `fLevel: INTEGER;`
  - field: `fLevelRect: Rect;`
  - field: `fPointerRect: Rect;`
  - method: `PROCEDURE IThresholdDialog (command: TThresholdCommand; hist: THistogram);`
  - method: `PROCEDURE DrawLevel;`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `PROCEDURE PrepareMap (forFeedback: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION DownInDialog (mousePt: Point): BOOLEAN; OVERRIDE;`
- `TThresholdCommand` object (extends `TAdjustmentCommand`)
  - field: `fThreshold: INTEGER;`
  - field: `fPreviewThreshold: INTEGER;`
  - method: `PROCEDURE SaveState; OVERRIDE;`
  - method: `FUNCTION SameState: BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE GetParameters; OVERRIDE;`
  - method: `PROCEDURE MapRGB (rPtr, gPtr, bPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TPosterizeDialog` object (extends `TFeedbackDialog`)
  - field: `fLevelsText: TFixedText;`
  - method: `PROCEDURE IPosterizeDialog (command: TPosterizeCommand);`
  - method: `PROCEDURE PrepareMap (forFeedback: BOOLEAN); OVERRIDE;`
- `TPosterizeCommand` object (extends `TAdjustmentCommand`)
  - field: `fLUT: TLookUpTable;`
  - field: `fPreviewLUT: TLookUpTable;`
  - method: `PROCEDURE SaveState; OVERRIDE;`
  - method: `FUNCTION SameState: BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE GetParameters; OVERRIDE;`
  - method: `PROCEDURE MapMonochrome (dataPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TSlidersDialog` object (extends `TFeedbackDialog`)
  - field: `fSliders: INTEGER;`
  - field: `fBlackOnes: INTEGER;`
  - field: `fRange: INTEGER;`
  - field: `fLevel: ARRAY [1..kMaxSliders] OF INTEGER;`
  - field: `fScaleRect: ARRAY [1..kMaxSliders] OF Rect;`
  - field: `fLevelRect: ARRAY [1..kMaxSliders] OF Rect;`
  - field: `fPointerRect: ARRAY [1..kMaxSliders] OF Rect;`
  - field: `fMinValue: ARRAY [1..kMaxSliders] OF INTEGER;`
  - field: `fMaxValue: ARRAY [1..kMaxSliders] OF INTEGER;`
  - field: `fSignedValue: ARRAY [1..kMaxSliders] OF BOOLEAN;`
  - method: `PROCEDURE ISlidersDialog (command: TAdjustmentCommand; location: PPoint; dialogID: INTEGER; sliders: INTEGER; blackOnes: INTEGER);`
  - method: `FUNCTION GetValue (which: INTEGER): INTEGER;`
  - method: `PROCEDURE DrawLevel (which: INTEGER);`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `FUNCTION DownInDialog (mousePt: Point): BOOLEAN; OVERRIDE;`
- `TBrightnessDialog` object (extends `TSlidersDialog`)
  - field: `fMean: INTEGER;`
  - method: `PROCEDURE IBrightnessDialog (command: TBrightnessCommand; mean: INTEGER);`
  - method: `PROCEDURE PrepareMap (forFeedback: BOOLEAN); OVERRIDE;`
- `TBrightnessCommand` object (extends `TAdjustmentCommand`)
  - field: `fLUT: TLookUpTable;`
  - field: `fPreviewLUT: TLookUpTable;`
  - method: `PROCEDURE SaveState; OVERRIDE;`
  - method: `FUNCTION SameState: BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE GetParameters; OVERRIDE;`
  - method: `PROCEDURE MapMonochrome (dataPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TBalanceDialog` object (extends `TFeedbackDialog`)
  - field: `fBand: INTEGER;`
  - field: `fRange: INTEGER;`
  - field: `fScaleRect: ARRAY [1..3] OF Rect;`
  - field: `fLevelRect: ARRAY [1..3] OF Rect;`
  - field: `fPointerRect: ARRAY [1..3] OF Rect;`
  - field: `fLevel: ARRAY [1..3, 1..3] OF INTEGER;`
  - method: `PROCEDURE IBalanceDialog (command: TBalanceCommand);`
  - method: `PROCEDURE DrawLevel (which: INTEGER);`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `FUNCTION DownInDialog (mousePt: Point): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE PrepareMap (forFeedback: BOOLEAN); OVERRIDE;`
- `TBalanceCommand` object (extends `TAdjustmentCommand`)
  - field: `fLUT: TRGBLookUpTable;`
  - field: `fPreviewLUT: TRGBLookUpTable;`
  - method: `PROCEDURE SaveState; OVERRIDE;`
  - method: `FUNCTION SameState: BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE GetParameters; OVERRIDE;`
  - method: `PROCEDURE MapRGB (rPtr, gPtr, bPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TLookUpTables` array: `ARRAY [0..3] OF TLookUpTable;`
- `TMapArbitraryDialog` object (extends `TFeedbackDialog`)
  - field: `fMapRect: Rect;`
  - field: `fActiveArea: Rect;`
  - field: `fXLevel: INTEGER;`
  - field: `fYLevel: INTEGER;`
  - field: `fXLevelRect: Rect;`
  - field: `fYLevelRect: Rect;`
  - field: `fPrevPoint: Point;`
  - field: `fIsColor: BOOLEAN;`
  - field: `fBand: INTEGER;`
  - field: `fSmoothCount: INTEGER;`
  - field: `fLUT: TLookUpTables;`
  - method: `PROCEDURE IMapArbitraryDialog (command: TMapArbitraryCommand);`
  - method: `PROCEDURE MarkRulers;`
  - method: `PROCEDURE DrawLevels;`
  - method: `PROCEDURE UpdateLevels (pt: Point);`
  - method: `PROCEDURE DrawMap;`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `PROCEDURE PrepareMap (forFeedback: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION DoSetCursor (localPoint: Point): BOOLEAN; OVERRIDE;`
  - method: `FUNCTION DownInDialog (mousePt: Point): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE DoLoadMap;`
  - method: `PROCEDURE DoSaveMap;`
  - method: `FUNCTION IsSafeButton (item: INTEGER): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE DoButtonPushed (anItem: INTEGER; VAR succeeded: BOOLEAN); OVERRIDE;`
- `TMapArbitraryCommand` object (extends `TBalanceCommand`)
  - method: `PROCEDURE GetParameters; OVERRIDE;`
- `TFiveLevels` record: `RECORD fBLevel: INTEGER; fGLevel: INTEGER; fWLevel: INTEGER; fLLevel: INTEGER; fHLevel: INTEGER; fGamma: INTEGER; fFraction: Fixed END;`
- `TLevelsDialog` object (extends `THistDialog`)
  - field: `fBRect: Rect;`
  - field: `fGRect: Rect;`
  - field: `fWRect: Rect;`
  - field: `fLRect: Rect;`
  - field: `fHRect: Rect;`
  - field: `fOutputRect: Rect;`
  - field: `fInLevelsRect: Rect;`
  - field: `fOutLevelsRect: Rect;`
  - field: `fBand: INTEGER;`
  - field: `fLevels: ARRAY [0..3] OF TFiveLevels;`
  - field: `fLUT: ARRAY [0..3] OF TLookUpTable;`
  - method: `PROCEDURE ILevelsDialog (command: TLevelsCommand; hist: THistogram);`
  - method: `PROCEDURE DrawInputLevels;`
  - method: `PROCEDURE DrawOutputLevels;`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `PROCEDURE PrepareMap (forFeedback: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE DoSetLevel (which, what: INTEGER);`
  - method: `FUNCTION DownInDialog (mousePt: Point): BOOLEAN; OVERRIDE;`
- `TLevelsCommand` object (extends `TBalanceCommand`)
  - method: `PROCEDURE GetParameters; OVERRIDE;`
- `TSaturationDialog` object (extends `TSlidersDialog`)
  - field: `fColorize: BOOLEAN;`
  - method: `PROCEDURE ISaturationDialog (command: TSaturationCommand);`
  - method: `PROCEDURE PrepareMap (forFeedback: BOOLEAN); OVERRIDE;`
- `TSaturationCommand` object (extends `TAdjustmentCommand`)
  - field: `fHueLUT: TLookUpTable;`
  - field: `fSatLUT: TLookUpTable;`
  - field: `fPreviewHue: TLookUpTable;`
  - field: `fPreviewSat: TLookUpTable;`
  - method: `PROCEDURE SaveState; OVERRIDE;`
  - method: `FUNCTION SameState: BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE GetParameters; OVERRIDE;`
  - method: `PROCEDURE MapRGB (rPtr, gPtr, bPtr: Ptr; count: INTEGER); OVERRIDE;`
**Routines**:
- `PROCEDURE InitAdjustments;`
- `PROCEDURE DrawNumber (n: LONGINT; r: Rect);`
- `PROCEDURE SetGammaTable (VAR LUT: TLookUpTable; g: INTEGER);`
- `PROCEDURE SmoothLUT (VAR LUT: TLookUpTable; radius, passes: INTEGER; wrap: BOOLEAN);`
- `FUNCTION LoadMapFile (VAR maps: TLookUpTables; isColor: BOOLEAN): BOOLEAN;`
- `PROCEDURE SaveMapFile (VAR maps: TLookUpTables; promptID: INTEGER);`
- `FUNCTION DoInvertCommand (view: TImageView): TCommand;`
- `FUNCTION DoEqualizeCommand (view: TImageView): TCommand;`
- `FUNCTION DoThresholdCommand (view: TImageView): TCommand;`
- `FUNCTION DoPosterizeCommand (view: TImageView): TCommand;`
- `FUNCTION DoMapArbitraryCommand (view: TImageView): TCommand;`
- `FUNCTION DoBrightnessCommand (view: TImageView): TCommand;`
- `FUNCTION DoBalanceCommand (view: TImageView): TCommand;`
- `FUNCTION DoLevelsCommand (view: TImageView): TCommand;`
- `FUNCTION DoSaturationCommand (view: TImageView): TCommand;`

### UBWDialog (`UBWDialog.p`)

**Purpose**: BW Dialog dialog/UI helpers
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UGhost`
**Types & Objects**:
- `TBWDialog` object (extends `TDialogView`)
  - field: `fCancelItem: INTEGER;`
  - method: `PROCEDURE IBWDialog (itsRsrcID: INTEGER; itsHookItem: INTEGER; itsDfltButton: INTEGER);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `FUNCTION DefineFixedText (itsItemNumber: INTEGER; places: INTEGER; blankOK: BOOLEAN; trim: BOOLEAN; minValue: LONGINT; maxValue: LONGINT): TFixedText;`
  - method: `FUNCTION DefinePopUpMenu (itsLabelNumber: INTEGER; itsItemNumber: INTEGER; menu: MenuHandle; pick: INTEGER): TPopUpMenu;`
  - method: `FUNCTION DefineUnitSelector (itsItemNumber: INTEGER; editItemNumber: INTEGER; editItemCount: INTEGER; blankOK: BOOLEAN; menuID: INTEGER; pick: INTEGER): TUnitSelector;`
  - method: `FUNCTION DefineResUnit (item: INTEGER; scale: INTEGER; pixels: INTEGER): TUnitSelector;`
  - method: `FUNCTION DefinePrintResUnit (item: INTEGER; scale: INTEGER): TUnitSelector;`
  - method: `FUNCTION DefineFreqUnit (item: INTEGER; count: INTEGER; scale: INTEGER): TUnitSelector;`
  - method: `FUNCTION DefineSizeUnit (item: INTEGER; scale: INTEGER; blankOK: BOOLEAN; allowPixels: BOOLEAN; allowColumns: BOOLEAN; allowZero: BOOLEAN; allowLarge: BOOLEAN): TUnitSelector;`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `PROCEDURE DoFilterEvent (VAR anEvent: EventRecord; VAR itemHit: INTEGER; VAR handledIt: BOOLEAN; VAR doReturn: BOOLEAN); OVERRIDE; FUNCTION DoItemSelected (anItem: INTEGER; VAR handledIt: BOOLEAN; VAR doneWithDialog: BOOLEAN): TCommand; OVERRIDE; END;`
- `TFixedText` object (extends `TKeyHandler`)
  - field: `fPlaces: INTEGER;`
  - field: `fBlankOK: BOOLEAN;`
  - field: `fTrim: BOOLEAN;`
  - field: `fMinValue: LONGINT;`
  - field: `fMaxValue: LONGINT;`
  - field: `fBlank: BOOLEAN;`
  - field: `fNumber: BOOLEAN;`
  - field: `fValue: LONGINT;`
  - method: `PROCEDURE IFixedText (itsItemNumber: INTEGER; itsParent: TDialogView; places: INTEGER; blankOK: BOOLEAN; trim: BOOLEAN; minValue: LONGINT; maxValue: LONGINT);`
  - method: `PROCEDURE StuffValue (value: LONGINT);`
  - method: `FUNCTION ParseValue: BOOLEAN;`
  - method: `PROCEDURE Validate (VAR succeeded: BOOLEAN); OVERRIDE;`
- `TPopUpMenu` object (extends `TDialogItem`)
  - field: `fMenu: MenuHandle;`
  - field: `fPick: INTEGER;`
  - field: `fLabelRect: Rect;`
  - field: `fMenuRect: Rect;`
  - field: `fPickAgain: BOOLEAN;`
  - method: `PROCEDURE DrawPopUpText;`
  - method: `PROCEDURE DrawPopUpMenu;`
  - method: `PROCEDURE SetMenu (menu: MenuHandle; pick: INTEGER);`
  - method: `PROCEDURE IPopUpMenu (itsLabelNumber: INTEGER; itsItemNumber: INTEGER; itsParent: TDialogView; menu: MenuHandle; pick: INTEGER);`
  - method: `FUNCTION DoPopUpMenu (optionDown: BOOLEAN): BOOLEAN;`
  - method: `FUNCTION ItemSelected (anItem: INTEGER; VAR handledIt: BOOLEAN; VAR doneWithDialog: BOOLEAN): TCommand; OVERRIDE;`
- `TUnitSelector` object (extends `TPopUpMenu`)
  - field: `fEditItemCount: INTEGER;`
  - field: `fEditItem: ARRAY [0..3] OF TFixedText;`
  - field: `fUnitCount: INTEGER;`
  - field: `fUnitInfo: ARRAY [1..6] OF RECORD fScale: EXTENDED;`
  - field: `fBase: EXTENDED;`
  - field: `fPlaces: INTEGER;`
  - field: `fLower: LONGINT;`
  - field: `fUpper: LONGINT END;`
**Routines**:
- `PROCEDURE ComputeCentered (VAR where: Point; width, height: INTEGER; titled: BOOLEAN);`
- `PROCEDURE CenterWindow (wp: WindowPtr; titled: BOOLEAN);`
- `FUNCTION BWAlert (itsRsrcID: INTEGER; error: INTEGER; beep: BOOLEAN): INTEGER;`
- `PROCEDURE BWNotice (itsRsrcID: INTEGER; beep: BOOLEAN);`
- `PROCEDURE ConvertFixed (value: LONGINT; places: INTEGER; trim: BOOLEAN; VAR s: Str255);`

### UCalculate (`UCalculate.p`)

**Purpose**: Calculate module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UProgress`
**Types & Objects**:
- `TChannelSelector` object (extends `TDialogItem`)
  - field: `fProtoView : TImageView;`
  - field: `fProtoDocument: TImageDocument;`
  - field: `fCanCreate : BOOLEAN;`
  - field: `fAllowMask : BOOLEAN;`
  - field: `fPreferMask: BOOLEAN;`
  - field: `fPreferRGB : BOOLEAN;`
  - field: `fSource: ARRAY [1..3] OF TChannelSelector;`
  - field: `fPickedDocument: TImageDocument;`
  - field: `fPickedChannel : INTEGER;`
  - field: `fMenu1: MenuHandle;`
  - field: `fMenu2: MenuHandle;`
  - field: `fPopUpMenu1: TPopUpMenu;`
  - field: `fPopUpMenu2: TPopUpMenu;`
  - field: `fNewChannelPick : INTEGER;`
  - field: `fOldChannelsPick: INTEGER;`
  - field: `fRGBChannelsPick: INTEGER;`
  - field: `fMaskChannelPick: INTEGER;`
  - method: `PROCEDURE IChannelSelector (itsDialog: TBWDialog; itsItemNumber: INTEGER; prototype: TImageView; canCreate: BOOLEAN; allowMask: BOOLEAN; preferMask: BOOLEAN; preferRGB: BOOLEAN; source1: TChannelSelector; source2: TChannelSelector; source3: TChannelSelector);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE ForAllSameSizeDocs (PROCEDURE DoIt (doc: TImageDocument));`
  - method: `PROCEDURE BuildMenu2 (VAR pick: INTEGER);`
  - method: `FUNCTION ItemSelected (anItem: INTEGER; VAR handledIt: BOOLEAN; VAR doneWithDialog: BOOLEAN): TCommand; OVERRIDE;`
  - method: `PROCEDURE Validate (VAR succeeded: BOOLEAN); OVERRIDE;`
- `TCalculateCommand` object (extends `TBufferCommand`)
  - field: `fDstDocument: TImageDocument;`
  - field: `fDstChannel : INTEGER;`
  - method: `PROCEDURE ICalculateCommand (view: TImageView);`
  - method: `PROCEDURE GetOptions;`
  - method: `FUNCTION ValidDestination (RGB: BOOLEAN): BOOLEAN;`
  - method: `PROCEDURE DoCalculation (band: INTEGER);`
  - method: `FUNCTION BandArray (doc: TImageDocument; channel: INTEGER; band: INTEGER): TVMArray;`
  - method: `PROCEDURE CopyToBuffer (doc: TImageDocument; channel: INTEGER; band: INTEGER);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TDuplicateChannel` object (extends `TCalculateCommand`)
  - field: `fInvert: BOOLEAN;`
  - field: `fSrcDocument: TImageDocument;`
  - field: `fSrcChannel : INTEGER;`
  - method: `PROCEDURE GetOptions; OVERRIDE;`
  - method: `PROCEDURE DoCalculation (band: INTEGER); OVERRIDE;`
- `TConstantChannel` object (extends `TCalculateCommand`)
  - field: `fConstant: INTEGER;`
  - method: `PROCEDURE GetOptions; OVERRIDE;`
  - method: `PROCEDURE DoCalculation (band: INTEGER); OVERRIDE;`
- `TCompositeChannels` object (extends `TCalculateCommand`)
  - field: `fForeDocument: TImageDocument;`
  - field: `fForeChannel : INTEGER;`
  - field: `fMaskDocument: TImageDocument;`
  - field: `fMaskChannel : INTEGER;`
  - field: `fBackDocument: TImageDocument;`
  - field: `fBackChannel : INTEGER;`
  - method: `PROCEDURE GetOptions; OVERRIDE;`
  - method: `PROCEDURE DoCalculation (band: INTEGER); OVERRIDE;`
- `TBinaryCalculation` object (extends `TCalculateCommand`)
  - field: `fSrc1Document: TImageDocument;`
  - field: `fSrc1Channel : INTEGER;`
  - field: `fSrc2Document: TImageDocument;`
  - field: `fSrc2Channel : INTEGER;`
  - method: `PROCEDURE PrepareCalculation;`
  - method: `PROCEDURE DoBinaryCalculation (srcPtr: Ptr; dstPtr: Ptr; count: INTEGER);`
  - method: `PROCEDURE DoCalculation (band: INTEGER); OVERRIDE;`
- `TBlendChannels` object (extends `TBinaryCalculation`)
  - field: `fPercent: INTEGER;`
  - field: `fMap1: TLookUpTable;`
  - field: `fMap2: TLookUpTable;`
  - method: `PROCEDURE GetOptions; OVERRIDE;`
  - method: `PROCEDURE PrepareCalculation; OVERRIDE;`
  - method: `PROCEDURE DoBinaryCalculation (srcPtr: Ptr; dstPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TSOffsetBinary` object (extends `TBinaryCalculation`)
  - field: `fIndex: INTEGER;`
  - field: `fScale: INTEGER;`
  - field: `fOffset: INTEGER;`
  - method: `PROCEDURE ISOffsetBinary (view: TImageView; index: INTEGER);`
  - method: `PROCEDURE GetOptions; OVERRIDE;`
- `TAddChannels` object (extends `TSOffsetBinary`)
  - method: `PROCEDURE DoBinaryCalculation (srcPtr: Ptr; dstPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TSubtractChannels` object (extends `TSOffsetBinary`)
  - method: `PROCEDURE DoBinaryCalculation (srcPtr: Ptr; dstPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TSimpleBinary` object (extends `TBinaryCalculation`)
  - field: `fIndex: INTEGER;`
  - method: `PROCEDURE ISimpleBinary (view: TImageView; index: INTEGER);`
  - method: `PROCEDURE GetOptions; OVERRIDE;`
- `TMultiplyChannels` object (extends `TSimpleBinary`)
  - method: `PROCEDURE DoBinaryCalculation (srcPtr: Ptr; dstPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TLighterChannel` object (extends `TSimpleBinary`)
  - method: `PROCEDURE DoBinaryCalculation (srcPtr: Ptr; dstPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TDarkerChannel` object (extends `TSimpleBinary`)
  - method: `PROCEDURE DoBinaryCalculation (srcPtr: Ptr; dstPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TDiffOfChannels` object (extends `TSimpleBinary`)
  - method: `PROCEDURE DoBinaryCalculation (srcPtr: Ptr; dstPtr: Ptr; count: INTEGER); OVERRIDE;`
- `TScreenChannels` object (extends `TSimpleBinary`)
  - method: `PROCEDURE DoBinaryCalculation (srcPtr: Ptr; dstPtr: Ptr; count: INTEGER); OVERRIDE;`
**Routines**:
- `PROCEDURE InitCalculate;`
- `FUNCTION DoDuplicateCommand (view: TImageView): TCommand;`
- `FUNCTION DoConstantCommand (view: TImageView): TCommand;`
- `FUNCTION DoCompositeCommand (view: TImageView): TCommand;`
- `FUNCTION DoBlendCommand (view: TImageView): TCommand;`
- `FUNCTION DoSubtractCommand (view: TImageView): TCommand;`
- `FUNCTION DoAddCommand (view: TImageView): TCommand;`
- `FUNCTION DoMultiplyCommand (view: TImageView): TCommand;`
- `FUNCTION DoLighterCommand (view: TImageView): TCommand;`
- `FUNCTION DoDarkerCommand (view: TImageView): TCommand;`
- `FUNCTION DoDifferenceCommand (view: TImageView): TCommand;`
- `FUNCTION DoScreenCommand (view: TImageView): TCommand;`

### UChannel (`UChannel.p`)

**Purpose**: Channel channel/color management
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`
**Types & Objects**:
- `TNewChannelCommand` object (extends `TBufferCommand`)
  - field: `fOldChannel: INTEGER;`
  - method: `PROCEDURE INewChannelCommand (view: TImageView);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TSplitChannels` object (extends `TBufferCommand`)
  - method: `PROCEDURE DoIt; OVERRIDE;`
- `TMergeChannels` object (extends `TBufferCommand`)
  - field: `fMode: TDisplayMode;`
  - field: `fChannels: INTEGER;`
  - field: `fLegalCount: INTEGER;`
  - field: `fMergeList: ARRAY [1..kMaxChannels] OF TImageDocument;`
  - method: `PROCEDURE IMergeChannels (view: TImageView);`
  - method: `PROCEDURE ForAllLegalDocuments (PROCEDURE DoToIt (doc: TImageDocument));`
  - method: `FUNCTION GuessMode (mode: TDisplayMode): BOOLEAN;`
  - method: `PROCEDURE GetMode;`
  - method: `PROCEDURE GetList;`
  - method: `PROCEDURE DoIt; OVERRIDE;`
**Routines**:
- `FUNCTION DoSetChannelCommand (view: TImageView; channel: INTEGER): TCommand;`
- `FUNCTION DoNewChannel (view: TImageView): TCommand;`
- `FUNCTION DoSplitChannels (view: TImageView): TCommand;`
- `FUNCTION DoMergeChannels (view: TImageView): TCommand;`

### UCommands (`UCommands.p`)

**Purpose**: Commands editing commands
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UProgress`
**Constants**:
- `kFileNameLength = 31;`
**Variables**:
- `gFirstPSAcquire: HPlugInInfo;`
- `gFirstDDAcquire: HPlugInInfo;`
- `gFirstBWAcquire: HPlugInInfo;`
- `gFirstPSExport : HPlugInInfo;`
- `gFirstPSFilter : HPlugInInfo;`
- `gFirstDDFilter : HPlugInInfo;`
**Types & Objects**:
- `TFileName` alias: `STRING [kFileNameLength];`
- `PFileName` pointer: `^TFileName;`
- `PPlugInInfo` pointer: `^TPlugInInfo;`
- `HPlugInInfo` pointer: `^PPlugInInfo;`
- `TPlugInInfo` record: `RECORD fName : Str255; fFileName : TFileName; fKind : ResType; fResourceID: INTEGER; fVersion : INTEGER; fData : LONGINT; fParameters: Handle; fNext : HPlugInInfo END;`
- `TPasteMode` enum → `PasteNormal`, `PasteColorOnly`, `PasteDarkenOnly`, `PasteLightenOnly`
- `TPasteControls` record: `RECORD fSrcMin: ARRAY [0..3] OF INTEGER; fSrcMax: ARRAY [0..3] OF INTEGER; fDstMin: ARRAY [0..3] OF INTEGER; fDstMax: ARRAY [0..3] OF INTEGER; fMode : TPasteMode; fBlend : INTEGER;`
- `PPasteControls` pointer: `^TPasteControls;`
- `HPasteControls` pointer: `^PPasteControls;`
- `TBufferCommand` object (extends `TCommand`)
  - field: `fView: TImageView;`
  - field: `fDoc : TImageDocument;`
  - field: `fBuffer: TChannelArrayList;`
  - method: `PROCEDURE IBufferCommand (itsCommand: INTEGER; view: TImageView);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE SwapAllChannels;`
- `TFloatCommand` object (extends `TBufferCommand`)
  - field: `fWasFloating: BOOLEAN;`
  - field: `fSwapMask: BOOLEAN;`
  - field: `fExactFloat: BOOLEAN;`
  - field: `fFloatRect: Rect;`
  - field: `fFloatMask: TVMArray;`
  - field: `fFloatData: TRGBArrayList;`
  - field: `fFloatBelow: TRGBArrayList;`
  - method: `PROCEDURE IFloatCommand (itsCommand: INTEGER; view: TImageView);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE SwapFloat;`
  - method: `PROCEDURE MakeMapLegal (VAR map: TLookUpTable);`
  - method: `PROCEDURE FloatSelection (duplicate: BOOLEAN);`
  - method: `PROCEDURE ComputeOverlap (VAR r: Rect);`
  - method: `PROCEDURE CopyOverlapArea (into: BOOLEAN; buffer: TVMArray; image: TVMArray);`
  - method: `PROCEDURE CopyOverlapAreas (into: BOOLEAN; buffer0: TVMArray; buffer1: TVMArray; buffer2: TVMArray);`
  - method: `PROCEDURE CopyBelow (into: BOOLEAN);`
  - method: `PROCEDURE BlendFloatSingle (srcArray: TVMArray; dstArray: TVMArray; maskArray: TVMArray; alphaArray: TVMArray; r1: Rect; r2: Rect; canAbort: BOOLEAN);`
  - method: `PROCEDURE BlendFloatRGB (src1Array: TVMArray; src2Array: TVMArray; src3Array: TVMArray; dst1Array: TVMArray; dst2Array: TVMArray; dst3Array: TVMArray; maskArray: TVMArray; alphaArray: TVMArray; r1: Rect; r2: Rect; canAbort: BOOLEAN);`
  - method: `PROCEDURE BlendFloat (canAbort: BOOLEAN);`
  - method: `FUNCTION CanSelect (VAR r: Rect; VAR mask: TVMArray): OSErr;`
  - method: `PROCEDURE SelectFloat;`
  - method: `PROCEDURE UpdateRects (r1, r2: Rect; highlight: BOOLEAN);`
**Routines**:
- `PROCEDURE InitPlugInList (kind: ResType; loVersion, hiVersion: INTEGER; VAR first: HPlugInInfo; command: INTEGER);`
- `PROCEDURE CheckForNoPlugIns (command: INTEGER);`
- `FUNCTION IsPlugIn (name: Str255; first: HPlugInInfo; VAR info: HPlugInInfo): BOOLEAN;`
- `PROCEDURE GetCenterPoint (view: TImageView; VAR center: Point);`
- `PROCEDURE SetTopLeft (view: TImageView; top, left: INTEGER);`
- `PROCEDURE SetCenterPoint (view: TImageView; center: Point);`
- `FUNCTION MakeMonochromeArray (rArray, gArray, bArray: TVMArray): TVMArray;`
- `FUNCTION CopyHalftoneRect (srcBuffer: TVMArray; r: Rect; depth: INTEGER): TVMArray;`
- `PROCEDURE GetPasteControls (doc: TImageDocument; VAR controls: TPasteControls);`

### UConstants (`UConstants.p`)

**Purpose**: Constants module
**Constants**:
- `pi = 3.14159265359;`
- `kEnterChar = CHR ($03);`
- `kBackspaceChar = CHR ($08);`
- `kTabChar = CHR ($09);`
- `kReturnChar = CHR ($0D);`
- `kClearChar = CHR ($1B);`
- `kEscapeChar = CHR ($1B);`
- `kLeftArrowChar = CHR ($1C);`
- `kRightArrowChar = CHR ($1D);`
- `kUpArrowChar = CHR ($1E);`
- `kDownArrowChar = CHR ($1F);`
- `kSpaceCode = $31;`
- `kCommandCode = $37;`
- `kShiftCode = $38;`
- `kCapsLockCode = $39;`
- `kOptionCode = $3A;`
- `kSignature = '8BIM';`
- `kFileType = '8BIM';`
- `kClipDataType = '8BIM';`
- `kLastMenuID = 7;`
- `kFmtCodeInternal = 0;`
- `kFmtCodeIFF = 1;`
- `kFmtCodeGIF = 2;`
- `kFmtCodeEPS = 3;`
- `kFmtCodeMacPaint = 4;`
- `kFmtCodePICTFile = 5;`
- `kFmtCodePICTResource = 6;`
- `kFmtCodePixar = 7;`
- `kFmtCodePixelPaint = 8;`
- `kFmtCodeRaw = 9;`
- `kFmtCodeTarga = 10;`
- `kFmtCodeThunderScan = 11;`
- `kFmtCodeTIFF = 12;`
- `kLastFmtCode = 12;`
- `kFmtCodeScitex = 10;`
- `kFmtCodeTarga = 11;`
- `kFmtCodeThunderScan = 12;`
- `kFmtCodeTIFF = 13;`
- `kLastFmtCode = 13;`
- `cOpenAs = 21;`
- `cOptionFill = 1001;`
- `cPreferences = 1002;`
- `cAnotherView = 1003;`
- `cZoomIn = 1004;`
- `cZoomOut = 1005;`
- `cScaleFactor = 1006;`
- `cFeather = 1007;`
- `cSelectInverse = 1008;`
- `cSelectFringe = 1009;`
- `cSelectSimilar = 1010;`
- `cPasteBehind = 1011;`
- `cCrop = 1012;`
- `cHalftone = 1013;`
- `cMonochrome = 1014;`
- `cIndexedColor = 1015;`
- `cRGBColor = 1016;`
- `cSeparationsCMYK = 1017;`
- `cSeparationsHSL = 1018;`
- `cSeparationsHSB = 1019;`
- `cMultichannel = 1020;`
- `cDeleteChannel = 1021;`
- `cSplitChannels = 1022;`
- `cMergeChannels = 1023;`
- `cResizeImage = 1024;`
- `cRepeatFilter = 1025;`
- `cPasteControls = 1026;`
- `cGrow = 1027;`
- `cPasteInto = 1028;`
- `cSelectNone = 1029;`
- `cResample = 1030;`
- `cMakeAlpha = 1031;`
- `cSelectAlpha = 1032;`
- `cDefinePattern = 1033;`
- `cHideEdges = 1034;`
- `cTrap = 1035;`
- `cDefineBrush = 1036;`
- `cHistogram = 1037;`
- `cNewChannel = 1038;`
- `cToggleRulers = 1039;`
- `cBrushesWindow = 1040;`
- `cDefringe = 1041;`
- `cPickerWindow = 1042;`
- `cCoordsWindow = 1043;`
- `cChannel = 1100;`
- `cColorTable = 1150;`
- `cEditTable = 1151;`
- `cFlip = 1200;`
- `cFlipHorizontal = 1201;`
- `cFlipVertical = 1202;`
- `cRotate = 1250;`
- `cRotate180 = 1251;`
- `cRotateLeft = 1252;`
- `cRotateRight = 1253;`
- `cRotateArbitrary = 1254;`
- `cEffects = 1300;`
- `cEffectResize = 1301;`
- `cEffectRotate = 1302;`
- `cEffectSkew = 1303;`
- `cEffectPerspective = 1304;`
- `cEffectDistort = 1305;`
- `cMap = 1400;`
- `cInvert = 1401;`
- `cEqualize = 1402;`
- `cThreshold = 1403;`
- `cPosterize = 1404;`
- `cMapArbitrary = 1405;`
- `cAdjust = 1450;`
- `cLevels = 1451;`
- `cBrightContrast = 1452;`
- `cBalance = 1453;`
- `cHueSaturation = 1454;`
- `cCalculate = 1500;`
- `cAddChannels = 1501;`
- `cBlendChannels = 1502;`
- `cCompositeChannels = 1503;`
- `cConstantChannel = 1504;`
- `cDarkerOfChannels = 1505;`
- `cDifferenceChannels = 1506;`
- `cDuplicateChannel = 1507;`
- `cLighterOfChannels = 1508;`
- `cMultiplyChannels = 1509;`
- `cScreenChannels = 1510;`
- `cSubtractChannels = 1511;`
- `cFilter = 1550;`
- `cAcquire = 1600;`
- `cExport = 1700;`
- `cMove = 2000;`
- `cDuplicate = 2001;`
- `cNudge = 2002;`
- `cConversion = 2003;`
- `cTableChange = 2004;`
- `cErasing = 2005;`
- `cDrawing = 2006;`
- `cPainting = 2007;`
- `cBlurring = 2008;`
- `cSharpening = 2009;`
- `cSmudging = 2010;`
- `cEraseAll = 2011;`
- `cSizeChange = 2012;`
- `cRotation = 2013;`
- `cInversion = 2014;`
- `cEqualization = 2015;`
- `cThresholding = 2016;`
- `cPosterization = 2017;`
- `cMapping = 2018;`
- `cAdjustment = 2019;`
- `cCalculation = 2020;`
- `cSkewing = 2021;`
- `cDistortion = 2022;`
- `cStamping = 2023;`
- `cPasteControls2 = 2024;`
- `cMagicWand = 2025;`
- `cLasso = 2026;`
- `cSelectFringe2 = 2027;`
- `cFeather2 = 2028;`
- `cPaintBucket = 2029;`
- `cReverting = 2030;`
- `cRulerOrigin = 2031;`
- `cFill = 2032;`
- `cResampling = 2033;`
- `cCloning = 2034;`
- `cTrapping = 2035;`
- `cTextTool = 2036;`
- `cDefringe2 = 2037;`
- `cLineTool = 2038;`
- `cAirbrushing = 2039;`
- `cBlendTool = 2040;`
- `cMarquee = 2041;`
- `cEllipse = 2042;`
- `cMoveOutline = 2043;`
- `cNudgeOutline = 2044;`
- `cColorCorrection = 2045;`
- `cSolveMaxInk = 2046;`
- `cYes = 2047;`
- `cNo = 2048;`
- `cCancel = 2049;`
- `cDeselect = 2050;`
- `cHalftoneWording = 3000;`
- `cHalftoneOptWording = 3001;`
- `cMonochromeWording = 3002;`
- `cMonochromeOptWording = 3003;`
- `cIndexedColorWording = 3004;`
- `cIndexedColorOptWording = 3005;`
- `cEqualizeWording = 3006;`
- `cEqualizeOptWording = 3007;`
- `cHideEdgesWording = 3008;`
- `cShowEdgesWording = 3009;`
- `cHideRulers = 3010;`
- `cShowRulers = 3011;`
- `cHideBrushes = 3012;`
- `cShowBrushes = 3013;`
- `cHidePicker = 3014;`
- `cShowPicker = 3015;`
- `cHideCoords = 3016;`
- `cShowCoords = 3017;`
- `cConvolve = 4001;`
- `cOffset = 4002;`
- `cGaussian = 4003;`
- `cSobel = 4004;`
- `cMaximum = 4005;`
- `cMinimum = 4006;`
- `cBlur = 4007;`
- `cBlurMore = 4008;`
- `cSharpen = 4009;`
- `cSharpenMore = 4010;`
- `cHighPass = 4011;`
- `cMedian = 4012;`
- `cFacet = 4013;`
- `cMotionBlur = 4014;`
- `cDiffuse = 4015;`
- `cAddNoise = 4016;`
- `cTraceContour = 4017;`
- `cMosaic = 4018;`
- `cSharpenEdges = 4019;`
- `cDespeckle = 4020;`
- `cUnsharpMask = 4021;`
- `errOldSys = -25010;`
- `errBadInternal = -25020;`
- `errNoPixels = -25030;`
- `errRgnTooComplex = -25040;`
- `errNoScratchPad = -25050;`
- `errRGBClipboard = -25060;`
- `errDiffTables = -25070;`
- `errBadPICT = -25080;`
- `errPICTTooComplex = -25090;`
- `errPICTTooWide = -25100;`
- `errNoPICTResource = -25110;`
- `errNoHalftone = -25120;`
- `errNoIndexedColor = -25130;`
- `errNoColorOnly = -25140;`
- `errNoDarkenOnly = -25150;`
- `errNoLightenOnly = -25160;`
- `errOneValueImage = -25170;`
- `errOneValueSelect = -25180;`
- `errEmptyFile = -25190;`
- `errBadThunderScan = -25200;`
- `errBadTIFF = -25210;`
- `errTooDeepTIFF = -25220;`
- `errCompressedTIFF = -25230;`
- `errBadMacPaint = -25240;`
- `errBadPixelPaint = -25250;`
- `errCanvasTooSmall = -25260;`
- `errBadGIF = -25270;`
- `errBadIFF = -25280;`
- `errBadFileVersion = -25290;`
- `errBadPixar = -25300;`
- `errResultTooBig = -25310;`
- `errDistortTooMuch = -25320;`
- `errNoBarneyscan = -25330;`
- `errNeverSaved = -25340;`
- `errNoChangeSince = -25350;`
- `errModeChanged = -25360;`
- `errSizeChanged = -25370;`
- `errNewChannel = -25380;`
- `errFileModified = -25390;`
- `errBadEPSF = -25400;`
- `errBadRegistration = -25410;`
- `errNoCloneSource = -25420;`
- `errNoTexture = -25430;`
- `errNoPattern = -25440;`
- `errBrushTooLarge = -25450;`
- `errNoCustomBrush = -25460;`
- `errSelectTooSmall = -25470;`
- `errBadScitex = -25480;`
- `errTextTooBig = -25490;`
- `errNoCorePixels = -25500;`
- `errBadTarga = -25510;`
- `errUnspTarga = -25520;`
- `errNoCMYK = -25530;`
- `errNoAuxEPSF = -25540;`
- `errPPVersion = -25550;`
- `errNotYetImp = -25990;`
- `msgCannotLasso = 1001 * $10000 + 1;`
- `msgCannotSelect = 1001 * $10000 + 2;`
- `msgCannotMove = 1001 * $10000 + 3;`
- `msgCannotDuplicate = 1001 * $10000 + 4;`
- `msgCannotErase = 1001 * $10000 + 5;`
- `msgCannotPencil = 1001 * $10000 + 6;`
- `msgCannotBrush = 1001 * $10000 + 7;`
- `msgCannotAirbrush = 1001 * $10000 + 8;`
- `msgCannotBlur = 1001 * $10000 + 9;`
- `msgCannotSmudge = 1001 * $10000 + 10;`
- `msgCannotSharpen = 1001 * $10000 + 11;`
- `msgCannotLoadCLUT = 1001 * $10000 + 12;`
- `msgCannotSaveCLUT = 1001 * $10000 + 13;`
- `msgCannotLoadMap = 1001 * $10000 + 14;`
- `msgCannotSaveMap = 1001 * $10000 + 15;`
- `msgCannotLoadKernel = 1001 * $10000 + 16;`
- `msgCannotSaveKernel = 1001 * $10000 + 17;`
- `msgCannotWand = 1001 * $10000 + 18;`
- `msgCannotBucket = 1001 * $10000 + 19;`
- `msgCannotMagic = 1001 * $10000 + 20;`
- `msgCannotNudge = 1001 * $10000 + 21;`
- `msgCannotGradient = 1001 * $10000 + 22;`
- `msgCannotLoadSSetup = 1001 * $10000 + 23;`
- `msgCannotSaveSSetup = 1001 * $10000 + 24;`
- `msgCannotCloneStamp = 1001 * $10000 + 25;`
- `msgCannotRevertStamp = 1001 * $10000 + 26;`
- `msgCannotTextureStamp = 1001 * $10000 + 27;`
- `msgCannotPatternStamp = 1001 * $10000 + 28;`
- `msgCannotStamp = 1001 * $10000 + 29;`
- `msgCannotImpressStamp = 1001 * $10000 + 30;`
- `msgCannotCrop = 1001 * $10000 + 31;`
- `msgCannotEllipse = 1001 * $10000 + 32;`
- `msgCannotUseText = 1001 * $10000 + 33;`
- `msgCannotUsePicker = 1001 * $10000 + 34;`
- `msgCannotLoadHalftone = 1001 * $10000 + 35;`
- `msgCannotLoadHalftones = 1001 * $10000 + 36;`
- `msgCannotSaveHalftone = 1001 * $10000 + 37;`
- `msgCannotSaveHalftones = 1001 * $10000 + 38;`
- `msgCannotLoadTransfer = 1001 * $10000 + 39;`
- `msgCannotLoadTransfers = 1001 * $10000 + 40;`
- `msgCannotSaveTransfer = 1001 * $10000 + 41;`
- `msgCannotSaveTransfers = 1001 * $10000 + 42;`
- `msgCannotLineTool = 1001 * $10000 + 43;`
- `msgCannotMarquee = 1001 * $10000 + 44;`
- `msgCannotMoveOutline = 1001 * $10000 + 45;`
- `msgCannotNudgeOutline = 1001 * $10000 + 46;`
- `msgCannotPersonalize = 1001 * $10000 + 47;`
- `msgBuildSepTable = 1001 * $10000 + 48;`
- `msgOpenTempFile = 1001 * $10000 + 49;`
- `kStringsID = 1002;`
- `strSelectForegroundColor = 1;`
- `strSelectBackgroundColor = 2;`
- `strSavePreferencesIn = 3;`
- `strSelectColor = 4;`
- `strSelectFirstColor = 5;`
- `strSelectLastColor = 6;`
- `strSaveColorTableIn = 7;`
- `strSaveMapIn = 8;`
- `strSaveKernelIn = 9;`
- `strSelectProgessive = 10;`
- `strAnInteger = 11;`
- `strANumber = 12;`
- `strSaveSSetupIn = 13;`
- `strSavePartIn = 14;`
- `strSaveHalftoneIn = 15;`
- `strSaveHalftonesIn = 16;`
- `strSaveTransferIn = 17;`
- `strSaveTransfersIn = 18;`
- `strReading = 19;`
- `strWriting = 20;`
- `strFormat = 21;`
- `strReadingPart = 22;`
- `strWritingPart = 23;`
- `strSaveBG = 24;`
- `strSaveUCR = 25;`
- `strSepTableName = 26;`
- `strBuildingTable = 27;`
**Types & Objects**:
- `PInteger` pointer: `^INTEGER;`
- `PLongInt` pointer: `^LONGINT;`
- `TDisplayMode` enum → `HalftoneMode`, `MonochromeMode`, `IndexedColorMode`, `RGBColorMode`, `SeparationsCMYK`, `SeparationsHSL`, `SeparationsHSB`, `MultichannelMode`
- `TLookUpTable` array: `PACKED ARRAY [0..255] OF CHAR;`
- `PLookUpTable` pointer: `^TLookUpTable;`
- `HLookUpTable` pointer: `^PLookUpTable;`
- `TRGBLookUpTable` record: `RECORD R: TLookUpTable; G: TLookUpTable; B: TLookUpTable END;`
- `PRGBLookUpTable` pointer: `^TRGBLookUpTable;`
- `HRGBLookUpTable` pointer: `^PRGBLookUpTable;`
- `THistogram` array: `ARRAY [0..255] OF LONGINT;`
- `TThresTable` array: `PACKED ARRAY [0..510] OF CHAR;`
- `TNoiseTable` array: `PACKED ARRAY [0..15, 0..15] OF CHAR;`

### UConvert (`UConvert.p`)

**Purpose**: Convert module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UScreen`, `USeparation`, `UProgress`
**Types & Objects**:
- `TCvtCommand` object (extends `TBufferCommand`)
  - field: `fState: ARRAY [BOOLEAN] OF RECORD fRows : INTEGER; fCols : INTEGER; fDepth : INTEGER; fChannels : INTEGER; fMode : TDisplayMode; fStyleInfo: TStyleInfo; fChannel: INTEGER END;`
**Routines**:
- `PROCEDURE InitCvtOptions;`
- `FUNCTION DeHalftoneDoc (doc: TImageDocument; scale: INTEGER; canAbort: BOOLEAN): TVMArray;`
- `FUNCTION DoConvertCommand (view: TImageView; mode: TDisplayMode): TCommand;`
- `FUNCTION DoDeleteChannel (view: TImageView): TCommand;`

### UCoords (`UCoords.p`)

**Purpose**: Coords module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UGhost`
**Types & Objects**:
- `TCoordsView` object (extends `TView`)
  - field: `fCoord: Point;`
  - field: `fColor1: INTEGER;`
  - field: `fColor2: INTEGER;`
  - field: `fColor3: INTEGER;`
  - method: `PROCEDURE ICoordsView;`
  - method: `PROCEDURE DrawRight (top, left, right: INTEGER; s: Str255);`
  - method: `PROCEDURE DrawCoords;`
  - method: `PROCEDURE Draw (area: Rect); OVERRIDE;`
**Routines**:
- `PROCEDURE InitCoords;`
- `FUNCTION CoordsVisible: BOOLEAN;`
- `PROCEDURE ShowCoords (visible: BOOLEAN);`
- `PROCEDURE UpdateCoords (view: TImageView; pt: Point);`

### UCrop (`UCrop.p`)

**Purpose**: Crop module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UGhost`, `USelect`, `UProgress`
**Types & Objects**:
- `TRectOptions` record: `RECORD mode : INTEGER; size : Point; ratioH: LONGINT; ratioV: LONGINT END;`
- `TMarqueeSelector` object (extends `TMaskCommand`)
  - field: `fLastRect: Rect;`
  - field: `fNextRect: Rect;`
  - field: `fMovedOnce: BOOLEAN;`
  - field: `fFlickerTime: LONGINT;`
  - field: `fFlickerState: INTEGER;`
  - field: `fOptions: TRectOptions;`
  - method: `PROCEDURE IMarqueeSelector (itsCommand: INTEGER; view: TImageView; add, remove, refine: BOOLEAN);`
  - method: `PROCEDURE CompNextRect (corner1, corner2: Point);`
  - method: `PROCEDURE TrackConstrain (anchorPoint, previousPoint: Point; VAR nextPoint: Point); OVERRIDE;`
  - method: `PROCEDURE DrawShape (r: Rect);`
  - method: `PROCEDURE TrackFeedBack (anchorPoint, nextPoint: Point; turnItOn, mouseDidMove: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE FillShape (r: Rect);`
  - method: `PROCEDURE SelectShape;`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint, previousPoint, nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
- `TEllipseSelector` object (extends `TMarqueeSelector`)
  - method: `PROCEDURE IEllipseSelector (view: TImageView; add, remove, refine: BOOLEAN);`
  - method: `PROCEDURE DrawShape (r: Rect); OVERRIDE;`
  - method: `PROCEDURE FillShape (r: Rect); OVERRIDE;`
  - method: `PROCEDURE SelectShape; OVERRIDE;`
- `TCroppingTool` object (extends `TMarqueeSelector`)
  - field: `fRatio: EXTENDED;`
  - field: `fStyleInfo: TStyleInfo;`
  - field: `fOptionDown: BOOLEAN;`
  - field: `fCommandDown: BOOLEAN;`
  - field: `fNextCorners: TCornerList;`
  - field: `fBaseCorners: TCornerList;`
  - field: `fLastCorners: TCornerList;`
  - method: `PROCEDURE ICroppingTool (view: TImageView);`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint, previousPoint, nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
  - method: `PROCEDURE DrawFeedback (state: INTEGER);`
  - method: `PROCEDURE MoveCorner (corner: INTEGER; delta: Point);`
  - method: `PROCEDURE TrackCorner (corner: INTEGER; downPt: Point);`
  - method: `FUNCTION InsideCorners (pt: Point): BOOLEAN;`
  - method: `PROCEDURE GetNewCorners;`
  - method: `PROCEDURE ComputeNewSize (VAR newRows: INTEGER; VAR newCols: INTEGER);`
  - method: `PROCEDURE SkewArray (srcArray: TVMArray; dstArray: TVMArray; offset1: EXTENDED; offset2: EXTENDED; oldWidth: EXTENDED; r: Rect);`
  - method: `PROCEDURE AngledCrop (srcArray: TVMArray; dstArray: TVMArray);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TCropCommand` object (extends `TBufferCommand`)
  - field: `fRows: INTEGER;`
  - field: `fCols: INTEGER;`
  - field: `fSelectionRect: Rect;`
  - method: `PROCEDURE ICropCommand (view: TImageView);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TRulerCommand` object (extends `TBufferCommand`)
  - field: `fOldOrigin: Point;`
  - field: `fNewOrigin: Point;`
  - method: `PROCEDURE IRulerCommand (view: TImageView; pt: Point);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
**Routines**:
- `PROCEDURE InitCrops;`
- `FUNCTION DoMarqueeTool (view: TImageView; add: BOOLEAN; remove: BOOLEAN; refine: BOOLEAN): TCommand;`
- `PROCEDURE DoMarqueeOptions;`
- `FUNCTION DoEllipseTool (view: TImageView; add: BOOLEAN; remove: BOOLEAN; refine: BOOLEAN): TCommand;`
- `PROCEDURE DoEllipseOptions;`
- `FUNCTION DoCroppingTool (view: TImageView): TCommand;`
- `PROCEDURE DoCroppingOptions;`
- `FUNCTION DoCropCommand (view: TImageView): TCommand;`
- `FUNCTION AdjustZeroPoint (view: TImageView): TCommand;`

### UDraw (`UDraw.p`)

**Purpose**: Draw editing commands
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UGhost`, `UPressure`
**Types & Objects**:
- `TMarkingTool` object (extends `TBufferCommand`)
  - field: `fChannel: INTEGER;`
  - field: `fMarkedArea: Rect;`
  - field: `fCachedArea: Rect;`
  - field: `fCacheSize: Point;`
  - field: `fLastPoint: Point;`
  - field: `fPixelAlign: BOOLEAN;`
  - field: `fConstrainH: BOOLEAN;`
  - field: `fConstrainV: BOOLEAN;`
  - field: `fLowerPage: INTEGER;`
  - field: `fUpperPage: INTEGER;`
  - field: `fPhysicalSize: INTEGER;`
  - field: `fFailMessage: LONGINT;`
  - field: `fAlphaMap: TLookUpTable;`
  - field: `fAlphaChannel: TVMArray;`
  - field: `fAuxCursor: BOOLEAN;`
  - field: `fAuxLocation: Point;`
  - field: `fAuxView: TImageView;`
  - method: `PROCEDURE IMarkingTool (view: TImageView; itsCommand: INTEGER; cacheSize: Point; failMessage: LONGINT; needAlpha: BOOLEAN);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE TrackFeedBack (anchorPoint: Point; nextPoint: Point; turnItOn: BOOLEAN; mouseDidMove: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE TrackConstrain (anchorPoint: Point; previousPoint: Point; VAR nextPoint: Point); OVERRIDE;`
  - method: `PROCEDURE BuildAlpha (lower, upper: INTEGER);`
  - method: `PROCEDURE SaveLines (lower, upper: INTEGER);`
  - method: `PROCEDURE AddToMarked (r: Rect);`
  - method: `PROCEDURE DrawAuxCursor (pt: Point);`
  - method: `PROCEDURE FlushCache;`
  - method: `PROCEDURE AddToCache (r: Rect);`
  - method: `PROCEDURE FixReleasePoint (anchorPoint: Point; VAR nextPoint: Point);`
  - method: `PROCEDURE SwapRect (r: Rect; iArray, bArray: TVMArray);`
  - method: `PROCEDURE SwapMarkedArea;`
  - method: `PROCEDURE FlushImage;`
  - method: `PROCEDURE RecoverFailure;`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TEraserTool` object (extends `TMarkingTool`)
  - field: `fMagic: BOOLEAN;`
  - field: `fColor1: INTEGER;`
  - field: `fColor2: INTEGER;`
  - field: `fColor3: INTEGER;`
  - method: `PROCEDURE IEraserTool (view: TImageView; magic: BOOLEAN);`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint: Point; VAR previousPoint: Point; VAR nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
- `TTip` record: `RECORD fSize: Point; fSpot: Point; fMask: Handle; fMask2: Handle; fData: ARRAY [0..3] OF Handle END;`
- `TDrawingMode` enum → `NormalDrawing`, `ColorOnly`, `DarkenOnly`, `LightenOnly`
- `TDrawingTool` object (extends `TMarkingTool`)
  - field: `fTip: TTip;`
  - field: `fMode: TDrawingMode;`
  - field: `fSpacing: INTEGER;`
  - field: `fFadeout: INTEGER;`
  - field: `fDelay: INTEGER;`
  - field: `fPressureMode: INTEGER;`
  - field: `fDip: BOOLEAN;`
  - field: `fMixMap: TLookUpTable;`
  - field: `fDrawings: LONGINT;`
  - field: `fLastDrawTime: LONGINT;`
  - field: `fSpacingCounter: INTEGER;`
  - field: `fStampMethod: INTEGER;`
  - field: `fImpressCounter: INTEGER;`
  - field: `fImpressTimer : LONGINT;`
  - field: `fTextureNoise: Handle;`
  - field: `fStampOffset: Point;`
  - field: `fFore: ARRAY [1..3] OF INTEGER;`
  - field: `fBack: ARRAY [1..3] OF INTEGER;`
  - method: `PROCEDURE IDrawingTool (view: TImageView; itsCommand: INTEGER; VAR tip: TTip; mode: TDrawingMode; spacing: INTEGER; fadeout: INTEGER; rate: INTEGER; failMessage: LONGINT; needAlpha: BOOLEAN);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE FindMask (offset: LONGINT; r: Rect);`
  - method: `PROCEDURE BlurOrSharpen (dataPtr: Ptr; offset: LONGINT; r: Rect; band: INTEGER; sharpen: BOOLEAN);`
  - method: `PROCEDURE SmudgeBand (dataPtr: Ptr; offset: LONGINT; r: Rect; band: INTEGER);`
  - method: `PROCEDURE MarkBand (dataPtr: Ptr; offset: LONGINT; r: Rect; band: INTEGER);`
  - method: `PROCEDURE MarkRGB (rDataPtr: Ptr; gDataPtr: Ptr; bDataPtr: Ptr; offset: LONGINT; r: Rect);`
  - method: `PROCEDURE LoadOverlap (r: Rect; srcArray1: TVMArray; srcArray2: TVMArray; srcArray3: TVMArray);`
  - method: `PROCEDURE LoadCloneTip (r: Rect);`
  - method: `PROCEDURE LoadRevertTip (r: Rect);`
  - method: `PROCEDURE LoadTextureTip;`
  - method: `PROCEDURE LoadPatternTip (r: Rect);`
  - method: `PROCEDURE LoadImpressTip (pt: Point);`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint: Point; VAR previousPoint: Point; VAR nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
- `TPencilTool` object (extends `TDrawingTool`)
  - field: `fAutoErase: BOOLEAN;`
  - method: `PROCEDURE IPencilTool (view: TImageView; pt: Point);`
- `TBrushTool` object (extends `TDrawingTool`)
  - method: `PROCEDURE IBrushTool (view: TImageView);`
- `TAirbrushTool` object (extends `TDrawingTool`)
  - method: `PROCEDURE IAirbrushTool (view: TImageView);`
- `TBlurTool` object (extends `TDrawingTool`)
  - method: `PROCEDURE IBlurTool (view: TImageView);`
- `TSharpenTool` object (extends `TDrawingTool`)
  - method: `PROCEDURE ISharpenTool (view: TImageView);`
- `TSmudgeTool` object (extends `TDrawingTool`)
  - method: `PROCEDURE ISmudgeTool (view: TImageView; dip: BOOLEAN);`
- `TStampTool` object (extends `TDrawingTool`)
  - method: `PROCEDURE IStampTool (view: TImageView; theMsg: LONGINT);`
- `TEraseAll` object (extends `TBufferCommand`)
  - field: `fChannel: INTEGER;`
  - method: `PROCEDURE IEraseAll (view: TImageView);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TBrushesView` object (extends `TView`)
  - field: `fShapeID: INTEGER;`
  - field: `fCustomRect: Rect;`
  - method: `PROCEDURE IBrushesView;`
  - method: `PROCEDURE HighlightShape (turnOn: BOOLEAN);`
  - method: `FUNCTION DoMouseCommand (VAR downLocalPoint: Point; VAR info: EventInfo; VAR hysteresis: Point): TCommand; OVERRIDE;`
  - method: `PROCEDURE Draw (area: Rect); OVERRIDE;`
- `TShapeDialog` object (extends `TBWDialog`)
  - field: `fShapeID: INTEGER;`
  - field: `fShapesRect: Rect;`
  - field: `fCustomRect: Rect;`
  - method: `PROCEDURE IShapeDialog (dialogID, shapeID: INTEGER);`
  - method: `PROCEDURE HighlightShape (turnOn: BOOLEAN);`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `PROCEDURE DoFilterEvent (VAR anEvent: EventRecord; VAR itemHit: INTEGER; VAR handledIt: BOOLEAN; VAR doReturn: BOOLEAN); OVERRIDE; END;`
**Routines**:
- `PROCEDURE InitDrawing;`
- `FUNCTION DoEraserTool (view: TImageView; magic: BOOLEAN): TCommand;`
- `FUNCTION DoPencilTool (view: TImageView; pt: Point): TCommand;`
- `FUNCTION DoBrushTool (view: TImageView): TCommand;`
- `FUNCTION DoAirbrushTool (view: TImageView): TCommand;`
- `FUNCTION DoBlurTool (view: TImageView): TCommand;`
- `FUNCTION DoSharpenTool (view: TImageView): TCommand;`
- `FUNCTION DoSmudgeTool (view: TImageView; dip: BOOLEAN): TCommand;`
- `FUNCTION DoStampTool (view: TImageView): TCommand;`
- `FUNCTION DoStampPadTool (view: TImageView; pt: Point): TCommand;`
- `FUNCTION DoEraseAll (view: TImageView): TCommand;`
- `FUNCTION BrushesVisible: BOOLEAN;`
- `PROCEDURE ShowBrushes (visible: BOOLEAN);`
- `PROCEDURE UpdateBrush;`
- `PROCEDURE DoPencilOptions;`
- `PROCEDURE DoBrushOptions;`
- `PROCEDURE DoAirbrushOptions;`
- `PROCEDURE DoBlurOptions;`
- `PROCEDURE DoSharpenOptions;`
- `PROCEDURE DoSmudgeOptions;`
- `PROCEDURE DoStampOptions;`
- `PROCEDURE DefineBrush (view: TImageView);`
- `PROCEDURE DefinePattern (view: TImageView);`

### UEPSFormat (`UEPSFormat.p`)

**Purpose**: EPS Format file format handler
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UPrinting`, `UCommands`, `URootFormat`, `UPICTFile`, `UPICTResource`, `UPostScript`, `UScreen`, `USeparation`, `UProgress`
**Types & Objects**:
- `TEPSFormat` object (extends `TPICTResourceFormat`)
  - field: `fBinary: BOOLEAN;`
  - field: `fFiveFiles: BOOLEAN;`
  - field: `fTransparent: BOOLEAN;`
  - field: `fIncludeScreen : BOOLEAN;`
  - field: `fIncludeTransfer: BOOLEAN;`
  - field: `fHalftonePreview: INTEGER;`
  - field: `fOtherPreview : INTEGER;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `PROCEDURE GetLine (VAR s: Str255);`
  - method: `PROCEDURE ReadImageData (doc: TImageDocument; binary: BOOLEAN; first: INTEGER; count: INTEGER; alpha: INTEGER; invert: BOOLEAN);`
  - method: `PROCEDURE ParseHeader (doc: TImageDocument; VAR binary: BOOLEAN; VAR cPlate: Str255; VAR mPlate: Str255; VAR yPlate: Str255; VAR kPlate: Str255; dcsPlate: BOOLEAN);`
  - method: `PROCEDURE ReadPostScript (doc: TImageDocument);`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION DataForkBytes (doc: TImageDocument): LONGINT; OVERRIDE;`
  - method: `FUNCTION MakePreviewPICT1 (doc: TImageDocument; newRows: INTEGER; newCols: INTEGER): Handle;`
  - method: `FUNCTION MakePreviewPICT2 (doc: TImageDocument; newRows: INTEGER; newCols: INTEGER): Handle;`
  - method: `PROCEDURE AddPreviewPICT (doc: TImageDocument; newRows: INTEGER; newCols: INTEGER);`
  - method: `PROCEDURE WritePostScript (doc: TImageDocument; refNum: INTEGER; channel: INTEGER; dstSize: Point; useDCS: BOOLEAN; depth: INTEGER);`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UFilter (`UFilter.p`)

**Purpose**: Filter filter or effect module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UFilters`, `UProgress`, `FilterInterface`
**Types & Objects**:
- `TFilterArrays` array: `ARRAY [0..2] OF TVMArray;`
- `TFilterCommand` object (extends `TFloatCommand`)
  - field: `fChannel: INTEGER;`
  - field: `fAutoMask: BOOLEAN;`
  - field: `fWholeImage: BOOLEAN;`
  - method: `PROCEDURE IFilterCommand (view: TImageView);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER);`
  - method: `PROCEDURE DoFilters (srcArrays: TFilterArrays; dstArrays: TFilterArrays; maskArray: TVMArray; r: Rect; bands: INTEGER);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TKernelElement` record: `RECORD dr : INTEGER; dc : INTEGER; weight: INTEGER; shift : INTEGER; offset: LONGINT END;`
- `TKernel` record: `RECORD count: INTEGER; scale: INTEGER; base : INTEGER; shift: INTEGER; valid: Rect; data : ARRAY [0..0] OF TKernelElement END;`
- `PKernel` pointer: `^TKernel;`
- `HKernel` pointer: `^PKernel;`
- `TConvolveCommand` object (extends `TFilterCommand`)
  - field: `fKernel: HKernel;`
  - field: `fMinDR: INTEGER;`
  - field: `fMaxDR: INTEGER;`
  - field: `fMinDC: INTEGER;`
  - field: `fMaxDC: INTEGER;`
  - method: `PROCEDURE IConvolveCommand (view: TImageView; kernel: HKernel);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE PrepareKernel (rows: INTEGER; cols: INTEGER; rowBytes: INTEGER);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `TOffsetFilter` object (extends `TFilterCommand`)
  - field: `fRowOffset: INTEGER;`
  - field: `fColOffset: INTEGER;`
  - field: `fEdgeMethod: INTEGER;`
  - method: `PROCEDURE IOffsetFilter (view: TImageView);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `TGaussianFilter` object (extends `TFilterCommand`)
  - field: `fRadius: INTEGER;`
  - method: `PROCEDURE IGaussianFilter (view: TImageView);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `THighPassFilter` object (extends `TGaussianFilter`)
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `TUnsharpMaskFilter` object (extends `TGaussianFilter`)
  - field: `fAmount: INTEGER;`
  - method: `PROCEDURE IUnsharpMaskFilter (view: TImageView);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `TMedianFilter` object (extends `TFilterCommand`)
  - field: `fRadius: INTEGER;`
  - method: `PROCEDURE IMedianFilter (view: TImageView);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `TMaximumFilter` object (extends `TFilterCommand`)
  - field: `fRadius: INTEGER;`
  - method: `PROCEDURE IMaximumFilter (view: TImageView);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `TMinimumFilter` object (extends `TFilterCommand`)
  - field: `fRadius: INTEGER;`
  - method: `PROCEDURE IMinimumFilter (view: TImageView);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `T3by3Filter` object (extends `TFilterCommand`)
  - field: `fWhich: INTEGER;`
  - method: `PROCEDURE I3by3Filter (view: TImageView; which: INTEGER);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `TFacetFilter` object (extends `TFilterCommand`)
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `TDiffuseFilter` object (extends `TFilterCommand`)
  - field: `fSeed: LONGINT;`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `TAddNoiseFilter` object (extends `TFilterCommand`)
  - field: `fAmount: INTEGER;`
  - field: `fGaussian: BOOLEAN;`
  - method: `PROCEDURE IAddNoiseFilter (view: TImageView; amount: INTEGER; gaussian: BOOLEAN);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `TMosaicFilter` object (extends `TFilterCommand`)
  - field: `fCellSize: INTEGER;`
  - method: `PROCEDURE IMosaicFilter (view: TImageView);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
- `TAreaBuffer` object (extends `TObject`)
  - field: `fValid: BOOLEAN;`
  - field: `fDirty: BOOLEAN;`
  - field: `fData: Handle;`
  - field: `fArea: Rect;`
  - field: `fLoPlane: INTEGER;`
  - field: `fHiPlane: INTEGER;`
  - field: `fArrays: TFilterArrays;`
  - method: `PROCEDURE IAreaBuffer (dirty: BOOLEAN; arrays: TFilterArrays);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE MoveArea (save: BOOLEAN);`
  - method: `PROCEDURE NextArea (VAR area: Rect; loPlane: INTEGER; hiPlane: INTEGER; bands: INTEGER);`
  - method: `PROCEDURE LoadPtr (VAR dataPtr: Ptr; VAR rowBytes: LONGINT);`
- `TPSFilter` object (extends `TFilterCommand`)
  - field: `fRepeating: BOOLEAN;`
  - field: `fFilterInfo: HPlugInInfo;`
  - field: `fCodeAddress: Ptr;`
  - method: `PROCEDURE IPSFilter (view: TImageView; repeating: BOOLEAN; filterInfo: HPlugInInfo);`
  - method: `PROCEDURE CallFilter (selector: INTEGER; VAR stuff: FilterRecord; testResult: BOOLEAN); PROCEDURE InnerFilterLoop (srcArrays: TFilterArrays; dstArrays: TFilterArrays; maskArray: TVMArray; r: Rect; bands: INTEGER; VAR stuff: FilterRecord); PROCEDURE DoPlugInFilters (srcArrays: TFilterArrays; dstArrays: TFilterArrays; maskArray: TVMArray; r: Rect; bands: INTEGER); PROCEDURE DoFilters (srcArrays: TFilterArrays; dstArrays: TFilterArrays; maskArray: TVMArray; r: Rect; bands: INTEGER); OVERRIDE; END;`
- `TDDFilter` object (extends `TFilterCommand`)
  - field: `fFilterInfo: HPlugInInfo;`
  - method: `PROCEDURE IDDFilter (view: TImageView; filterInfo: HPlugInInfo);`
  - method: `PROCEDURE DoFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; band: INTEGER); OVERRIDE;`
**Routines**:
- `PROCEDURE InitFilters;`
- `FUNCTION DoFilterCommand (view: TImageView; name: Str255; repeating: BOOLEAN): TCommand;`

### UFilters (`UFilters.p`)

**Purpose**: Filters filter or effect module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UProgress`
**Constants**:
- `cFacetPass1 = -1;`
- `cFacetPass2 = -2;`
- `cFacetPass3 = -3;`
- `cFacetPass4 = -4;`
- `cDiffuseDarken = -5;`
- `cDiffuseLighten = -6;`
- `cSelectFringeNarrow = -7;`
- `cSelectFringeWide = -8;`
- `kMaxParameters = 27;`
**Variables**:
- `gFilterParameter: ARRAY [1..kMaxParameters] OF LONGINT;`
**Routines**:
- `PROCEDURE GaussianFilter (data: TVMArray; VAR r: Rect; width: INTEGER; quick: BOOLEAN; canAbort: BOOLEAN);`
- `PROCEDURE MinOrMaxFilter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; radius: INTEGER; maxFlag: BOOLEAN; alternate: BOOLEAN);`
- `PROCEDURE Do3by3Filter (srcArray: TVMArray; dstArray: TVMArray; r: Rect; which: INTEGER);`

### UFloat (`UFloat.p`)

**Purpose**: Float module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `PickerIntf`, `UDialog`, `UBWDialog`, `UCommands`, `UFilters`, `URootFormat`, `UPICTFile`, `UPICTResource`
**Types & Objects**:
- `TMoveCommand` object (extends `TFloatCommand`)
  - field: `fDuplicate: BOOLEAN;`
  - field: `fOutline: BOOLEAN;`
  - field: `fNudge: BOOLEAN;`
  - field: `fHome : Point;`
  - field: `fDest : Point;`
  - field: `fDelta: Point;`
  - field: `fExactHome: BOOLEAN;`
  - field: `fMovedOnce: BOOLEAN;`
  - field: `fHysteresis: Point;`
  - field: `fOutlineMag: INTEGER;`
  - field: `fOutlineData: Handle;`
  - field: `fOutlineVRect: Rect;`
  - field: `fOutlineBounds: Rect;`
  - field: `fBaseChangeCount: LONGINT;`
  - field: `fPreparedFeedback: BOOLEAN;`
  - field: `fSelectRect: Rect;`
  - field: `fSelectMask: TVMArray;`
  - method: `PROCEDURE IMoveCommand (view: TImageView; duplicate: BOOLEAN; outline: BOOLEAN; nudge: Point; VAR hysteresis: Point);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE TrackConstrain (anchorPoint, previousPoint: Point; VAR nextPoint: Point); OVERRIDE;`
  - method: `PROCEDURE PrepareFeedback (downPoint: Point);`
  - method: `PROCEDURE TrackFeedback (anchorPoint, nextPoint: Point; turnItOn, mouseDidMove: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint, previousPoint, nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
  - method: `PROCEDURE MoveFloat (pt: Point; obscure: BOOLEAN; canAbort: BOOLEAN);`
  - method: `PROCEDURE SwapBelow;`
  - method: `PROCEDURE SelectOverlap (r: Rect);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TClipImageView` object (extends `TView`)
  - field: `fSize: Point;`
  - field: `fMask: TVMArray;`
  - field: `fMode: TDisplayMode;`
  - field: `fResolution: FixedScaled;`
  - field: `fData: ARRAY [0..2] OF TVMArray;`
  - field: `fIndexedColorTable: TRGBLookUpTable;`
  - method: `PROCEDURE IClipImageView;`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `FUNCTION ContainsClipType (aType: ResType): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE CompTransMap (iTable: TRGBLookUpTable; VAR map: TLookUpTable);`
  - method: `PROCEDURE WriteToDeskScrap; OVERRIDE;`
- `TCutCopyCommand` object (extends `TFloatCommand`)
  - field: `fDuplicate: BOOLEAN;`
  - method: `PROCEDURE ICutCopyCommand (view: TImageView; duplicate: BOOLEAN);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TPasteCommand` object (extends `TFloatCommand`)
  - field: `fPasteMode: INTEGER;`
  - method: `PROCEDURE IPasteCommand (view: TImageView; pasteMode: INTEGER);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TClearCommand` object (extends `TFloatCommand`)
  - method: `PROCEDURE IClearCommand (view: TImageView);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TFillCommand` object (extends `TFloatCommand`)
  - field: `fWithPattern: BOOLEAN;`
  - field: `fBlend: INTEGER;`
  - field: `fMode: TPasteMode;`
  - field: `fChannel: INTEGER;`
  - field: `fWholeImage: BOOLEAN;`
  - field: `fNeedOriginal: BOOLEAN;`
  - field: `fOldControls: TPasteControls;`
  - field: `fNewControls: TPasteControls;`
  - method: `PROCEDURE IFillCommand (itsCommand: INTEGER; view: TImageView; withPattern: BOOLEAN; blend: INTEGER; mode: TPasteMode);`
  - method: `PROCEDURE PatternFill (band: INTEGER; dstArray: TVMArray);`
  - method: `PROCEDURE DoFill (r: Rect; maskArray: TVMArray; floatArray: TRGBArrayList);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TFillBorderCommand` object (extends `TFillCommand`)
  - field: `fWidth: INTEGER;`
  - method: `PROCEDURE IFillBorderCommand (view: TImageView; width: INTEGER; blend: INTEGER; mode: TPasteMode);`
  - method: `PROCEDURE DoFill (r: Rect; maskArray: TVMArray; floatArray: TRGBArrayList); OVERRIDE;`
- `TGradientTool` object (extends `TFillCommand`)
  - field: `fPt1: Point;`
  - field: `fPt2: Point;`
  - field: `fSpace: INTEGER;`
  - field: `fRadial: BOOLEAN;`
  - field: `fOffset: INTEGER;`
  - field: `fMidpoint: INTEGER;`
  - method: `PROCEDURE IGradientTool (view: TImageView; radial: BOOLEAN; midpoint: INTEGER; offset: INTEGER; space: INTEGER);`
  - method: `PROCEDURE TrackConstrain (anchorPoint: Point; previousPoint: Point; VAR nextPoint: Point); OVERRIDE;`
  - method: `PROCEDURE TrackFeedBack (anchorPoint: Point; nextPoint: Point; turnItOn: BOOLEAN; mouseDidMove: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint, previousPoint, nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
  - method: `PROCEDURE DoFill (r: Rect; maskArray: TVMArray; floatArray: TRGBArrayList); OVERRIDE;`
**Routines**:
- `PROCEDURE InitFloatCommands;`
- `FUNCTION GetClipSize (VAR width: INTEGER; VAR height: INTEGER; VAR resolution: FixedScaled; VAR color: BOOLEAN): BOOLEAN;`
- `FUNCTION DoMoveSelection (view: TImageView; duplicate: BOOLEAN; outline: BOOLEAN; VAR hysteresis: Point): TCommand;`
- `FUNCTION DoNudgeSelection (view: TImageView; nudge: Point; duplicate: BOOLEAN; outline: BOOLEAN): TCommand;`
- `FUNCTION ConvertPICTDeskScrap (size: LONGINT): TView;`
- `FUNCTION DoCutCopyCommand (view: TImageView; duplicate: BOOLEAN): TCommand;`
- `FUNCTION DoPasteCommand (view: TImageView; pasteMode: INTEGER): TCommand;`
- `FUNCTION DoClearCommand (view: TImageView): TCommand;`
- `FUNCTION DoFillCommand (view: TImageView; options: BOOLEAN): TCommand;`
- `FUNCTION DoGradientTool (view: TImageView): TCommand;`
- `PROCEDURE DoGradientOptions;`

### UGhost (`UGhost.p`)

**Purpose**: Ghost module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `SysEqu`, `Traps`, `UPatch`
**Types & Objects**:
- `TGhostWindow` object (extends `TWindow`)
  - field: `fClosed: BOOLEAN;`
  - method: `PROCEDURE ShowGhost (visible: BOOLEAN);`
  - method: `PROCEDURE Close; OVERRIDE;`
  - method: `PROCEDURE MoveByUser (startPt: Point); OVERRIDE;`
  - method: `PROCEDURE UpdateEvent; OVERRIDE;`
**Routines**:
- `PROCEDURE InitGhosts;`
- `PROCEDURE MoveGhostsForward;`
- `FUNCTION FrontVisible: WindowPtr;`
- `FUNCTION IsGhostWindow (wp: WindowPtr): BOOLEAN;`
- `PROCEDURE MakeIntoGhost (wp: WindowPtr; ghost: BOOLEAN);`
- `PROCEDURE HiliteGhosts (state: BOOLEAN);`
- `PROCEDURE MySelectWindow (theWindow: WindowPtr);`
- `PROCEDURE MyDragWindow (theWindow: WindowPtr; startPt: Point; bounds: Rect);`
- `FUNCTION ToggleGhosts: BOOLEAN;`
- `FUNCTION NewGhostWindow (itsRsrcID: INTEGER; itsView: TView): TWindow;`

### UGIFFormat (`UGIFFormat.p`)

**Purpose**: GIF Format file format handler
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `URootFormat`, `ULZWCompress`, `UProgress`
**Types & Objects**:
- `TGIFFormat` object (extends `TRootFormat`)
  - field: `fDepth: INTEGER;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `PROCEDURE ReadRaster (canAbort: BOOLEAN);`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE WriteRaster (doc: TImageDocument);`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UHistogram (`UHistogram.p`)

**Purpose**: Histogram module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UProgress`
**Types & Objects**:
- `THistogramDialog` object (extends `TBWDialog`)
  - field: `fLevel: INTEGER;`
  - field: `fHist: THistogram;`
  - field: `fHistRect: Rect;`
  - method: `PROCEDURE IHistogramDialog (hist: THistogram);`
  - method: `PROCEDURE DrawStatistics;`
  - method: `PROCEDURE DrawLevelInfo;`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `FUNCTION DoSetCursor (localPoint: Point): BOOLEAN; OVERRIDE;`
**Routines**:
- `PROCEDURE GetHistogram (view: TImageView; luminosity: BOOLEAN; VAR hist0: THistogram; VAR hist1: THistogram; VAR hist2: THistogram; VAR hist3: THistogram);`
- `PROCEDURE DrawHistogram (hist: THistogram; bounds: Rect);`
- `PROCEDURE DoHistogramCommand (view: TImageView);`

### UIFFFormat (`UIFFFormat.p`)

**Purpose**: IFF Format file format handler
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `URootFormat`, `UProgress`
**Types & Objects**:
- `TIFFFormat` object (extends `TRootFormat`)
  - field: `fDepth: INTEGER;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `FUNCTION ReadCMap (VAR cMap: TRGBLookUpTable): INTEGER;`
  - method: `PROCEDURE TransCMap (doc: TImageDocument; VAR cMap: TRGBLookUpTable; nPlanes: INTEGER; depth: INTEGER; planePick: INTEGER; planeOnOff: INTEGER; planeMask: INTEGER);`
  - method: `PROCEDURE ReadBody (doc: TImageDocument; nPlanes: INTEGER; masked: BOOLEAN; compressed: BOOLEAN);`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE WriteBody (doc: TImageDocument; bounds: Rect);`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UInitFormats (`UInitFormats.p`)

**Purpose**: Init Formats file format handler
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `URootFormat`, `UInternal`, `UPICTFile`, `UPICTResource`, `URawFormat`, `UThunderScan`, `UTIFFormat`, `UGIFFormat`, `UMacPaint`, `UPixelPaint`, `UIFFFormat`, `UPixar`, `UEPSFormat`, `UScitexFormat`, `UTarga`
**Routines**:
- `PROCEDURE InitFormats;`

### UInternal (`UInternal.p`)

**Purpose**: Internal module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `URootFormat`, `UProgress`
**Types & Objects**:
- `TMultidiskStamp` record: `RECORD fName: STRING[63]; fDate: LONGINT; fTime: LONGINT; fPart: INTEGER END;`
- `PMultidiskStamp` pointer: `^TMultidiskStamp;`
- `HMultidiskStamp` pointer: `^PMultidiskStamp;`
- `TInternalFormat` object (extends `TRootFormat`)
  - field: `fMultidisk: BOOLEAN;`
  - field: `fRow: INTEGER;`
  - field: `fChannel: INTEGER;`
  - field: `fLastVRefNum: INTEGER;`
  - field: `fStamp: TMultidiskStamp;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE ReadPart (doc: TImageDocument);`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE ReadNext (doc: TImageDocument; name: Str255);`
  - method: `PROCEDURE ReadOther (doc: TImageDocument; name: Str255); OVERRIDE;`
  - method: `PROCEDURE AboutToSave (doc: TImageDocument; itsCmd: INTEGER; VAR name: Str255; VAR vRefNum: INTEGER; VAR makingCopy: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION DataForkBytes (doc: TImageDocument): LONGINT; OVERRIDE;`
  - method: `FUNCTION SpotBytes (doc: TImageDocument): LONGINT;`
  - method: `FUNCTION RsrcForkBytes (doc: TImageDocument): LONGINT; OVERRIDE;`
  - method: `PROCEDURE AddResources (doc: TImageDocument);`
  - method: `PROCEDURE AddStamp;`
  - method: `PROCEDURE FillUpDisk (doc: TImageDocument);`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`
  - method: `PROCEDURE EjectLastVolume;`
  - method: `PROCEDURE WriteNext (doc: TImageDocument; name: Str255);`
  - method: `PROCEDURE WriteOther (doc: TImageDocument; name: Str255); OVERRIDE;`
- `TMiscResource` object (extends `TObject`)
  - field: `fID: INTEGER;`
  - field: `fType: ResType;`
  - field: `fData: Handle;`
  - method: `PROCEDURE Free; OVERRIDE;`
**Routines**:
- `PROCEDURE ReadMiscResources (doc: TImageDocument);`
- `PROCEDURE MiscResourcesBytes (doc: TImageDocument; VAR rsrcForkBytes: LONGINT);`
- `PROCEDURE WriteMiscResources (doc: TImageDocument);`

### ULine (`ULine.p`)

**Purpose**: Line module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`
**Types & Objects**:
- `TArrowLocation` record: `RECORD bounds: Rect; corner1: Point; corner2: Point; corner3: Point; corner4: Point END;`
- `TLineTool` object (extends `TBufferCommand`)
  - field: `fPt1: Point;`
  - field: `fPt2: Point;`
  - field: `fLineRect: Rect;`
  - field: `fArrow1: BOOLEAN;`
  - field: `fArrow2: BOOLEAN;`
  - field: `fChannel: INTEGER;`
  - field: `fDrawLine: BOOLEAN;`
  - field: `fArrowLoc1: TArrowLocation;`
  - field: `fArrowLoc2: TArrowLocation;`
  - method: `PROCEDURE ILineTool (view: TImageView);`
  - method: `PROCEDURE TrackConstrain (anchorPoint: Point; previousPoint: Point; VAR nextPoint: Point); OVERRIDE;`
  - method: `PROCEDURE TrackFeedBack (anchorPoint: Point; nextPoint: Point; turnItOn: BOOLEAN; mouseDidMove: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint, previousPoint, nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
  - method: `PROCEDURE LocateArrow (hLoc: Fixed; vLoc: Fixed; normH: EXTENDED; normV: EXTENDED; VAR arrow: TArrowLocation);`
  - method: `PROCEDURE GetBounds (VAR r: Rect);`
  - method: `PROCEDURE ImageLine (maskArray: TVMArray);`
  - method: `PROCEDURE ImageArrow (maskArray: TVMArray; arrow: TArrowLocation);`
  - method: `PROCEDURE MarkArray (srcArray: TVMArray; dstArray: TVMArray; level: INTEGER);`
  - method: `PROCEDURE MultiplyMasks (dstArray: TVMArray);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE SwapRect (iArray: TVMArray; bArray: TVMArray);`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
**Routines**:
- `PROCEDURE InitLineTool;`
- `FUNCTION DoLineTool (view: TImageView): TCommand;`
- `PROCEDURE DoLineToolOptions;`

### ULZWCompress (`ULZWCompress.p`)

**Purpose**: LZW Compress module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`
**Variables**:
- `lzwWordSize: INTEGER;`
**Routines**:
- `PROCEDURE LZWCompress (codeSize: INTEGER; FUNCTION GetData (VAR pixel: INTEGER): BOOLEAN; PROCEDURE PutCodeWord (code: INTEGER); tiff: BOOLEAN);`
- `PROCEDURE LZWExpand (codeSize: INTEGER; errorCode: INTEGER; FUNCTION GetCodeWord: INTEGER; PROCEDURE PutData (pixel: INTEGER); tiff: BOOLEAN);`

### UMacPaint (`UMacPaint.p`)

**Purpose**: Mac Paint module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `URootFormat`, `UCommands`, `UProgress`
**Types & Objects**:
- `TMacPaintFormat` object (extends `TRootFormat`)
  - field: `fCenter: BOOLEAN;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UMagnification (`UMagnification.p`)

**Purpose**: Magnification module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`
**Routines**:
- `FUNCTION DoZoomInCommand (view: TImageView): TCommand;`
- `FUNCTION DoZoomOutCommand (view: TImageView): TCommand;`
- `FUNCTION DoScaleFactorCommand (view: TImageView): TCommand;`
- `FUNCTION DoNormalSize (view: TImageView): TCommand;`
- `FUNCTION DoOverviewSize (view: TImageView): TCommand;`
- `FUNCTION DoZoomTool (view: TImageView; downPoint: Point; zoomOut: BOOLEAN): TCommand;`

### UMovableWDEF (`MovableWDEF.p`)

**Purpose**: Movable WDEF module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`
**Routines**:
- `FUNCTION MovableWDEF (varCode: INTEGER; theWindow: WindowPtr; message: INTEGER; param: LONGINT): LONGINT;`

### UPaletteWDEF (`PaletteWDEF.p`)

**Purpose**: Palette WDEF module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`
**Routines**:
- `FUNCTION PaletteWDEF (varCode: INTEGER; theWindow: WindowPtr; message: INTEGER; param: LONGINT): LONGINT;`

### UPasteControls (`UPasteControls.p`)

**Purpose**: Paste Controls module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UAdjust`
**Types & Objects**:
- `TPasteControlsDialog` object (extends `TFeedbackDialog`)
  - field: `fControls: TPasteControls;`
  - field: `fSrcBarRect: Rect;`
  - field: `fDstBarRect: Rect;`
  - field: `fSrcMinRect: Rect;`
  - field: `fSrcMaxRect: Rect;`
  - field: `fDstMinRect: Rect;`
  - field: `fDstMaxRect: Rect;`
  - field: `fSrcLevelsRect: Rect;`
  - field: `fDstLevelsRect: Rect;`
  - field: `fBlendText: TFixedText;`
  - field: `fFuzzText : TFixedText;`
  - field: `fBandCluster: TRadioCluster;`
  - field: `fModeCluster: TRadioCluster;`
  - method: `PROCEDURE IPasteControlsDialog (view: TImageView; controls: TPasteControls; mode: TDisplayMode);`
  - method: `PROCEDURE GetSettings (VAR controls: TPasteControls);`
  - method: `PROCEDURE DrawSrcLevels;`
  - method: `PROCEDURE DrawDstLevels;`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `PROCEDURE DoSetLevel (which, what: INTEGER);`
  - method: `FUNCTION DownInDialog (mousePt: Point): BOOLEAN; OVERRIDE;`
- `TPasteControlsCommand` object (extends `TFloatCommand`)
  - field: `fNewControls: TPasteControls;`
  - field: `fOldControls: TPasteControls;`
  - method: `PROCEDURE IPasteControls (view: TImageView);`
  - method: `PROCEDURE PreviewControls (useNew: BOOLEAN);`
  - method: `PROCEDURE GetParameters;`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
**Routines**:
- `PROCEDURE InitPasteControls;`
- `FUNCTION DoPasteControls (view: TImageView): TCommand;`

### UPhotoshop (`UPhotoshop.p`)

**Purpose**: Photoshop module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `QuickDraw32Bit`, `SysEqu`, `Traps`, `UPrinting`, `UPatch`, `UDialog`, `UConstants`, `UVMemory`, `UBWDialog`, `UProgress`
**Constants**:
- `kMaxChannels = 16;`
- `kRGBChannels = -1;`
- `kMaskChannel = -2;`
- `kDummyChannel = -3;`
- `kCMYKChannels = -4;`
- `kRoundUp = TRUE;`
- `kRoundDown = FALSE;`
- `kMarqueeWidth = 1;`
- `kHLPatterns = 8;`
- `kHLDelay = 3;`
- `kProgressive = 7;`
- `kRulerWidth = 15;`
**Variables**:
- `gPreferences: TPreferences;`
- `gSerialNumber: LONGINT;`
- `gMetric: BOOLEAN;`
- `gInitializedPS: BOOLEAN;`
- `gBuffer: Ptr;`
- `gTool: TTool;`
- `gUseTool: TTool;`
- `gForegroundColor: RGBColor;`
- `gBackgroundColor: RGBColor;`
- `gCloneDoc : TImageDocument;`
- `gCloneTarget : TImageDocument;`
- `gCloneChannel: INTEGER;`
- `gClonePoint : Point;`
- `gCloneOffset : Point;`
- `gPatternRect: Rect;`
- `gPattern: ARRAY [0..3] OF TVMArray;`
- `gToolsView: TToolsView;`
- `gToolsWindow: WindowPtr;`
- `gPickerWmgrWindow: WindowPtr;`
- `gScratchDoc: TImageDocument;`
- `gTables: TDitherTables;`
- `gFormats: ARRAY [0..kLastFmtCode] OF TImageFormat;`
- `gFormatCode: INTEGER;`
- `gReply: SFReply;`
- `gNullLUT: TLookUpTable;`
- `gInvertLUT: TLookUpTable;`
- `gGrayLUT: TRGBLookUpTable;`
- `gGeneva: INTEGER;`
- `gMonaco: INTEGER;`
- `gHelvetica: INTEGER;`
- `gDecimalPt: CHAR;`
- `gHas32BitQuickDraw: BOOLEAN;`
- `gStaggerCount: INTEGER;`
- `gPrinterResolution: FixedScaled;`
- `gHLPattern : ARRAY [0..kHLPatterns-1] OF Pattern;`
- `gHLPatternDelta: ARRAY [0..kHLPatterns-1] OF Pattern;`
**Types & Objects**:
- `TPhotoshopApplication` object (extends `TApplication`)
  - method: `PROCEDURE IPhotoshopApplication;`
  - method: `PROCEDURE Terminate; OVERRIDE;`
  - method: `PROCEDURE ShowError (error: OSErr; message: LONGINT); OVERRIDE;`
  - method: `PROCEDURE MainEventLoop; OVERRIDE;`
  - method: `FUNCTION GetEvent (eventMask: INTEGER; VAR anEvent: EventRecord): BOOLEAN; OVERRIDE; PROCEDURE DoTrackCursor (mousePt: Point; spaceDown: BOOLEAN; shiftDown: BOOLEAN; optionDown: BOOLEAN; commandDown: BOOLEAN); PROCEDURE TrackCursor; OVERRIDE; FUNCTION ObeyMouseDown (whereMouseDown: INTEGER; aWmgrWindow: WindowPtr; nextEvent: PEventRecord): TCommand; OVERRIDE; PROCEDURE SpaceIsLow; OVERRIDE; PROCEDURE OpenNew (itsCmdNumber: CmdNumber); OVERRIDE; FUNCTION CanOpenDocument (itsCmdNumber: CmdNumber; VAR anAppFile: AppFile): BOOLEAN; OVERRIDE; FUNCTION AlreadyOpen (fileName: Str255; volRefnum: INTEGER): TDocument; OVERRIDE; PROCEDURE SFGetParms (itsCmdNumber: CmdNumber; VAR dlgID: INTEGER; VAR where: Point; VAR fileFilter, dlgHook, filterProc: ProcPtr; typeList: HTypeList); OVERRIDE; FUNCTION ChooseDocument (itsCmdNumber: CmdNumber; VAR anAppFile: AppFile): BOOLEAN; OVERRIDE; FUNCTION DoMakeDocument (itsCmdNumber: CmdNumber): TDocument; OVERRIDE; PROCEDURE CloseDocument (docToClose: TDocument); OVERRIDE; PROCEDURE AboutToLoseControl (convertClipboard: BOOLEAN); OVERRIDE; PROCEDURE RegainControl (checkClipboard: BOOLEAN); OVERRIDE; FUNCTION MakeViewForAlienClipboard: TView; OVERRIDE; PROCEDURE DoIdle (phase: IdlePhase); OVERRIDE; PROCEDURE SetUndoText (cmdDone: BOOLEAN; aCmdNumber: CmdNumber); OVERRIDE; PROCEDURE DoSetupMenus; OVERRIDE; FUNCTION DoMenuCommand (aCmdNumber: CmdNumber): TCommand; OVERRIDE; FUNCTION DoKeyCommand (ch: CHAR; aKeyCode: INTEGER; VAR info: EventInfo): TCommand; OVERRIDE; FUNCTION CommandKey (ch: CHAR; aKeyCode: INTEGER; VAR info: EventInfo): TCommand; OVERRIDE; END;`
- `TChannelArrayList` array: `ARRAY [0..kMaxChannels-1] OF TVMArray;`
- `TRGBArrayList` array: `ARRAY [0..2] OF TVMArray;`
- `TCornerList` array: `ARRAY [0..3] OF Point;`
- `FixedScaled` record: `RECORD value: Fixed; scale: INTEGER END;`
- `THalftoneSpec` record: `RECORD frequency : FixedScaled; angle : Fixed; shape : INTEGER; spot : Handle END;`
- `THalftoneSpecs` array: `ARRAY [0..3] OF THalftoneSpec;`
- `TTransferSpec` array: `ARRAY [0..4] OF INTEGER;`
- `TTransferSpecs` array: `ARRAY [0..3] OF TTransferSpec;`
- `TStyleInfo` record: `RECORD fResolution: FixedScaled; fWidthUnit : INTEGER; fHeightUnit: INTEGER; fGamma: INTEGER; fHalftoneSpec: THalftoneSpec; fTransferSpec: TTransferSpec; fHalftoneSpecs: THalftoneSpecs; fTransferSpecs: TTransferSpecs; fCropMarks : BOOLEAN; fRegistrationMarks: BOOLEAN; fLabel : BOOLEAN; fColorBars : BOOLEAN; fNegative : BOOLEAN; fFlip : BOOLEAN; fBorder : FixedScaled; fCaption : Str255 END;`
- `TImageDocument` object (extends `TDocument`)
  - field: `fRows: INTEGER;`
  - field: `fCols: INTEGER;`
  - field: `fDepth: INTEGER;`
  - field: `fChannels: INTEGER;`
  - field: `fMode: TDisplayMode;`
  - field: `fIndexedColorTable: TRGBLookUpTable;`
  - field: `fTableItem: INTEGER;`
  - field: `fData: TChannelArrayList;`
  - field: `fRulerOrigin: Point;`
  - field: `fSelectionRect: Rect;`
  - field: `fSelectionMask: TVMArray;`
  - field: `fSelectionFloating: BOOLEAN;`
  - field: `fExactFloat: BOOLEAN;`
  - field: `fFloatCommand: TCommand;`
  - field: `fFloatChannel: INTEGER;`
  - field: `fFloatRect: Rect;`
  - field: `fFloatMask: TVMArray;`
  - field: `fFloatData: TRGBArrayList;`
  - field: `fFloatBelow: TRGBArrayList;`
  - field: `fFloatAlpha: TVMArray;`
  - field: `fPasteControls: Handle;`
  - field: `fEffectMode: INTEGER;`
  - field: `fEffectChannel: INTEGER;`
  - field: `fEffectCommand: TCommand;`
  - field: `fEffectCorners: TCornerList;`
  - field: `fImported: BOOLEAN;`
  - field: `fMasterChanges: BOOLEAN;`
  - field: `fFormatCode: INTEGER;`
  - field: `fReverting: BOOLEAN;`
  - field: `fRevertInfo: Handle;`
  - field: `fMergeItem : INTEGER;`
  - field: `fMergeDefault: INTEGER;`
  - field: `fStyleInfo: TStyleInfo;`
  - field: `fMagicRows: INTEGER;`
  - field: `fMagicCols: INTEGER;`
  - field: `fMagicChannels: INTEGER;`
  - field: `fMagicMode: TDisplayMode;`
  - field: `fMagicData: TChannelArrayList;`
  - field: `fFlickerTime: LONGINT;`
  - field: `fFlickerState: INTEGER;`
  - field: `fMiscResources: TList;`
  - method: `PROCEDURE DefaultState;`
  - method: `PROCEDURE IImageDocument;`
  - method: `FUNCTION ValidSize: BOOLEAN;`
  - method: `FUNCTION Interleave (channel: INTEGER): INTEGER;`
  - method: `PROCEDURE DefaultMode;`
  - method: `PROCEDURE DoInitialState; OVERRIDE;`
  - method: `PROCEDURE FreeFloat;`
  - method: `PROCEDURE FreeMagic;`
  - method: `PROCEDURE FreeData; OVERRIDE;`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE TestColorTable;`
  - method: `PROCEDURE SFPutParms (itsCmdNumber: CmdNumber; VAR dlgID: INTEGER; VAR where: Point; VAR defaultName, prompt: Str255; VAR dlgHook, filterProc: ProcPtr); OVERRIDE;`
  - method: `PROCEDURE SaveAgain (itsCmdNumber: CmdNumber; makingCopy: BOOLEAN; savingDoc: TDocument); OVERRIDE;`
  - method: `PROCEDURE Save (itsCmdNumber: CmdNumber; askForFilename, makingCopy: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE AboutToSave (itsCmd: CmdNumber; VAR newName: Str255; VAR newVolRefnum: INTEGER; VAR makingCopy: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION GetSaveInfo (itsCmdNumber: CmdNumber; copyFInfo: BOOLEAN; VAR cInfo: CInfoPBRec): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SavedOn (VAR fileName: Str255; volRefNum: INTEGER); OVERRIDE;`
  - method: `PROCEDURE DoNeedDiskSpace (VAR dataForkBytes, rsrcForkBytes: LONGINT); OVERRIDE;`
  - method: `PROCEDURE DoWrite (aRefNum: INTEGER; makingCopy: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE DoRead (aRefNum: INTEGER; rsrcExists, forPrinting: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE ReadFromFile (VAR anAppFile: AppFile; forPrinting: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE DoMakeViews (forPrinting: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE DoMakeWindows; OVERRIDE;`
  - method: `PROCEDURE OpenAgain (itsCmdNumber: INTEGER; openingDoc: TDocument); OVERRIDE;`
  - method: `FUNCTION CanRevert: BOOLEAN;`
  - method: `PROCEDURE MyRevert;`
  - method: `PROCEDURE DoIdle (phase: IdlePhase); OVERRIDE;`
  - method: `PROCEDURE GetBoundsRect (VAR r: Rect);`
  - method: `PROCEDURE SectBoundsRect (VAR r: Rect);`
  - method: `PROCEDURE KillEffect (fixup: BOOLEAN);`
  - method: `PROCEDURE DeSelect (redraw: BOOLEAN);`
  - method: `PROCEDURE Select (r: Rect; mask: TVMArray);`
  - method: `PROCEDURE MoveSelection (r: Rect);`
  - method: `PROCEDURE UpdateImageArea (area: Rect; highlight: BOOLEAN; doFront: BOOLEAN; channel: INTEGER);`
  - method: `PROCEDURE UpdateStatus;`
  - method: `PROCEDURE InvalRulers;`
  - method: `PROCEDURE ChannelName (channel: INTEGER; VAR name: Str255);`
  - method: `PROCEDURE DoSetupMenus; OVERRIDE;`
  - method: `FUNCTION DoMenuCommand (aCmdNumber: CmdNumber): TCommand; OVERRIDE;`
- `TDitherTables` object (extends `TObject`)
  - field: `fMethod: (DitherMethodHalftone, DitherMethodSimple, DitherMethodIndexed, DitherMethodRGB, DitherMethodRGBMonochrome, DitherMethod24BitRGB, DitherMethod24BitTable, DitherMethod16BitRGB, DitherMethod16BitTable);`
  - field: `fSystemPalette: BOOLEAN;`
  - field: `fMonochrome: BOOLEAN;`
  - field: `fDepth: INTEGER;`
  - field: `fResolution: INTEGER;`
  - field: `fColorTable: CTabHandle;`
  - field: `fLUT1: TLookUpTable;`
  - field: `fLUT2: TLookUpTable;`
  - field: `fLUT3: TLookUpTable;`
  - field: `fDitherSize: INTEGER;`
  - field: `fNoiseTable: TNoiseTable;`
  - field: `fThresTable1: TThresTable;`
  - field: `fThresTable2: TThresTable;`
  - field: `fThresTable3: TThresTable;`
  - method: `PROCEDURE ITables;`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE CompTables (doc: TImageDocument; channel: INTEGER; forceMonochrome: BOOLEAN; forceSystem: BOOLEAN; depth: INTEGER; resolution: INTEGER; autoDepth: BOOLEAN; autoResolution: BOOLEAN; ditherCode: INTEGER);`
  - method: `FUNCTION CompRowBytes (width: INTEGER): LONGINT;`
  - method: `FUNCTION BufferSize (r: Rect): LONGINT;`
  - method: `PROCEDURE DitherRect (doc: TImageDocument; channel: INTEGER; magnification: INTEGER; r: Rect; buffer: Ptr; doFlush: BOOLEAN);`
- `TImageView` object (extends `TView`)
  - field: `fChannel: INTEGER;`
  - field: `fMagnification: INTEGER;`
  - field: `fScreenMode: INTEGER;`
  - field: `fRulers: BOOLEAN;`
  - field: `fWindow: TWindow;`
  - field: `fTables: TDitherTables;`
  - field: `fPalette: PaletteHandle;`
  - field: `fTransSeed: LONGINT;`
  - field: `fTransLUT: TLookUpTable;`
  - field: `fDelayedUpdateRgn: RgnHandle;`
  - field: `fCmdNumber: INTEGER;`
  - field: `fObscured: BOOLEAN;`
  - field: `fObscureTime: LONGINT;`
  - method: `PROCEDURE IImageView (doc: TImageDocument);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `FUNCTION GetScreen: GDHandle;`
  - method: `PROCEDURE GetViewScreenInfo (VAR depth: INTEGER; VAR monochrome: BOOLEAN);`
  - method: `PROCEDURE CvtImage2View (VAR pt: Point; way: BOOLEAN);`
  - method: `PROCEDURE CvtView2Image (VAR pt: Point);`
  - method: `PROCEDURE GetImageColor (pt: Point; VAR r, g, b: INTEGER);`
  - method: `PROCEDURE GetViewColor (pt: Point; VAR r, g, b: INTEGER);`
  - method: `FUNCTION GroundByte (color: RGBColor; channel: INTEGER): INTEGER;`
  - method: `FUNCTION ForegroundByte (channel: INTEGER): INTEGER;`
  - method: `FUNCTION BackgroundByte (channel: INTEGER): INTEGER;`
  - method: `PROCEDURE CompBounds (VAR bounds: Rect);`
  - method: `FUNCTION MinMagnification: INTEGER;`
  - method: `FUNCTION MaxMagnification: INTEGER;`
  - method: `PROCEDURE ValidateView;`
  - method: `PROCEDURE ChangeExtent;`
  - method: `PROCEDURE AdjustExtent; OVERRIDE;`
  - method: `PROCEDURE ShowReverted; OVERRIDE;`
  - method: `FUNCTION ColorizeBand (VAR band: INTEGER; VAR subtractive: BOOLEAN): BOOLEAN;`
  - method: `PROCEDURE IDither;`
  - method: `PROCEDURE ReDither (redraw: BOOLEAN);`
  - method: `FUNCTION CompTransLUT (device: GDHandle): BOOLEAN;`
  - method: `PROCEDURE CheckDither;`
  - method: `PROCEDURE DrawNow (area: Rect; doFlush: BOOLEAN);`
  - method: `PROCEDURE Draw (area: Rect); OVERRIDE;`
  - method: `PROCEDURE UpdateImageArea (area: Rect; highlight: BOOLEAN);`
  - method: `FUNCTION CompHighlightAreas (VAR r, area: Rect): BOOLEAN;`
  - method: `PROCEDURE DoHighlightRect (fromHL, toHL: HLState);`
  - method: `PROCEDURE DoHighlightMask (fromHL, toHL: HLState);`
  - method: `FUNCTION CompCornerRect (pt: Point; VAR r: Rect): BOOLEAN;`
  - method: `FUNCTION FindCorner (corners: TCornerList; pt: Point): INTEGER;`
  - method: `PROCEDURE DoHighlightCorner (pt: Point; turnOn: BOOLEAN);`
  - method: `PROCEDURE DoHighlightCorners (turnOn: BOOLEAN);`
  - method: `PROCEDURE DoHighlightSelection (fromHL, toHL: HLState); OVERRIDE;`
  - method: `PROCEDURE UpdateSelection;`
  - method: `PROCEDURE ObscureSelection (delay: INTEGER);`
  - method: `PROCEDURE DoDrawStatus (r: Rect);`
  - method: `PROCEDURE DrawStatus;`
  - method: `PROCEDURE InvalRulers;`
  - method: `PROCEDURE TrackRulers;`
  - method: `PROCEDURE GetGlobalArea (VAR area: Rect);`
  - method: `PROCEDURE ResetGlobalArea (area: Rect);`
  - method: `PROCEDURE GetZoomLimits (VAR limits: Rect);`
  - method: `PROCEDURE GetZoomSize (VAR pt: Point);`
  - method: `PROCEDURE AdjustZoomSize;`
  - method: `PROCEDURE SetToZoomSize;`
  - method: `PROCEDURE SetScreenMode (mode: INTEGER);`
  - method: `PROCEDURE ShowRulers (rulers: BOOLEAN);`
  - method: `PROCEDURE Activate (wasActive, beActive: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE UpdateWindowTitle;`
  - method: `PROCEDURE DoSetupMenus; OVERRIDE;`
  - method: `FUNCTION DoMenuCommand (aCmdNumber: CmdNumber): TCommand; OVERRIDE;`
  - method: `FUNCTION DoKeyCommand (ch: CHAR; aKeyCode: INTEGER; VAR info: EventInfo): TCommand; OVERRIDE;`
  - method: `FUNCTION DoMouseCommand (VAR downLocalPoint: Point; VAR info: EventInfo; VAR hysteresis: Point): TCommand; OVERRIDE;`
- `TImageWindow` object (extends `TWindow`)
  - method: `PROCEDURE UpdateEvent; OVERRIDE;`
  - method: `PROCEDURE MoveByUser (startPt: Point); OVERRIDE;`
  - method: `FUNCTION TrackInContent (localPoint: Point; VAR info: EventInfo): TCommand; OVERRIDE;`
- `TRulerFrame` object (extends `TFrame`)
  - field: `fVertical: BOOLEAN;`
  - method: `PROCEDURE IRulerFrame (window: TImageWindow; vertical: BOOLEAN);`
  - method: `PROCEDURE ResizedContainer (oldBotRight, newBotRight: Point); OVERRIDE;`
  - method: `PROCEDURE ScrollRuler (invalWholeFrame: BOOLEAN);`
- `TRulerView` object (extends `TView`)
  - field: `fImageView: TImageView;`
  - field: `fOrigin: INTEGER;`
  - field: `fScale: Fixed;`
  - field: `fLabel: LONGINT;`
  - field: `fSteps: ARRAY [0..5] OF INTEGER;`
  - field: `fLastRes: Fixed;`
  - field: `fLastMag: INTEGER;`
  - field: `fLastUnit: INTEGER;`
  - field: `fHaveMark: BOOLEAN;`
  - field: `fMarkOffset: INTEGER;`
  - method: `PROCEDURE IRulerView (view: TImageView);`
  - method: `PROCEDURE FindOrigin;`
  - method: `PROCEDURE FindScale;`
  - method: `PROCEDURE Draw (area: Rect); OVERRIDE;`
  - method: `PROCEDURE DoHighlightSelection (fromHL, toHL: HLState); OVERRIDE;`
- `TImageFrame` object (extends `TFrame`)
  - field: `fStatusRect: Rect;`
  - field: `fRuler: ARRAY [VHSelect] OF TRulerFrame;`
  - method: `PROCEDURE PositionRulers;`
  - method: `FUNCTION AdjustSBars: BOOLEAN; OVERRIDE;`
  - method: `FUNCTION CalcSBarMin (direction: VHSelect): INTEGER; OVERRIDE;`
  - method: `FUNCTION CalcSBarMax (direction: VHSelect): INTEGER; OVERRIDE;`
  - method: `PROCEDURE DrawAll; OVERRIDE;`
  - method: `PROCEDURE ChangedSize (oldBotRight: Point; newBotRight: Point); OVERRIDE;`
  - method: `PROCEDURE ScrlToSBars (invalWholeFrame: BOOLEAN); OVERRIDE;`
- `TTool` enum → `LassoTool`, `MarqueeTool`, `HandTool`, `CroppingTool`, `ZoomTool`, `EyedropperTool`, `EraserTool`, `PencilTool`, `BrushTool`, `AirbrushTool`, `BlurTool`, `SmudgeTool`, `BucketTool`, `SharpenTool`, `WandTool`, `StampTool`, `GradientTool`, `TextTool`, `EllipseTool`, `LineTool`, `MoveTool`, `EffectsTool`, `StampPadTool`, `EyedropperBackTool`, `MagicTool`, `ZoomOutTool`, `ZoomLimitTool`, `CropFinishTool`, `CropAdjustTool`, `NullTool`
- `TToolsView` object (extends `TView`)
  - field: `fPictRect1: Rect;`
  - field: `fPictRect2: Rect;`
  - field: `fPict1: PicHandle;`
  - field: `fPict2: PicHandle;`
  - field: `fToolRect: ARRAY [LassoTool..LineTool] OF Rect;`
  - field: `fForeRgn: RgnHandle;`
  - field: `fBackRgn: RgnHandle;`
  - field: `fModeRect: ARRAY [0..2] OF Rect;`
  - field: `fMarkRect: ARRAY [0..2] OF Rect;`
  - method: `PROCEDURE IToolsView;`
  - method: `PROCEDURE DrawForeground;`
  - method: `PROCEDURE DrawBackground;`
  - method: `PROCEDURE InvalidateColors;`
  - method: `PROCEDURE MarkMode (mode: INTEGER);`
  - method: `PROCEDURE Draw (area: Rect); OVERRIDE;`
  - method: `PROCEDURE DoHighlightSelection (fromHL, toHL: HLState); OVERRIDE;`
  - method: `FUNCTION PickTool (tool: TTool; click: INTEGER): TCommand;`
  - method: `FUNCTION FindTool (pt: Point): TTool;`
  - method: `FUNCTION DoMouseCommand (VAR downLocalPoint: Point; VAR info: EventInfo; VAR hysteresis: Point): TCommand; OVERRIDE;`
- `TImageFormat` object (extends `TObject`)
  - field: `fCanRead: BOOLEAN;`
  - field: `fReadType1: OSType;`
  - field: `fReadType2: OSType;`
  - field: `fReadType3: OSType;`
  - field: `fFileType: OSType;`
  - field: `fFileCreator: OSType;`
  - field: `fUsesDataFork: BOOLEAN;`
  - field: `fUsesRsrcFork: BOOLEAN;`
  - method: `PROCEDURE IImageFormat;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument);`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN);`
  - method: `PROCEDURE ReadOther (doc: TImageDocument; name: Str255);`
  - method: `PROCEDURE AboutToSave (doc: TImageDocument; itsCmd: INTEGER; VAR name: Str255; VAR vRefNum: INTEGER; VAR makingCopy: BOOLEAN);`
  - method: `FUNCTION DataForkBytes (doc: TImageDocument): LONGINT;`
  - method: `FUNCTION RsrcForkBytes (doc: TImageDocument): LONGINT;`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER);`
  - method: `PROCEDURE WriteOther (doc: TImageDocument; name: Str255);`
- `TColorCoord` record: `RECORD rgb : RGBColor; percent : INTEGER END;`
- `TProgressive` array: `ARRAY [1..kProgressive] OF TColorCoord;`
- `TSeparationSetup` record: `RECORD fProgressive : TProgressive; fGamma : INTEGER; fInkMaximum : INTEGER; fBlackID : INTEGER; fGCRTable : TLookUpTable; fUCRTable : TLookUpTable; fUCAPercent : INTEGER END;`
- `TPreferences` record: `RECORD fColorize : BOOLEAN; fUseSystem : BOOLEAN; fUseDirectLUT : BOOLEAN; fClipOption : INTEGER; fInterpolate : INTEGER; fColumnWidth : FixedScaled; fColumnGutter : FixedScaled; fHalftone : THalftoneSpec; fTransfer : TTransferSpec; fHalftones : THalftoneSpecs; fTransfers : TTransferSpecs; fSeparation : TSeparationSetup END;`
**Routines**:
- `FUNCTION CreateOutputFile (prompt: Str255; fileType: OSType; VAR reply: SFReply): INTEGER;`
- `PROCEDURE SetToolCursor (tool: TTool; allowCross: BOOLEAN);`
- `FUNCTION SpaceWasDown: BOOLEAN;`
- `PROCEDURE WhereToPlaceDialog (id: INTEGER; VAR where: Point);`
- `PROCEDURE SetSFDirectory (vRefNum: INTEGER);`
- `PROCEDURE ForAllImageViewsDo (PROCEDURE DoIt (view: TImageView));`
- `FUNCTION MakeColorTable (levels: INTEGER): CTabHandle;`
- `FUNCTION MakeMonochromeTable (levels: INTEGER): CTabHandle;`
- `PROCEDURE CompThresTable (grayLevels: INTEGER; VAR grayGap: INTEGER; VAR thresTable: TThresTable);`
- `PROCEDURE CompNoiseTable (ditherCode: INTEGER; grayGap: INTEGER; VAR ditherSize: INTEGER; VAR noiseTable: TNoiseTable);`
- `PROCEDURE DrawMaskOutline (map: BitMap; maskData: TVMArray; maskRect: Rect; mag: INTEGER);`
- `PROCEDURE SlideRectInto (VAR inner: Rect; outer: Rect);`
- `PROCEDURE GetScreenInfo (device: GDHandle; VAR depth: INTEGER; VAR monochrome: BOOLEAN);`
- `PROCEDURE RgnFillRGB (rgn: RgnHandle; color: RGBColor; depth: INTEGER);`
- `PROCEDURE DoColorizedFill (rgn: RgnHandle; color: RGBColor; depth: INTEGER);`
- `PROCEDURE ColorizedFill (rgn: RgnHandle; color: RGBColor);`

### UPick (`UPick.p`)

**Purpose**: Pick module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `QuickDraw32Bit`, `PickerIntf`, `UDialog`, `UBWDialog`, `UCommands`, `UAdjust`, `UGhost`, `USeparation`
**Constants**:
- `kStorageCells = 30;`
**Types & Objects**:
- `TPickerView` object (extends `TView`)
  - field: `fColorRect: Rect;`
  - field: `fLevelsRect: Rect;`
  - field: `fMenuRect1: Rect;`
  - field: `fMenuRect2: Rect;`
  - field: `fMenu1: MenuHandle;`
  - field: `fMenu2: MenuHandle;`
  - field: `fColorSpace: INTEGER;`
  - field: `fBackground: BOOLEAN;`
  - field: `fLevelsLocked: BOOLEAN;`
  - field: `fLevel: ARRAY [0..3] OF INTEGER;`
  - field: `fOffset: ARRAY [0..3] OF INTEGER;`
  - field: `fStorageRect: Rect;`
  - field: `fStorage: ARRAY [0..kStorageCells-1] OF RGBColor;`
  - field: `fScratchRect: Rect;`
  - field: `fScratchView: TScratchView;`
  - method: `PROCEDURE IPickerView;`
  - method: `PROCEDURE ComputeLevels;`
  - method: `PROCEDURE ComputeColor (VAR color: RGBColor);`
  - method: `PROCEDURE DrawColor;`
  - method: `PROCEDURE DrawStorage (cell1: INTEGER; cell2: INTEGER);`
  - method: `PROCEDURE GetSliderRect (band: INTEGER; VAR r: Rect);`
  - method: `PROCEDURE DrawSliders;`
  - method: `PROCEDURE DrawLevel (band: INTEGER);`
  - method: `PROCEDURE DrawLevels;`
  - method: `PROCEDURE UpdateColor;`
  - method: `PROCEDURE Draw (area: Rect); OVERRIDE;`
  - method: `FUNCTION DoMouseCommand (VAR downLocalPoint: Point; VAR info: EventInfo; VAR hysteresis: Point): TCommand; OVERRIDE;`
- `TScratchFrame` object (extends `TFrame`)
  - method: `FUNCTION AdjustSBars: BOOLEAN; OVERRIDE;`
- `TScratchView` object (extends `TImageView`)
  - field: `fLastBand: INTEGER;`
  - field: `fLastSubtractive: BOOLEAN;`
  - method: `PROCEDURE IScratchView (doc: TImageDocument);`
  - method: `FUNCTION DoMouseCommand (VAR downLocalPoint: Point; VAR info: EventInfo; VAR hysteresis: Point): TCommand; OVERRIDE;`
  - method: `PROCEDURE GetViewScreenInfo (VAR depth: INTEGER; VAR monochrome: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION ColorizeBand (VAR band: INTEGER; VAR subtractive: BOOLEAN): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE CheckDither; OVERRIDE;`
  - method: `FUNCTION MinMagnification: INTEGER; OVERRIDE;`
- `DualColor` record: `RECORD rgb: RGBColor; hsv: HSVColor END;`
- `TCubeDialog` object (extends `TBWDialog`)
  - field: `fOldColor: DualColor;`
  - field: `fCurColor: DualColor;`
  - field: `fNewColor: DualColor;`
  - field: `fWarnRect: Rect;`
  - field: `fCoreRect: Rect;`
  - field: `fCrossRect: Rect;`
  - field: `fPatchRect: Rect;`
  - field: `fColorTable: CTabHandle;`
  - field: `fPalette: PaletteHandle;`
  - field: `fBuffer1: Handle;`
  - field: `fBuffer2: Handle;`
  - field: `fCoreCluster: TRadioCluster;`
  - field: `fCoords: ARRAY [0..9] OF TFixedText;`
  - field: `fCMYKMode: BOOLEAN;`
  - field: `fWarning: BOOLEAN;`
  - field: `fDirty: BOOLEAN;`
  - field: `fDirtyTime: LONGINT;`
  - method: `PROCEDURE ICubeDialog (color: RGBColor);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `FUNCTION GetDepth: INTEGER;`
  - method: `PROCEDURE DrawRGB (rPtr: Ptr; gPtr: Ptr; bPtr: Ptr; area: Rect; magnification: INTEGER);`
  - method: `PROCEDURE DrawPatch (which: BOOLEAN);`
  - method: `PROCEDURE DecodeCoords (color: DualColor; VAR hsb: BOOLEAN; VAR a1, a2, a3: INTEGER; VAR c1, c2, c3: INTEGER);`
  - method: `PROCEDURE DrawCircle (c1, c2: INTEGER; turnOn: BOOLEAN);`
  - method: `PROCEDURE DrawCross (area: Rect);`
  - method: `PROCEDURE DrawLevel (c3: INTEGER);`
  - method: `PROCEDURE DrawCore (level: BOOLEAN);`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `PROCEDURE CoreChanged;`
  - method: `PROCEDURE StuffCoordsHSB;`
  - method: `PROCEDURE StuffCoordsRGB;`
  - method: `PROCEDURE StuffCoordsCMYK;`
  - method: `PROCEDURE StuffCoords;`
  - method: `PROCEDURE UpdateNewColor (c1, c2, c3: INTEGER);`
  - method: `PROCEDURE TrackLevel;`
  - method: `PROCEDURE TrackCircle;`
  - method: `PROCEDURE DoFilterEvent (VAR anEvent: EventRecord; VAR itemHit: INTEGER; VAR handledIt: BOOLEAN; VAR doReturn: BOOLEAN); OVERRIDE; PROCEDURE ClearDirty; PROCEDURE TypedHSB; PROCEDURE TypedRGB; PROCEDURE TypedCMYK; END;`
- `TEyedropperTool` object (extends `TCommand`)
  - field: `fView: TImageView;`
  - field: `fBackground: BOOLEAN;`
  - method: `PROCEDURE IEyedropperTool (view: TImageView; background: BOOLEAN);`
  - method: `PROCEDURE TrackFeedBack (anchorPoint, nextPoint: Point; turnItOn, mouseDidMove: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint, previousPoint, nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
**Routines**:
- `PROCEDURE InitPicker;`
- `FUNCTION PickerVisible: BOOLEAN;`
- `FUNCTION PickerBackground: BOOLEAN;`
- `PROCEDURE ShowPicker (visible: BOOLEAN);`
- `PROCEDURE TrackPickerCursor (mousePt: Point; spaceDown: BOOLEAN; shiftDown: BOOLEAN; optionDown: BOOLEAN; commandDown: BOOLEAN);`
- `PROCEDURE InvalidateGhostColors;`
- `PROCEDURE InvalidateCMYKPicker;`
- `PROCEDURE ResetGroundColors;`
- `FUNCTION DoSetColor (cube: BOOLEAN; index: INTEGER; VAR color: RGBColor): BOOLEAN;`
- `PROCEDURE DoSetForeground;`
- `PROCEDURE DoSetBackground;`
- `FUNCTION DoEyedropperTool (view: TImageView; background: BOOLEAN): TCommand;`

### UPICTFile (`UPICTFile.p`)

**Purpose**: PICT File module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `QuickDraw32Bit`, `UDialog`, `URootFormat`, `UProgress`
**Types & Objects**:
- `TPICTFileFormat` object (extends `TRootFormat`)
  - field: `fDepth: INTEGER;`
  - field: `fTransferMode: INTEGER;`
  - field: `fSystemPalette: BOOLEAN;`
  - field: `fVersion1: BOOLEAN;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `PROCEDURE AdjustRects (doc: TImageDocument; hRes: Fixed; vRes: Fixed; pictBounds: Rect; bounds: Rect; VAR srcRect: Rect; VAR dstRect: Rect);`
  - method: `PROCEDURE ParseCopyBits (doc: TImageDocument; opcode: INTEGER; pictBounds: Rect; canAbort: BOOLEAN);`
  - method: `PROCEDURE ParseDirectBits (doc: TImageDocument; opcode: INTEGER; pictBounds: Rect; canAbort: BOOLEAN);`
  - method: `PROCEDURE ParsePICT (doc: TImageDocument; canAbort: BOOLEAN);`
  - method: `PROCEDURE ParseOldPICT (doc: TImageDocument);`
  - method: `PROCEDURE ParseNewPICT (doc: TImageDocument);`
  - method: `PROCEDURE DoReadPICT (doc: TImageDocument; canAbort: BOOLEAN);`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE PutOpcode (opcode: INTEGER);`
  - method: `PROCEDURE DoWritePICT (doc: TImageDocument);`
  - method: `PROCEDURE AddPixelPaintStuff;`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UPICTResource (`UPICTResource.p`)

**Purpose**: PICT Resource module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `URootFormat`, `UPICTFile`
**Variables**:
- `gClipFormat: TClipFormat;`
**Types & Objects**:
- `TPICTResourceFormat` object (extends `TPICTFileFormat`)
  - field: `fResID: INTEGER;`
  - field: `fResName: Str255;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `PROCEDURE ConvertPICT (thePICT: Handle; doc: TImageDocument);`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION MakePICT (doc: TImageDocument): Handle;`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`
- `TClipFormat` object (extends `TPICTResourceFormat`)
  - method: `FUNCTION MakePICT (doc: TImageDocument): Handle; OVERRIDE;`

### UPixar (`UPixar.p`)

**Purpose**: Pixar module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `URootFormat`, `UProgress`
**Types & Objects**:
- `TPixarFormat` object (extends `TRootFormat`)
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `PROCEDURE DecodeRow (dBytes: INTEGER; pBytes: INTEGER; rBytes: LONGINT; blockSize: INTEGER; buffer: Ptr);`
  - method: `PROCEDURE ReadTile (doc: TImageDocument; rowOffset: INTEGER; colOffset: INTEGER; tileRows: INTEGER; tileCols: INTEGER; storage: INTEGER; blockSize: INTEGER);`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION SaveChannels (doc: TImageDocument): INTEGER;`
  - method: `FUNCTION DataForkBytes (doc: TImageDocument): LONGINT; OVERRIDE;`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UPixelPaint (`UPixelPaint.p`)

**Purpose**: Pixel Paint module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `URootFormat`, `UPICTFile`, `UProgress`
**Types & Objects**:
- `TPixelPaintFormat` object (extends `TPICTFileFormat`)
  - field: `fCenter: BOOLEAN;`
  - field: `fCanvasSize: INTEGER;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `PROCEDURE ReadRow (cols: INTEGER);`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION DataForkBytes (doc: TImageDocument): LONGINT; OVERRIDE;`
  - method: `FUNCTION RsrcForkBytes (doc: TImageDocument): LONGINT; OVERRIDE;`
  - method: `PROCEDURE DoWriteImage (doc: TImageDocument);`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UPostScript (`UPostScript.p`)

**Purpose**: Post Script printing pipeline
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UScreen`, `UTransfer`, `UProgress`
**Types & Objects**:
- `TRegMarkList` array: `ARRAY [0..7] OF Point;`
**Routines**:
- `PROCEDURE BeginPostScript (toFile: BOOLEAN; refNum: INTEGER);`
- `PROCEDURE FlushPostScript;`
- `PROCEDURE EndPostScript;`
- `PROCEDURE GenerateEPSFHeader (doc: TImageDocument; channel: INTEGER; inputArea: Rect; outputArea: Rect; useDCS: BOOLEAN; color: BOOLEAN; screen: BOOLEAN; transfer: BOOLEAN; binary: BOOLEAN);`
- `PROCEDURE GeneratePostScript (doc: TImageDocument; channel: INTEGER; inputArea: Rect; outputArea: Rect; color: BOOLEAN; screen: BOOLEAN; transfer: BOOLEAN; mask: BOOLEAN; binary: BOOLEAN; printing: BOOLEAN);`
- `PROCEDURE GenerateRegMarks (marks: TRegMarkList);`
- `PROCEDURE GenerateStarTargets (bounds: Rect);`
- `PROCEDURE GenerateCropMarks (bounds: Rect);`
- `PROCEDURE GenerateGrayBar (bounds: Rect);`
- `PROCEDURE GenerateColorBars (bounds: Rect; channel: INTEGER);`
- `PROCEDURE GenerateBorder (location: Point; width: INTEGER; height: INTEGER; resolution: Fixed; border: Fixed);`
- `PROCEDURE GenerateSetFont;`
- `PROCEDURE GenerateText (s: Str255; center: BOOLEAN; left: INTEGER; right: INTEGER; bottom: INTEGER);`
- `PROCEDURE GenerateOther (s: Str255);`

### UPreferences (`UPreferences.p`)

**Purpose**: Preferences module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `SysEqu`, `UDialog`, `UBWDialog`, `USeparation`
**Routines**:
- `PROCEDURE InitPreferences;`
- `PROCEDURE SavePreferences;`
- `PROCEDURE DoPreferencesCommand;`

### UPressure (`UPressure.p`)

**Purpose**: Pressure module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`
**Variables**:
- `gHavePressure: BOOLEAN;`
**Routines**:
- `PROCEDURE InitPressure;`
- `FUNCTION UsingPressure: BOOLEAN;`
- `FUNCTION ReadPressure: INTEGER;`

### UPrint (`UPrint.p`)

**Purpose**: Print printing pipeline
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `QuickDraw32Bit`, `PrintTraps`, `UPrinting`, `UDialog`, `UBWDialog`, `UPostScript`, `UScreen`, `USeparation`, `UTransfer`, `UProgress`
**Types & Objects**:
- `TImageStyleCommand` object (extends `TPrintStyleChangeCommand`)
  - field: `fDoc: TImageDocument;`
  - field: `fOldStyleInfo: TStyleInfo;`
  - field: `fNewStyleInfo: TStyleInfo;`
  - method: `PROCEDURE ImageStyleCommand (itsPrintHandler: TStdPrintHandler);`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TImagePrintHandler` object (extends `TStdPrintHandler`)
  - field: `fColor: BOOLEAN;`
  - field: `fCorrect: BOOLEAN;`
  - field: `fSelection: BOOLEAN;`
  - field: `fAllChannels: BOOLEAN;`
  - field: `fPrintUsingASCII: BOOLEAN;`
  - field: `fAllowColor: BOOLEAN;`
  - field: `fAllowCorrect: BOOLEAN;`
  - field: `fInputArea: Rect;`
  - field: `fOutputArea: Rect;`
  - field: `fExpandedArea: Rect;`
  - field: `fRegMarks: TRegMarkList;`
  - method: `PROCEDURE IImagePrintHandler (view: TImageView);`
  - method: `FUNCTION IsPostScript: BOOLEAN;`
  - method: `PROCEDURE DoStyleItem (theDialog: DialogPtr; itemNo: INTEGER);`
  - method: `PROCEDURE AddStyleItems (theDialog: DialogPtr);`
  - method: `FUNCTION DoPageSetupDialog: BOOLEAN;`
  - method: `FUNCTION PosePageSetupDialog (VAR cancelled: BOOLEAN): TCommand; OVERRIDE;`
  - method: `PROCEDURE DoJobItem (theDialog: DialogPtr; itemNo: INTEGER);`
  - method: `PROCEDURE AddJobItems (theDialog: DialogPtr);`
  - method: `FUNCTION DoJobDialog: BOOLEAN;`
  - method: `PROCEDURE PosePrintDialog; OVERRIDE;`
  - method: `PROCEDURE ShowDocBeingPrinted (entering: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE PoseJobDialog (VAR proceed: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION MaxPageNumber: INTEGER; OVERRIDE;`
  - method: `PROCEDURE SetPage (aPageNumber: INTEGER); OVERRIDE;`
  - method: `FUNCTION OneSubJob (subjobFirstPage, subjobLastPage: INTEGER; justSpool: BOOLEAN; partialJob: BOOLEAN; VAR ranOutOfSpace: BOOLEAN; VAR lastPageTried: INTEGER; VAR proceed: BOOLEAN): TCommand; OVERRIDE;`
  - method: `PROCEDURE FocusOnInterior (aPageNumber: INTEGER); OVERRIDE;`
  - method: `FUNCTION WarnIfTooLarge: BOOLEAN;`
  - method: `FUNCTION WarnIfTooFine: BOOLEAN;`
  - method: `PROCEDURE PositionStuffOnPage;`
  - method: `PROCEDURE PrintUsingPostScript (doc: TImageDocument; channel: INTEGER);`
  - method: `FUNCTION GetPortDepth: INTEGER;`
  - method: `PROCEDURE PrintUsingQuickDraw (doc: TImageDocument; channel: INTEGER);`
  - method: `PROCEDURE PrintPostScriptMarks (doc: TImageDocument; channel: INTEGER);`
  - method: `PROCEDURE PrintQuickDrawMarks (doc: TImageDocument; channel: INTEGER);`
  - method: `FUNCTION CorrectPrintingColors (doc: TImageDocument; rgb: BOOLEAN): TImageDocument;`
  - method: `PROCEDURE DrawPageInterior (aPageNumber: INTEGER); OVERRIDE;`
**Routines**:
- `PROCEDURE InitImagePrinting;`
- `PROCEDURE GetPrintRects (doc: TImageDocument; bounds: Rect; VAR thePaper: Rect; VAR theInk: Rect; VAR theImage: Rect);`
- `PROCEDURE AddImagePrintHander (view: TImageView);`

### UProgress (`UProgress.p`)

**Purpose**: Progress infrastructure
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `UDialog`, `UBWDialog`
**Routines**:
- `PROCEDURE InitProgress;`
- `PROCEDURE StartProgress (s: Str255);`
- `PROCEDURE CommandProgress (cmd: INTEGER);`
- `PROCEDURE FinishProgress;`
- `PROCEDURE UpdateProgress (m, n: LONGINT);`
- `PROCEDURE StartTask (f: EXTENDED);`
- `PROCEDURE FinishTask;`

### URawFormat (`URawFormat.p`)

**Purpose**: Raw Format file format handler
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `URootFormat`, `UProgress`
**Types & Objects**:
- `TRawFormat` object (extends `TRootFormat`)
  - field: `fHeader: LONGINT;`
  - field: `fInterleaved: BOOLEAN;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION DataForkBytes (doc: TImageDocument): LONGINT; OVERRIDE;`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UResize (`UResize.p`)

**Purpose**: Resize module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UProgress`
**Types & Objects**:
- `TWordArray` array: `ARRAY [0..kMaxCoord-1] OF INTEGER;`
- `PWordArray` pointer: `^TWordArray;`
- `HWordArray` pointer: `^PWordArray;`
- `TByteArray` array: `PACKED ARRAY [0..kMaxCoord-1] OF CHAR;`
- `PByteArray` pointer: `^TByteArray;`
- `HByteArray` pointer: `^PByteArray;`
- `TResizeMode` enum → `ResizeModeSample`, `ResizeModeInterpolate`, `ResizeModeBiCubic`, `ResizeModeBigAverage`, `ResizeModeAverage`
- `TResizeTable` object (extends `TObject`)
  - field: `fOldSize: INTEGER;`
  - field: `fNewSize: INTEGER;`
  - field: `fMode: TResizeMode;`
  - field: `fTable1: HWordArray;`
  - field: `fTable2: HByteArray;`
  - field: `fTotalWeight: INTEGER;`
  - method: `PROCEDURE IResizeTable (oldSize: INTEGER; newSize: INTEGER; sample: BOOLEAN);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE ResizeLine (srcPtr, dstPtr: Ptr);`
- `TResizeCommand` object (extends `TBufferCommand`)
  - field: `fNewRows: INTEGER;`
  - field: `fNewCols: INTEGER;`
  - field: `fSameSize: BOOLEAN;`
  - field: `fVPlacement: INTEGER;`
  - field: `fHPlacement: INTEGER;`
  - field: `fOldStyle: TStyleInfo;`
  - field: `fNewStyle: TStyleInfo;`
  - method: `PROCEDURE IResizeCommand (itsCommand: INTEGER; view: TImageView; newRows: INTEGER; newCols: INTEGER; vPlacement: INTEGER; hPlacement: INTEGER);`
  - method: `PROCEDURE CopyPart (image: TVMArray; buffer: TVMArray; background: INTEGER);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
**Routines**:
- `PROCEDURE InitResize;`
- `PROCEDURE DoResizeArray (srcArray: TVMArray; dstArray: TVMArray; hTable: TResizeTable; vTable: TResizeTable; canAbort: BOOLEAN);`
- `PROCEDURE ResizeArray (srcArray: TVMArray; dstArray: TVMArray; sample: BOOLEAN; canAbort: BOOLEAN);`
- `FUNCTION DoResizeImage (view: TImageView): TCommand;`
- `FUNCTION DoResampleImage (view: TImageView): TCommand;`

### URootFormat (`URootFormat.p`)

**Purpose**: Root Format file format handler
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UProgress`
**Types & Objects**:
- `TOSTypeText` object (extends `TKeyHandler`)
  - field: `fValue: OSType;`
  - method: `PROCEDURE IOSTypeText (itsItemNumber: INTEGER; itsParent: TDialogView; initValue: OSType);`
  - method: `PROCEDURE Validate (VAR succeeded: BOOLEAN); OVERRIDE;`
- `TRootFormat` object (extends `TImageFormat`)
  - field: `fDialogID: INTEGER;`
  - field: `fFTypeItem: INTEGER;`
  - field: `fFCreatorItem: INTEGER;`
  - field: `fCheckBoxes: INTEGER;`
  - field: `fCheck1Item: INTEGER;`
  - field: `fCheck2Item: INTEGER;`
  - field: `fCheck3Item: INTEGER;`
  - field: `fRadioClusters: INTEGER;`
  - field: `fRadio1Item: INTEGER;`
  - field: `fRadio1Count: INTEGER;`
  - field: `fRadio2Item: INTEGER;`
  - field: `fRadio2Count: INTEGER;`
  - field: `fInts: INTEGER;`
  - field: `fInt1Item: INTEGER;`
  - field: `fInt1Lower: LONGINT;`
  - field: `fInt1Upper: LONGINT;`
  - field: `fStrs: INTEGER;`
  - field: `fStr1Item: INTEGER;`
  - field: `fCheck1: BOOLEAN;`
  - field: `fCheck2: BOOLEAN;`
  - field: `fCheck3: BOOLEAN;`
  - field: `fRadio1: INTEGER;`
  - field: `fRadio2: INTEGER;`
  - field: `fInt1: LONGINT;`
  - field: `fStr1: StringPtr;`
  - field: `fLSBFirst: BOOLEAN;`
  - field: `fRefNum: INTEGER;`
  - field: `fSpool: BOOLEAN;`
  - field: `fSpoolData: Handle;`
  - field: `fSpoolPosition: LONGINT;`
  - field: `fSpoolEOFPosition: LONGINT;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `PROCEDURE DoOptionsDialog;`
  - method: `FUNCTION GetFileLength: LONGINT;`
  - method: `FUNCTION GetFilePosition: LONGINT;`
  - method: `PROCEDURE SeekTo (n: LONGINT);`
  - method: `PROCEDURE SkipBytes (n: LONGINT);`
  - method: `PROCEDURE GetBytes (n: LONGINT; p: Ptr);`
  - method: `FUNCTION GetByte: INTEGER;`
  - method: `FUNCTION GetWord: INTEGER;`
  - method: `FUNCTION GetLong: LONGINT;`
  - method: `PROCEDURE GetRawRows (buffer: TVMArray; rowBytes: INTEGER; first: INTEGER; count: INTEGER; canAbort: BOOLEAN);`
  - method: `PROCEDURE GetInterleavedRows (buffer: TChannelArrayList; channels: INTEGER; first: INTEGER; count: INTEGER; canAbort: BOOLEAN);`
  - method: `PROCEDURE PutBytes (n: LONGINT; p: Ptr);`
  - method: `PROCEDURE PutByte (w: INTEGER);`
  - method: `PROCEDURE PutWord (w: INTEGER);`
  - method: `PROCEDURE PutLong (l: LONGINT);`
  - method: `PROCEDURE PutZeros (n: LONGINT);`
  - method: `PROCEDURE PutRawRows (buffer: TVMArray; rowBytes: INTEGER; first: INTEGER; count: INTEGER);`
  - method: `PROCEDURE PutInterleavedRows (buffer: TChannelArrayList; channels: INTEGER; first: INTEGER; count: INTEGER);`
**Routines**:
- `PROCEDURE MyPackBits (VAR srcPtr, dstPtr: Ptr; srcBytes: INTEGER);`
- `PROCEDURE TestForMonochrome (doc: TImageDocument);`
- `PROCEDURE TestForHalftone (doc: TImageDocument);`
- `FUNCTION AskAdjustAspect: BOOLEAN;`

### URotate (`URotate.p`)

**Purpose**: Rotate module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UResize`, `UProgress`
**Types & Objects**:
- `TFlipImageCommand` object (extends `TBufferCommand`)
  - field: `fVertical: BOOLEAN;`
  - field: `fHorizontal: BOOLEAN;`
  - method: `PROCEDURE IFlipImageCommand (view: TImageView; horizontal, vertical: BOOLEAN);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TRotateImageCommand` object (extends `TBufferCommand`)
  - field: `fAngle: INTEGER;`
  - method: `PROCEDURE IRotateImageCommand (view: TImageView; angle: INTEGER);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TFlipFloatCommand` object (extends `TFloatCommand`)
  - field: `fVertical: BOOLEAN;`
  - field: `fHorizontal: BOOLEAN;`
  - method: `PROCEDURE IFlipFloatCommand (view: TImageView; horizontal, vertical: BOOLEAN);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TRotateFloatCommand` object (extends `TFloatCommand`)
  - field: `fAngle: INTEGER;`
  - method: `PROCEDURE IRotateFloatCommand (view: TImageView; angle: INTEGER);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TEffectsCommand` object (extends `TFloatCommand`)
  - field: `fMode: INTEGER;`
  - field: `fSrcRect: Rect;`
  - field: `fDstRect: Rect;`
  - field: `fMidRect: Rect;`
  - field: `fComplex: BOOLEAN;`
  - field: `fRecycled: BOOLEAN;`
  - field: `fAnother: BOOLEAN;`
  - field: `fCorner: INTEGER;`
  - field: `fChangeCount: LONGINT;`
  - field: `fOldCorners: TCornerList;`
  - field: `fNewCorners: TCornerList;`
  - field: `fLastCorners: TCornerList;`
  - field: `fBaseCorners: TCornerList;`
  - method: `PROCEDURE IEffectsCommand (itsCommand: INTEGER; view: TImageView; downPoint: Point);`
  - method: `PROCEDURE Recycle (view: TImageView; downPoint: Point);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE TrackConstrain (anchorPoint, previousPoint: Point; VAR nextPoint: Point); OVERRIDE;`
  - method: `PROCEDURE TrackFeedback (anchorPoint, nextPoint: Point; turnItOn, mouseDidMove: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint, previousPoint, nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
  - method: `PROCEDURE ComputeNewCorners (delta: Point);`
  - method: `PROCEDURE CompDstRect;`
  - method: `PROCEDURE DoEffect (srcArray: TVMArray; dstArray: TVMArray; sample: BOOLEAN; background: INTEGER);`
  - method: `FUNCTION TestAnother: BOOLEAN;`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE SwapIt (undo: BOOLEAN);`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
  - method: `PROCEDURE Commit; OVERRIDE;`
- `TResizeEffect` object (extends `TEffectsCommand`)
  - method: `PROCEDURE IResizeEffect (view: TImageView; downPoint: Point);`
  - method: `PROCEDURE ComputeNewCorners (delta: Point); OVERRIDE;`
  - method: `PROCEDURE DoEffect (srcArray: TVMArray; dstArray: TVMArray; sample: BOOLEAN; background: INTEGER); OVERRIDE;`
- `TRotateEffect` object (extends `TEffectsCommand`)
  - field: `fAngle: INTEGER;`
  - field: `fRowRadius: EXTENDED;`
  - field: `fColRadius: EXTENDED;`
  - field: `fCenterRow: EXTENDED;`
  - field: `fCenterCol: EXTENDED;`
  - field: `fBaseAngle: EXTENDED;`
  - method: `PROCEDURE IRotateEffect (view: TImageView; downPoint: Point);`
  - method: `PROCEDURE Recycle (view: TImageView; downPoint: Point); OVERRIDE;`
  - method: `PROCEDURE ComputeBaseAngle;`
  - method: `PROCEDURE ComputeNewCorners (delta: Point); OVERRIDE;`
  - method: `PROCEDURE CompDstRect; OVERRIDE;`
  - method: `PROCEDURE DoEffect (srcArray: TVMArray; dstArray: TVMArray; sample: BOOLEAN; background: INTEGER); OVERRIDE;`
- `TSkewEffect` object (extends `TEffectsCommand`)
  - field: `fCoupled: BOOLEAN;`
  - field: `fHaveAxis: BOOLEAN;`
  - field: `fVertical: BOOLEAN;`
  - method: `PROCEDURE ISkewEffect (view: TImageView; downPoint: Point);`
  - method: `PROCEDURE Recycle (view: TImageView; downPoint: Point); OVERRIDE;`
  - method: `PROCEDURE ComputeNewCorners (delta: Point); OVERRIDE;`
  - method: `PROCEDURE DoEffect (srcArray: TVMArray; dstArray: TVMArray; sample: BOOLEAN; background: INTEGER); OVERRIDE;`
- `TPerspectiveTable` object (extends `TResizeTable`)
  - method: `PROCEDURE IPerspectiveTable (oldSize: INTEGER; newSize: INTEGER; sample: BOOLEAN; a: EXTENDED);`
- `TPerspectiveEffect` object (extends `TEffectsCommand`)
  - method: `PROCEDURE IPerspectiveEffect (view: TImageView; downPoint: Point);`
  - method: `PROCEDURE ComputeNewCorners (delta: Point); OVERRIDE;`
  - method: `PROCEDURE DoEffect (srcArray: TVMArray; dstArray: TVMArray; sample: BOOLEAN; background: INTEGER); OVERRIDE;`
- `TDistortEffect` object (extends `TEffectsCommand`)
  - method: `PROCEDURE IDistortEffect (view: TImageView; downPoint: Point);`
  - method: `PROCEDURE ComputeNewCorners (delta: Point); OVERRIDE;`
  - method: `PROCEDURE DoEffect (srcArray: TVMArray; dstArray: TVMArray; sample: BOOLEAN; background: INTEGER); OVERRIDE;`
**Routines**:
- `PROCEDURE InitRotations;`
- `PROCEDURE DoTransposeArray (srcArray: TVMArray; dstArray: TVMArray; horizontal: BOOLEAN; vertical: BOOLEAN);`
- `FUNCTION DoFlipCommand (view: TImageView; horizontal, vertical: BOOLEAN): TCommand;`
- `FUNCTION DoRotateCommand (view: TImageView; angle: INTEGER): TCommand;`
- `FUNCTION DoRotateArbitraryCommand (view: TImageView): TCommand;`
- `FUNCTION SetEffectMode (view: TImageView; mode: INTEGER): TCommand;`
- `FUNCTION DoEffectsCommand (view: TImageView; downPoint: Point): TCommand;`

### UScan (`UScan.p`)

**Purpose**: Scan module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UCommands`, `UProgress`, `AcquireInterface`, `ExportInterface`
**Routines**:
- `PROCEDURE VerifyHardware;`
- `PROCEDURE InitScanners;`
- `PROCEDURE DoAcquireCommand (name: Str255);`
- `PROCEDURE DoExportCommand (doc: TImageDocument; name: Str255);`

### UScitexFormat (`UScitexFormat.p`)

**Purpose**: Scitex Format file format handler
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `URootFormat`, `UProgress`
**Types & Objects**:
- `TScitexFormat` object (extends `TRootFormat`)
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION DataForkBytes (doc: TImageDocument): LONGINT; OVERRIDE;`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UScreen (`UScreen.p`)

**Purpose**: Screen module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UResize`, `UProgress`
**Constants**:
- `kMaxCellSize = 256;`
**Types & Objects**:
- `TLSDialog` object (extends `TBWDialog`)
  - field: `fLoadTitle1: Str255;`
  - field: `fSaveTitle1: Str255;`
  - field: `fLoadTitle2: Str255;`
  - field: `fSaveTitle2: Str255;`
  - field: `fOptionDown: BOOLEAN;`
  - field: `fLoadButton: ControlHandle;`
  - field: `fSaveButton: ControlHandle;`
  - method: `PROCEDURE ILSDialog (dialogID: INTEGER; loadItem: INTEGER; saveItem: INTEGER);`
  - method: `PROCEDURE UpdateButtons;`
  - method: `FUNCTION DoSetCursor (localPoint: Point): BOOLEAN; OVERRIDE;`
**Routines**:
- `PROCEDURE InitScreens;`
- `PROCEDURE RegisterSpot (h: Handle);`
- `PROCEDURE MarkSpotDirty;`
- `PROCEDURE CollectSpotGarbage;`
- `PROCEDURE SetHalftoneScreen (VAR spec: THalftoneSpec; allowCustom: BOOLEAN);`
- `PROCEDURE SetHalftoneScreens (VAR specs: THalftoneSpecs; allowCustom: BOOLEAN);`
- `PROCEDURE MakeScreen (limit: INTEGER; resolution: Fixed; spec: THalftoneSpec; VAR cellData: Handle; VAR cellSize: INTEGER);`
- `FUNCTION ConvertScreen (cellData: Handle; cellSize: INTEGER): TVMArray;`
- `PROCEDURE HalftoneArea (srcArray: TVMArray; dstArray: TVMArray; r: Rect; newRows: INTEGER; newCols: INTEGER; map: PLookUpTable; screen: TVMArray; canAbort: BOOLEAN);`

### USelect (`USelect.p`)

**Purpose**: Select editing commands
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UFilters`, `UProgress`
**Types & Objects**:
- `TSelectRect` object (extends `TFloatCommand`)
  - field: `fSelectRect: Rect;`
  - method: `PROCEDURE ISelectRect (itsCommand: INTEGER; view: TImageView; r: Rect);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TMaskCommand` object (extends `TFloatCommand`)
  - field: `fAdd: BOOLEAN;`
  - field: `fDrop: BOOLEAN;`
  - field: `fRemove: BOOLEAN;`
  - field: `fRefine: BOOLEAN;`
  - field: `fObscure: BOOLEAN;`
  - field: `fTrim: BOOLEAN;`
  - field: `fMask: TVMArray;`
  - field: `fMaskBounds: Rect;`
  - field: `fSaveRect: Rect;`
  - field: `fSaveMask: TVMArray;`
  - method: `PROCEDURE IMaskCommand (itsCommand: INTEGER; view: TImageView; add, remove, refine, drop: BOOLEAN; needMask: BOOLEAN; obscure: BOOLEAN);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE FixObscured;`
  - method: `PROCEDURE TrackFeedBack (anchorPoint, nextPoint: Point; turnItOn, mouseDidMove: BOOLEAN); OVERRIDE;`
  - method: `PROCEDURE CombineMask (sr: Rect; sm: TVMArray; VAR delta: Rect);`
  - method: `FUNCTION SolidMask: BOOLEAN;`
  - method: `PROCEDURE DropDifference;`
  - method: `PROCEDURE TrimFloat (delta: Rect);`
  - method: `PROCEDURE UpdateSelection;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TLassoSelector` object (extends `TMaskCommand`)
  - field: `fWhite: BOOLEAN;`
  - field: `fMovedOnce: BOOLEAN;`
  - field: `fViewBounds: Rect;`
  - field: `fMouseRect: Rect;`
  - method: `PROCEDURE ILassoSelector (view: TImageView; downPoint: Point; add, remove, refine, drop: BOOLEAN);`
  - method: `PROCEDURE TrackConstrain (anchorPoint, previousPoint: Point; VAR nextPoint: Point); OVERRIDE;`
  - method: `FUNCTION TrackMouseUp (VAR didMove: BOOLEAN; VAR anchorPoint: Point; VAR previousPoint: Point): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE ComputeMask;`
  - method: `PROCEDURE MarkMask (fromPt, toPt: Point);`
  - method: `PROCEDURE Extend (fromPt, toPt: Point);`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint, previousPoint, nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
- `THistograms` array: `ARRAY [0..5] OF THistogram;`
- `TWandSelector` object (extends `TMaskCommand`)
  - field: `fIgnore : INTEGER;`
  - field: `fTolerance: INTEGER;`
  - field: `fFuzziness: INTEGER;`
  - field: `fConnected: BOOLEAN;`
  - field: `fMap: ARRAY [0..5] OF TLookUpTable;`
  - method: `PROCEDURE IWandSelector (itsCommand: INTEGER; view: TImageView; add, remove, refine: BOOLEAN);`
  - method: `PROCEDURE HistRegion (src1Array: TVMArray; src2Array: TVMArray; src3Array: TVMArray; rgnRect: Rect; rgnMask: TVMArray; VAR hists: THistograms);`
  - method: `PROCEDURE BuildMap (hist: THistogram; VAR map: TLookUpTable; tolerance: INTEGER; fuzziness: INTEGER);`
  - method: `PROCEDURE BuildMaps (rgnRect: Rect; rgnMask: TVMArray);`
  - method: `PROCEDURE PrepareLine (row: INTEGER);`
  - method: `PROCEDURE Grow4Connected (VAR lower: INTEGER; VAR upper: INTEGER; VAR r: Rect);`
  - method: `PROCEDURE DilateArea (r: Rect);`
  - method: `PROCEDURE MarkRegion (rgnRect: Rect; rgnMask: TVMArray);`
  - method: `PROCEDURE GrowRegion (rgnRect: Rect; rgnMask: TVMArray);`
  - method: `PROCEDURE GrowFromSeed (downPoint: Point);`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint, previousPoint, nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
- `TBucketTool` object (extends `TWandSelector`)
  - method: `PROCEDURE IBucketTool (view: TImageView; refine: BOOLEAN);`
  - method: `PROCEDURE FillMaskedArea;`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint, previousPoint, nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TGrowCommand` object (extends `TWandSelector`)
  - method: `PROCEDURE IGrowCommand (view: TImageView; connected: BOOLEAN);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
- `THandTool` object (extends `TCommand`)
  - field: `fView: TImageView;`
  - method: `PROCEDURE IHandTool (view: TImageView);`
  - method: `PROCEDURE TrackFeedBack (anchorPoint, nextPoint: Point; turnItOn, mouseDidMove: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION TrackMouse (aTrackPhase: TrackPhase; VAR anchorPoint, previousPoint, nextPoint: Point; mouseDidMove: BOOLEAN): TCommand; OVERRIDE;`
- `TSelectInverse` object (extends `TMaskCommand`)
  - method: `PROCEDURE ISelectInverse (view: TImageView);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
- `TSelectFringe` object (extends `TMaskCommand`)
  - method: `PROCEDURE ISelectFringe (view: TImageView);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
- `TFeatherCommand` object (extends `TMaskCommand`)
  - method: `PROCEDURE IFeatherCommand (view: TImageView);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
- `TDefringeCommand` object (extends `TFloatCommand`)
  - field: `fWidth: INTEGER;`
  - field: `fChannel: INTEGER;`
  - method: `PROCEDURE IDefringeCommand (view: TImageView; width: INTEGER);`
  - method: `PROCEDURE DefringeData (maskArray: TVMArray; dst1Array: TVMArray; dst2Array: TVMArray; dst3Array: TVMArray);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TMakeAlphaCommand` object (extends `TBufferCommand`)
  - field: `fSolid: BOOLEAN;`
  - method: `PROCEDURE IMakeAlphaCommand (view: TImageView);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TSelectAlphaCommand` object (extends `TBufferCommand`)
  - field: `fOldRect: Rect;`
  - field: `fChannel: INTEGER;`
  - method: `PROCEDURE ISelectAlphaCommand (view: TImageView);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
**Routines**:
- `PROCEDURE InitSelections;`
- `FUNCTION DoSelectAll (view: TImageView): TCommand;`
- `FUNCTION DoSelectNone (view: TImageView): TCommand;`
- `FUNCTION DropSelection (view: TImageView): TCommand;`
- `PROCEDURE InterpolatePoints (pt1, pt2: Point; PROCEDURE EachPoint (pt: Point));`
- `FUNCTION DoLassoTool (view: TImageView; downPoint: Point; add: BOOLEAN; remove: BOOLEAN; refine: BOOLEAN; drop: BOOLEAN): TCommand;`
- `PROCEDURE DoLassoOptions;`
- `FUNCTION DoWandTool (view: TImageView; add: BOOLEAN; remove: BOOLEAN; refine: BOOLEAN): TCommand;`
- `PROCEDURE DoWandOptions;`
- `FUNCTION DoBucketTool (view: TImageView): TCommand;`
- `PROCEDURE DoBucketOptions;`
- `FUNCTION DoGrowCommand (view: TImageView; connected: BOOLEAN): TCommand;`
- `FUNCTION DoHandTool (view: TImageView): TCommand;`
- `PROCEDURE CopyAlphaChannel (doc: TImageDocument; buffer: TVMArray);`
- `FUNCTION DoSelectInverse (view: TImageView): TCommand;`
- `PROCEDURE FindTaxiCab (buffer: TVMArray; r: Rect; block: INTEGER);`
- `FUNCTION DoSelectFringe (view: TImageView): TCommand;`
- `FUNCTION DoFeatherCommand (view: TImageView): TCommand;`
- `FUNCTION DoDefringeCommand (view: TImageView): TCommand;`
- `FUNCTION DoMakeAlphaCommand (view: TImageView): TCommand;`
- `FUNCTION DoSelectAlphaCommand (view: TImageView): TCommand;`

### USeparation (`USeparation.p`)

**Purpose**: Separation module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `PickerIntf`, `UDialog`, `UBWDialog`, `UCommands`, `UAdjust`, `UProgress`
**Types & Objects**:
- `TBlackPopUp` object (extends `TPopUpMenu`)
  - field: `fUseGCR: BOOLEAN;`
  - field: `fCmdPick: INTEGER;`
  - method: `PROCEDURE IBlackPopUp (itsLabelNumber: INTEGER; itsItemNumber: INTEGER; itsParent: TDialogView);`
  - method: `FUNCTION DoPopUpMenu (optionDown: BOOLEAN): BOOLEAN; OVERRIDE;`
- `TSeparationDialog` object (extends `TBWDialog`)
  - field: `fSetup: TSeparationSetup;`
  - field: `fPalette: PaletteHandle;`
  - field: `fColorItems: INTEGER;`
  - field: `fColorRect: ARRAY [1..kProgressive] OF Rect;`
  - field: `fScreenColor: ARRAY [1..kProgressive] OF RGBColor;`
  - field: `fColorPercent: ARRAY [1..kProgressive] OF TFixedText;`
  - field: `fGamma: TFixedText;`
  - field: `fInkMaximum: TFixedText;`
  - field: `fUCAPercent: TFixedText;`
  - field: `fBlackPopUp: TBlackPopUp;`
  - field: `fLastGamma: INTEGER;`
  - method: `PROCEDURE ISeparationDialog (VAR setup: TSeparationSetup);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE StuffValues;`
  - method: `PROCEDURE UpdatePalette;`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `FUNCTION DoItemSelected (anItem: INTEGER; VAR handledIt: BOOLEAN; VAR doneWithDialog: BOOLEAN): TCommand; OVERRIDE;`
  - method: `PROCEDURE Validate (VAR succeeded: BOOLEAN); OVERRIDE;`
**Routines**:
- `PROCEDURE InitSeparation;`
- `PROCEDURE GetBlackTables (VAR gcrTable: TLookUpTable; VAR ucrTable: TLookUpTable; id: INTEGER);`
- `PROCEDURE InitCMYK;`
- `PROCEDURE SolveForCMYK (r: INTEGER; g: INTEGER; b: INTEGER; VAR c: INTEGER; VAR m: INTEGER; VAR y: INTEGER; VAR k: INTEGER; VAR inside: BOOLEAN);`
- `PROCEDURE SolveForCMY (r: INTEGER; g: INTEGER; b: INTEGER; VAR c: INTEGER; VAR m: INTEGER; VAR y: INTEGER);`
- `PROCEDURE SolveForRGB (c: INTEGER; m: INTEGER; y: INTEGER; k: INTEGER; VAR r: INTEGER; VAR g: INTEGER; VAR b: INTEGER);`
- `FUNCTION CvtToPercent (gray: INTEGER): INTEGER;`
- `FUNCTION CvtFromPercent (percent: INTEGER): INTEGER;`
- `PROCEDURE DoSeparationSetup (VAR setup: TSeparationSetup);`
- `PROCEDURE SeparateColorLUT (LUT: TRGBLookUpTable; VAR map1: TLookUpTable; VAR map2: TLookUpTable; VAR map3: TLookUpTable; VAR map4: TLookUpTable);`
- `PROCEDURE BuildSeparationTable;`
- `PROCEDURE ConvertRGB2CMYK (srcArray1: TVMArray; srcArray2: TVMArray; srcArray3: TVMArray; dstArray1: TVMArray; dstArray2: TVMArray; dstArray3: TVMArray; dstArray4: TVMArray);`
- `PROCEDURE ConvertRGB2CMY (srcArray1: TVMArray; srcArray2: TVMArray; srcArray3: TVMArray; dstArray1: TVMArray; dstArray2: TVMArray; dstArray3: TVMArray);`
- `PROCEDURE ConvertCMYK2RGB (srcArray1: TVMArray; srcArray2: TVMArray; srcArray3: TVMArray; srcArray4: TVMArray; dstArray1: TVMArray; dstArray2: TVMArray; dstArray3: TVMArray);`
- `PROCEDURE ConvertCMYK2Gray (srcArray1: TVMArray; srcArray2: TVMArray; srcArray3: TVMArray; srcArray4: TVMArray; dstArray: TVMArray);`

### UTable (`UTable.p`)

**Purpose**: Table module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `PickerIntf`, `UDialog`, `UBWDialog`, `UCommands`
**Types & Objects**:
- `TTableCommand` object (extends `TBufferCommand`)
  - field: `fTable: TRGBLookUpTable;`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TTableDialog` object (extends `TBWDialog`)
  - field: `fTableRect: Rect;`
  - field: `fTable: TRGBLookUpTable;`
  - field: `fSystemPalette: PaletteHandle;`
  - method: `PROCEDURE ITableDialog (table: TRGBLookUpTable);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `PROCEDURE DrawAmendments (theItem: INTEGER); OVERRIDE;`
  - method: `PROCEDURE PickRange (index1, index2: INTEGER; cube: BOOLEAN);`
  - method: `PROCEDURE DownInTable (pt: Point; optionDown: BOOLEAN);`
  - method: `PROCEDURE DoFilterEvent (VAR anEvent: EventRecord; VAR itemHit: INTEGER; VAR handledIt: BOOLEAN; VAR doReturn: BOOLEAN); OVERRIDE; PROCEDURE DoLoadTable; PROCEDURE DoSaveTable; PROCEDURE DoButtonPushed (anItem: INTEGER; VAR succeeded: BOOLEAN); OVERRIDE; END;`
**Routines**:
- `FUNCTION DoTableCommand (view: TImageView; name: Str255): TCommand;`
- `FUNCTION DoEditTableCommand (view: TImageView): TCommand;`

### UTarga (`UTarga.p`)

**Purpose**: Targa module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `URootFormat`, `UProgress`
**Types & Objects**:
- `TTargaFormat` object (extends `TRootFormat`)
  - field: `fDepth: INTEGER;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION DataForkBytes (doc: TImageDocument): LONGINT; OVERRIDE;`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UText (`UText.p`)

**Purpose**: Text module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UProgress`
**Types & Objects**:
- `TOffsetTable` array: `ARRAY [0..255] OF INTEGER;`
- `TTextTool` object (extends `TFloatCommand`)
  - field: `fBasePt: Point;`
  - field: `fText: Str255;`
  - field: `fFont : INTEGER;`
  - field: `fSize : INTEGER;`
  - field: `fLeading: INTEGER;`
  - field: `fSpacing: INTEGER;`
  - field: `fStyle : Style;`
  - field: `fAlignment: INTEGER;`
  - field: `fFeather: BOOLEAN;`
  - method: `PROCEDURE ITextTool (view: TImageView; basePt: Point; theText: Str255; theFont: INTEGER; theSize: INTEGER; theLeading: INTEGER; theSpacing: INTEGER; theStyle: Style; alignment: INTEGER; feather: BOOLEAN);`
  - method: `PROCEDURE BuildOffsetTable (s: Str255; scale: INTEGER; VAR offsets: TOffsetTable);`
  - method: `FUNCTION ImageText (VAR r: Rect): TVMArray;`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
- `TTextDialog` object (extends `TBWDialog`)
  - field: `fTextHandler: TKeyHandler;`
  - method: `PROCEDURE DoFilterEvent (VAR anEvent: EventRecord; VAR itemHit: INTEGER; VAR handledIt: BOOLEAN; VAR doReturn: BOOLEAN); OVERRIDE; END;`
**Routines**:
- `PROCEDURE InitTextTool;`
- `FUNCTION DoTextTool (view: TImageView; pt: Point): TCommand;`

### UThunderScan (`UThunderScan.p`)

**Purpose**: Thunder Scan module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `URootFormat`, `UProgress`
**Types & Objects**:
- `TThunderScanFormat` object (extends `TRootFormat`)
  - field: `fDepth: INTEGER;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `PROCEDURE ReadSCANLine (doc: TImageDocument; row: INTEGER);`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION DataForkBytes (doc: TImageDocument): LONGINT; OVERRIDE;`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UTIFFormat (`UTIFFormat.p`)

**Purpose**: TIF Format file format handler
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `URootFormat`, `ULZWCompress`, `UProgress`
**Types & Objects**:
- `TTIFFormat` object (extends `TRootFormat`)
  - field: `fDoc: TImageDocument;`
  - field: `fMotorola: BOOLEAN;`
  - field: `fCompressed: BOOLEAN;`
  - field: `fMetric: BOOLEAN;`
  - field: `fResolution: EXTENDED;`
  - field: `fPredictor: INTEGER;`
  - field: `fBitsPerSample: INTEGER;`
  - field: `fCompressionCode: INTEGER;`
  - field: `fPlanarConfiguration: INTEGER;`
  - field: `fPhotometricInterpretation: INTEGER;`
  - field: `fStripOffsets: LONGINT;`
  - field: `fStripByteCounts: LONGINT;`
  - field: `fLongStripOffsets: BOOLEAN;`
  - field: `fLongStripByteCounts: BOOLEAN;`
  - field: `fRowsPerStrip: INTEGER;`
  - method: `PROCEDURE IImageFormat; OVERRIDE;`
  - method: `FUNCTION CanWrite (doc: TImageDocument): BOOLEAN; OVERRIDE;`
  - method: `PROCEDURE SetFormatOptions (doc: TImageDocument); OVERRIDE;`
  - method: `PROCEDURE ParseTag (tagCode: INTEGER; tagType: INTEGER; tagCount: LONGINT);`
  - method: `PROCEDURE DecompressCCITT (VAR srcPtr: Ptr; dstPtr: Ptr);`
  - method: `PROCEDURE DecompressLZW (srcPtr, dstPtr: Ptr; count: LONGINT);`
  - method: `PROCEDURE ReadPlaneStrip (plane: INTEGER; strip: INTEGER; count: LONGINT);`
  - method: `PROCEDURE ReadRGBStrip (strip: INTEGER; count: LONGINT);`
  - method: `PROCEDURE AdjustPlane (plane: INTEGER);`
  - method: `PROCEDURE AddBitPlane (srcArray: TVMArray; dstArray: TVMArray);`
  - method: `PROCEDURE DoRead (doc: TImageDocument; refNum: INTEGER; rsrcExists: BOOLEAN); OVERRIDE;`
  - method: `FUNCTION DataForkBytes (doc: TImageDocument): LONGINT; OVERRIDE;`
  - method: `FUNCTION CompressStrip (srcPtr: Ptr; dstPtr: Ptr; srcBytes: LONGINT; dstBytes: LONGINT): LONGINT;`
  - method: `PROCEDURE WriteLZW (doc: TImageDocument; stripsPerImage: INTEGER; rowBytes: LONGINT);`
  - method: `PROCEDURE DoWrite (doc: TImageDocument; refNum: INTEGER); OVERRIDE;`

### UTransfer (`UTransfer.p`)

**Purpose**: Transfer module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UScreen`
**Types & Objects**:
- `TTransferArray` array: `ARRAY [0..20] OF INTEGER;`
**Routines**:
- `PROCEDURE SolveTransfer (spec: TTransferSpec; VAR transfer: TTransferArray);`
- `PROCEDURE SetTransferFunction (VAR spec: TTransferSpec; VAR gamma: INTEGER);`
- `PROCEDURE SetTransferFunctions (VAR specs: TTransferSpecs; VAR gamma: INTEGER);`

### UTrap (`UTrap.p`)

**Purpose**: Trap module
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UConstants`, `UVMemory`, `UPhotoshop`, `UDialog`, `UBWDialog`, `UCommands`, `UProgress`
**Types & Objects**:
- `TTrapCommand` object (extends `TBufferCommand`)
  - field: `fWidth: INTEGER;`
  - method: `PROCEDURE ITrapCommand (view: TImageView; width: INTEGER);`
  - method: `PROCEDURE TrapAcross (srcArray1: TVMArray; srcArray2: TVMArray; srcArray3: TVMArray; srcArray4: TVMArray; dstArray1: TVMArray; dstArray2: TVMArray; dstArray3: TVMArray; clear: BOOLEAN);`
  - method: `PROCEDURE CombineTrap (srcArray: TVMArray; dstArray: TVMArray);`
  - method: `PROCEDURE DoIt; OVERRIDE;`
  - method: `PROCEDURE UndoIt; OVERRIDE;`
  - method: `PROCEDURE RedoIt; OVERRIDE;`
**Routines**:
- `PROCEDURE InitTraps;`
- `FUNCTION DoTrapCommand (view: TImageView): TCommand;`

### UVMemory (`UVMemory.p`)

**Purpose**: V Memory infrastructure
**Depends on**: `MemTypes`, `QuickDraw`, `OSIntf`, `ToolIntf`, `PackIntf`, `UObject`, `UList`, `UMacApp`, `PaletteMgr`, `UDialog`, `UConstants`, `UBWDialog`
**Constants**:
- `kVMPageSize = 30720;`
**Variables**:
- `gMovingHands: BOOLEAN;`
- `gPouchRefNum: INTEGER;`
- `gVMPageLimit: INTEGER;`
- `gVMMinPageLimit: INTEGER;`
**Types & Objects**:
- `TVMPageList` array: `ARRAY [0..32767] OF INTEGER;`
- `PVMPageList` pointer: `^TVMPageList;`
- `HVMPageList` pointer: `^PVMPageList;`
- `TVMArray` object (extends `TObject`)
  - field: `fBlockCount: LONGINT;`
  - field: `fLogicalSize: INTEGER;`
  - field: `fPhysicalSize: INTEGER;`
  - field: `fBlocksPerPage: INTEGER;`
  - field: `fPageCount: INTEGER;`
  - field: `fPageList: HVMPageList;`
  - field: `fData: Handle;`
  - field: `fDirty: BOOLEAN;`
  - field: `fLoPage: INTEGER;`
  - field: `fHiPage: INTEGER;`
  - field: `fNeedDepth: INTEGER;`
  - method: `PROCEDURE IVMArray (count: LONGINT; size: INTEGER; interleave: INTEGER);`
  - method: `PROCEDURE Free; OVERRIDE;`
  - method: `FUNCTION NeedPtr (loBlock, hiBlock: LONGINT; dirty: BOOLEAN): Ptr;`
  - method: `PROCEDURE DoneWithPtr;`
  - method: `PROCEDURE Flush;`
  - method: `PROCEDURE Undefine;`
  - method: `PROCEDURE Preload (total: INTEGER);`
  - method: `PROCEDURE SetBytes (x: INTEGER);`
  - method: `PROCEDURE SetRect (r: Rect; x: INTEGER);`
  - method: `PROCEDURE SetOutsideRect (r: Rect; x: INTEGER);`
  - method: `PROCEDURE MapBytes (map: TLookUpTable);`
  - method: `PROCEDURE MapRect (r: Rect; map: TLookUpTable);`
  - method: `PROCEDURE HistBytes (VAR hist: THistogram);`
  - method: `PROCEDURE HistRect (r: Rect; VAR hist: THistogram);`
  - method: `PROCEDURE MoveArray (aVMArray: TVMArray);`
  - method: `FUNCTION CopyArray (interleave: INTEGER): TVMArray;`
  - method: `PROCEDURE MoveRect (aVMArray: TVMArray; r1, r2: Rect);`
  - method: `FUNCTION CopyRect (r: Rect; interleave: INTEGER): TVMArray;`
  - method: `PROCEDURE FindInnerBounds (VAR r: Rect);`
  - method: `PROCEDURE FindBounds (VAR r: Rect);`
**Routines**:
- `PROCEDURE InitWatches;`
- `PROCEDURE MoveHands (canAbort: BOOLEAN);`
- `FUNCTION TestAbort: BOOLEAN;`
- `PROCEDURE InitVM;`
- `PROCEDURE TermVM;`
- `FUNCTION VMCanReserve: LONGINT;`
- `PROCEDURE VMAdjustReserve (change: LONGINT);`
- `FUNCTION NewLargeHandle (size: LONGINT): Handle;`
- `PROCEDURE ResizeLargeHandle (h: Handle; size: LONGINT);`
- `PROCEDURE FreeLargeHandle (h: Handle);`
- `FUNCTION NewVMArray (count: LONGINT; size: INTEGER; interleave: INTEGER): TVMArray;`
- `PROCEDURE VMCompress (complete: BOOLEAN);`

