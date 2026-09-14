import ReactMarkdown from 'react-markdown'

export default function InsightsMarkdown({ content }) {
  if (!content) return null

  return (
    <div className="insights-markdown">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  )
}
