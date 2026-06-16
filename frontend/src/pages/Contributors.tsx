import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getContributors, createContributor } from '../lib/api';

export default function Contributors() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ name: '', email: '', country: '', language: '' });
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState('');

  const { data: contributors, isLoading } = useQuery({
    queryKey: ['contributors'],
    queryFn: getContributors,
  });

  console.log(contributors)

  const mutation = useMutation({
    mutationFn: createContributor,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contributors'] });
      setForm({ name: '', email: '', country: '', language: '' });
      setShowForm(false);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to create contributor');
    },
  });

  const handleSubmit = () => {
    if (!form.name || !form.email || !form.country || !form.language) {
      setError('All fields required');
      return;
    }
    mutation.mutate(form);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Contributors</h1>
        <button onClick={() => setShowForm(!showForm)} className="bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors">
          {showForm ? 'Cancel' : '+ Add Contributor'}
        </button>
      </div>

      {showForm && (
        <div className="bg-gray-800 rounded-xl p-5 border border-gray-700 space-y-3 max-w-md">
          {['name', 'email', 'country', 'language'].map(field => (
            <div key={field}>
              <label className="block text-xs text-gray-400 mb-1 capitalize">{field}</label>
              <input
                type={field === 'email' ? 'email' : 'text'}
                value={(form as any)[field]}
                onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 text-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
              />
            </div>
          ))}
          {error && <p className="text-red-400 text-xs">{error}</p>}
          <button onClick={handleSubmit} disabled={mutation.isPending} className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white text-sm font-medium py-2 rounded-lg transition-colors">
            {mutation.isPending ? 'Creating...' : 'Create Contributor'}
          </button>
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
      ) : (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700 text-gray-400 text-xs uppercase tracking-wide">
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">Country</th>
                <th className="text-left px-4 py-3">Language</th>
                <th className="text-left px-4 py-3">Submissions</th>
                <th className="text-left px-4 py-3">Pass Rate</th>
                <th className="text-left px-4 py-3">Quality Score</th>
              </tr>
            </thead>
            <tbody>
              {!contributors?.length && (
                <tr><td colSpan={6} className="text-center text-gray-500 py-12">No contributors yet</td></tr>
              )}
              {contributors?.map((c: any) => {
                const passRate = c.total_submissions > 0
                  ? ((c.passed_submissions / c.total_submissions) * 100).toFixed(1)
                  : '—';
                return (
                  <tr key={c.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors">
                    <td className="px-4 py-3">
                      <p className="text-white font-medium">{c.name}</p>
                      <p className="text-gray-500 text-xs">{c.email}</p>
                    </td>
                    <td className="px-4 py-3 text-gray-300">{c.country}</td>
                    <td className="px-4 py-3 text-gray-300">{c.language}</td>
                    <td className="px-4 py-3 text-gray-300">{c.total_submissions}</td>
                    <td className="px-4 py-3 text-gray-300">{passRate}{c.total_submissions > 0 ? '%' : ''}</td>
                    <td className="px-4 py-3">
                      <span className={`font-medium ${c.quality_score >= 80 ? 'text-green-400' : c.quality_score >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                        {c.quality_score?.toFixed(1)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
