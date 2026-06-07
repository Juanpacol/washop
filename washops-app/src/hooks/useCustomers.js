import { useEffect, useState } from 'react';
import { getCustomers, createCustomer, createVehicle } from '../lib/db';

export function useCustomers() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    try {
      setLoading(true);
      setError(null);
      const data = await getCustomers();
      setCustomers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function addCustomer(payload) {
    const customer = await createCustomer(payload);
    setCustomers(prev => [customer, ...prev]);
    return customer;
  }

  async function addVehicle(payload) {
    const vehicle = await createVehicle(payload);
    await load();
    return vehicle;
  }

  return { customers, loading, error, addCustomer, addVehicle, reload: load };
}
