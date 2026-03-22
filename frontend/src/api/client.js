import axios from 'axios'

const BASE = 'http://localhost:8000/api/v1'

const api = axios.create({ baseURL: BASE, timeout: 30000 })

export async function getHealth() {
    const { data } = await api.get('/health')
    return data
}

export async function analyzeTicker(ticker) {
    const { data } = await api.get(`/analyze/${ticker}`)
    return data
}

export async function getSentiment(ticker) {
    const { data } = await api.get(`/sentiment/${ticker}`)
    return data
}

export async function getTopPicks() {
    const { data } = await api.get('/picks')
    return data
}

export async function getSummary() {
    const { data } = await api.get('/summary')
    return data
}