import { useEffect, useState } from 'react';
import { getPayments, createPayment } from '../lib/db';

export function usePayments(filters = {}) {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    try {
      setLoading(true);
      setError(null);
      const data = await getPayments(filters);
      setPayments(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [filters.month]);

  async function addPayment(payload) {
    const payment = await createPayment(payload);
    setPayments(prev => [payment, ...prev]);
    return payment;
  }

  const totalRevenue = payments.reduce((sum, p) => sum + Number(p.amount), 0);

  return { payments, loading, error, addPayment, totalRevenue, reload: load };
}
