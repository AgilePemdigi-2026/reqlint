import axios from 'axios';
import { AuditResponse } from '../types/audit';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

// Otomatis pasang Bearer Token jika ada sesi aktif di browser
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    try {
      const raw = window.localStorage.getItem('reqlint.auth_session');
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed?.token) {
          config.headers.Authorization = `Bearer ${parsed.token}`;
        }
      }
    } catch {
      /* abaikan kegagalan baca storage */
    }
  }
  return config;
});

export interface BackendEnvelope<T = any> {
  status: 'success' | 'error';
  message: string;
  data?: T;
  error_code?: string;
  errors?: Array<{ field: string; message: string }>;
}

export interface AuthUserData {
  id_user: number;
  name: string;
  email: string;
  tanggal_registrasi?: string | null;
}

export interface LoginResponseData {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUserData;
}

export interface RegisterResponseData {
  id_user: number;
  name: string;
  email: string;
  tanggal_registrasi: string;
}

/** Mengekstrak pesan kesalahan dari respons error API backend */
export function extractApiError(err: unknown): { message: string; field?: string; errorCode?: string } {
  if (axios.isAxiosError(err)) {
    if (err.response?.data) {
      const data = err.response.data as BackendEnvelope;
      const firstError = data.errors?.[0];
      return {
        message: firstError?.message || data.message || 'Terjadi kesalahan pada server.',
        field: firstError?.field,
        errorCode: data.error_code,
      };
    }
    if (err.code === 'ECONNABORTED') {
      return { message: 'Koneksi ke server backend batas waktu (timeout).' };
    }
    if (!err.response) {
      return {
        message: 'Tidak dapat terhubung ke server backend (http://localhost:8000). Pastikan server FastAPI sedang berjalan.',
      };
    }
  }
  return { message: (err as Error)?.message || 'Terjadi kesalahan tidak terduga.' };
}

/* ---------------- Auth API ---------------- */

export const apiRegister = async (payload: {
  name: string;
  email: string;
  password: string;
  password_confirmation: string;
}): Promise<BackendEnvelope<RegisterResponseData>> => {
  const response = await apiClient.post<BackendEnvelope<RegisterResponseData>>('/auth/register', payload);
  return response.data;
};

export const apiLogin = async (payload: {
  email: string;
  password: string;
}): Promise<BackendEnvelope<LoginResponseData>> => {
  const response = await apiClient.post<BackendEnvelope<LoginResponseData>>('/auth/login', payload);
  return response.data;
};

export const apiGetMe = async (): Promise<BackendEnvelope<AuthUserData>> => {
  const response = await apiClient.get<BackendEnvelope<AuthUserData>>('/auth/me');
  return response.data;
};

/* ---------------- Health & Documents API ---------------- */

export const checkBackendHealth = async (): Promise<{ ok: boolean; version?: string }> => {
  try {
    const response = await apiClient.get('/health', { timeout: 2500 });
    return { ok: response.status === 200, version: '1.0.0' };
  } catch {
    return { ok: false };
  }
};

export interface DocumentUploadResponse {
  id_dokumen: number | null;
  nama_dokumen: string;
  ukuran_dokumen: number;
  jumlah_halaman: number;
  jumlah_karakter: number;
  truncated: boolean;
  teks: string;
}

export const uploadDocumentPdf = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<DocumentUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<BackendEnvelope<DocumentUploadResponse>>(
    '/documents/upload',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    }
  );

  return response.data.data!;
};

/* ---------------- Audits API (Tahap 2 Pipeline) ---------------- */

export interface CreateAuditPayload {
  konten: string;
  judul_klausul?: string;
  tipe_masukan?: string;
  id_dokumen?: number | null;
}

export interface BackendAuditFinding {
  id_temuan: number;
  story_index: number;
  kategori_cacat: string;
  severity: string;
  stage: number;
  iso_characteristic?: string;
  potongan_teks_asli: string;
  highlight_start: number;
  highlight_end: number;
  saran_perbaikan: string;
}

export interface BackendAcceptanceCriteria {
  given: string;
  when: string;
  then: string;
}

export interface BackendAIRecommendation {
  ai_rewrite: string;
  acceptance_criteria: BackendAcceptanceCriteria[];
}

export interface BackendScorecard {
  skor_awal: number;
  skor_kualitas: number;
  breakdown: {
    iso_29148?: Record<string, number | null>;
    /** P0/UI-48: null = kriteria belum dievaluasi (bukan lulus). */
    invest?: Record<string, number | null>;
  };
}

export interface BackendAuditDetail {
  id_audit: number;
  id_draf: number;
  judul_klausul: string;
  tipe_masukan: string;
  status_audit: 'PROCESSING' | 'COMPLETED' | 'PARTIAL' | 'FAILED';
  stage2_status: 'PENDING' | 'PROCESSING' | 'DONE' | 'FAILED' | 'SKIPPED';
  status_revisi: 'BELUM_DIREVISI' | 'SUDAH_DIREVISI';
  tanggal_audit: string;
  scorecard: BackendScorecard | null;
  ringkasan: {
    ambiguity: number;
    tidak_lengkap: number;
    weak_directive: number;
    passive_voice: number;
    total: number;
  };
  temuan: BackendAuditFinding[];
  rekomendasi_ai: BackendAIRecommendation | null;
  diff: {
    original: { teks: string; skor: number | null };
    revised: { teks: string; skor: number | null };
  };
  notifikasi: { tipe: string; message: string; aksi: string } | null;
}

