---
inclusion: always
---

# Figma Design System Integration Rules

## Overview

This document provides comprehensive rules for integrating Figma designs with the AI Workflow Architect codebase using the Figma MCP (Model Context Protocol) power. The system uses React 18 + TypeScript with Tailwind CSS v4 and shadcn/ui components.

## Design System Structure

### 1. Token Definitions

**Location**: `client/src/index.css`
**Format**: CSS Custom Properties with HSL color space

```css
:root {
  /* Core Brand Colors - Dark Future Theme */
  --primary: 180 100% 50%;        /* Electric Cyan */
  --accent: 260 100% 65%;         /* Electric Purple */
  --background: 222 47% 11%;      /* Deep Space Blue */
  --foreground: 210 40% 98%;      /* Near White */
  
  /* Semantic Colors */
  --card: 222 47% 13%;
  --muted: 217 33% 17%;
  --border: 217 33% 20%;
  --destructive: 0 62% 30%;
  
  /* Spacing & Layout */
  --radius: 0.5rem;
  --radius-sm: calc(var(--radius) - 4px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}
```

**Typography Tokens**:
```css
--font-sans: "Space Grotesk", sans-serif;
--font-mono: "JetBrains Mono", monospace;
```

### 2. Component Library

**Location**: `client/src/components/ui/`
**Architecture**: shadcn/ui (New York style) with Radix UI primitives
**Configuration**: `components.json`

```json
{
  "style": "new-york",
  "tailwind": {
    "baseColor": "neutral",
    "cssVariables": true
  },
  "iconLibrary": "lucide"
}
```

**Component Categories**:
- **Layout**: `card.tsx`, `separator.tsx`, `sidebar.tsx`, `resizable.tsx`
- **Forms**: `button.tsx`, `input.tsx`, `select.tsx`, `checkbox.tsx`, `form.tsx`
- **Navigation**: `navigation-menu.tsx`, `breadcrumb.tsx`, `pagination.tsx`
- **Feedback**: `alert.tsx`, `toast.tsx`, `progress.tsx`, `spinner.tsx`
- **Overlays**: `dialog.tsx`, `popover.tsx`, `sheet.tsx`, `tooltip.tsx`

### 3. Frameworks & Libraries

**Frontend Stack**:
- **React 18** with TypeScript 5.6+
- **Vite** for build tooling and HMR
- **Tailwind CSS v4** with CSS variables
- **Framer Motion** for animations
- **Wouter** for client-side routing
- **TanStack Query** for server state

**Styling Libraries**:
- **tailwindcss-animate** for animations
- **tw-animate-css** for additional animations
- **class-variance-authority** for component variants
- **tailwind-merge** for conditional classes

### 4. Asset Management

**Static Assets**: `client/public/`
- Favicon and PWA icons
- Static images and graphics
- Manifest files

**Generated Assets**: `attached_assets/`
- AI-generated images
- Temporary files
- Dynamic content

**Asset Optimization**:
- Vite handles bundling and optimization
- Images processed through `vite-plugin-meta-images`
- CDN-ready for production deployment

### 5. Icon System

**Library**: Lucide React
**Usage Pattern**:
```typescript
import { ChevronRight, Settings, User } from "lucide-react"

// Standard size: 16px (h-4 w-4)
<ChevronRight className="h-4 w-4" />

// Large size: 20px (h-5 w-5)
<Settings className="h-5 w-5" />
```

**Icon Conventions**:
- Use semantic names from Lucide library
- Consistent sizing: `h-4 w-4` (default), `h-5 w-5` (large), `h-6 w-6` (xl)
- Color inheritance from parent text color

### 6. Styling Approach

**Primary Method**: Tailwind CSS v4 with CSS variables
**Component Styling**: Class Variance Authority (CVA) for variants

```typescript
import { cva, type VariantProps } from "class-variance-authority"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
      },
    },
  }
)
```

**Global Styles**: `client/src/index.css`
- Base layer resets
- Custom utility classes
- Glassmorphism effects

**Utility Classes**:
```css
.glass-panel {
  @apply bg-card/60 backdrop-blur-md border border-white/10 shadow-xl;
}

.glass-card {
  @apply bg-card/40 backdrop-blur-sm border border-white/5 hover:bg-card/60 transition-colors;
}

.text-glow {
  text-shadow: 0 0 20px hsl(var(--primary) / 0.5);
}

.neon-border {
  box-shadow: 0 0 10px -2px hsl(var(--primary) / 0.3);
}
```

### 7. Project Structure

**Monorepo Organization**:
```
AI-Workflow-Architect/
├── client/src/
│   ├── components/
│   │   ├── ui/           # shadcn/ui components
│   │   ├── assistant/    # AI assistant interface
│   │   ├── dashboard/    # Dashboard components
│   │   ├── diff/         # Code diff viewer
│   │   └── editor/       # Monaco code editor
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utility functions
│   └── pages/            # Route components
├── server/               # Express.js backend
├── shared/               # Shared TypeScript types
└── docs/                 # Documentation
```

