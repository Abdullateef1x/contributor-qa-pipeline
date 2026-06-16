import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSubmissions } from '../lib/api';

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-gray-700 text-gray-300',
  processing: 'bg-blue-900 text-blue-300',
  passed: 'bg-green-900 text-green-300',
  failed: 'bg-red-900 text-red-300',
  flagged: 'bg-yellow-900 text-yellow-300',
};

export default function Submissions() {
  const [status, setStatus] = useState('');
  const [fileType, setFileType] = useState('');
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<any>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['submissions', status, fileType, page],
    queryFn: () => getSubmissions({ status: status || undefined, file_type: fileType || undefined, page }),
    refetchInterval: 3000,
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Submissions</h1>
        <div className="flex gap-3">
          <select
            value={status}
            onChange={e => { setStatus(e.target.value); setPage(1); }}
            className="bg-gray-800 border border-gray-600 text-gray-200 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="passed">Passed</option>
            <option value="failed">Failed</option>
            <option value="flagged">Flagged</option>
          </select>
          <select
            value={fileType}
            onChange={e => { setFileType(e.target.value); setPage(1); }}
            className="bg-gray-800 border border-gray-600 text-gray-200 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">All types</option>
            <option value="image">Image</option>
            <option value="audio">Audio</option>
            <option value="video">Video</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
      ) : (
        <>
          <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700 text-gray-400 text-xs uppercase tracking-wide">
                  <th className="text-left px-4 py-3">File</th>
                  <th className="text-left px-4 py-3">Type</th>
                  <th className="text-left px-4 py-3">Status</th>
                  <th className="text-left px-4 py-3">QA Score</th>
                  <th className="text-left px-4 py-3">Processing</th>
                  <th className="text-left px-4 py-3">Submitted</th>
                </tr>
              </thead>
              <tbody>
                {data?.submissions?.length === 0 && (
                  <tr>
                    <td colSpan={6} className="text-center text-gray-500 py-12">No submissions found</td>
                  </tr>
                )}
                {data?.submissions?.map((s: any) => (
                  <tr
                    key={s.id}
                    onClick={() => setSelected(s)}
                    className="border-b border-gray-700/50 hover:bg-gray-700/40 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-xs text-gray-300 max-w-[180px] truncate">{s.file_name}</td>
                    <td className="px-4 py-3 capitalize text-gray-300">{s.file_type}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[s.status] || ''}`}>
                        {s.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-300">{s.qa_score != null ? `${s.qa_score.toFixed(1)}/100` : '—'}</td>
                    <td className="px-4 py-3 text-gray-400">{s.processing_time_ms ? `${s.processing_time_ms}ms` : '—'}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{new Date(s.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex justify-between items-center text-sm text-gray-400">
            <span>{data?.total || 0} total submissions</span>
            <div className="flex gap-2">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 bg-gray-700 rounded disabled:opacity-40">Prev</button>
              <span className="px-3 py-1">Page {page}</span>
              <button onClick={() => setPage(p => p + 1)} disabled={!data?.submissions?.length || data.submissions.length < 20} className="px-3 py-1 bg-gray-700 rounded disabled:opacity-40">Next</button>
            </div>
          </div>
        </>
      )}

      {selected && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={() => setSelected(null)}>
          <div className="bg-gray-800 rounded-2xl p-6 max-w-lg w-full border border-gray-600" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-lg font-semibold text-white">Submission Detail</h2>
              <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-white text-xl leading-none">×</button>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-400">File</span><span className="text-gray-200 font-mono text-xs">{selected.file_name}</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Status</span><span className={`px-2 py-0.5 rounded-full text-xs ${STATUS_COLORS[selected.status]}`}>{selected.status}</span></div>
              <div className="flex justify-between"><span className="text-gray-400">QA Score</span><span className="text-gray-200">{selected.qa_score?.toFixed(1) ?? '—'}/100</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Processing time</span><span className="text-gray-200">{selected.processing_time_ms ? `${selected.processing_time_ms}ms` : '—'}</span></div>
              {selected.flag_reason && (
                <div className="mt-3 p-3 bg-yellow-900/30 border border-yellow-700 rounded-lg">
                  <p className="text-yellow-300 text-xs font-medium mb-1">Flag reason</p>
                  <p className="text-yellow-200 text-xs">{selected.flag_reason}</p>
                </div>
              )}
              {selected.ai_analysis && (
                <div className="mt-3 p-3 bg-blue-900/20 border border-blue-800 rounded-lg">
                  <p className="text-blue-300 text-xs font-medium mb-1">AI Analysis</p>
                  <p className="text-blue-100 text-xs leading-relaxed">{selected.ai_analysis}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
