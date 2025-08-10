import { cn } from '@/lib/utils'
import { ReactNode } from 'react'

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  // Simple markdown-to-HTML conversion for basic formatting
  const renderMarkdown = (text: string): ReactNode => {
    // Split by lines and process each one
    const lines = text.split('\n')
    const elements: ReactNode[] = []
    let i = 0

    while (i < lines.length) {
      const line = lines[i].trim()
      
      // Skip empty lines
      if (!line) {
        elements.push(<br key={i} />)
        i++
        continue
      }

      // Headers
      if (line.startsWith('### ')) {
        elements.push(
          <h3 key={i} className="text-sm font-medium mb-1 text-foreground mt-2">
            {line.substring(4)}
          </h3>
        )
      } else if (line.startsWith('## ')) {
        elements.push(
          <h2 key={i} className="text-base font-semibold mb-2 text-foreground mt-3">
            {line.substring(3)}
          </h2>
        )
      } else if (line.startsWith('# ')) {
        elements.push(
          <h1 key={i} className="text-lg font-bold mb-2 text-foreground mt-3">
            {line.substring(2)}
          </h1>
        )
      }
      // Lists
      else if (line.startsWith('- ') || line.startsWith('* ')) {
        const listItems: ReactNode[] = []
        while (i < lines.length && (lines[i].trim().startsWith('- ') || lines[i].trim().startsWith('* '))) {
          const item = lines[i].trim().substring(2)
          listItems.push(
            <li key={`${i}-li`} className="text-foreground">
              {formatInlineText(item)}
            </li>
          )
          i++
        }
        elements.push(
          <ul key={`${i}-ul`} className="list-disc list-inside mb-2 space-y-1 text-sm ml-4">
            {listItems}
          </ul>
        )
        continue
      }
      // Numbered lists
      else if (line.match(/^\d+\. /)) {
        const listItems: ReactNode[] = []
        while (i < lines.length && lines[i].trim().match(/^\d+\. /)) {
          const item = lines[i].trim().replace(/^\d+\. /, '')
          listItems.push(
            <li key={`${i}-li`} className="text-foreground">
              {formatInlineText(item)}
            </li>
          )
          i++
        }
        elements.push(
          <ol key={`${i}-ol`} className="list-decimal list-inside mb-2 space-y-1 text-sm ml-4">
            {listItems}
          </ol>
        )
        continue
      }
      // Code blocks
      else if (line.startsWith('```')) {
        const codeLines: string[] = []
        i++ // Skip opening ```
        while (i < lines.length && !lines[i].trim().startsWith('```')) {
          codeLines.push(lines[i])
          i++
        }
        elements.push(
          <pre key={`${i}-pre`} className="bg-muted p-3 rounded-md overflow-x-auto mb-2 text-xs font-mono">
            <code className="text-foreground">
              {codeLines.join('\n')}
            </code>
          </pre>
        )
      }
      // Blockquotes
      else if (line.startsWith('> ')) {
        elements.push(
          <blockquote key={i} className="border-l-4 border-muted pl-4 italic text-muted-foreground mb-2">
            {formatInlineText(line.substring(2))}
          </blockquote>
        )
      }
      // Regular paragraphs
      else {
        elements.push(
          <p key={i} className="mb-2 text-sm text-foreground leading-relaxed">
            {formatInlineText(line)}
          </p>
        )
      }
      
      i++
    }

    return <>{elements}</>
  }

  // Format inline text (bold, italic, code, links)
  const formatInlineText = (text: string): ReactNode => {
    // Split by inline code first
    const parts = text.split(/(`[^`]+`)/)
    
    return parts.map((part, index) => {
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={index} className="bg-muted px-1 py-0.5 rounded text-xs font-mono text-foreground">
            {part.slice(1, -1)}
          </code>
        )
      }
      
      // Process bold and italic
      return formatBoldItalic(part, index)
    })
  }

  const formatBoldItalic = (text: string, baseIndex: number): ReactNode => {
    // Bold text
    const boldParts = text.split(/(\*\*[^*]+\*\*)/)
    
    return boldParts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={`${baseIndex}-${index}`} className="font-semibold text-foreground">
            {part.slice(2, -2)}
          </strong>
        )
      }
      
      // Italic text
      const italicParts = part.split(/(\*[^*]+\*)/)
      
      return italicParts.map((italicPart, italicIndex) => {
        if (italicPart.startsWith('*') && italicPart.endsWith('*') && !italicPart.startsWith('**')) {
          return (
            <em key={`${baseIndex}-${index}-${italicIndex}`} className="italic text-foreground">
              {italicPart.slice(1, -1)}
            </em>
          )
        }
        
        return italicPart
      })
    })
  }

  return (
    <div className={cn("prose prose-sm dark:prose-invert max-w-none", className)}>
      {renderMarkdown(content)}
    </div>
  )
}