**Path Aliases** (tsconfig.json):
```json
{
  "paths": {
    "@/*": ["./client/src/*"],
    "@shared/*": ["./shared/*"],
    "@assets/*": ["./attached_assets/*"]
  }
}
```

## Figma Integration Workflow

### 1. Design Token Mapping

When converting Figma designs, map design tokens as follows:

**Colors**:
- Figma Primary → `hsl(var(--primary))`
- Figma Secondary → `hsl(var(--accent))`
- Figma Background → `hsl(var(--background))`
- Figma Text → `hsl(var(--foreground))`

**Spacing**:
- Figma 4px → `space-1` (0.25rem)
- Figma 8px → `space-2` (0.5rem)
- Figma 16px → `space-4` (1rem)
- Figma 24px → `space-6` (1.5rem)

**Typography**:
- Figma Heading → `text-2xl font-bold` or `text-xl font-semibold`
- Figma Body → `text-base` or `text-sm`
- Figma Caption → `text-xs text-muted-foreground`

### 2. Component Conversion Rules

**Replace Figma Output with Existing Components**:
```typescript
// Instead of Figma's generic button
<button className="bg-blue-500 text-white px-4 py-2 rounded">

// Use project's Button component
import { Button } from "@/components/ui/button"
<Button variant="default" size="default">
```

**Reuse Existing Patterns**:
- Cards → `<Card>`, `<CardHeader>`, `<CardContent>`
- Forms → `<Form>`, `<FormField>`, `<FormItem>`
- Dialogs → `<Dialog>`, `<DialogContent>`, `<DialogHeader>`

### 3. Responsive Design Patterns

**Breakpoint System** (Tailwind defaults):
- `sm:` 640px and up
- `md:` 768px and up  
- `lg:` 1024px and up
- `xl:` 1280px and up

**Mobile-First Approach**:
```typescript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

### 4. Animation Guidelines

**Framer Motion Integration**:
```typescript
import { motion } from "framer-motion"

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
```

**Tailwind Animations**:
- `animate-pulse` for loading states
- `animate-spin` for spinners
- `transition-colors` for hover effects

## AWS Integration Considerations

### 1. Asset Delivery

**CloudFront CDN**:
- Static assets served from S3 + CloudFront
- Optimized image delivery
- Global edge locations

**S3 Bucket Structure**:
```
assets/
├── images/
├── icons/
├── fonts/
└── generated/
```

### 2. Environment Configuration

**AWS-Specific Variables**:
```bash
# .env.example
AWS_REGION=us-east-1
AWS_S3_BUCKET=ai-workflow-assets
AWS_CLOUDFRONT_DOMAIN=assets.aiworkflow.com
```

### 3. Build Optimization

**Vite Configuration for AWS**:
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-button']
        }
      }
    }
  }
})
```

## Code Connect Integration

### 1. Component Mapping

Map Figma components to code components:
```typescript
// Button component mapping
// Figma: "Primary Button" → Code: Button (variant="default")
// Figma: "Secondary Button" → Code: Button (variant="outline")
```

### 2. Prop Mapping

**Figma Properties → React Props**:
- Figma "variant" → React `variant` prop
- Figma "size" → React `size` prop
- Figma "disabled" → React `disabled` prop

### 3. Documentation Standards

**Component Documentation**:
```typescript
/**
 * Primary button component with multiple variants
 * @param variant - Button style variant
 * @param size - Button size
 * @param disabled - Whether button is disabled
 */
export interface ButtonProps {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link"
  size?: "default" | "sm" | "lg" | "icon"
  disabled?: boolean
}
```

## Quality Assurance

### 1. Visual Parity Checklist

- [ ] Colors match Figma design tokens
- [ ] Typography scales correctly
- [ ] Spacing matches design specifications
- [ ] Interactive states (hover, focus, active) work
- [ ] Responsive behavior matches design
- [ ] Animations feel natural and performant

### 2. Code Quality Standards

- [ ] Uses existing components where possible
- [ ] Follows TypeScript strict mode
- [ ] Includes proper accessibility attributes
- [ ] Optimized for performance
- [ ] Follows project naming conventions
- [ ] Includes proper error handling

### 3. Testing Requirements

- [ ] Component renders without errors
- [ ] Interactive elements work correctly
- [ ] Responsive design functions properly
- [ ] Accessibility standards met (WCAG 2.1)
- [ ] Performance metrics acceptable

## Best Practices

### 1. Design System Consistency

- Always use design tokens instead of hardcoded values
- Reuse existing components before creating new ones
- Maintain consistent spacing and typography scales
- Follow established color and interaction patterns

### 2. Performance Optimization

- Lazy load components when appropriate
- Optimize images and assets
- Use React.memo for expensive components
- Implement proper code splitting

### 3. Accessibility

- Include proper ARIA labels and roles
- Ensure keyboard navigation works
- Maintain sufficient color contrast
- Provide alternative text for images

### 4. Maintainability

- Document component APIs thoroughly
- Use TypeScript for type safety
- Follow consistent file naming conventions
- Keep components focused and single-purpose

This design system ensures seamless integration between Figma designs and the AI Workflow Architect codebase while maintaining consistency, performance, and accessibility standards.