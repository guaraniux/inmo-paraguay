'use client'

import PropertyResults from '../property/PropertyResults'
import { Mensaje } from '../../lib/types'

interface ChatMessageProps {
  mensaje: Mensaje
}

export default function ChatMessage({ mensaje }: ChatMessageProps) {
  const isUser = mensaje.rol === 'user'
  
  return (
    <div className={`animate-fade-in ${isUser ? 'flex justify-end' : ''}`}>
      {isUser ? (
        <div className="chat-bubble-user px-4 py-3 max-w-[85%]">
          <p className="text-sm">{mensaje.contenido}</p>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="chat-bubble-assistant px-4 py-3">
            <p className="text-sm whitespace-pre-wrap leading-relaxed">{mensaje.contenido}</p>
          </div>
          
          {mensaje.inmuebles && mensaje.inmuebles.length > 0 && (
            <PropertyResults inmuebles={mensaje.inmuebles} />
          )}
        </div>
      )}
    </div>
  )
}
