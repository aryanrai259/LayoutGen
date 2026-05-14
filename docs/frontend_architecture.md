# Frontend Documentation - AI Floor Plan Designer

**Complete unified documentation for the frontend application**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Architecture & Design](#architecture--design)
5. [Component Details](#component-details)
6. [State Management](#state-management)
7. [API Integration](#api-integration)
8. [SSE Streaming Implementation](#sse-streaming-implementation)
9. [UI Layouts & States](#ui-layouts--states)
10. [Theme System](#theme-system)
11. [Styling Guidelines](#styling-guidelines)
12. [Development Workflow](#development-workflow)
13. [Testing & Debugging](#testing--debugging)

---

## 🎯 Project Overview

**AI Floor Plan Designer** is a React-based frontend application that generates compliant residential floor plans using AI. The application features a dark, professional CAD-style UI with real-time streaming updates and intelligent commentary extraction.

### Key Features

- **Dual Generation Modes**: Streaming (SSE) and Direct (REST) endpoints
- **Real-time Updates**: Live commentary with intelligent token filtering
- **Ghost Canvas Animation**: Realistic floor plan drafting visualization
- **Dark Theme**: Professional CAD-style dark mode interface
- **Responsive Design**: Mobile-first, works on all screen sizes
- **Intelligent SSE Parsing**: Filters raw tokens into meaningful messages

---

## 🛠 Tech Stack

### Core Technologies

- **React 18.2.0** - UI library
- **Vite 5.0.8** - Build tool and dev server
- **JavaScript (ES6+)** - Programming language (no TypeScript)
- **CSS3** - Styling (no Tailwind, no UI libraries)
- **react-router-dom** - Client-side routing

### Development Tools

- **@vitejs/plugin-react** - Vite React plugin
- **ES Modules** - Modern JavaScript module system

### No External Dependencies

- ❌ No state management library (Redux, Zustand, etc.)
- ❌ No UI component libraries (Material-UI, Ant Design, etc.)
- ❌ No CSS frameworks (Tailwind, Bootstrap, etc.)
- ✅ Pure React with hooks
- ✅ Vanilla CSS with CSS variables

---

## 📁 Project Structure

```
floorplan_frontend/
├── public/
│   └── index.html              # HTML entry point with Google Fonts
│
├── src/
│   ├── api/
│   │   ├── backend.js          # Legacy API (deprecated)
│   │   └── floorPlanApi.js     # Main API client (streaming + direct)
│   │
│   ├── components/
│   │   ├── Navbar.jsx          # Navigation bar with glassmorphism
│   │   ├── Navbar.css
│   │   ├── InputForm.jsx       # User input form (2-column idle layout)
│   │   ├── InputForm.css
│   │   ├── LiveCommentary.jsx  # Live updates panel (filtered commentary)
│   │   ├── LiveCommentary.css
│   │   ├── SvgPreview.jsx      # SVG viewer with ghost canvas
│   │   ├── SvgPreview.css
│   │   ├── SummaryPanel.jsx   # Generation summary (plot details, metadata)
│   │   ├── SummaryPanel.css
│   │   ├── GhostCanvas.jsx     # Animated floor plan drafting canvas
│   │   ├── GhostCanvas.css
│   │   ├── ResultView.jsx      # Legacy component (unused)
│   │   ├── Loader.jsx          # Loading indicator (unused)
│   │   └── ErrorBox.jsx        # Error display (unused)
│   │
│   ├── hooks/
│   │   └── useSSEFloorPlan.js  # SSE hook with token filtering & state
│   │
│   ├── pages/
│   │   ├── Home.jsx            # Landing page (Hero, Features, How It Works)
│   │   ├── Home.css
│   │   ├── Generate.jsx        # Generate page wrapper
│   │   ├── Generate.css
│   │   ├── FloorPlanGenerator.jsx  # Main generation page (all UI states)
│   │   └── FloorPlanGenerator.css
│   │
│   ├── styles/
│   │   ├── theme.css           # CSS variables (dark theme)
│   │   └── globals.css         # Global styles and resets
│   │
│   ├── utils/
│   │   └── sseTextProcessor.js # Intelligent SSE token filtering
│   │
│   ├── App.jsx                 # Root component with routing
│   └── main.jsx                # Application entry point
│
├── .env                        # Environment variables (legacy)
├── .env.local                  # Local environment (VITE_API_BASE_URL)
├── .gitignore
├── package.json
├── vite.config.js              # Vite config with proxy
└── README.md                    # Project readme
```

---

## 🏗 Architecture & Design

### Component Hierarchy

```
App
├── Navbar
│   ├── Brand Name
│   └── Nav Links (Features, How It Works, Create Plan)
└── Router
    ├── Home (Landing Page)
    │   ├── Hero Section
    │   ├── Features Section
    │   └── How It Works Section
    └── Generate (Floor Plan Generation)
        └── FloorPlanGenerator
            ├── Top Bar (Title, Actions)
            ├── Input Form (Idle State)
            ├── Live Commentary Panel
            ├── Ghost Canvas / SVG Preview
            ├── Summary Panel
            └── Error Banner
```

### Data Flow

```
User Input → InputForm
    ↓
FloorPlanGenerator (handles generation mode)
    ↓
useSSEFloorPlan Hook
    ↓
floorPlanApi.js (API client)
    ↓
Vite Proxy (/floor_plan → localhost:8000)
    ↓
Backend API
    ↓
SSE Stream / JSON Response
    ↓
Token Processing (sseTextProcessor.js)
    ↓
UI State Updates
    ↓
Component Re-renders
```

---

## 🧩 Component Details

### 1. **App.jsx** (Root Component)

- **Purpose**: Main application wrapper with routing
- **Routing**: Uses `react-router-dom` for navigation
- **Routes**:
  - `/` → Home page
  - `/generate` → FloorPlanGenerator page

### 2. **Navbar.jsx**

- **Purpose**: Top navigation bar
- **Features**:
  - Dark glassmorphism background
  - Accent glow line at bottom
  - Brand name with color highlight
  - Smooth scroll navigation links
- **Links**:
  - Features → `#features`
  - How It Works → `#how-it-works`
  - Create Plan → `/generate`

### 3. **Home.jsx** (Landing Page)

- **Purpose**: Marketing/landing page
- **Sections**:
  1. Hero Section (full viewport height)
  2. Features Section (3-card grid)
  3. How It Works Section (3-step process)
- **CTA**: Button to navigate to `/generate`

### 4. **FloorPlanGenerator.jsx** (Main Generation Page)

- **Purpose**: Core floor plan generation interface
- **UI States**:
  - `idle`: Input form layout
  - `streaming_active`: 2-grid (Live Updates + Ghost Canvas)
  - `streaming_final`: 3-grid (Live Updates + Summary + SVG)
  - `normal_final`: 2-grid (Summary + SVG)
- **State Management**: Uses `useSSEFloorPlan` hook
- **Features**:
  - Handles both streaming and direct generation
  - Manages UI mode transitions
  - Error handling and display

### 5. **InputForm.jsx** (User Input Form)

- **Purpose**: Collect user input for floor plan generation
- **Layout** (Idle State):
  - **Left/Center**: Large description textarea (Claude-style, min-height: 300px)
  - **Right Sidebar (400px)**: Other form fields stacked vertically
    - Dimensions (Width, Height)
    - Requirements (Rooms, Orientation)
    - Room Types (checkboxes)
    - Jurisdiction
  - **Below**: Two generate buttons spanning full width
- **Form Fields**:
  - Description (textarea, min 10 chars)
  - Width (number, ft)
  - Height (number, ft)
  - Rooms (number, 1-20)
  - Orientation (select: north, south, east, west)
  - Room Types (checkboxes)
  - Jurisdiction (text input)
- **Validation**: Client-side validation with error messages
- **Buttons**:
  - "Generate with Streaming" (primary)
  - "Quick Generate" (secondary)

### 6. **LiveCommentary.jsx**

- **Purpose**: Display filtered, meaningful commentary from SSE stream
- **Features**:
  - Fixed height with internal scrolling
  - Auto-scrolls to latest message
  - Shows title + detail for each update
  - Custom scrollbar styling
  - Pulse indicator when generating
- **Data Structure**:
  ```javascript
  {
    id: number,
    title: string,
    detail?: string,
    timestamp: number
  }
  ```

### 7. **GhostCanvas.jsx**

- **Purpose**: Animated floor plan drafting visualization
- **Modes**:
  - **Explore Mode**: Wandering architect cursor (stages 0-2)
  - **Draft Mode**: Realistic floor plan drawing (stages 3-4)
- **Draft Mode Features**:
  - Sequential path drawing (plot boundary → rooms → walls → doors)
  - Animated marker cursor following path
  - Room labels appear when outlines complete
  - Different line weights for different elements
  - Slow motion drawing speed (0.01 progress per frame)
  - 600ms pause between paths
- **Drawing Sequence**:
  1. Plot boundary (outer outline)
  2. Room outlines (Living, Kitchen, Bedrooms, Bathroom, Corridor)
  3. Internal walls (partition lines)
  4. Door openings (gaps in walls)

### 8. **SvgPreview.jsx**

- **Purpose**: Display generated SVG floor plan
- **Features**:
  - Shows GhostCanvas during generation
  - Transitions to SVG when final arrives
  - Download SVG button
  - Zoom fit and center alignment
  - Smooth fade transitions

### 9. **SummaryPanel.jsx**

- **Purpose**: Display generation summary and metadata
- **Sections**:
  - Plot Details (width, height, built-up area)
  - Layout (bedrooms, orientation, confidence)
  - References (bylaws used, blueprints referenced)

---

## 🔄 State Management

### State Machine

```
idle → streaming_active → streaming_final → done
  ↓           ↓
error      cancelled

normal_final (direct generation)
```

### State Structure (useSSEFloorPlan Hook)

```javascript
{
  status: 'idle' | 'streaming' | 'refining' | 'done' | 'error' | 'cancelled',
  commentary: Array<{
    id: number,
    title: string,
    detail?: string,
    timestamp: number
  }>,
  svgDraft: string | null,
  svgFinal: string | null,
  metadata: {
    confidence: number,
    bylaws_used: Array,
    blueprints_referenced: Array,
    summary?: string
  } | null,
  error: string | null,
  currentLabel: string | null,  // For GhostCanvas
  canvasMode: 'explore' | 'draft'  // GhostCanvas mode
}
```

### UI Mode States (FloorPlanGenerator)

- **idle**: Input form visible (2-column: description + sidebar)
- **streaming_active**: 2-grid layout (40% Live Updates, 60% Ghost Canvas)
- **streaming_final**: 3-grid layout (20% Live Updates, 20% Summary, 60% SVG)
- **normal_final**: 2-grid layout (30% Summary, 70% SVG)

---

## 🔌 API Integration

### Backend Configuration

**Vite Proxy** (`vite.config.js`):
```javascript
server: {
  proxy: {
    "/floor_plan": {
      target: "http://localhost:8000",
      changeOrigin: true,
      secure: false
    }
  }
}
```

**API Client** (`src/api/floorPlanApi.js`):
- Uses relative paths (`/floor_plan/...`) to leverage Vite proxy
- No hardcoded URLs
- Supports both streaming and direct endpoints

### Endpoints

#### 1. Streaming Endpoint

**POST** `/floor_plan/generate/stream`

- **Headers**:
  - `Content-Type: application/json`
  - `Accept: text/event-stream`
- **Request Body**:
  ```javascript
  {
    description: string (min 10 chars),
    width: number,
    height: number,
    rooms: number (1-20),
    orientation: "north" | "south" | "east" | "west",
    room_types: string[],
    jurisdiction: string
  }
  ```
- **Response**: `text/event-stream` with SSE events
- **Events**:
  - `progress`: `{stage, stage_name, text}`
  - `svg`: `{stage, svg, is_final, label}`
  - `final_response`: `{text, metadata}`

#### 2. Direct Endpoint

**POST** `/floor_plan/generate`

- **Headers**: `Content-Type: application/json`
- **Request Body**: Same as streaming endpoint
- **Response**: JSON
  ```javascript
  {
    svg: string,
    confidence: number,
    bylaws_used: Array,
    blueprints_referenced: Array,
    summary: string
  }
  ```

### API Client Functions

**`generateStream(payload, handlers, abortSignal)`**
- Handles SSE streaming
- Manual parsing with `response.body.getReader()`
- Supports `AbortController` for cancellation
- Dispatches events to handlers: `onProgress`, `onSvg`, `onFinal`, `onError`

**`generateDirect(payload)`**
- Handles direct JSON response
- Returns parsed JSON
- Throws errors with status codes

---

## 📡 SSE Streaming Implementation

### How SSE Parsing Works

1. **Connection**: Uses `fetch()` with `response.body.getReader()` (not EventSource, because POST with JSON body)

2. **Stream Reading**:
   - Reads chunks from the stream
   - Decodes using `TextDecoder`
   - Maintains a buffer for incomplete lines
   - Splits by `\n` to process complete lines

3. **Event Detection**:
   - Tracks `currentEvent` when line starts with `event:`
   - Parses JSON when line starts with `data:`
   - Dispatches to appropriate handlers based on event type

### SSE Message Format

```
event: progress
data: {"stage": 0, "stage_name": "Initialization", "text": "Starting..."}

event: svg
data: {"svg": "<svg>...</svg>", "is_final": false}

event: final_response
data: {"text": "Generation complete", "metadata": {...}}
```

### Intelligent Token Filtering

**File**: `src/utils/sseTextProcessor.js`

The SSE text processor intelligently extracts meaningful messages from fragmented tokens:

#### Filtering Rules

1. **Garbage Token Detection**:
   - Ignores markdown symbols only (`#`, `|`, `` ` ``, `-`, `*`, `_`)
   - Ignores ASCII arrows/separators (`→`, `↓`, `↑`, `─`)
   - Ignores table rows (`|...|`)
   - Ignores code fences (`` ``` ``)
   - Ignores whitespace-only tokens
   - Ignores numbers-only tokens
   - Ignores punctuation-only tokens

2. **Semantic Extraction**:
   - Matches patterns to extract meaningful messages
   - Returns structured objects: `{title, detail}`
   - Examples:
     - "Total Dimensions: 30ft × 40ft" → `{title: "Plot dimensions detected", detail: "30ft × 40ft rectangular plot"}`
     - "Retrieved 5 blueprints" → `{title: "Loaded 5 blueprint references", detail: "Architectural database queried successfully"}`
     - "Kitchen L-shaped" → `{title: "Kitchen layout finalized", detail: "Kitchen configured as L-shaped"}`

3. **Throttling**:
   - Processes tokens every 120ms
   - UI updates throttled to 500ms
   - Prevents UI spam from token-by-token updates

4. **Deduplication**:
   - Tracks seen messages to prevent duplicates
   - Keeps last 15 commentary items
   - Auto-scrolls to latest message

### Stage Mapping

- **Stage 0**: Initializing → Explore mode
- **Stage 1**: Spatial Planning → Explore mode
- **Stage 2**: Coordinates → Explore mode
- **Stage 3**: SVG Layout → **Draft mode** (realistic floor plan drawing)
- **Stage 4**: Refining → Draft mode (continues drawing)

---

## 🎨 UI Layouts & States

### Idle State (Initial)

**Layout**: 2-column grid
- **Left/Center (main)**: Large description textarea (Claude-style, min-height: 300px)
- **Right Sidebar (400px)**: Other form fields stacked vertically
  - Dimensions (Width, Height)
  - Requirements (Rooms, Orientation)
  - Room Types (checkboxes)
  - Jurisdiction
- **Below**: Two generate buttons spanning full width

### Streaming Active State

**Layout**: 2-grid (40% + 60%)
- **Left (40%)**: Live Commentary Panel
  - Fixed height with scrolling
  - Auto-scrolls to latest
  - Shows filtered commentary with titles + details
- **Right (60%)**: Ghost Canvas
  - Explore mode (stages 0-2): Wandering cursor
  - Draft mode (stages 3-4): Realistic floor plan drawing

### Streaming Final State

**Layout**: 3-grid (20% + 20% + 60%)
- **Left (20%)**: Live Commentary Panel (scrollable)
- **Center (20%)**: Summary Panel (plot details, metadata)
- **Right (60%)**: SVG Preview (final floor plan)

### Normal Final State (Direct Generation)

**Layout**: 2-grid (30% + 70%)
- **Left (30%)**: Summary Panel
- **Right (70%)**: SVG Preview
- **No Status Panel**: Removed as per requirements

---

## 🎨 Theme System

### Dark Theme (CAD Style)

**File**: `src/styles/theme.css`

#### Color Palette

```css
/* Professional CAD Dark Mode Colors */
--color-primary: #22D3EE;        /* Cyan - Primary actions */
--color-secondary: #0F172A;      /* Dark slate */
--color-accent: #22D3EE;         /* Cyan - Accents */
--color-success: #34D399;        /* Emerald - Success states */
--color-error: #F43F5E;          /* Rose - Error states */

/* Backgrounds */
--bg-app: #0B1220;               /* Main background */
--bg-surface: rgba(18, 25, 45, 0.85);  /* Panel backgrounds */
--bg-card: rgba(18, 25, 45, 0.85);     /* Card backgrounds */

/* Text */
--text-primary: #E5E7EB;         /* Primary text */
--text-secondary: rgba(229, 231, 235, 0.7);  /* Secondary text */

/* Borders */
--border-light: rgba(34, 211, 238, 0.15);   /* Subtle borders */
--border-glow: rgba(34, 211, 238, 0.3);    /* Glow borders */
```

#### Spacing Scale

```css
--space-xs: 4px
--space-sm: 8px
--space-md: 16px
--space-lg: 24px
--space-xl: 40px
```

#### Border Radius

```css
--radius-sm: 8px
--radius-md: 12px
--radius-lg: 18px
```

#### Shadows

```css
--shadow-sm: 0 6px 24px rgba(0, 0, 0, 0.35)
--shadow-md: 0 14px 48px rgba(0, 0, 0, 0.4)
--shadow-glow: 0 0 20px rgba(34, 211, 238, 0.3)
```

#### Typography

```css
--font-main: 'Inter', system-ui, sans-serif
```

### Design Features

- **Glassmorphism**: Cards with `backdrop-filter: blur(10px)`
- **Glow Effects**: Cyan glow on active elements
- **Grid Background**: Subtle dot grid pattern
- **Smooth Transitions**: 0.3s-0.4s ease transitions
- **Custom Scrollbars**: Thin cyan scrollbars

---

## 💅 Styling Guidelines

### CSS Architecture

1. **CSS Variables**: All design tokens in `theme.css`
2. **Component Styles**: Separate CSS files per component
3. **Global Styles**: Reset and base styles in `globals.css`
4. **No Inline Styles**: Except dynamic values (opacity, transforms)

### Naming Conventions

- **CSS Classes**: kebab-case (`.form-input`, `.generator-top-bar-dark`)
- **CSS Variables**: kebab-case (`--color-primary`, `--space-md`)
- **Component Files**: PascalCase (`InputForm.jsx`, `GhostCanvas.jsx`)

### Responsive Design

- **Mobile-first**: Base styles for mobile, media queries for larger screens
- **Breakpoints**:
  - Mobile: `< 768px`
  - Tablet: `768px - 1200px`
  - Desktop: `> 1200px`
- **Grid Layouts**: Switch to single column on mobile

---

## 🚀 Development Workflow

### Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Environment Variables**:
   - Create `.env.local` (optional, uses Vite proxy by default)
   - `VITE_API_BASE_URL` (optional, proxy handles routing)

3. **Start Development Server**:
   ```bash
   npm run dev
   ```
   - Runs on `http://localhost:5173`
   - Vite proxy forwards `/floor_plan` to `http://localhost:8000`

4. **Backend Setup**:
   - Ensure backend is running on `http://localhost:8000`
   - Backend should handle `/floor_plan/generate` and `/floor_plan/generate/stream`

### Build & Deploy

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Code Style

1. **Component Structure**:
   ```javascript
   import React, { useState, useEffect } from 'react'
   import './Component.css'
   
   function Component() {
     // Hooks
     // Event handlers
     // Render
   }
   
   export default Component
   ```

2. **State Management**:
   - Use `useState` for local state
   - Use `useSSEFloorPlan` hook for generation state
   - Lift state only when needed

3. **CSS Guidelines**:
   - Always use CSS variables from `theme.css`
   - Component-specific CSS files
   - Mobile-first responsive design

---

## 🧪 Testing & Debugging

### Testing Checklist

- [x] SSE stream connects and parses events correctly
- [x] Token filtering reduces spam (not showing every token)
- [x] Ghost visualization appears during generation
- [x] Draft mode activates only at stage 3 (SVG generation)
- [x] SVG preview updates when draft/final arrives
- [x] Markdown renders cleanly (no raw backticks)
- [x] Cancel button stops generation
- [x] Direct generation works (non-streaming)
- [x] UI layouts switch correctly between states
- [x] Responsive layout works on mobile
- [x] Error handling displays user-friendly messages

### Debugging Tips

1. **Console Logs**:
   - API requests logged in `floorPlanApi.js`
   - Draft mode activation logged in `useSSEFloorPlan.js`

2. **Network Tab**:
   - Check `/floor_plan/generate/stream` requests
   - Verify SSE events are received
   - Check response status codes

3. **React DevTools**:
   - Inspect component state
   - Check hook state in `useSSEFloorPlan`
   - Monitor re-renders

---

## 📝 Key Implementation Details

### GhostCanvas Draft Mode

- **Activation**: Only when `stage === 3` or `stage === 4`
- **Drawing Speed**: `0.01` progress per frame (slow motion)
- **Pause Between Paths**: 600ms
- **Drawing Sequence**:
  1. Plot boundary
  2. Room outlines (Living, Kitchen, Bedrooms, Bathroom, Corridor)
  3. Internal walls
  4. Door openings

### SSE Text Processing

- **Processor**: `SSETextProcessor` class in `utils/sseTextProcessor.js`
- **Buffering**: 120ms processing interval
- **UI Updates**: 500ms throttling
- **Max Commentary**: 15 items
- **Deduplication**: Tracks seen titles

### UI State Transitions

- **Smooth Animations**: 0.4s fade transitions
- **Layout Changes**: CSS Grid with `transition: all 0.4s ease`
- **Auto-scroll**: Commentary panel scrolls to bottom on new messages

---

## 🔧 Configuration

### Vite Configuration

```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/floor_plan": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false
      }
    }
  }
})
```

### Environment Variables

- **`.env.local`**: Optional, can set `VITE_API_BASE_URL`
- **Default**: Uses Vite proxy (relative paths)

---

## 📚 File Reference

### Core Files

- `src/pages/FloorPlanGenerator.jsx` - Main generation page
- `src/hooks/useSSEFloorPlan.js` - SSE hook with state management
- `src/api/floorPlanApi.js` - API client
- `src/utils/sseTextProcessor.js` - Token filtering logic
- `src/components/GhostCanvas.jsx` - Drafting animation
- `src/components/LiveCommentary.jsx` - Commentary panel
- `src/styles/theme.css` - Design system variables

### Styling Files

- `src/styles/globals.css` - Global styles
- `src/pages/FloorPlanGenerator.css` - Main page styles
- `src/components/*.css` - Component-specific styles

---

## 🎯 Future Enhancements

### Potential Improvements

1. **Markdown Rendering**: Use proper markdown library (e.g., `react-markdown`)
2. **Progress Percentage**: Calculate and display estimated progress
3. **Error Recovery**: Add retry logic for failed generations
4. **Plan History**: Save and load previous floor plans
5. **Export Options**: PDF, PNG export
6. **Zoom/Pan Controls**: Interactive SVG viewer
7. **Room Labels**: Interactive room labels on SVG

---

**Last Updated**: Current as of latest implementation
**Version**: 1.0.0
