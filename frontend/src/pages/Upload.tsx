import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getContributors, uploadSubmission } from '../lib/api';

export default function Upload() {
  const queryClient = useQueryClient();
  const [contributorId, setContributorId] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [dragOver, setDragOver] = useState(false);

  const { data: contributors } = useQuery({
    queryKey: ['contributors'],
    queryFn: getContributors,
  });

  const mutation = useMutation({
    mutationFn: () => uploadSubmission(contributorId, file!),
    onSuccess: (data) => {
      setResult(data);
      setFile(null);
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
    onError: (err: any) => {
      setResult({ error: err.response?.data?.detail || 'Upload failed' });
    },
  });

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  }, []);

  return (
    <div className="max-w-xl space-y-6">
      <h1 className="text-2xl font-bold text-white">Upload Submission</h1>

      <div className="space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Contributor</label>
          <select
            value={contributorId}
            onChange={e => setContributorId(e.target.value)}
            className="w-full bg-gray-800 border border-gray-600 text-gray-200 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Select a contributor</option>
            {contributors?.map((c: any) => (
              <option key={c.id} value={c.id}>{c.name} — {c.country}</option>
            ))}
          </select>
        </div>

        <div
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-10 text-center transition-colors ${
            dragOver ? 'border-blue-500 bg-blue-900/10' : 'border-gray-600 hover:border-gray-500'
          }`}
        >
          {file ? (
            <div className="space-y-1">
              <p className="text-green-400 font-medium">{file.name}</p>
              <p className="text-gray-500 text-sm">{(file.size / 1024).toFixed(1)} KB · {file.type}</p>
              <button onClick={() => setFile(null)} className="text-xs text-red-400 hover:text-red-300 mt-2">Remove</button>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-gray-400">Drag & drop file here</p>
              <p className="text-gray-600 text-sm">or</p>
              <label className="cursor-pointer text-blue-400 hover:text-blue-300 text-sm underline">
                Browse files
                <input type="file" className="hidden" accept="image/*,audio/*,video/*" onChange={e => setFile(e.target.files?.[0] || null)} />
              </label>
              <p className="text-gray-600 text-xs mt-2">Supported: JPEG, PNG, WebP, MP3, WAV, OGG, MP4</p>
            </div>
          )}
        </div>

        <button
          onClick={() => mutation.mutate()}
          disabled={!contributorId || !file || mutation.isPending}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-lg transition-colors"
        >
          {mutation.isPending ? 'Uploading & queuing QA...' : 'Upload & Run QA'}
        </button>
      </div>

      {result && (
        <div className={`p-4 rounded-xl border ${result.error ? 'bg-red-900/20 border-red-700' : 'bg-green-900/20 border-green-700'}`}>
          {result.error ? (
            <p className="text-red-300 text-sm">{result.error}</p>
          ) : (
            <div className="space-y-1 text-sm">
              <p className="text-green-300 font-medium">✓ Submission received</p>
              <p className="text-gray-400 font-mono text-xs">{result.submission_id}</p>
              <p className="text-gray-400 text-xs">{result.message}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
