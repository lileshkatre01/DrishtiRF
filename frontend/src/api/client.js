import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export const healthCheck = () => api.get('/health')

export const uploadSignalFile = (file, opts = {}) => {
  const form = new FormData()
  form.append('file', file)
  if (opts.sampleRate)    form.append('sample_rate_override', opts.sampleRate)
  if (opts.centerFreq)    form.append('center_freq_override', opts.centerFreq)
  if (opts.formatOverride) form.append('format_override', opts.formatOverride)
  return api.post('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: opts.onProgress,
  })
}

export const createJob = (captureId) =>
  api.post('/jobs', { capture_id: captureId })

export const getJob = (jobId) =>
  api.get(`/jobs/${jobId}`)

export const getJobResults = (jobId) =>
  api.get(`/jobs/${jobId}/results`)

export const getJobFrames = (jobId) =>
  api.get(`/jobs/${jobId}/frames`)

export const getCaptureSpectrum = (captureId) =>
  api.get(`/captures/${captureId}/spectrum`)

export default api
