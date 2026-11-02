import { useState, useEffect, useCallback } from 'react';

export default function useApi(apiFn, options = {}) {
  const { immediate = true, params = null } = options;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);
      try {
        const result = await apiFn(...args);
        setData(result);
        return result;
      } catch (err) {
        setError(err.message || 'An error occurred');
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFn]
  );

  useEffect(() => {
    if (immediate) {
      if (params !== null && params !== undefined) {
        execute(params);
      } else {
        execute();
      }
    }
  }, []);

  const retry = useCallback(() => {
    if (params !== null && params !== undefined) {
      execute(params);
    } else {
      execute();
    }
  }, [execute, params]);

  return { data, loading, error, execute, retry, setData };
}
