import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

export async function getStats() {
  const { data } = await api.get('/api/submissions/stats/overview');
  return data;
}

export async function getSubmissions(params?: {
  status?: string;
  file_type?: string;
  page?: number;
  page_size?: number;
}) {
  const { data } = await api.get('/api/submissions/', { params });
  return data;
}

export async function getSubmission(id: string) {
  const { data } = await api.get(`/api/submissions/${id}`);
  return data;
}

export async function uploadSubmission(contributorId: string, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post(
    `/api/submissions/upload?contributor_id=${contributorId}`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return data;
}

export async function getContributors() {
  const { data } = await api.get('/api/contributors/');
  return data;
}

export async function createContributor(payload: {
  name: string;
  email: string;
  country: string;
  language: string;
}) {
  const { data } = await api.post('/api/contributors/', payload);
  return data;
}
