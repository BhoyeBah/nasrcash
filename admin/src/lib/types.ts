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
