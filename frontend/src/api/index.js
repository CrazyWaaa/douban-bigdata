import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 10000
})

client.interceptors.response.use(
  (r) => r.data,
  (err) => {
    console.error('API error', err)
    return Promise.reject(err)
  }
)

export const api = {
  health: () => client.get('/health'),
  dashboard: () => client.get('/dashboard/summary'),
  byGenre: () => client.get('/movies/count_by_genre'),
  byCountry: () => client.get('/movies/count_by_country'),
  byYear: () => client.get('/movies/count_by_year'),
  topRated: (limit = 50) => client.get('/movies/top_rated', { params: { limit } }),
  detail: (id) => client.get(`/movies/${id}`)
}

export default client