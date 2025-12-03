"use client";

import { useEffect, useRef, useState } from "react";
import { fetchLogs } from "@/api/logs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface LogViewerProps {
  isActive: boolean;
  onComplete?: () => void;
}

export function LogViewer({ isActive, onComplete }: LogViewerProps) {
  const [logs, setLogs] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const lastFetchTimeRef = useRef<string | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [logs]);

  // Fetch logs function
  const fetchLogMessages = async () => {
    if (!isActive) return;

    setIsLoading(true);
    setError(null);

    try {
      const since = lastFetchTimeRef.current || undefined;
      const response = await fetchLogs(200, since);
      
      if (response.error) {
        setError(response.error);
        return;
      }

      if (response.logs && response.logs.length > 0) {
        // Update last fetch time to current time (ISO format)
        lastFetchTimeRef.current = new Date().toISOString();
        
        // If we have existing logs, only add new ones
        if (logs.length > 0 && since) {
          // Find the index where new logs start
          const lastLog = logs[logs.length - 1];
          const newLogsStartIndex = response.logs.findIndex(log => log === lastLog);
          
          if (newLogsStartIndex !== -1 && newLogsStartIndex < response.logs.length - 1) {
            // Add only the new logs
            setLogs(prev => [...prev, ...response.logs.slice(newLogsStartIndex + 1)]);
          } else {
            // If we can't find the last log, replace all (might be a new session)
            setLogs(response.logs);
          }
        } else {
          // First fetch or no since parameter - set all logs
          setLogs(response.logs);
        }

        // Check if indexing is complete
        const hasStatusUpdate = response.logs.some(log => 
          log.includes("Video Status updated successfully")
        );
        
        if (hasStatusUpdate && onComplete) {
          // Use a simple flag to prevent multiple calls
          const completionFlag = "log_status_updated";
          if (!sessionStorage.getItem(completionFlag)) {
            sessionStorage.setItem(completionFlag, "true");
            // Small delay to ensure all logs are visible
            setTimeout(() => {
              onComplete();
            }, 1000);
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch logs");
    } finally {
      setIsLoading(false);
    }
  };

  // Start polling when active
  useEffect(() => {
    if (isActive) {
      // Initial fetch
      fetchLogMessages();
      
      // Set up polling every 2 seconds
      pollingIntervalRef.current = setInterval(() => {
        fetchLogMessages();
      }, 2000);

      return () => {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
      };
    } else {
      // Reset when inactive
      setLogs([]);
      lastFetchTimeRef.current = null;
      sessionStorage.removeItem("log_status_updated");
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    }
  }, [isActive]);

  // Format log line for display
  const formatLogLine = (line: string) => {
    // Extract timestamp and message
    const timestampMatch = line.match(/^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}): (INFO|ERROR|WARNING|DEBUG): (.*)$/);
    
    if (timestampMatch) {
      const [, timestamp, level, message] = timestampMatch;
      return { timestamp, level, message };
    }
    
    return { timestamp: "", level: "INFO", message: line };
  };

  if (!isActive && logs.length === 0) {
    return null;
  }

  return (
    <Card className="w-full mt-6">
      <CardHeader>
        <CardTitle>Upload & Indexing Progress</CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
            Error: {error}
          </div>
        )}
        <div 
          ref={scrollAreaRef}
          className="h-[400px] w-full rounded border p-4 bg-gray-50 overflow-y-auto"
        >
          <div className="space-y-1 font-mono text-sm">
            {logs.length === 0 && !isLoading && (
              <div className="text-gray-500">No logs available yet...</div>
            )}
            {logs.map((log, index) => {
              const { timestamp, level, message } = formatLogLine(log);
              const levelColor = 
                level === "ERROR" ? "text-red-600" :
                level === "WARNING" ? "text-yellow-600" :
                "text-blue-600";
              
              return (
                <div key={index} className="flex gap-2 py-1">
                  {timestamp && (
                    <span className="text-gray-500 text-xs flex-shrink-0">
                      {timestamp}
                    </span>
                  )}
                  {level && (
                    <span className={`${levelColor} font-semibold flex-shrink-0`}>
                      [{level}]
                    </span>
                  )}
                  <span className="text-gray-800 flex-1 break-words">
                    {message || log}
                  </span>
                </div>
              );
            })}
            {isLoading && logs.length > 0 && (
              <div className="text-gray-500 text-xs mt-2">Loading new logs...</div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

