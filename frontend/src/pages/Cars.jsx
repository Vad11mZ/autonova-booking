import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export function Cars() {
  const [cars, setCars] = useState([])
  const [categories, setCategories] = useState([])
  const [q, setQ] = useState('')
  const [category, setCategory] = useState('')
  const [transmission, setTransmission] = useState('')
  const [loading, setLoading] = useState(false)

  const load = async (params = {}) => {
    setLoading(true)
    try { setCars(await api.cars(params)) }
    finally { setLoading(false) }
  }

  useEffect(() => {
    api.categories().then(setCategories)
    load()
  }, [])

  const submit = (e) => {
    e.preventDefault()
    const p = {}
    if (q) p.q = q
    if (category) p.category = category
    if (transmission) p.transmission = transmission
    load(p)
  }

  return (
    <div className="page">
      <h1>Автомобили</h1>

      <form className="filters" onSubmit={submit}>
        <input value={q} onChange={e => setQ(e.target.value)}
          placeholder="Марка или модель" className="input filter-input" />
        <select value={category} onChange={e => setCategory(e.target.value)} className="select">
          <option value="">Все классы</option>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={transmission} onChange={e => setTransmission(e.target.value)} className="select">
          <option value="">Все КПП</option>
          <option value="AT">Автомат</option>
          <option value="MT">Механика</option>
          <option value="ROBOT">Робот</option>
        </select>
        <button type="submit" className="btn-primary">Найти</button>
      </form>

      {loading ? <div className="loading">Загрузка...</div> : (
        <div className="cars-grid">
          {cars.map(car => (
            <Link to={`/cars/${car.id}`} key={car.id} className="car-card">
              <div className="car-img" style={{ backgroundImage: `url(${car.image_url})` }} />
              <div className="car-info">
                <div className="car-title">{car.brand} {car.model}</div>
                <div className="car-meta">{car.year} · {car.transmission} · {car.fuel_type}</div>
                <div className="car-price">{Number(car.price_per_day).toLocaleString('ru')} ₽/сут</div>
                <span className={`car-status ${car.public_status === 'Свободен' ? 'available' : 'busy'}`}>
                  {car.public_status}
                </span>
              </div>
            </Link>
          ))}
          {cars.length === 0 && <p className="empty">Автомобили не найдены.</p>}
        </div>
      )}
    </div>
  )
}
