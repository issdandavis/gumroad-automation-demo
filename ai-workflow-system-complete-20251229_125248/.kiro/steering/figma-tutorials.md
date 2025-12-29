---
inclusion: manual
---

# Figma Power Integration Tutorials & Guides

## Quick Start Guide

### Step 1: Authentication
The Figma power is already authenticated for your account (issdandavis7795@gmail.com) with Pro team access.

### Step 2: Basic Workflow
1. **Get Figma URL**: Copy the Figma design URL from your browser
2. **Extract Design**: Use `get_design_context` to convert Figma to React code
3. **Integrate Code**: Replace Tailwind utilities with project design tokens
4. **Connect Components**: Map Figma components to your codebase using Code Connect

## Tutorial 1: Converting a Figma Design to React Component

### Example: Converting a Button Component

**Step 1: Get the Figma URL**
```
https://figma.com/design/ABC123/MyProject?node-id=1-2
```

**Step 2: Extract Design Context**
```typescript
// Kiro will call: get_design_context
// Parameters:
// - fileKey: "ABC123" 
// - nodeId: "1:2"
// - clientLanguages: "typescript,javascript"
// - clientFrameworks: "react,tailwind"
```

**Step 3: Convert Output to Project Standards**

**Figma Output (Raw)**:
```typescript
export function Button({ children, variant = "primary" }) {
  return (
    <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600">
      {children}
    </button>
  )
}
```

**Project-Compliant Output**:
```typescript
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "underline-offset-4 hover:underline text-primary",
      },
      size: {
        default: "h-10 py-2 px-4",
        sm: "h-9 px-3 rounded-md",
        lg: "h-11 px-8 rounded-md",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"
```

## Tutorial 2: Setting Up Code Connect

### Step 1: Map Component to Figma
```typescript
// After creating your component, map it to Figma
// Kiro will call: add_code_connect_map
// Parameters:
// - fileKey: "ABC123"
// - nodeId: "1:2" 
// - source: "client/src/components/ui/button.tsx"
// - componentName: "Button"
// - label: "React"
```

### Step 2: Verify Mapping
```typescript
// Check existing mappings
// Kiro will call: get_code_connect_map
// Returns: {'1:2': { codeConnectSrc: 'client/src/components/ui/button.tsx', codeConnectName: 'Button' }}
```

## Tutorial 3: Working with Complex Layouts

### Example: Dashboard Card Component

**Figma Design Features**:
- Card container with glassmorphism effect
- Header with title and action button
- Content area with metrics
- Footer with timestamp

**Step 1: Extract Layout Structure**
```typescript
// Use get_metadata first to understand structure
// Then get_design_context for detailed implementation
```

**Step 2: Apply Project Design System**
```typescript
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export function DashboardCard({ title, metrics, timestamp, onAction }) {
  return (
    <Card className="glass-card">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Button variant="ghost" size="sm" onClick={onAction}>
          View Details
        </Button>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-glow">{metrics.value}</div>
        <p className="text-xs text-muted-foreground">
          {metrics.change > 0 ? "+" : ""}{metrics.change}% from last month
        </p>
        <Badge variant="secondary" className="mt-2">
          Updated {timestamp}
        </Badge>
      </CardContent>
    </Card>
  )
}
```

## Tutorial 4: Responsive Design Implementation

### Mobile-First Approach
```typescript
// Figma desktop design → Responsive React component
export function ResponsiveGrid({ items }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4">
      {items.map((item, index) => (
        <motion.div
          key={item.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
          className="glass-card p-6"
        >
          {/* Item content */}
        </motion.div>
      ))}
    </div>
  )
}
```

### Breakpoint-Specific Adjustments
```typescript
// Adjust spacing and layout for different screen sizes
<div className="
  px-4 py-2          // Mobile: tight spacing
  sm:px-6 sm:py-4    // Small: moderate spacing  
  lg:px-8 lg:py-6    // Large: generous spacing
  xl:px-12 xl:py-8   // XL: maximum spacing
">
```

## Tutorial 5: Animation Integration

### Framer Motion with Figma Designs
```typescript
import { motion, AnimatePresence } from "framer-motion"

// Convert Figma prototype animations to Framer Motion
const cardVariants = {
  hidden: { 
    opacity: 0, 
    scale: 0.8,
    y: 20 
  },
  visible: { 
    opacity: 1, 
    scale: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: "easeOut"
    }
  },
  hover: {
    scale: 1.02,
    boxShadow: "0 10px 30px -10px hsl(var(--primary) / 0.3)",
    transition: {
      duration: 0.2
    }
  }
}

export function AnimatedCard({ children, ...props }) {
  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      className="glass-card"
      {...props}
    >
      {children}
    </motion.div>
  )
}
```

