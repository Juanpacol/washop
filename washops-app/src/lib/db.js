import { supabase } from './supabase';
import { SERVICE_PRICES, VALID_TRANSITIONS } from '../shared/utils/constants';

// ─── AUTH ────────────────────────────────────────────────
export async function signIn(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data.session;
}

export async function signOut() {
  await supabase.auth.signOut();
}

export function onAuthStateChange(callback) {
  const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
    callback(session);
  });
  return () => subscription.unsubscribe();
}

// ─── CLIENTES ────────────────────────────────────────────
export async function getCustomers() {
  const { data, error } = await supabase
    .from('customers')
    .select('*, vehicles(plate)')
    .order('created_at', { ascending: false });
  if (error) throw error;
  return data;
}

export async function createCustomer({ name, phone, email, type }) {
  const { data, error } = await supabase
    .from('customers')
    .insert({ name, phone, email, type })
    .select()
    .single();
  if (error) throw error;
  return data;
}

// ─── VEHÍCULOS ───────────────────────────────────────────
export async function createVehicle({ customer_id, plate, brand, model, color }) {
  const { data, error } = await supabase
    .from('vehicles')
    .insert({ customer_id, plate, brand, model, color })
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function getVehicles() {
  const { data, error } = await supabase
    .from('vehicles')
    .select('*, customers(name)')
    .order('created_at', { ascending: false });
  if (error) throw error;
  return data;
}

// ─── SERVICIOS ───────────────────────────────────────────

export async function getServices(filters = {}) {
  let query = supabase
    .from('services')
    .select('*, vehicles(plate, brand, model, color), customers(name)')
    .order('created_at', { ascending: false });

  if (filters.status) query = query.eq('status', filters.status);
  if (filters.today) {
    const start = new Date(); start.setHours(0, 0, 0, 0);
    const end   = new Date(); end.setHours(23, 59, 59, 999);
    query = query.gte('created_at', start.toISOString()).lte('created_at', end.toISOString());
  }

  const { data, error } = await query;
  if (error) throw error;
  return data;
}

export async function createService({ vehicle_id, customer_id, type }) {
  const { data, error } = await supabase
    .from('services')
    .insert({ vehicle_id, customer_id, type, price: SERVICE_PRICES[type], status: 'PENDING' })
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function updateServiceStatus(id, newStatus, currentStatus) {
  const allowed = VALID_TRANSITIONS[currentStatus] || [];
  if (!allowed.includes(newStatus)) {
    throw new Error(`Transición no permitida: ${currentStatus} → ${newStatus}`);
  }
  const extra = {};
  if (newStatus === 'IN_PROGRESS') extra.started_at = new Date().toISOString();
  if (newStatus === 'COMPLETED')   extra.completed_at = new Date().toISOString();

  const { data, error } = await supabase
    .from('services')
    .update({ status: newStatus, ...extra })
    .eq('id', id)
    .select()
    .single();
  if (error) throw error;
  return data;
}

// ─── PAGOS ───────────────────────────────────────────────
export async function getPayments(filters = {}) {
  let query = supabase
    .from('payments')
    .select('*, services(type, vehicles(plate), customers(name))')
    .order('created_at', { ascending: false });

  if (filters.month) {
    const [year, month] = filters.month.split('-');
    const start = new Date(year, month - 1, 1).toISOString();
    const end   = new Date(year, month, 0, 23, 59, 59).toISOString();
    query = query.gte('created_at', start).lte('created_at', end);
  }

  const { data, error } = await query;
  if (error) throw error;
  return data;
}

export async function createPayment({ service_id, method, amount }) {
  const { data: service } = await supabase
    .from('services')
    .select('status')
    .eq('id', service_id)
    .single();

  if (service?.status !== 'COMPLETED') {
    throw new Error('Solo se puede cobrar un servicio completado');
  }

  const { data, error } = await supabase
    .from('payments')
    .insert({ service_id, method, amount, status: 'CONFIRMED' })
    .select()
    .single();
  if (error) throw error;
  return data;
}
