import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

function CarCard({ car }) {
  return (
    <Link to={`/cars/${car.id}`} className="car-card">
      <div className="car-img" style={{ backgroundImage: `url(${car.image_url})` }} />
      <div className="car-info">
        <div className="car-title">{car.brand} {car.model}</div>
        <div className="car-meta">{car.year} · {car.transmission} · {car.category}</div>
        <div className="car-price">{Number(car.price_per_day).toLocaleString('ru')} ₽/сут</div>
        <span className={`car-status ${car.public_status === 'Свободен' ? 'available' : 'busy'}`}>
          {car.public_status}
        </span>
      </div>
    </Link>
  )
}

export function Home() {
  const [cars, setCars] = useState([])
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.stats().then(setStats).catch(() => {})
    api.cars().then(d => setCars(d.slice(0, 6))).catch(() => {})
  }, [])

  return (
    <div className="page">
      <section className="hero">
        <h1>AutoNova Booking</h1>
        <p>Аренда автомобилей в Чите — быстро, удобно, надёжно</p>
        <Link to="/cars" className="btn-primary">Выбрать автомобиль</Link>
      </section>

      {stats && (
        <section className="stats">
          <div className="stat-card"><strong>{stats.cars}</strong><span>Автомобилей</span></div>
          <div className="stat-card"><strong>{stats.bookings}</strong><span>Бронирований</span></div>
          <div className="stat-card"><strong>{stats.clients}</strong><span>Клиентов</span></div>
        </section>
      )}

      <section className="section">
        <h2>Популярные автомобили</h2>
        <div className="cars-grid">
          {cars.map(car => <CarCard key={car.id} car={car} />)}
        </div>
        <div className="section-footer">
          <Link to="/cars" className="btn-outline">Все автомобили →</Link>
        </div>
      </section>
    </div>
  )
}
