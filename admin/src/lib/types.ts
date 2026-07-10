export interface DashboardStats {
  users_count: number;
  kyc_pending_count: number;
  cards_count: number;
  successful_topups_volume: string;
  settled_payments_volume: string;
  declined_payments_count: number;
  revenue_total: string;
  total_wallet_cached_balance: string;
}

export interface AdminUserListItem {
  id: string;
  phone: string;
  country_code: string;
  status: string;
  kyc_level: number;
  created_at: string;
}

export interface AdminKycPendingItem {
  id: string;
  user_id: string;
  level_requested: number;
  status: string;
  submitted_at: string | null;
}

export interface AdminTransactionItem {
  id: string;
  account_id: string;
  direction: string;
  amount: string;
  currency: string;
  created_at: string;
}

export interface AdminCardListItem {
  id: string;
  user_id: string;
  masked_pan: string;
  brand: string;
  status: string;
  displayed_currency: string;
  created_at: string;
}

export interface FxRate {
  base_currency: string;
  quote_currency: string;
  rate: string;
  created_at: string;
}

export interface LimitRule {
  id: string;
  limit_type: string;
  country_code: string | null;
  kyc_level: number | null;
  max_amount: string | null;
  max_count: number | null;
  is_active: boolean;
  created_at: string;
}

export interface FeeRule {
  id: string;
  fee_type: string;
  country_code: string | null;
  provider_name: string | null;
  kyc_level: number | null;
  rate: string | null;
  fixed_amount: string;
  is_active: boolean;
  created_at: string;
}

export interface AuditLogItem {
  id: string;
  actor_type: string;
  actor_id: string | null;
  action: string;
  target_type: string | null;
  target_id: string | null;
  context: Record<string, unknown>;
  ip_address: string | null;
  created_at: string;
}

export interface AdminAccount {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface ComplianceAlert {
  id: string;
  user_id: string;
  alert_type: string;
  severity: string;
  status: string;
  context: Record<string, unknown>;
  resolved_at: string | null;
  resolved_by: string | null;
  resolution_notes: string | null;
  created_at: string;
}

export interface RiskScore {
  user_id: string;
  score: number;
  alert_count: number;
  breakdown: Record<string, number>;
  window_days: number;
}

export interface SupportTicket {
  id: string;
  user_id: string;
  subject: string;
  category: string;
  status: string;
  created_at: string;
}

export interface SupportMessage {
  id: string;
  ticket_id: string;
  sender_type: string;
  sender_id: string;
  body: string;
  created_at: string;
}

export interface SupportTicketDetail {
  ticket: SupportTicket;
  messages: SupportMessage[];
}
