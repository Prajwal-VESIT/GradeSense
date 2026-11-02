export function formatNumber(n, decimals = 2) {
  if (n === null || n === undefined || isNaN(n)) return '—';
  return Number(n).toFixed(decimals);
}

export function formatPercentage(n, decimals = 1) {
  if (n === null || n === undefined || isNaN(n)) return '—';
  return `${(Number(n) * 100).toFixed(decimals)}%`;
}

export function getGradeCategory(grade) {
  if (grade === null || grade === undefined || isNaN(grade)) return 'Unknown';
  const g = Number(grade);
  if (g >= 16) return 'Excellent';
  if (g >= 14) return 'Good';
  if (g >= 12) return 'Satisfactory';
  if (g >= 10) return 'Sufficient';
  return 'Fail';
}

export function getGradeColor(grade) {
  if (grade === null || grade === undefined || isNaN(grade)) return 'text-slate-500';
  const g = Number(grade);
  if (g >= 16) return 'text-emerald-600';
  if (g >= 14) return 'text-blue-600';
  if (g >= 12) return 'text-amber-600';
  if (g >= 10) return 'text-orange-600';
  return 'text-rose-600';
}

export function getGradeBgColor(grade) {
  if (grade === null || grade === undefined || isNaN(grade)) return 'bg-slate-100 text-slate-700';
  const g = Number(grade);
  if (g >= 16) return 'bg-emerald-100 text-emerald-800';
  if (g >= 14) return 'bg-blue-100 text-blue-800';
  if (g >= 12) return 'bg-amber-100 text-amber-800';
  if (g >= 10) return 'bg-orange-100 text-orange-800';
  return 'bg-rose-100 text-rose-800';
}

export function getGradeCategoryBadgeClass(category) {
  const map = {
    Excellent: 'badge-green',
    Good: 'badge-blue',
    Satisfactory: 'badge-yellow',
    Sufficient: 'badge-orange',
    Fail: 'badge-red',
  };
  return map[category] || 'badge';
}

export function formatMetricName(name) {
  const map = {
    cv_mae: 'CV MAE',
    test_mae: 'Test MAE',
    test_mse: 'Test MSE',
    test_rmse: 'Test RMSE',
    test_r2: 'Test R²',
    mae: 'MAE',
    mse: 'MSE',
    rmse: 'RMSE',
    r2: 'R²',
    is_selected: 'Selected',
  };
  return map[name] || name.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}

export function getMetricTooltip(name) {
  const map = {
    mae: 'Mean Absolute Error — average absolute difference between predicted and actual grades.',
    test_mae: 'Mean Absolute Error on the hold-out test set.',
    cv_mae: 'Mean Absolute Error averaged across cross-validation folds.',
    mse: 'Mean Squared Error — average of squared differences; penalizes large errors.',
    test_mse: 'Mean Squared Error on the hold-out test set.',
    rmse: 'Root Mean Squared Error — square root of MSE; same unit as the grade.',
    test_rmse: 'Root Mean Squared Error on the hold-out test set.',
    r2: 'R² (Coefficient of Determination) — proportion of variance explained. 1 = perfect.',
    test_r2: 'R² on the hold-out test set. Higher is better; 1.0 = perfect prediction.',
  };
  return map[name] || '';
}