export interface BackendAuditStatus {
  id_audit: number;
  status_audit: 'PROCESSING' | 'COMPLETED' | 'PARTIAL' | 'FAILED';
  stage2_status: string;
  stage1_ready: boolean;
}

export const apiCreateAudit = async (
  payload: CreateAuditPayload
): Promise<BackendEnvelope<{ id_audit: number; id_draf: number; status_audit: string; stage2_status: string; poll_url: string }>> => {
  const response = await apiClient.post<BackendEnvelope<{ id_audit: number; id_draf: number; status_audit: string; stage2_status: string; poll_url: string }>>(
    '/audits',
    payload
  );
  return response.data;
};

export interface BackendAuditHistoryItem {
  id_audit: number;
  id_draf: number;
  tanggal_audit: string;
  judul_klausul: string;
  skor_kualitas: number;
  status_revisi: string;
  status_audit: string;
}

export interface BackendAuditHistoryResponse {
  message: string;
  items: BackendAuditHistoryItem[];
  pagination: {
    page: number;
    limit: number;
    total_items: number;
    total_pages: number;
  };
  has_any_history: boolean;
}

export const apiGetAuditsHistory = async (params?: {
  q?: string;
  page?: number;
  limit?: number;
  min_score?: number;
  max_score?: number;
  status_revisi?: string;
}): Promise<BackendEnvelope<BackendAuditHistoryResponse>> => {
  const response = await apiClient.get<BackendEnvelope<BackendAuditHistoryResponse>>('/audits', {
    params,
  });
  return response.data;
};

export const apiGetAuditStatus = async (
  id: number | string
): Promise<BackendEnvelope<BackendAuditStatus>> => {
  const response = await apiClient.get<BackendEnvelope<BackendAuditStatus>>(`/audits/${id}/status`);
  return response.data;
};

export const apiGetAuditDetail = async (
  id: number | string
): Promise<BackendEnvelope<BackendAuditDetail>> => {
  const response = await apiClient.get<BackendEnvelope<BackendAuditDetail>>(`/audits/${id}`);
  return response.data;
};

export const apiReanalyzeAudit = async (
  id: number | string
): Promise<BackendEnvelope<{ id_audit: number; status_audit: string }>> => {
  const response = await apiClient.post<BackendEnvelope<{ id_audit: number; status_audit: string }>>(
    `/audits/${id}/reanalyze`
  );
  return response.data;
};

export const apiApplyAudit = async (
  id: number | string,
  terapkan: string[] = ['rewrite', 'acceptance_criteria']
): Promise<BackendEnvelope<{ id_audit: number; status_revisi: string; label: string; konten_revisi: string }>> => {
  const response = await apiClient.post<BackendEnvelope<{ id_audit: number; status_revisi: string; label: string; konten_revisi: string }>>(
    `/audits/${id}/apply`,
    { terapkan }
  );
  return response.data;
};

export const apiManualRevision = async (
  id: number | string,
  konten_revisi: string
): Promise<BackendEnvelope<{ id_audit: number; status_revisi: string; skor_kualitas: number; konten_revisi: string }>> => {
  const response = await apiClient.put<BackendEnvelope<{ id_audit: number; status_revisi: string; skor_kualitas: number; konten_revisi: string }>>(
    `/audits/${id}/revision`,
    { konten_revisi }
  );
  return response.data;
};

export const apiDownloadExport = async (
  id: number | string,
  format: 'pdf' | 'md' | 'json'
): Promise<{ blob: Blob; filename: string }> => {
  const response = await apiClient.get(`/audits/${id}/export?format=${format}`, {
    responseType: 'blob',
  });
  return { blob: response.data, filename: `audit-${id}.${format}` };
};

/* ---------------- Forgot / Reset Password API ---------------- */

export const apiForgotPassword = async (payload: {
  email: string;
}): Promise<BackendEnvelope> => {
  const response = await apiClient.post<BackendEnvelope>('/auth/forgot-password', payload);
  return response.data;
};

export const apiResetPassword = async (payload: {
  token: string;
  password: string;
  password_confirmation: string;
}): Promise<BackendEnvelope> => {
  const response = await apiClient.post<BackendEnvelope>('/auth/reset-password', payload);
  return response.data;
};

export const auditRequirement = async (
  requirementText: string,
  overrideLanguage?: string
): Promise<AuditResponse> => {
  const response = await apiClient.post<AuditResponse>(
    '/requirements/audit',
    {
      requirement_text: requirementText,
      override_language: overrideLanguage,
    },
    { timeout: 8000 }
  );
  return response.data;
};
