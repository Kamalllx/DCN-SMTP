"use client"

import { useEffect, useState } from "react"
import { io, type Socket } from "socket.io-client"

export function useSocket(token: string | null) {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (token) {
      const newSocket = io("http://localhost:5000", {
        auth: {
          token: token,
        },
      })

      newSocket.on("connect", () => {
        setIsConnected(true)
      })

      newSocket.on("disconnect", () => {
        setIsConnected(false)
      })

      setSocket(newSocket)

      return () => {
        newSocket.close()
      }
    } else {
      if (socket) {
        socket.close()
        setSocket(null)
        setIsConnected(false)
      }
    }
  }, [token])

  return { socket, isConnected }
}
