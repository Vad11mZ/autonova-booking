import { useState, useEffect } from 'react'
import { api } from '../api'

export function Analytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.analytics().then(setData).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading">Загрузка...</div>
  if (!data) return null

  const metrics = [
    { label: 'Всего авто',        value: data.cars_total },
    { label: 'Доступно',          value: data.cars_available },
    { label: 'На обслуживании',   value: data.cars_service },
    { label: 'Всего бронирований',value: data.bookings_total },
    { label: 'На рассмотрении',   value: data.bookings_pending },
    { label: 'Подтверждено',      value: data.bookings_confirmed },
    { label: 'Выручка',           value: `${Number(data.revenue).toLocaleString('ru')} ₽` },
    { label: 'Клиентов',          value: data.clients_total },
  ]

  return (
    <div className="page">
      <h1>Аналитика</h1>

      <div className="stats-grid">
        {metrics.map(m => (
          <div key={m.label} className="stat-card">
            <strong>{m.value}</strong>
            <span>{m.label}</span>
          </div>
        ))}
      </div>

      <h2 style={{ margin: '2rem 0 1rem' }}>Топ автомобилей по выручке</h2>
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr><th>#</th><th>Автомобиль</th><th>Выручка, ₽</th></tr>
          </thead>
          <tbody>
            {data.cars_revenue.map((r, i) => (
              <tr key={i}>
                <td>{i + 1}</td>
                <td>{r.car}</td>
                <td>{Number(r.revenue).toLocaleString('ru')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
