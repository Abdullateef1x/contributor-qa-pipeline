import { useQuery } from '@tanstack/react-query';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { getStats } from '../lib/api';

const STATUS_COLORS: Record<string, string> = {
  passed: '#22c55e',
  failed: '#ef4444',
  flagged: '#f59e0b',
  pending: '#6b7280',
  processing: '#3b82f6',
};

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p className="text-3xl font-bold text-white">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: getStats,
    refetchInterval: 5000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (!stats) return <p className="text-gray-400">No data available.</p>;

  const pieData = [
    { name: 'Passed', value: stats.passed },
    { name: 'Failed', value: stats.failed },
    { name: 'Flagged', value: stats.flagged },
    { name: 'Pending', value: stats.pending },
    { name: 'Processing', value: stats.processing },
  ].filter(d => d.value > 0);

  const barData = [
    { name: 'Passed', count: stats.passed, fill: STATUS_COLORS.passed },
    { name: 'Failed', count: stats.failed, fill: STATUS_COLORS.failed },
    { name: 'Flagged', count: stats.flagged, fill: STATUS_COLORS.flagged },
    { name: 'Pending', count: stats.pending, fill: STATUS_COLORS.pending },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">QA Overview</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Submissions" value={stats.total} />
        <StatCard label="Pass Rate" value={`${stats.pass_rate}%`} sub={`${stats.passed} passed`} />
        <StatCard label="Avg QA Score" value={`${stats.avg_qa_score}/100`} />
        <StatCard label="Avg Processing" value={`${Math.round(stats.avg_processing_time_ms)}ms`} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
          <h2 className="text-sm font-medium text-gray-400 mb-4">Status Distribution</h2>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                  {pieData.map((entry) => (
                    <Cell key={entry.name} fill={STATUS_COLORS[entry.name.toLowerCase()] || '#6b7280'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-sm text-center py-16">No submissions yet</p>
          )}
        </div>

        <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
          <h2 className="text-sm font-medium text-gray-400 mb-4">Submissions by Status</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={barData}>
              <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {barData.map((entry) => (
                  <Cell key={entry.name} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
