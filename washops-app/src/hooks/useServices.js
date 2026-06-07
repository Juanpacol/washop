import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { getServices, createService, updateServiceStatus } from '../lib/db';

export function useServices(filters = {}) {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    try {
      setLoading(true);
      setError(null);
      const data = await getServices(filters);
      setServices(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();

    // Realtime: actualiza la lista cuando cambia un servicio en la BD
    const channel = supabase
      .channel('services-changes')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'services' }, load)
      .subscribe();

    return () => supabase.removeChannel(channel);
  }, [filters.status, filters.today]);

  async function addService(payload) {
    const service = await createService(payload);
    await load();
    return service;
  }

  async function changeStatus(id, newStatus, currentStatus) {
    const updated = await updateServiceStatus(id, newStatus, currentStatus);
    setServices(prev => prev.map(s => s.id === id ? { ...s, ...updated } : s));
    return updated;
  }

  return { services, loading, error, addService, changeStatus, reload: load };
}
