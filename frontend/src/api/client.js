import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export const healthCheck = () => api.get('/health')

export const uploadSignalFile = (fileOrPath, opts = {}) => {
  const form = new FormData()
  if (typeof fileOrPath === 'string') {
    form.append('file_path', fileOrPath)
  } else if (fileOrPath && fileOrPath.path) {
    form.append('file_path', fileOrPath.path)
  } else {
    form.append('file', fileOrPath)
  }
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

export const exportSigMF = (jobId) =>
  api.get(`/jobs/${jobId}/export/sigmf`)

export const getExportCsvUrl = (jobId) =>
  `/api/jobs/${jobId}/export/csv`

export default api

