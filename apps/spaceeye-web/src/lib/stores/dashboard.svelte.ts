import type { SavedAnalysis } from '$lib/api/types';

let _analyses = $state<SavedAnalysis[]>([]);
let _total = $state(0);
let _isLoading = $state(false);
let _selectedProduct = $state<string>('');
let _selectedCollection = $state<string>('');

const API_URL = import.meta.env.VITE_API_URL || '/api';

export const dashboardState = {
  get analyses() { return _analyses; },
  get total() { return _total; },
  get isLoading() { return _isLoading; },
  get selectedProduct() { return _selectedProduct; },
  set selectedProduct(v: string) { _selectedProduct = v; },
  get selectedCollection() { return _selectedCollection; },
  set selectedCollection(v: string) { _selectedCollection = v; },
};

export async function loadAnalyses() {
  _isLoading = true;
  try {
    const params = new URLSearchParams();
    if (_selectedProduct) params.set('product', _selectedProduct);
    if (_selectedCollection) params.set('collection', _selectedCollection);
    params.set('limit', '100');
    const resp = await fetch(`${API_URL}/analyses?${params}`);
    if (resp.ok) {
      const data = await resp.json();
      _analyses = data.analyses || [];
      _total = data.total || 0;
    }
  } catch { /* offline */ }
  _isLoading = false;
}

export async function deleteAnalysis(id: string) {
  try {
    await fetch(`${API_URL}/analyses/${id}`, { method: 'DELETE' });
    _analyses = _analyses.filter(a => a.id !== id);
    _total--;
  } catch { /* ignore */ }
}
