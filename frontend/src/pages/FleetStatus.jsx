import { useState, useEffect } from 'react'
import { api } from '../api'

const STATUS_OPTS = [
  { value: 'AVAILABLE', label: 'Доступен' },
  { value: 'SERVICE',   label: 'На обслуживании' },
  { value: 'HIDDEN',    label: 'Скрыт' },
]

export function FleetStatus() {
  const [cars, setCars] = useState([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.fleet().then(setCars).finally(() => setLoading(false))
  }

  useEffect(load, [])

  const updateStatus = async (carId, status) => {
    try { await api.updateCarStatus(carId, status); load() }
    catch (err) { alert(err.message) }
  }

  if (loading) return <div className="loading">Загрузка...</div>

  return (
    <div className="page">
      <h1>Статус автопарка</h1>
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>Автомобиль</th>
              <th>Категория</th>
              <th>Цена/сут</th>
              <th>Статус</th>
              <th>Аренд</th>
              <th>Изменить статус</th>
            </tr>
          </thead>
          <tbody>
            {cars.map(car => (
              <tr key={car.id} className={car.is_booked_now ? 'row-busy' : ''}>
                <td>{car.brand} {car.model} ({car.year})</td>
                <td>{car.category}</td>
                <td>{Number(car.price_per_day).toLocaleString('ru')} ₽</td>
                <td>
                  <span className={`status-badge status-${car.status.toLowerCase()}`}>
                    {car.status_display}
                  </span>
                  {car.is_booked_now && <span className="badge-busy">В аренде</span>}
                </td>
                <td>{car.bookings_count}</td>
                <td>
                  <select value={car.status}
                    onChange={e => updateStatus(car.id, e.target.value)}
                    className="select select-sm">
                    {STATUS_OPTS.map(s => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
