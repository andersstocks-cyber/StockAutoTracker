import { useEffect, useState } from 'react'

const emptyRule = {
  ticker: 'AAPL',
  trigger_type: 'rsi',
  comparator: 'gt',
  threshold: 70,
  window_minutes: 15,
  enabled: true,
  alert_channels: ['iphone', 'sms'],
}

export default function App() {
  const [rule, setRule] = useState(emptyRule)
  const [rules, setRules] = useState([])
  const [testPayload, setTestPayload] = useState({
    ticker: 'AAPL',
    rsi: 72,
    volume: 1500000,
    percent_move: 4.6,
  })
  const [matches, setMatches] = useState([])

  const fetchRules = async () => {
    const response = await fetch('http://localhost:8000/api/triggers')
    const data = await response.json()
    setRules(data.rules || [])
  }

  useEffect(() => {
    fetchRules()
  }, [])

  const handleChange = (field, value) => {
    setRule((prev) => ({ ...prev, [field]: value }))
  }

  const submitRule = async () => {
    const response = await fetch('http://localhost:8000/api/triggers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(rule),
    })

    const data = await response.json()
    if (response.ok) {
      fetchRules()
      alert(`Saved trigger for ${data.rule.ticker}`)
    }
  }

  const runCheck = async () => {
    const response = await fetch('http://localhost:8000/api/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testPayload),
    })

    const data = await response.json()
    setMatches(data.matches || [])
  }

  return (
    <div className="app-shell">
      <header>
        <h1>StockAutoTracker</h1>
        <p>Monitor stock triggers and alert via iPhone + SMS</p>
      </header>

      <main className="layout">
        <section className="panel">
          <h2>Create trigger</h2>

          <label>
            Ticker
            <input value={rule.ticker} onChange={(e) => handleChange('ticker', e.target.value.toUpperCase())} />
          </label>

          <label>
            Trigger type
            <select value={rule.trigger_type} onChange={(e) => handleChange('trigger_type', e.target.value)}>
              <option value="rsi">RSI</option>
              <option value="volume">Volume</option>
              <option value="percent_move">% Move</option>
            </select>
          </label>

          <label>
            Comparator
            <select value={rule.comparator} onChange={(e) => handleChange('comparator', e.target.value)}>
              <option value="gt">Greater than</option>
              <option value="lt">Less than</option>
              <option value="gte">Greater than or equal</option>
              <option value="lte">Less than or equal</option>
              <option value="eq">Equal</option>
            </select>
          </label>

          <label>
            Threshold
            <input type="number" value={rule.threshold} onChange={(e) => handleChange('threshold', Number(e.target.value))} />
          </label>

          <label>
            Window (minutes)
            <input type="number" value={rule.window_minutes} onChange={(e) => handleChange('window_minutes', Number(e.target.value))} />
          </label>

          <label>
            Alert channels
            <div className="channel-row">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={rule.alert_channels.includes('iphone')}
                  onChange={(e) => {
                    const next = e.target.checked
                      ? [...rule.alert_channels, 'iphone']
                      : rule.alert_channels.filter((item) => item !== 'iphone')
                    handleChange('alert_channels', next)
                  }}
                />
                iPhone
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={rule.alert_channels.includes('sms')}
                  onChange={(e) => {
                    const next = e.target.checked
                      ? [...rule.alert_channels, 'sms']
                      : rule.alert_channels.filter((item) => item !== 'sms')
                    handleChange('alert_channels', next)
                  }}
                />
                SMS
              </label>
            </div>
          </label>

          <button onClick={submitRule}>Save trigger</button>
        </section>

        <section className="panel">
          <h2>Trigger rules</h2>
          <ul className="rule-list">
            {rules.length === 0 ? <li>No rules created yet.</li> : rules.map((item, index) => (
              <li key={`${item.ticker}-${index}`}>
                <strong>{item.ticker}</strong> · {item.trigger_type.toUpperCase()} · {item.comparator} · {item.threshold}
                <div>{item.alert_channels.join(', ')}</div>
              </li>
            ))}
          </ul>
        </section>

        <section className="panel wide">
          <h2>Simulate trigger evaluation</h2>
          <div className="simulator-grid">
            <label>
              Ticker
              <input value={testPayload.ticker} onChange={(e) => setTestPayload({ ...testPayload, ticker: e.target.value.toUpperCase() })} />
            </label>
            <label>
              RSI
              <input type="number" value={testPayload.rsi} onChange={(e) => setTestPayload({ ...testPayload, rsi: Number(e.target.value) })} />
            </label>
            <label>
              Volume
              <input type="number" value={testPayload.volume} onChange={(e) => setTestPayload({ ...testPayload, volume: Number(e.target.value) })} />
            </label>
            <label>
              % Move
              <input type="number" step="0.1" value={testPayload.percent_move} onChange={(e) => setTestPayload({ ...testPayload, percent_move: Number(e.target.value) })} />
            </label>
          </div>

          <button onClick={runCheck}>Check triggers</button>

          <div className="matches">
            {matches.length === 0 ? <p>No trigger matches.</p> : matches.map((match, index) => (
              <div key={`${match.ticker}-${match.trigger_type}-${index}`} className="match-card">
                <strong>{match.ticker}</strong>
                <div>{match.trigger_type.toUpperCase()} hit at {match.actual_value}</div>
                <div>Channels: {match.channels.join(', ')}</div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}
