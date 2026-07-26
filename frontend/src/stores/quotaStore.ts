import { create } from 'zustand';
import type { QuotaStatusResponse } from '../api/types';

interface QuotaState {
    quota: QuotaStatusResponse | null;
    isLoading: boolean;
    error: string | null;
    fetchQuota: () => Promise<void>;
}

const mockQuota: QuotaStatusResponse = {
    date: new Date().toISOString().split('T')[0],
    queries: { used: 0, limit: 999999 },
    prescriptions: { used: 0, limit: 999999 },
    api_calls: { used: 0, limit: 999999 }
};

export const useQuotaStore = create<QuotaState>()((set) => ({
    quota: mockQuota,
    isLoading: false,
    error: null,
    fetchQuota: async () => {
        // Do nothing, we're fully local and free
        set({ quota: mockQuota, isLoading: false, error: null });
    },
}));
