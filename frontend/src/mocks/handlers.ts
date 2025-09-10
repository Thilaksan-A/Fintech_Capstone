import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/test-mock', () => {
    return HttpResponse.json({
      desc: '[/api/test-mock] The mock server is working',
      time: new Date().toISOString(),
    })
  }),
]