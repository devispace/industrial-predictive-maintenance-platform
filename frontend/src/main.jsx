import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const sample = {'Type':'M','Air temperature [K]':300.1,'Process temperature [K]':310.2,'Rotational speed [rpm]':1500,'Torque [Nm]':42,'Tool wear [min]':180};
const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

function App() {
  const [metrics, setMetrics] = useState({predictions_total: 0, alerts_total: 0});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);
  useEffect(() => {
    Promise.all([fetch(`${API_BASE}/health`).then(r => r.json()), fetch(`${API_BASE}/metrics`).then(r => r.json())])
      .then(([health, nextMetrics]) => { setApiOnline(health.model_loaded); setMetrics(nextMetrics); })
      .catch(() => setApiOnline(false));
  }, []);
  async function runPrediction() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/predict`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(sample)});
      if (!res.ok) throw new Error(`Prediction failed: ${res.status}`);
      const nextResult = await res.json();
      setResult(nextResult);
      const nextMetrics = await fetch(`${API_BASE}/metrics`).then(r => r.json());
      setMetrics(nextMetrics);
    }
    finally { setLoading(false); }
  }
  const alertRate = metrics.predictions_total ? (metrics.alerts_total / metrics.predictions_total * 100).toFixed(1) : '0.0';
  return <main>
    <header><div><p className="eyebrow">INDUSTRIAL OPS / PREDICTIVE MAINTENANCE</p><h1>设备健康监控台</h1><p className="muted">AI4I 2020 synthetic data demo · 人工确认闭环</p></div><span className={apiOnline ? 'status' : 'status offline'}>● API {apiOnline ? 'ONLINE' : 'OFFLINE'}</span></header>
    <section className="grid"><article><span className="label">PREDICTIONS</span><strong>{metrics.predictions_total}</strong><small>已处理样本</small></article><article className="danger"><span className="label">ALERTS</span><strong>{metrics.alerts_total}</strong><small>需要人工确认</small></article><article><span className="label">ALERT RATE</span><strong>{alertRate}%</strong><small>当前记录窗口</small></article></section>
    <section className="panel"><div><p className="eyebrow">LIVE INFERENCE</p><h2>单台设备风险预测</h2><p className="muted">示例工况：M 型设备，1500 rpm，42 Nm，工具磨损 180 min</p></div><button onClick={runPrediction} disabled={loading || !apiOnline}>{loading ? '计算中…' : '运行预测'}</button>{result && <div className={result.alert ? 'result alert' : 'result'}><div><span className="label">FAILURE PROBABILITY</span><strong>{(result.probability*100).toFixed(2)}%</strong></div><div><span className="label">DECISION</span><b>{result.alert ? '⚠ 需要人工确认' : '✓ 继续监测'}</b><small>{result.action}</small></div></div>}</section>
    <footer>数据源：UCI AI4I 2020 · 公开合成工业数据，不代表真实工厂或中铝生产数据</footer>
  </main>;
}
createRoot(document.getElementById('root')).render(<App />);
