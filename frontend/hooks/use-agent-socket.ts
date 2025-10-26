import { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

export interface Log {
  id: string;
  level: string;
  message: string;
  timestamp: string;
}

export const useAgentSocket = (serverUrl: string) => {
  const [logs, setLogs] = useState<Log[]>([]);
  const [finalDoc, setFinalDoc] = useState<string>("");
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    const socket = io(serverUrl);
    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('Connected to WebSocket server with ID:', socket.id);
      setIsConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server.');
      setIsConnected(false);
    });

    socket.on('log', (data: { level: string; message: string }) => {
      const newLog: Log = {
        id: `log-${Date.now()}-${Math.random()}`,
        level: data.level,
        message: data.message,
        timestamp: new Date().toLocaleTimeString(),
      };
      setLogs((prevLogs) => [...prevLogs, newLog]);
    });

    socket.on('final_result', (data: { documentation: string }) => {
      setFinalDoc(data.documentation);
      setLogs((prevLogs) => [...prevLogs, {
        id: `log-final`,
        level: 'SUCCESS',
        message: 'Mission Complete! Final documentation received.',
        timestamp: new Date().toLocaleTimeString(),
      }]);
    });

    return () => {
      socket.disconnect();
    };
  }, [serverUrl]);

  const startMission = (projectPath: string) => {
    if (!socketRef.current || !isConnected) {
      alert("Not connected to the agent server. Please wait or refresh.");
      return;
    }

    setLogs([]);
    setFinalDoc("");
    
    // *** THE FIX IS HERE: Use socket.emit, not fetch ***
    // This sends a 'start_agent' event over the WebSocket to the back end.
    socketRef.current.emit('start_agent', { project_path: projectPath });
  };

  return { logs, finalDoc, isConnected, startMission };
};