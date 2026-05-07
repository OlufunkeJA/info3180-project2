export async function requestJson(path, options = {}) {
    const headers = new Headers(options.headers || {})
    let body = options.body

    if (body && typeof body === 'object' && !(body instanceof FormData) && !(body instanceof URLSearchParams)) {
        headers.set('Content-Type', 'application/json')
        body = JSON.stringify(body)
    }
    console.log('Requesting', path, options)

    const response = await fetch(path, {
        ...options,
        body,
        headers,
        credentials: 'include'
    })

    const text = await response.text()
    let data = null

    if (text) {
        try {
            data = JSON.parse(text)
        } catch {
            data = text
        }
    }

    return { response, data }
}
