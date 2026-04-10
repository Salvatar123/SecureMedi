import { useState } from 'react';
import { NextPage } from 'next';
import { Header } from '../components/Header';
import { apiClient } from '../lib/api';

const RequestAccessPage: NextPage = () => {
  const [accessKey, setAccessKey] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleRequestKey = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.requestAccessKey();
      if (response.success && response.key) {
        setAccessKey(response.key);
      } else {
        setError(response.message || 'Failed to request access key.');
      }
    } catch (err) {
      setError('An unexpected error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white shadow-md rounded-lg p-6">
            <h1 className="text-2xl font-bold mb-4">Request Access Key</h1>
            <p className="text-gray-600 mb-6">
              Click the button below to generate a new, random access key.
            </p>
            <button
              onClick={handleRequestKey}
              disabled={isLoading}
              className="w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isLoading ? 'Generating...' : 'Generate Access Key'}
            </button>
            {error && <p className="mt-4 text-red-500">{error}</p>}
            {accessKey && (
              <div className="mt-6 p-4 bg-gray-100 rounded-md">
                <h2 className="text-lg font-semibold">Your New Access Key:</h2>
                <p className="mt-2 text-green-700 font-mono bg-gray-200 p-2 rounded">
                  {accessKey}
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default RequestAccessPage;
