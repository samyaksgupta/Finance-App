import React, { useState, useEffect } from 'react';
import { Plus, Search, Download, Trash2, Shield, BarChart3, TrendingUp, TrendingDown, Wallet, Moon, Sun } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';

interface Transaction {
  id: number;
  amount: number;
  type: 'income' | 'expense';
  category: string;
  date: string;
  notes: string;
}

interface Summary {
  total_income: number;
  total_expenses: number;
  current_balance: number;
  category_breakdown: { category: string; total: number }[];
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';
const COLORS = ['#2563eb', '#22c55e', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4'];

function App() {
  const [userId, setUserId] = useState(1);
  const [role, setRole] = useState('admin');
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const pageSize = 10;
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    amount: '',
    type: 'expense',
    category: '',
    notes: ''
  });

  const fetchData = async () => {
    try {
      const headers = { 'X-User-ID': userId.toString() };
      const userRes = await fetch(`${API_BASE}/users/me`, { headers });
      const userData = await userRes.json();
      setRole(userData.role);

      const skip = page * pageSize;
      const transRes = await fetch(`${API_BASE}/transactions/?search=${search}&skip=${skip}&limit=${pageSize}`, { headers });
      const transData = await transRes.json();
      setTransactions(Array.isArray(transData) ? transData : []);

      const summaryRes = await fetch(`${API_BASE}/analytics/summary`, { headers });
      const summaryData = await summaryRes.json();
      setSummary(summaryData);
    } catch (err) {
      console.error('Fetch error:', err);
    }
  };

