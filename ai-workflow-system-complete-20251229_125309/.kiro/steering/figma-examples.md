---
inclusion: manual
---

# Figma Power Examples & Demonstrations

## Example 1: Simple Button Component

Let's demonstrate the Figma power with a simple example. Here's how you would convert a Figma button design to a React component:

### Step 1: Provide Figma URL
```
Example URL: https://figma.com/design/ABC123/MyProject?node-id=1-2
```

### Step 2: Kiro Extracts the Design
```typescript
// Kiro automatically calls:
// get_design_context(fileKey="ABC123", nodeId="1:2", clientLanguages="typescript", clientFrameworks="react,tailwind")
```

### Step 3: Raw Figma Output (Example)
```typescript
export function Button({ children, variant = "primary", size = "medium" }) {
  const baseClasses = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
  
  const variantClasses = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500",
  };
  
  const sizeClasses = {
    small: "px-3 py-1.5 text-sm",
    medium: "px-4 py-2 text-base",
    large: "px-6 py-3 text-lg",
  };
  
  return (
    <button className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}>
      {children}
    </button>
  );
}
```

### Step 4: Kiro Converts to Project Standards
```typescript
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        default: "h-10 py-2 px-4",
        sm: "h-9 px-3 rounded-md",
        lg: "h-11 px-8 rounded-md",
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
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"
```

## Example 2: Dashboard Card with Glassmorphism

### Figma Design Features
- Card with glassmorphism background
- Header with title and action button  
- Metrics display with glow effect
- Status badge

### Converted Component
```typescript
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown } from "lucide-react"

interface MetricCardProps {
  title: string
  value: string | number
  change: number
  changeLabel: string
  status: "active" | "inactive" | "pending"
  onViewDetails?: () => void
}

export function MetricCard({ 
  title, 
  value, 
  change, 
  changeLabel, 
  status, 
  onViewDetails 
}: MetricCardProps) {
  const isPositive = change > 0
  
  return (
    <Card className="glass-card hover:glass-panel transition-all duration-300">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={onViewDetails}
          className="h-8 w-8 p-0"
        >
          <span className="sr-only">View details</span>
          →
        </Button>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-glow mb-2">
          {value}
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <div className={`flex items-center ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? (
              <TrendingUp className="h-3 w-3 mr-1" />
            ) : (
              <TrendingDown className="h-3 w-3 mr-1" />
            )}
            {Math.abs(change)}%
          </div>
          <span className="text-muted-foreground">{changeLabel}</span>
        </div>
        <Badge 
          variant={status === 'active' ? 'default' : status === 'pending' ? 'secondary' : 'outline'}
          className="mt-3"
        >
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </Badge>
      </CardContent>
    </Card>
  )
}
```

## Example 3: Creating a Diagram with FigJam

### Generate a Workflow Diagram
```typescript
// Kiro can create diagrams directly in FigJam
// Example: User authentication flow

const mermaidSyntax = `
flowchart LR
    A["User Login"] --> B["Validate Credentials"]
    B --> C{"Valid?"}
    C -->|Yes| D["Generate JWT"]
    C -->|No| E["Show Error"]
    D --> F["Redirect to Dashboard"]
    E --> A
    F --> G["Load User Data"]
    G --> H["Display Interface"]
`;

// Kiro calls: generate_diagram(name="User Authentication Flow", mermaidSyntax=mermaidSyntax)
// Returns: FigJam URL for viewing and editing
```

## Example 4: Code Connect Integration

### Mapping Components to Figma
```typescript
// After creating a component, map it to Figma design
// Kiro calls: add_code_connect_map(
//   fileKey="ABC123",
//   nodeId="1:2", 
//   source="client/src/components/ui/button.tsx",
//   componentName="Button",
//   label="React"
// )

// Verify the mapping
// Kiro calls: get_code_connect_map(fileKey="ABC123", nodeId="1:2")
// Returns: {'1:2': { codeConnectSrc: 'client/src/components/ui/button.tsx', codeConnectName: 'Button' }}
```

## Example 5: Responsive Layout Component

### Figma Design: Mobile + Desktop Layout
```typescript
import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"

interface ResponsiveGridProps {
  items: Array<{
    id: string
    title: string
    description: string
    image?: string
  }>
}

export function ResponsiveGrid({ items }: ResponsiveGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4">
      {items.map((item, index) => (
        <motion.div
          key={item.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ 
            duration: 0.3, 
            delay: index * 0.1,
            ease: "easeOut"
          }}
        >
          <Card className="glass-card hover:neon-border transition-all duration-300 h-full">
            {item.image && (
              <div className="aspect-video bg-muted rounded-t-lg overflow-hidden">
                <img 
                  src={item.image} 
                  alt={item.title}
                  className="w-full h-full object-cover"
                />
              </div>
            )}
            <CardContent className="p-4">
              <h3 className="font-semibold text-lg mb-2 text-glow">
                {item.title}
              </h3>
              <p className="text-sm text-muted-foreground">
                {item.description}
              </p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  )
}
```

## Example 6: Getting Screenshots for Documentation

### Capture Component Screenshots
```typescript
// Get a screenshot of a specific Figma component
// Kiro calls: get_screenshot(
//   fileKey="ABC123",
//   nodeId="1:2",
//   clientLanguages="typescript",
//   clientFrameworks="react"
// )
// Returns: Base64 encoded image for documentation
```

## Example 7: Working with Design Variables

### Extract and Use Figma Variables
```typescript
// Get design variables from Figma
// Kiro calls: get_variable_defs(fileKey="ABC123", nodeId="1:2")
// Returns: {'color/primary': '#00FFFF', 'spacing/base': '16px', 'font/heading': 'Space Grotesk'}

// Convert to CSS custom properties
const figmaVariables = {
  'color/primary': '#00FFFF',
  'color/secondary': '#8B5CF6', 
  'spacing/base': '16px',
  'spacing/large': '24px',
  'font/heading': 'Space Grotesk',
  'font/body': 'Inter'
}

// Generate CSS
const cssVariables = Object.entries(figmaVariables)
  .map(([key, value]) => `  --figma-${key.replace('/', '-')}: ${value};`)
  .join('\n')

console.log(`:root {\n${cssVariables}\n}`)
```

## Testing Your Setup

### Quick Test Checklist

1. **Authentication Test**
   ```typescript
   // Kiro calls: whoami()
   // Should return your Figma user info
   ```

2. **Basic Design Extraction**
   ```typescript
   // Provide any Figma URL
   // Kiro calls: get_design_context(fileKey, nodeId)
   // Should return React component code
   ```

3. **Screenshot Generation**
   ```typescript
   // Kiro calls: get_screenshot(fileKey, nodeId)
   // Should return image data
   ```

4. **Code Connect Mapping**
   ```typescript
   // Kiro calls: add_code_connect_map(...)
   // Then: get_code_connect_map(...)
   // Should show the mapping
   ```

### Common Use Cases

**Design System Documentation**
- Extract all components from Figma design system
- Generate component library documentation
- Create visual regression tests

**Rapid Prototyping**
- Convert Figma mockups to working React components
- Maintain design-code consistency
- Speed up development workflow

**Asset Management**
- Export optimized images and icons
- Generate multiple formats (WebP, PNG, SVG)
- Integrate with AWS CDN for performance

**Team Collaboration**
- Real-time design updates via webhooks
- Automated component mapping
- Design feedback integration

This setup provides a complete Figma-to-code workflow that integrates seamlessly with your AI Workflow Architect platform and AWS infrastructure.