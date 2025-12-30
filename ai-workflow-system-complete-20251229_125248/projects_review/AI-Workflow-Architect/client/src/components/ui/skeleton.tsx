
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

import { cn } from "@/lib/utils"

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-primary/10", className)}
      {...props}
    />
  )
}

export { Skeleton }
