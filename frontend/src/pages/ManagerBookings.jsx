import { useState, useEffect } from 'react'
import { api } from '../api'

const FILTERS = [
  { value: '', label: 'Все' },
  { value: 'PENDING', label: 'На рассмотрении' },
  { value: 'CONFIRMED', label: 'Подтверждено' },
  { value: 'COMPLETED', label: 'Завершено' },
  { value: 'CANCELLED', label: 'Отменено' },
]

export function ManagerBookings() {
  const [bookings, setBookings] = useState([])
  const [filter, setFilter] = useState('')
  const [comments, setComments] = useState({})
  const [loading, setLoading] = useState(true)

  const load = (s = filter) => {
    setLoading(true)
    api.managerBookings(s).then(setBookings).finally(() => setLoading(false))
  }

  useEffect(() => load(), [])

  const applyFilter = (s) => { setFilter(s); load(s) }

  const action = async (id, act) => {
    try { await api.bookingAction(id, { action: act, manager_comment: comments[id] || '' }); load() }
    catch (err) { alert(err.message) }
  }

  return (
    <div className="page">
      <h1>Управление бронированиями</h1>

      <div className="filters" style={{ marginBottom: '1.5rem' }}>
        {FILTERS.map(f => (
          <button key={f.value}
            className={filter === f.value ? 'btn-primary btn-sm' : 'btn-outline btn-sm'}
            onClick={() => applyFilter(f.value)}>
            {f.label}
          </button>
        ))}
      </div>

      {loading ? <div className="loading">Загрузка...</div> : (
        <div className="bookings-list">
          {bookings.map(b => (
            <div key={b.id} className="booking-card">
              <div className="booking-header">
                <strong>#{b.id} — {b.car}</strong>
                <span className={`status-badge status-${b.status.toLowerCase()}`}>{b.status_display}</span>
              </div>
              <div className="booking-meta">Клиент: {b.client}</div>
              <div className="booking-dates">{b.start_date} → {b.end_date}</div>
              <div className="booking-price">Итого: {Number(b.total_price).toLocaleString('ru')} ₽</div>
              {b.comment && <div className="booking-comment">Клиент: {b.comment}</div>}
              <textarea
                value={comments[b.id] || b.manager_comment}
                onChange={e => setComments(c => ({ ...c, [b.id]: e.target.value }))}
                placeholder="Комментарий менеджера"
                className="input textarea" style={{ marginTop: '0.5rem' }}
              />
              <div className="booking-actions">
                {b.status === 'PENDING' && (
                  <>
                    <button onClick={() => action(b.id, 'confirm')} className="btn-success btn-sm">Подтвердить</button>
                    <button onClick={() => action(b.id, 'cancel')} className="btn-danger btn-sm">Отменить</button>
                  </>
                )}
                {b.status === 'CONFIRMED' && (
                  <>
                    <button onClick={() => action(b.id, 'complete')} className="btn-primary btn-sm">Завершить</button>
                    <button onClick={() => action(b.id, 'cancel')} className="btn-danger btn-sm">Отменить</button>
                  </>
                )}
              </div>
            </div>
          ))}
          {bookings.length === 0 && <p className="empty">Бронирований не найдено.</p>}
        </div>
      )}
    </div>
  )
}