## Tutorial 6: AWS Integration Setup

### Environment Configuration
```bash
# .env.example - Add these AWS-specific variables
AWS_REGION=us-east-1
AWS_S3_BUCKET=ai-workflow-assets
AWS_CLOUDFRONT_DOMAIN=assets.aiworkflow.com
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Figma-specific
FIGMA_ACCESS_TOKEN=your_figma_token
FIGMA_TEAM_ID=your_team_id
```

### Asset Pipeline Configuration
```typescript
// vite.config.ts - AWS asset optimization
export default defineConfig({
  plugins: [
    // ... existing plugins
    {
      name: 'aws-asset-upload',
      generateBundle(options, bundle) {
        // Upload assets to S3 during build
        // Integrate with CloudFront for CDN delivery
      }
    }
  ],
  build: {
    rollupOptions: {
      output: {
        assetFileNames: (assetInfo) => {
          // Organize assets for AWS deployment
          const extType = assetInfo.name.split('.').at(1);
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            return `images/[name]-[hash][extname]`;
          }
          if (/woff2?|ttf|otf/i.test(extType)) {
            return `fonts/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        }
      }
    }
  }
})
```

### CloudFront Integration
```typescript
// lib/aws-assets.ts
export function getAssetUrl(path: string): string {
  const isDev = process.env.NODE_ENV === 'development'
  const baseUrl = isDev 
    ? 'http://localhost:5000' 
    : process.env.AWS_CLOUDFRONT_DOMAIN

  return `${baseUrl}/${path}`
}

// Usage in components
import { getAssetUrl } from "@/lib/aws-assets"

export function OptimizedImage({ src, alt, ...props }) {
  return (
    <img 
      src={getAssetUrl(src)} 
      alt={alt}
      loading="lazy"
      {...props}
    />
  )
}
```

## Tutorial 7: Advanced Figma Features

### Working with Variables
```typescript
// Extract Figma variables for consistent theming
// Kiro will call: get_variable_defs
// Returns: {'color/primary': '#00FFFF', 'spacing/base': '16px'}

// Convert to CSS custom properties
:root {
  --figma-color-primary: #00FFFF;
  --figma-spacing-base: 16px;
}
```

### FigJam Integration
```typescript
// For workflow diagrams and documentation
// Kiro will call: get_figjam
// Parameters:
// - fileKey: "FIGJAM123"
// - nodeId: "1:2"
// - includeImagesOfNodes: true
```

### Generating Diagrams
```typescript
// Create workflow diagrams directly in FigJam
// Kiro will call: generate_diagram
// Parameters:
// - name: "User Authentication Flow"
// - mermaidSyntax: "flowchart LR\n  A[Login] --> B[Validate]\n  B --> C[Dashboard]"
```

## Best Practices Checklist

### Before Converting Figma Designs
- [ ] Ensure Figma file is properly organized with named layers
- [ ] Check that design uses consistent spacing and typography
- [ ] Verify color palette matches project design tokens
- [ ] Confirm interactive states are defined (hover, focus, active)

### During Conversion
- [ ] Use existing UI components instead of creating new ones
- [ ] Replace hardcoded colors with CSS custom properties
- [ ] Implement proper TypeScript interfaces
- [ ] Add accessibility attributes (ARIA labels, roles)
- [ ] Include responsive breakpoints

### After Implementation
- [ ] Test component in different screen sizes
- [ ] Verify keyboard navigation works
- [ ] Check color contrast meets WCAG standards
- [ ] Validate performance with React DevTools
- [ ] Set up Code Connect mapping

### AWS Deployment
- [ ] Optimize images for web delivery
- [ ] Configure CloudFront caching headers
- [ ] Set up proper CORS policies
- [ ] Monitor asset loading performance
- [ ] Implement fallback strategies for asset failures

## Troubleshooting Common Issues

### Issue: Figma Colors Don't Match
**Solution**: Use design token mapping instead of hardcoded values
```typescript
// Wrong
className="bg-blue-500"

// Correct  
className="bg-primary"
```

### Issue: Component Not Responsive
**Solution**: Implement mobile-first responsive design
```typescript
// Add responsive classes
className="text-sm sm:text-base lg:text-lg"
```

### Issue: Poor Performance
**Solution**: Implement lazy loading and code splitting
```typescript
const LazyComponent = React.lazy(() => import('./HeavyComponent'))

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  )
}
```

### Issue: AWS Assets Not Loading
**Solution**: Check CORS configuration and CloudFront settings
```typescript
// Verify asset URLs are correct
console.log('Asset URL:', getAssetUrl('images/logo.png'))
```

This comprehensive guide ensures smooth integration between Figma designs and your AI Workflow Architect platform while maintaining AWS compatibility and performance standards.