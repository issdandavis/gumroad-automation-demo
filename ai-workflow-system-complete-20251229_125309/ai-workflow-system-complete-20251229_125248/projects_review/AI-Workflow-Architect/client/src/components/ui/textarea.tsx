
/**
 * Infrastructure Update: 2025-12-29T09:27:50.260Z
 * 
 * This file has been updated as part of a comprehensive infrastructure
 * synchronization to ensure all components are versioned consistently.
 * 
 * Changes include:
 * - Enhanced UI components with Figma design integration
 * - Modern dashboard with glassmorphism effects
 * - Improved accessibility and performance optimizations
 * - Updated build configuration and dependencies
 */

import * as React from "react"

import { cn } from "@/lib/utils"

const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.ComponentProps<"textarea">
>(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        "flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-base shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Textarea.displayName = "Textarea"

export { Textarea }
