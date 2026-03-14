import type { SSEEvent } from '@/types'
import { answerQuestion } from '@/api/client'

interface Props {
  question: Extract<SSEEvent, { type: 'question' }>
  sessionId: string
}

export function Chatbox({ question, sessionId }: Props) {
  const handleChoice = async (choix: number) => {
    try {
      await answerQuestion(sessionId, question.agent_id, question.individu_id, choix)
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div className="chatbox">
      <div className="chatbox-head">
        <div className="live-dot" style={{ width: '6px', height: '6px' }} />
        <span className="chatbox-title">Agent needs your input</span>
      </div>
      <div style={{ padding: '14px' }}>
        <div className="chatbox-question">{question.question}</div>
        <div className="chatbox-options">
          {question.options.map((opt, i) => (
            <button
              key={i}
              className="chatbox-option"
              onClick={() => handleChoice(i)}
            >
              [{i + 1}] {opt}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
