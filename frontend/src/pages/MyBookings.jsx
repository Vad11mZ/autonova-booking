import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export function MyBookings() {
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.myBookings().then(setBookings).finally(() => setLoading(false))
  }

  useEffect(load, [])

  const cancel = async (id) => {
    if (!confirm('Отменить бронирование?')) return
    try { await api.cancelBooking(id); load() }
    catch (err) { alert(err.message) }
  }

  if (loading) return <div className="loading">Загрузка...</div>

  return (
    <div className="page">
      <h1>Мои бронирования</h1>
      {bookings.length === 0 ? (
        <p className="empty">Нет бронирований. <Link to="/cars">Выбрать автомобиль</Link></p>
      ) : (
        <div className="bookings-list">
          {bookings.map(b => (
            <div key={b.id} className="booking-card">
              <div className="booking-header">
                <strong>#{b.id} — {b.car}</strong>
                <span className={`status-badge status-${b.status.toLowerCase()}`}>{b.status_display}</span>
              </div>
              <div className="booking-dates">{b.start_date} → {b.end_date}</div>
              <div className="booking-price">Итого: {Number(b.total_price).toLocaleString('ru')} ₽</div>
              {b.comment && <div className="booking-comment">Ваш комментарий: {b.comment}</div>}
              {b.manager_comment && <div className="booking-comment">Менеджер: {b.manager_comment}</div>}
              {['PENDING', 'CONFIRMED'].includes(b.status) && (
                <button onClick={() => cancel(b.id)} className="btn-danger btn-sm" style={{ marginTop: '0.5rem' }}>
                  Отменить
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
