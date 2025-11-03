import React, { useState, useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import './App.css';

function App() {
  const [logs, setLogs] = useState<string[]>([]);
  const [positions, setPositions] = useState<any[]>([]);
  const [symbols, setSymbols] = useState('AAPL,TSLA');
  const [riskPerTrade, setRiskPerTrade] = useState(1.0);
  const [riskRewardRatio, setRiskRewardRatio] = useState(3.0);
  const [timeBasedExit, setTimeBasedExit] = useState(5);

  const { messages, sendMessage } = useWebSocket('ws://localhost:8080/ws');

  useEffect(() => {
    messages.forEach((msg) => {
      if (msg.type === 'log') {
        setLogs((prevLogs) => [...prevLogs, msg.payload]);
      } else if (msg.type === 'position_update') {
        setPositions(msg.payload);
      }
    });
  }, [messages]);

  const handleStart = () => {
    const config = {
      symbols: symbols.split(','),
      riskPerTrade,
      riskRewardRatio,
      timeBasedExit,
    };
    sendMessage({ type: 'start', payload: config });
  };

  const handleStop = () => {
    sendMessage({ type: 'stop', payload: {} });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AionVanguard - Trading Agent Dashboard</h1>
      </header>
      <div className="main-content">
        <div className="config-panel">
          <h2>Configuration</h2>
          <div className="form-group">
            <label>Symbols (comma-separated)</label>
            <input
              type="text"
              value={symbols}
              onChange={(e) => setSymbols(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Risk Per Trade (%)</label>
            <input
              type="number"
              value={riskPerTrade}
              onChange={(e) => setRiskPerTrade(parseFloat(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label>Risk/Reward Ratio</label>
            <input
              type="number"
              value={riskRewardRatio}
              onChange={(e) => setRiskRewardRatio(parseFloat(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label>Time-based Exit (minutes)</label>
            <input
              type="number"
              value={timeBasedExit}
              onChange={(e) => setTimeBasedExit(parseInt(e.target.value))}
            />
          </div>
          <div className="controls">
            <button onClick={handleStart}>Start Agent</button>
            <button onClick={handleStop}>Stop Agent</button>
          </div>
        </div>
        <div className="dashboard">
          <div className="activity-log">
            <h2>Activity Log</h2>
            <div className="logs">
              {logs.map((log, index) => (
                <div key={index}>{log}</div>
              ))}
            </div>
          </div>
          <div className="positions">
            <h2>Open Positions</h2>
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Quantity</th>
                  <th>Side</th>
                  <th>Entry Price</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos, index) => (
                  <tr key={index}>
                    <td>{pos.symbol}</td>
                    <td>{pos.qty}</td>
                    <td>{pos.side}</td>
                    <td>{pos.avg_entry_price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
