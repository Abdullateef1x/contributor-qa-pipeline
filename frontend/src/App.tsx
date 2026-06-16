import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './pages/Dashboard';
import Submissions from './pages/Submissions';
import Upload from './pages/Upload';
import Contributors from './pages/Contributors';

const queryClient = new QueryClient();

function Nav() {
  const link = ({ isActive }: { isActive: boolean }) =>
    `px-4 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-700'
    }`;

  return (
    <nav className="bg-gray-900 border-b border-gray-700 px-6 py-3 flex items-center gap-6">
      <span className="text-white font-bold text-lg mr-4">Hub QA Pipeline</span>
      <NavLink to="/" end className={link}>Dashboard</NavLink>
      <NavLink to="/submissions" className={link}>Submissions</NavLink>
      <NavLink to="/upload" className={link}>Upload</NavLink>
      <NavLink to="/contributors" className={link}>Contributors</NavLink>
    </nav>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-950 text-gray-100">
          <Nav />
          <main className="p-6 max-w-7xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/submissions" element={<Submissions />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/contributors" element={<Contributors />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