  useEffect(() => {
    fetchData();
  }, [userId, search, page]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(p => p === 'light' ? 'dark' : 'light');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/transactions/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-ID': userId.toString() },
        body: JSON.stringify({ ...formData, amount: parseFloat(formData.amount) })
      });
      if (res.ok) {
        setIsModalOpen(false);
        setFormData({ amount: '', type: 'expense', category: '', notes: '' });
        fetchData();
      }
    } catch (err) { alert('Error creating'); }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure?')) return;
    try {
      await fetch(`${API_BASE}/transactions/${id}`, {
        method: 'DELETE',
        headers: { 'X-User-ID': userId.toString() }
      });
      fetchData();
    } catch (err) { alert('Error deleting'); }
  };

  const handleExport = () => {
    window.open(`${API_BASE}/transactions/export/csv?x-user-id=${userId}`, '_blank');
  };

  // Calculate Gauge (Budget Health: Expense vs Income Ratio)
  const expenseRatio = summary && summary.total_income > 0 
    ? Math.min((summary.total_expenses / summary.total_income) * 100, 100)
    : 0;

  return (
    <div className="container">
      <header>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <BarChart3 size={32} color="#2563eb" />
          <h1>FinanceTracker Pro</h1>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button 
            onClick={toggleTheme} 
            className="btn" 
            style={{ 
              background: 'none', 
              border: '1px solid var(--border)', 
              display: 'flex', 
              alignItems: 'center', 
              padding: '0.4rem',
              borderRadius: '0.5rem',
              cursor: 'pointer'
            }}
          >
            {theme === 'light' ? <Moon size={18} color="#475569" /> : <Sun size={18} color="#fbbf24" />}
          </button>
          
          <span className={`role-badge role-${role}`}>
            <Shield size={14} style={{ marginRight: '4px' }} /> {role}
          </span>
          <select value={userId} onChange={(e) => { setUserId(parseInt(e.target.value)); setPage(0); }} className="btn">
            <option value={1}>Admin User</option>
            <option value={2}>Analyst User</option>
            <option value={3}>Viewer User</option>
          </select>
        </div>
      </header>

      {/* Visual Analytics Row */}
      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', marginBottom: '2rem' }}>
        {/* Gauge Card */}
        <div className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <h3 style={{ marginBottom: '1rem', color: '#64748b' }}>Expense/Income Ratio</h3>
          <div style={{ position: 'relative', width: '200px', height: '100px', overflow: 'hidden' }}>
            <svg width="200" height="200" style={{ transform: 'rotate(-90deg)' }}>
              <circle cx="100" cy="100" r="80" fill="none" stroke="#e2e8f0" strokeWidth="20" />
              <circle cx="100" cy="100" r="80" fill="none" stroke={expenseRatio > 80 ? '#ef4444' : '#22c55e'} 
                strokeWidth="20" strokeDasharray={`${(expenseRatio / 100) * 251} 502`} 
              />
            </svg>
            <div style={{ position: 'absolute', top: '70px', left: '0', width: '100%', textAlign: 'center', fontWeight: 'bold', fontSize: '1.5rem' }}>
              {Math.round(expenseRatio)}%
            </div>
          </div>
          <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '10px' }}>
            {expenseRatio < 50 ? 'Excellent Health' : expenseRatio < 85 ? 'Healthy Spending' : 'High Alert'}
          </p>
        </div>

        {/* Category Breakdown Graph */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem', color: '#64748b' }}>Spending Breakdown</h3>
          <div style={{ height: '200px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie 
                  data={summary?.category_breakdown || []} 
                  innerRadius={60} outerRadius={80} 
                  paddingAngle={5} dataKey="total" nameKey="category"
                >
                  {(summary?.category_breakdown || []).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Summary Bar Chart */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem', color: '#64748b' }}>Total Overview</h3>
          <div style={{ height: '200px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[
                { name: 'Income', amount: summary?.total_income || 0 },
                { name: 'Expense', amount: summary?.total_expenses || 0 }
              ]}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="amount" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="stat-label">Income</span><TrendingUp color="#22c55e" size={20}/></div>
          <div className="stat-value income">${summary?.total_income.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="stat-label">Expense</span><TrendingDown color="#ef4444" size={20}/></div>
          <div className="stat-value expense">${summary?.total_expenses.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="stat-label">Balance</span><Wallet color="#2563eb" size={20}/></div>
          <div className="stat-value" style={{ color: (summary?.current_balance || 0) >= 0 ? '#22c55e' : '#ef4444' }}>
            ${summary?.current_balance.toLocaleString()}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <div style={{ position: 'relative' }}>
              <Search size={18} style={{ position: 'absolute', left: '10px', top: '10px', color: '#64748b' }} />
              <input type="text" placeholder="Search..." className="search-bar" style={{ paddingLeft: '2.5rem' }} value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }} />
            </div>
            <button className="btn" onClick={handleExport} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Download size={18} /> Export
            </button>
          </div>
          {role === 'admin' && (
            <button className="btn btn-primary" onClick={() => setIsModalOpen(true)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Plus size={18} /> Add Record
            </button>
          )}
        </div>

        <table>
          <thead>
            <tr>
              <th>Date</th><th>Category</th><th>Notes</th><th>Type</th><th>Amount</th>{role === 'admin' && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {transactions.map(t => (
              <tr key={t.id}>
                <td>{new Date(t.date).toLocaleDateString()}</td>
                <td><span className="category-badge">{t.category}</span></td>
                <td>{t.notes || '-'}</td>
                <td><span style={{ color: t.type === 'income' ? '#22c55e' : '#ef4444', fontWeight: 600, fontSize: '0.875rem' }}>{t.type.toUpperCase()}</span></td>
                <td style={{ fontWeight: 600 }}>${t.amount.toLocaleString()}</td>
                {role === 'admin' && (
                  <td>
                    <button onClick={() => handleDelete(t.id)} style={{ color: '#ef4444', background: 'none', border: 'none', cursor: 'pointer' }}><Trash2 size={18} /></button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
        
        {/* Pagination */}
        <div style={{ padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #e2e8f0' }}>
          <span style={{ fontSize: '0.875rem', color: '#64748b' }}>Page {page + 1}</span>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn" onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} style={{ opacity: page === 0 ? 0.5 : 1 }}>Previous</button>
            <button className="btn" onClick={() => setPage(p => p + 1)} disabled={transactions.length < pageSize} style={{ opacity: transactions.length < pageSize ? 0.5 : 1 }}>Next</button>
          </div>
        </div>
      </div>

      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal">
            <h2 style={{ marginBottom: '1.5rem' }}>Add Record</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group"><label>Amount</label><input type="number" required value={formData.amount} onChange={e => setFormData({...formData, amount: e.target.value})} /></div>
              <div className="form-group">
                <label>Type</label>
                <select value={formData.type} onChange={e => setFormData({...formData, type: e.target.value as any})}>
                  <option value="expense">Expense</option><option value="income">Income</option>
                </select>
              </div>
              <div className="form-group"><label>Category</label><input type="text" required value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})} /></div>
              <div className="form-group"><label>Notes</label><input type="text" value={formData.notes} onChange={e => setFormData({...formData, notes: e.target.value})} /></div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                <button type="button" className="btn" onClick={() => setIsModalOpen(false)} style={{ flex: 1 }}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
