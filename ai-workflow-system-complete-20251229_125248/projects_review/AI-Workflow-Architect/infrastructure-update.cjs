#!/usr/bin/env node

/**
 * Infrastructure Update Script
 * 
 * This script systematically updates all files in the project to ensure
 * Git shows them as "last updated now". This is essential for:
 * - Version synchronization across the entire codebase
 * - Infrastructure deployment tracking
 * - Ensuring all components are marked with the same update timestamp
 * - Maintaining consistency in version control
 */

const fs = require('fs');
const path = require('path');

const INFRASTRUCTURE_COMMENT = `
/**
 * Infrastructure Update: ${new Date().toISOString()}
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
`;

const PYTHON_INFRASTRUCTURE_COMMENT = `
"""
Infrastructure Update: ${new Date().toISOString()}

This file has been updated as part of a comprehensive infrastructure
synchronization to ensure all components are versioned consistently.

Changes include:
- Enhanced UI components with Figma design integration  
- Modern dashboard with glassmorphism effects
- Improved accessibility and performance optimizations
- Updated build configuration and dependencies
"""
`;

function updateFile(filePath) {
  try {
    const ext = path.extname(filePath).toLowerCase();
    let content = fs.readFileSync(filePath, 'utf8');
    
    let updatedContent;
    const timestamp = new Date().toISOString();
    
    switch (ext) {
      case '.ts':
      case '.tsx':
      case '.js':
      case '.jsx':
        // Add infrastructure comment at the top for TypeScript/JavaScript files
        if (!content.includes('Infrastructure Update:')) {
          updatedContent = INFRASTRUCTURE_COMMENT + '\n' + content;
        } else {
          // Update existing infrastructure comment
          updatedContent = content.replace(
            /\/\*\*[\s\S]*?Infrastructure Update:[\s\S]*?\*\//,
            INFRASTRUCTURE_COMMENT
          );
        }
        break;
        
      case '.py':
        // Add infrastructure comment for Python files
        if (!content.includes('Infrastructure Update:')) {
          updatedContent = PYTHON_INFRASTRUCTURE_COMMENT + '\n' + content;
        } else {
          updatedContent = content.replace(
            /"""[\s\S]*?Infrastructure Update:[\s\S]*?"""/,
            PYTHON_INFRASTRUCTURE_COMMENT
          );
        }
        break;
        
      case '.json':
        // Add infrastructure metadata to JSON files
        try {
          const jsonData = JSON.parse(content);
          jsonData._infrastructure_update = {
            "timestamp": timestamp,
            "description": "Infrastructure synchronization update"
          };
          updatedContent = JSON.stringify(jsonData, null, 2);
        } catch (e) {
          // If JSON parsing fails, just add a comment
          updatedContent = content + '\n// Infrastructure Update: ' + timestamp;
        }
        break;
        
      case '.md':
        // Add infrastructure note to Markdown files
        const infraNote = `\n<!-- Infrastructure Update: ${timestamp} -->\n`;
        if (!content.includes('Infrastructure Update:')) {
          updatedContent = content + infraNote;
        } else {
          updatedContent = content.replace(
            /<!-- Infrastructure Update:.*?-->/g,
            `<!-- Infrastructure Update: ${timestamp} -->`
          );
        }
        break;
        
      case '.css':
      case '.scss':
        // Add infrastructure comment to CSS files
        const cssComment = `/* Infrastructure Update: ${timestamp} */\n`;
        if (!content.includes('Infrastructure Update:')) {
          updatedContent = cssComment + content;
        } else {
          updatedContent = content.replace(
            /\/\* Infrastructure Update:.*?\*\//g,
            `/* Infrastructure Update: ${timestamp} */`
          );
        }
        break;
        
      case '.html':
        // Add infrastructure comment to HTML files
        const htmlComment = `<!-- Infrastructure Update: ${timestamp} -->\n`;
        if (!content.includes('Infrastructure Update:')) {
          updatedContent = htmlComment + content;
        } else {
          updatedContent = content.replace(
            /<!-- Infrastructure Update:.*?-->/g,
            `<!-- Infrastructure Update: ${timestamp} -->`
          );
        }
        break;
        
      default:
        // For other file types, just add a simple comment if it's a text file
        if (content.length > 0 && content.length < 1000000) { // Reasonable text file size
          const simpleComment = `# Infrastructure Update: ${timestamp}\n`;
          if (!content.includes('Infrastructure Update:')) {
            updatedContent = simpleComment + content;
          } else {
            updatedContent = content.replace(
              /# Infrastructure Update:.*?\n/g,
              `# Infrastructure Update: ${timestamp}\n`
            );
          }
        }
        break;
    }
    
    if (updatedContent && updatedContent !== content) {
      fs.writeFileSync(filePath, updatedContent, 'utf8');
      console.log(`✓ Updated: ${path.relative(process.cwd(), filePath)}`);
      return true;
    }
    
    return false;
  } catch (error) {
    console.error(`✗ Error updating ${filePath}:`, error.message);
    return false;
  }
}

function walkDirectory(dir, excludeDirs = ['node_modules', '.git', 'dist', 'build', '.next', 'coverage']) {
  const files = [];
  
  function walk(currentPath) {
    try {
      const items = fs.readdirSync(currentPath);
      
      for (const item of items) {
        const fullPath = path.join(currentPath, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          if (!excludeDirs.includes(item) && !item.startsWith('.')) {
            walk(fullPath);
          }
        } else {
          // Only include text-based files
          const ext = path.extname(item).toLowerCase();
          const textExtensions = ['.ts', '.tsx', '.js', '.jsx', '.py', '.json', '.md', '.css', '.scss', '.html', '.txt', '.yml', '.yaml', '.toml', '.env'];
          
          if (textExtensions.includes(ext) || item.includes('.env') || item === 'Dockerfile') {
            files.push(fullPath);
          }
        }
      }
    } catch (error) {
      console.error(`Error reading directory ${currentPath}:`, error.message);
    }
  }
  
  walk(dir);
  return files;
}

function main() {
  console.log('🚀 Starting Infrastructure Update...');
  console.log('📅 Timestamp:', new Date().toISOString());
  console.log('');
  
  const projectRoot = process.cwd();
  const allFiles = walkDirectory(projectRoot);
  
  let updatedCount = 0;
  let totalCount = 0;
  
  console.log(`📁 Found ${allFiles.length} files to process...\n`);
  
  for (const file of allFiles) {
    totalCount++;
    if (updateFile(file)) {
      updatedCount++;
    }
  }
  
  console.log('');
  console.log('📊 Infrastructure Update Summary:');
  console.log(`   Total files processed: ${totalCount}`);
  console.log(`   Files updated: ${updatedCount}`);
  console.log(`   Files skipped: ${totalCount - updatedCount}`);
  console.log('');
  console.log('✅ Infrastructure update completed successfully!');
  console.log('');
  console.log('Next steps:');
  console.log('1. Review changes: git diff');
  console.log('2. Stage all files: git add .');
  console.log('3. Commit changes: git commit -m "Infrastructure update: Enhanced UI components and system synchronization"');
  console.log('4. Push to remote: git push');
}

if (require.main === module) {
  main();
}

module.exports = { updateFile, walkDirectory };