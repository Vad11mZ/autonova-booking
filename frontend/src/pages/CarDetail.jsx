import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'

export function CarDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [car, setCar] = useState(null)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [comment, setComment] = useState('')
  const [avail, setAvail] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    api.car(id).then(setCar).catch(() => navigate('/cars'))
  }, [id])

  const checkAvail = async () => {
    if (!startDate || !endDate) return
    try { setAvail(await api.availability(id, startDate, endDate)) }
    catch { setAvail(null) }
  }

  const handleBook = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.createBooking({ car_id: Number(id), start_date: startDate, end_date: endDate, comment })
      setSuccess('Заявка создана и ожидает подтверждения менеджера.')
    } catch (err) { setError(err.message) }
  }

  if (!car) return <div className="loading">Загрузка...</div>

  const today = new Date().toISOString().split('T')[0]

  return (
    <div className="page">
      <div className="car-detail">
        <div className="car-detail-img" style={{ backgroundImage: `url(${car.image_url})` }} />
        <div className="car-detail-body">
          <h1>{car.brand} {car.model} ({car.year})</h1>
          <div className="car-badges">
            {[car.category, car.transmission, car.fuel_type, `${car.seats} мест`].map(b => (
              <span key={b} className="badge">{b}</span>
            ))}
          </div>
          <p className="car-description">{car.description}</p>
          <div className="car-pricing">
            <span><strong>{Number(car.price_per_day).toLocaleString('ru')} ₽</strong> / сутки</span>
            <span>Залог: {Number(car.deposit).toLocaleString('ru')} ₽</span>
          </div>
          <div className="car-location">📍 {car.city}, {car.address}</div>

          {success && <div className="alert alert-success">{success} <Link to="/my-bookings">Мои бронирования</Link></div>}

          {!success && user?.role === 'CLIENT' && (
            <form className="booking-form" onSubmit={handleBook}>
              <h3>Забронировать</h3>
              <div className="form-row">
                <div className="form-group">
                  <label>Дата начала</label>
                  <input type="date" min={today} value={startDate} required className="input"
                    onChange={e => { setStartDate(e.target.value); setAvail(null) }} />
                </div>
                <div className="form-group">
                  <label>Дата возврата</label>
                  <input type="date" min={startDate || today} value={endDate} required className="input"
                    onChange={e => { setEndDate(e.target.value); setAvail(null) }} />
                </div>
              </div>
              <button type="button" className="btn-outline btn-sm" onClick={checkAvail} style={{ marginBottom: '0.75rem' }}>
                Проверить доступность
              </button>
              {avail && (
                <div className={`alert ${avail.available ? 'alert-success' : 'alert-error'}`}>
                  {avail.message}
                </div>
              )}
              <textarea value={comment} onChange={e => setComment(e.target.value)}
                placeholder="Комментарий (необязательно)" className="input textarea" />
              {error && <div className="alert alert-error">{error}</div>}
              <button type="submit" className="btn-primary" disabled={avail != null && !avail.available}>
                Оформить бронирование
              </button>
            </form>
          )}

          {!user && (
            <div className="alert alert-info" style={{ marginTop: '1rem' }}>
              <Link to="/login">Войдите</Link>, чтобы забронировать этот автомобиль.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
