import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { getApiClient } from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';

interface Doctor {
  id: string;
  wallet_address: string;
  name: string;
  email?: string;
  specialization?: string;
  hospital?: string;
  status: string;
  registered_on: string;
}

interface Patient {
  id: string;
  patient_id: string;
  wallet_address?: string;
  name?: string;
  email?: string;
  date_of_birth?: string;
  emergency_contact?: string;
  assigned_doctor_id?: string | null;
  assigned_doctor_name?: string | null;
  status: string;
  registered_on: string;
}

interface DoctorWalletDetails {
  success: boolean;
  doctor?: {
    id?: string;
    name?: string;
    email?: string;
  };
  wallet?: {
    address?: string;
    private_key?: string | null;
    account_index?: number | null;
    assigned_at?: string | null;
    user_type?: string;
  };
  message?: string;
}

interface PatientWalletDetails {
  success: boolean;
  patient?: {
    id?: string;
    patient_id?: string;
    name?: string;
    email?: string;
  };
  wallet?: {
    address?: string;
    private_key?: string | null;
    account_index?: number | null;
    assigned_at?: string | null;
    user_type?: string;
  };
  message?: string;
}

interface EmergencySession {
  session_id: string;
  doctor_address: string;
  patient_id: string;
  status: 'PENDING' | 'ACTIVE' | 'EXPIRED' | 'CLOSED' | 'REJECTED';
  severity?: 'INFO' | 'WARNING' | 'CRITICAL';
  reason?: string;
  requested_at?: string;
  activated_at?: string;
  expires_at?: string;
  closed_at?: string;
}

export default function AdminDashboard() {
  const { isAuthenticated, userRole } = useAuthStore();
  const isAdminRole = String(userRole || '').toUpperCase() === 'ADMIN';
  const [activeTab, setActiveTab] = useState<'doctors' | 'patients' | 'emergency'>('doctors');
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItem, setSelectedItem] = useState<Doctor | Patient | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [formData, setFormData] = useState<any>({});
  const [generatedCredentials, setGeneratedCredentials] = useState<any>(null);
  const [availableWallets, setAvailableWallets] = useState<any>(null);
  const [doctorWalletDetails, setDoctorWalletDetails] = useState<DoctorWalletDetails | null>(null);
  const [isWalletModalOpen, setIsWalletModalOpen] = useState(false);
  const [patientWalletDetails, setPatientWalletDetails] = useState<PatientWalletDetails | null>(null);
  const [isPatientWalletModalOpen, setIsPatientWalletModalOpen] = useState(false);
  const [walletLoading, setWalletLoading] = useState(false);
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [selectedPatientForAssign, setSelectedPatientForAssign] = useState<Patient | null>(null);
  const [selectedDoctorIdForAssign, setSelectedDoctorIdForAssign] = useState('');
  const [assignLoading, setAssignLoading] = useState(false);
  const [emergencySessions, setEmergencySessions] = useState<EmergencySession[]>([]);
  const [emergencyLoading, setEmergencyLoading] = useState(false);
  const [emergencyError, setEmergencyError] = useState<string | null>(null);

  const client = getApiClient();

  // ==================== WALLET MANAGEMENT ====================

  const fetchAvailableWallets = async () => {
    try {
      const response = await client.get('/api/admin/wallets/available');
      if (response.data.success) {
        setAvailableWallets(response.data);
      }
    } catch (error) {
      console.error('Error fetching wallets:', error);
    }
  };

  const generateWallet = async (userId: string, userType: 'doctor' | 'patient') => {
    try {
      const response = await client.post(`/api/admin/wallets/generate?user_id=${userId}&user_type=${userType}`);
      if (response.data.success) {
        setGeneratedCredentials(response.data);
        toast.success('Wallet generated! Copy the private key securely.');
        fetchAvailableWallets();
        return response.data;
      } else {
        toast.error(response.data.message || 'Failed to generate wallet');
        return null;
      }
    } catch (error: any) {
      toast.error('Error generating wallet');
      console.error(error);
      return null;
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard`);
  };

  const fetchEmergencySessions = async () => {
    if (!isAuthenticated || !isAdminRole) {
      setEmergencySessions([]);
      setEmergencyError('Only ADMIN users can view emergency history.');
      return;
    }

    setEmergencyLoading(true);
    try {
      const params = new URLSearchParams();
      params.set('limit', '1000');
      const response = await client.get(`/api/admin/emergency/sessions?${params.toString()}`);
      if (response.data?.success) {
        setEmergencySessions(response.data.data || []);
        setEmergencyError(null);
      } else {
        const message = response.data?.message || 'Failed to load emergency sessions';
        setEmergencyError(message);
        toast.error(message);
      }
    } catch (error: any) {
      const message = error?.response?.data?.detail || error?.message || 'Error loading emergency sessions';
      setEmergencyError(message);
      toast.error(message);
    } finally {
      setEmergencyLoading(false);
    }
  };

  useEffect(() => {
    fetchAvailableWallets();
  }, []);

  useEffect(() => {
    if (activeTab !== 'emergency') {
      return;
    }

    if (isAuthenticated && isAdminRole) {
      fetchEmergencySessions();
    } else {
      setEmergencySessions([]);
    }
  }, [activeTab, isAuthenticated, isAdminRole]);

  useEffect(() => {
    if (activeTab !== 'emergency' || !isAuthenticated || !isAdminRole) {
      return;
    }

    const intervalId = setInterval(() => {
      fetchEmergencySessions();
    }, 5000);

    return () => clearInterval(intervalId);
  }, [activeTab, isAuthenticated, isAdminRole]);

  const fetchDoctors = async () => {
    setLoading(true);
    try {
      const response = await client.get('/api/admin/registry/doctors');
      if (response.data.success) {
        setDoctors(response.data.data || []);
      } else {
        toast.error('Failed to fetch doctors');
      }
    } catch (error) {
      toast.error('Error fetching doctors');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const searchDoctors = async () => {
    if (!searchQuery.trim()) {
      fetchDoctors();
      return;
    }

    setLoading(true);
    try {
      const response = await client.get(`/api/admin/registry/doctors/search?q=${searchQuery}`);
      if (response.data.success) {
        setDoctors(response.data.data || []);
      } else {
        toast.error('Search failed');
      }
    } catch (error) {
      toast.error('Error searching doctors');
    } finally {
      setLoading(false);
    }
  };

  const addDoctor = async () => {
    if (!formData.name) {
      toast.error('Name is required');
      return;
    }

    setLoading(true);
    try {
      const response = await client.post('/api/admin/registry/doctors', formData);
      if (response.data.success) {
        // Store generated credentials if available
        if (response.data.private_key) {
          setGeneratedCredentials({
            user_type: 'doctor',
            wallet_address: response.data.wallet_address,
            private_key: response.data.private_key,
            credentials_message: response.data.credentials_message,
            name: formData.name
          });
        }
        toast.success('Doctor added successfully');
        setFormData({});
        setIsFormOpen(false);
        fetchDoctors();
        fetchAvailableWallets();
      } else {
        toast.error(response.data.error || 'Failed to add doctor');
      }
    } catch (error) {
      toast.error('Error adding doctor');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const updateDoctor = async () => {
    if (!selectedItem) return;

    setLoading(true);
    try {
      const response = await client.put(`/api/admin/registry/doctors/${selectedItem.id}`, formData);
      if (response.data.success) {
        toast.success('Doctor updated successfully');
        setFormData({});
        setIsFormOpen(false);
        setSelectedItem(null);
        fetchDoctors();
      } else {
        toast.error(response.data.error || 'Failed to update doctor');
      }
    } catch (error) {
      toast.error('Error updating doctor');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const deleteDoctor = async (id: string) => {
    if (!confirm('Are you sure you want to delete this doctor?')) return;

    setLoading(true);
    try {
      const response = await client.delete(`/api/admin/registry/doctors/${id}`);
      if (response.data.success) {
        toast.success('Doctor deleted successfully');
        fetchDoctors();
      } else {
        toast.error(response.data.error || 'Failed to delete doctor');
      }
    } catch (error) {
      toast.error('Error deleting doctor');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const exportDoctorsCSV = async () => {
    try {
      const response = await client.get('/api/admin/registry/doctors/export/csv', {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'doctors_export.csv');
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      toast.success('Doctors exported successfully');
    } catch (error) {
      toast.error('Error exporting doctors');
      console.error(error);
    }
  };

  const openDoctorWalletModal = async (doctor: Doctor) => {
    setWalletLoading(true);
    try {
      const response = await client.get(`/api/admin/registry/doctors/${doctor.id}/wallet`);
      if (response.data.success) {
        setDoctorWalletDetails(response.data);
        setIsWalletModalOpen(true);
      } else {
        toast.error(response.data.message || 'Failed to load wallet details');
      }
    } catch (error: any) {
      toast.error(error?.message || 'Error loading wallet details');
      console.error(error);
    } finally {
      setWalletLoading(false);
    }
  };

  const openPatientWalletModal = async (patient: Patient) => {
    setWalletLoading(true);
    try {
      const response = await client.get(`/api/admin/registry/patients/${patient.id}/wallet`);
      if (response.data.success) {
        setPatientWalletDetails(response.data);
        setIsPatientWalletModalOpen(true);
      } else {
        toast.error(response.data.message || 'Failed to load patient wallet details');
      }
    } catch (error: any) {
      toast.error(error?.message || 'Error loading patient wallet details');
      console.error(error);
    } finally {
      setWalletLoading(false);
    }
  };

  // ==================== PATIENTS ====================

  const fetchPatients = async () => {
    setLoading(true);
    try {
      const response = await client.get('/api/admin/registry/patients');
      if (response.data.success) {
        setPatients(response.data.data || []);
      } else {
        toast.error('Failed to fetch patients');
      }
    } catch (error) {
      toast.error('Error fetching patients');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const searchPatients = async () => {
    if (!searchQuery.trim()) {
      fetchPatients();
      return;
    }

    setLoading(true);
    try {
      const response = await client.get(`/api/admin/registry/patients/search?q=${searchQuery}`);
      if (response.data.success) {
        setPatients(response.data.data || []);
      } else {
        toast.error('Search failed');
      }
    } catch (error) {
      toast.error('Error searching patients');
    } finally {
      setLoading(false);
    }
  };

  const addPatient = async () => {
    if (!formData.patient_id) {
      toast.error('Patient ID is required');
      return;
    }

    setLoading(true);
    try {
      const response = await client.post('/api/admin/registry/patients', formData);
      if (response.data.success) {
        // Store generated credentials if available
        if (response.data.private_key) {
          setGeneratedCredentials({
            user_type: 'patient',
            wallet_address: response.data.wallet_address,
            private_key: response.data.private_key,
            credentials_message: response.data.credentials_message,
            patient_id: formData.patient_id
          });
        }
        toast.success('Patient added successfully');
        setFormData({});
        setIsFormOpen(false);
        fetchPatients();
        fetchAvailableWallets();
      } else {
        toast.error(response.data.error || 'Failed to add patient');
      }
    } catch (error) {
      toast.error('Error adding patient');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const updatePatient = async () => {
    if (!selectedItem) return;

    setLoading(true);
    try {
      const response = await client.put(`/api/admin/registry/patients/${selectedItem.id}`, formData);
      if (response.data.success) {
        toast.success('Patient updated successfully');
        setFormData({});
        setIsFormOpen(false);
        setSelectedItem(null);
        fetchPatients();
      } else {
        toast.error(response.data.error || 'Failed to update patient');
      }
    } catch (error) {
      toast.error('Error updating patient');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const deletePatient = async (id: string) => {
    if (!confirm('Are you sure you want to delete this patient?')) return;

    setLoading(true);
    try {
      const response = await client.delete(`/api/admin/registry/patients/${id}`);
      if (response.data.success) {
        toast.success('Patient deleted successfully');
        fetchPatients();
      } else {
        toast.error(response.data.error || 'Failed to delete patient');
      }
    } catch (error) {
      toast.error('Error deleting patient');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const exportPatientsCSV = async () => {
    try {
      const response = await client.get('/api/admin/registry/patients/export/csv', {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'patients_export.csv');
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      toast.success('Patients exported successfully');
    } catch (error) {
      toast.error('Error exporting patients');
      console.error(error);
    }
  };

  const openAssignDoctorModal = async (patient: Patient) => {
    if (!doctors.length) {
      await fetchDoctors();
    }

    setSelectedPatientForAssign(patient);
    setSelectedDoctorIdForAssign(patient.assigned_doctor_id || '');
    setIsAssignModalOpen(true);
  };

  const assignPatientToDoctor = async () => {
    if (!selectedPatientForAssign) return;

    setAssignLoading(true);
    try {
      const response = await client.post('/api/admin/registry/assignments', {
        patient_id: selectedPatientForAssign.id,
        doctor_id: selectedDoctorIdForAssign || null,
      });

      if (response.data.success) {
        toast.success(response.data.message || 'Assignment updated successfully');
        setIsAssignModalOpen(false);
        setSelectedPatientForAssign(null);
        setSelectedDoctorIdForAssign('');
        fetchPatients();
      } else {
        toast.error(response.data.message || 'Failed to update assignment');
      }
    } catch (error: any) {
      toast.error(error?.message || 'Error updating assignment');
      console.error(error);
    } finally {
      setAssignLoading(false);
    }
  };

  // ==================== EFFECTS ====================

  useEffect(() => {
    if (activeTab === 'doctors') {
      fetchDoctors();
    } else if (activeTab === 'patients') {
      fetchPatients();
    }
  }, [activeTab]);

  // ==================== RENDER ====================

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Admin Registry Management</h1>
          <p className="text-gray-600">Manage doctors and patients in the Supabase registry</p>
        </div>

        {/* Generated Credentials Display */}
        {generatedCredentials && (
          <div className="mb-8 bg-amber-50 border-2 border-amber-400 rounded-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-amber-900 mb-1">✅ Credentials Generated</h3>
                <p className="text-amber-800 text-sm">
                  {generatedCredentials.user_type === 'doctor' ? 'Doctor' : 'Patient'}: {generatedCredentials.name || generatedCredentials.patient_id}
                </p>
              </div>
              <button
                onClick={() => setGeneratedCredentials(null)}
                className="text-amber-600 hover:text-amber-800 text-xl font-bold"
              >
                ✕
              </button>
            </div>
            
            <div className="bg-white rounded p-4 mb-4 border border-amber-200">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Wallet Address</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={generatedCredentials.wallet_address}
                    readOnly
                    className="flex-1 px-3 py-2 bg-gray-100 border border-gray-300 rounded font-mono text-sm"
                  />
                  <button
                    onClick={() => copyToClipboard(generatedCredentials.wallet_address, 'Wallet address')}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium"
                  >
                    Copy
                  </button>
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Private Key</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={generatedCredentials.private_key}
                    readOnly
                    className="flex-1 px-3 py-2 bg-gray-100 border border-gray-300 rounded font-mono text-sm"
                  />
                  <button
                    onClick={() => copyToClipboard(generatedCredentials.private_key, 'Private key')}
                    className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm font-medium"
                  >
                    Copy
                  </button>
                </div>
              </div>

              <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-800">
                <strong>⚠️ Important:</strong> {generatedCredentials.credentials_message || 'Save the private key securely. It will not be shown again and will be needed for login.'}
              </div>
            </div>

            <button
              onClick={() => setGeneratedCredentials(null)}
              className="w-full px-4 py-2 bg-amber-100 text-amber-900 rounded hover:bg-amber-200 font-medium"
            >
              Credentials Saved - Close
            </button>
          </div>
        )}

        {/* Wallet Status */}
        {availableWallets && (
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-900">
              <strong>Wallet Status:</strong> {availableWallets.available_count} of {availableWallets.total_accounts} accounts available
            </p>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('doctors')}
            className={`px-6 py-3 font-medium border-b-2 transition ${
              activeTab === 'doctors'
                ? 'text-blue-600 border-blue-600'
                : 'text-gray-600 border-transparent hover:text-gray-800'
            }`}
          >
            Doctors
          </button>
          <button
            onClick={() => setActiveTab('patients')}
            className={`px-6 py-3 font-medium border-b-2 transition ${
              activeTab === 'patients'
                ? 'text-blue-600 border-blue-600'
                : 'text-gray-600 border-transparent hover:text-gray-800'
            }`}
          >
            Patients
          </button>
          <button
            onClick={() => setActiveTab('emergency')}
            className={`px-6 py-3 font-medium border-b-2 transition ${
              activeTab === 'emergency'
                ? 'text-red-600 border-red-600'
                : 'text-gray-600 border-transparent hover:text-gray-800'
            }`}
          >
            Emergency Access
          </button>
        </div>

        {activeTab === 'doctors' ? (
          <DoctorsSection
            doctors={doctors}
            loading={loading}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onSearch={searchDoctors}
            onAdd={() => {
              setFormData({});
              setSelectedItem(null);
              setIsFormOpen(true);
            }}
            onEdit={(doctor: Doctor) => {
              setSelectedItem(doctor);
              setFormData(doctor);
              setIsFormOpen(true);
            }}
            onViewWallet={openDoctorWalletModal}
            onDelete={deleteDoctor}
            onExport={exportDoctorsCSV}
            isFormOpen={isFormOpen}
            formData={formData}
            selectedItem={selectedItem}
            onFormChange={setFormData}
            onFormSubmit={selectedItem ? updateDoctor : addDoctor}
            onFormClose={() => {
              setIsFormOpen(false);
              setSelectedItem(null);
              setFormData({});
            }}
          />
        ) : activeTab === 'patients' ? (
          <PatientsSection
            patients={patients}
            loading={loading}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onSearch={searchPatients}
            onAdd={() => {
              setFormData({});
              setSelectedItem(null);
              setIsFormOpen(true);
            }}
            onEdit={(patient: Patient) => {
              setSelectedItem(patient);
              setFormData(patient);
              setIsFormOpen(true);
            }}
            onViewWallet={openPatientWalletModal}
            onDelete={deletePatient}
            onAssignDoctor={openAssignDoctorModal}
            onExport={exportPatientsCSV}
            isFormOpen={isFormOpen}
            formData={formData}
            selectedItem={selectedItem}
            onFormChange={setFormData}
            onFormSubmit={selectedItem ? updatePatient : addPatient}
            onFormClose={() => {
              setIsFormOpen(false);
              setSelectedItem(null);
              setFormData({});
            }}
          />
        ) : activeTab === 'emergency' ? (
          <EmergencyAccessSection
            isAuthenticated={isAuthenticated}
            userRole={userRole}
            isAdminRole={isAdminRole}
            emergencyLoading={emergencyLoading}
            emergencyError={emergencyError}
            onRefresh={fetchEmergencySessions}
            emergencySessions={emergencySessions}
          />
        ) : null}

        {isWalletModalOpen && (
          <DoctorWalletModal
            walletDetails={doctorWalletDetails}
            loading={walletLoading}
            onClose={() => {
              setIsWalletModalOpen(false);
              setDoctorWalletDetails(null);
            }}
            onCopy={copyToClipboard}
          />
        )}

        {isPatientWalletModalOpen && (
          <PatientWalletModal
            walletDetails={patientWalletDetails}
            loading={walletLoading}
            onClose={() => {
              setIsPatientWalletModalOpen(false);
              setPatientWalletDetails(null);
            }}
            onCopy={copyToClipboard}
          />
        )}

        {isAssignModalOpen && selectedPatientForAssign && (
          <AssignDoctorModal
            patient={selectedPatientForAssign}
            doctors={doctors}
            selectedDoctorId={selectedDoctorIdForAssign}
            onDoctorChange={setSelectedDoctorIdForAssign}
            loading={assignLoading}
            onSubmit={assignPatientToDoctor}
            onClose={() => {
              setIsAssignModalOpen(false);
              setSelectedPatientForAssign(null);
              setSelectedDoctorIdForAssign('');
            }}
          />
        )}
      </div>
    </div>
  );
}

function EmergencyAccessSection({
  isAuthenticated,
  userRole,
  isAdminRole,
  emergencyLoading,
  emergencyError,
  onRefresh,
  emergencySessions,
}: any) {
  const sortedSessions = [...emergencySessions].sort((a: EmergencySession, b: EmergencySession) => {
    const aTime = new Date(a.closed_at || a.activated_at || a.requested_at || 0).getTime();
    const bTime = new Date(b.closed_at || b.activated_at || b.requested_at || 0).getTime();
    return bTime - aTime;
  });

  return (
    <div className="space-y-4">
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Emergency Access History</h2>
            <p className="text-sm text-gray-600">Track which doctor accessed which patient report and when.</p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={onRefresh}
              className="px-3 py-1.5 text-sm rounded-md bg-gray-100 text-gray-800 border border-gray-300 hover:bg-gray-200"
            >
              Refresh
            </button>
          </div>
        </div>

        {!isAuthenticated || !isAdminRole ? (
          <p className="text-sm text-gray-600">Login as an ADMIN account to view emergency access history. Current role: {userRole || 'UNKNOWN'}</p>
        ) : emergencyError ? (
          <p className="text-sm text-red-600">Failed to load emergency history: {emergencyError}</p>
        ) : emergencyLoading ? (
          <p className="text-sm text-gray-600">Loading emergency access history...</p>
        ) : sortedSessions.length === 0 ? (
          <p className="text-sm text-gray-600">No emergency access history found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-left text-gray-600">
                  <th className="px-3 py-2">Session</th>
                  <th className="px-3 py-2">Access Type</th>
                  <th className="px-3 py-2">Doctor</th>
                  <th className="px-3 py-2">Patient</th>
                  <th className="px-3 py-2">Accessed At</th>
                  <th className="px-3 py-2">Ended At</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Reason</th>
                </tr>
              </thead>
              <tbody>
                {sortedSessions.map((session: EmergencySession) => {
                  const statusColors: { [key: string]: string } = {
                    ACTIVE: 'bg-red-100 text-red-800',
                    PENDING: 'bg-yellow-100 text-yellow-800',
                    EXPIRED: 'bg-gray-100 text-gray-800',
                    CLOSED: 'bg-blue-100 text-blue-800',
                    REJECTED: 'bg-orange-100 text-orange-800',
                  };
                  const statusColor = statusColors[session.status] || 'bg-gray-100 text-gray-800';

                  return (
                    <tr key={session.session_id} className="border-b border-gray-100 align-top">
                      <td className="px-3 py-2 font-mono text-xs">{session.session_id.slice(0, 16)}...</td>
                      <td className="px-3 py-2">
                        <span className="px-2 py-1 rounded text-xs font-semibold bg-red-100 text-red-800">EMERGENCY</span>
                      </td>
                      <td className="px-3 py-2 font-mono text-xs">{session.doctor_address || '-'}</td>
                      <td className="px-3 py-2">{session.patient_id || '-'}</td>
                      <td className="px-3 py-2">{session.activated_at ? new Date(session.activated_at).toLocaleString() : session.requested_at ? new Date(session.requested_at).toLocaleString() : '-'}</td>
                      <td className="px-3 py-2">{session.closed_at ? new Date(session.closed_at).toLocaleString() : '-'}</td>
                      <td className="px-3 py-2">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${statusColor}`}>{session.status}</span>
                      </td>
                      <td className="px-3 py-2 max-w-sm truncate" title={session.reason || ''}>{session.reason || '-'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// ==================== DOCTORS SECTION ====================

function DoctorsSection({
  doctors,
  loading,
  searchQuery,
  onSearchChange,
  onSearch,
  onAdd,
  onEdit,
  onViewWallet,
  onDelete,
  onExport,
  isFormOpen,
  formData,
  selectedItem,
  onFormChange,
  onFormSubmit,
  onFormClose,
}: any) {
  return (
    <div className="space-y-6">
      {/* Search and Actions */}
      <div className="flex gap-4 items-end">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
          <input
            type="text"
            placeholder="Search by name, email, specialization, or wallet..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && onSearch()}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          onClick={onSearch}
          className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
        >
          Search
        </button>
        <button
          onClick={onAdd}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Add Doctor
        </button>
        <button
          onClick={onExport}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Export CSV
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : doctors.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No doctors found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Name</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Wallet</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Email</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Specialization</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Hospital</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {doctors.map((doctor: Doctor) => (
                  <tr key={doctor.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900">{doctor.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-500 font-mono">{doctor.wallet_address.slice(0, 10)}...</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{doctor.email || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{doctor.specialization || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{doctor.hospital || '-'}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        doctor.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {doctor.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm space-x-2">
                      <button
                        onClick={() => onViewWallet(doctor)}
                        className="text-emerald-600 hover:text-emerald-800 font-medium"
                      >
                        View Wallet
                      </button>
                      <button
                        onClick={() => onEdit(doctor)}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => onDelete(doctor.id)}
                        className="text-red-600 hover:text-red-800 font-medium"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Form Modal */}
      {isFormOpen && (
        <DoctorForm
          doctor={selectedItem}
          formData={formData}
          onFormChange={onFormChange}
          onSubmit={onFormSubmit}
          onClose={onFormClose}
        />
      )}
    </div>
  );
}

function DoctorWalletModal({ walletDetails, loading, onClose, onCopy }: any) {
  const wallet = walletDetails?.wallet;
  const doctor = walletDetails?.doctor;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900">Doctor Wallet Details</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <div className="p-6 space-y-4">
          {loading ? (
            <div className="text-center text-gray-500">Loading wallet details...</div>
          ) : (
            <>
              <div className="bg-blue-50 border border-blue-200 rounded p-4 text-sm text-blue-900">
                <div><strong>Doctor:</strong> {doctor?.name || '-'}</div>
                <div><strong>Email:</strong> {doctor?.email || '-'}</div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Wallet Address</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    readOnly
                    value={wallet?.address || ''}
                    className="flex-1 px-3 py-2 bg-gray-100 border border-gray-300 rounded font-mono text-sm"
                  />
                  <button
                    onClick={() => wallet?.address && onCopy(wallet.address, 'Wallet address')}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium"
                    disabled={!wallet?.address}
                  >
                    Copy
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Private Key</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    readOnly
                    value={wallet?.private_key || ''}
                    className="flex-1 px-3 py-2 bg-gray-100 border border-gray-300 rounded font-mono text-sm"
                  />
                  <button
                    onClick={() => wallet?.private_key && onCopy(wallet.private_key, 'Private key')}
                    className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm font-medium"
                    disabled={!wallet?.private_key}
                  >
                    Copy
                  </button>
                </div>
                {!wallet?.private_key && (
                  <p className="mt-2 text-xs text-amber-700">
                    Private key is not available for this doctor in local wallet assignment records.
                  </p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm text-gray-700">
                <div>
                  <strong>Account Index:</strong> {wallet?.account_index ?? '-'}
                </div>
                <div>
                  <strong>Assigned At:</strong> {wallet?.assigned_at || '-'}
                </div>
              </div>

              {walletDetails?.message && (
                <div className="bg-gray-50 border border-gray-200 rounded p-3 text-sm text-gray-700">
                  {walletDetails.message}
                </div>
              )}
            </>
          )}
        </div>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function PatientWalletModal({ walletDetails, loading, onClose, onCopy }: any) {
  const wallet = walletDetails?.wallet;
  const patient = walletDetails?.patient;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900">Patient Wallet Details</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <div className="p-6 space-y-4">
          {loading ? (
            <div className="text-center text-gray-500">Loading wallet details...</div>
          ) : (
            <>
              <div className="bg-blue-50 border border-blue-200 rounded p-4 text-sm text-blue-900">
                <div><strong>Patient ID:</strong> {patient?.patient_id || '-'}</div>
                <div><strong>Name:</strong> {patient?.name || '-'}</div>
                <div><strong>Email:</strong> {patient?.email || '-'}</div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Wallet Address</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    readOnly
                    value={wallet?.address || ''}
                    className="flex-1 px-3 py-2 bg-gray-100 border border-gray-300 rounded font-mono text-sm"
                  />
                  <button
                    onClick={() => wallet?.address && onCopy(wallet.address, 'Wallet address')}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium"
                    disabled={!wallet?.address}
                  >
                    Copy
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Private Key</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    readOnly
                    value={wallet?.private_key || ''}
                    className="flex-1 px-3 py-2 bg-gray-100 border border-gray-300 rounded font-mono text-sm"
                  />
                  <button
                    onClick={() => wallet?.private_key && onCopy(wallet.private_key, 'Private key')}
                    className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm font-medium"
                    disabled={!wallet?.private_key}
                  >
                    Copy
                  </button>
                </div>
                {!wallet?.private_key && (
                  <p className="mt-2 text-xs text-amber-700">
                    Private key is not available for this patient in local wallet assignment records.
                  </p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm text-gray-700">
                <div>
                  <strong>Account Index:</strong> {wallet?.account_index ?? '-'}
                </div>
                <div>
                  <strong>Assigned At:</strong> {wallet?.assigned_at || '-'}
                </div>
              </div>

              {walletDetails?.message && (
                <div className="bg-gray-50 border border-gray-200 rounded p-3 text-sm text-gray-700">
                  {walletDetails.message}
                </div>
              )}
            </>
          )}
        </div>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

// ==================== PATIENTS SECTION ====================

function PatientsSection({
  patients,
  loading,
  searchQuery,
  onSearchChange,
  onSearch,
  onAdd,
  onViewWallet,
  onEdit,
  onDelete,
  onAssignDoctor,
  onExport,
  isFormOpen,
  formData,
  selectedItem,
  onFormChange,
  onFormSubmit,
  onFormClose,
}: any) {
  return (
    <div className="space-y-6">
      {/* Search and Actions */}
      <div className="flex gap-4 items-end">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
          <input
            type="text"
            placeholder="Search by name, email, patient ID, or wallet..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && onSearch()}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          onClick={onSearch}
          className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
        >
          Search
        </button>
        <button
          onClick={onAdd}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Add Patient
        </button>
        <button
          onClick={onExport}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Export CSV
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : patients.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No patients found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Patient ID</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Name</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Assigned Doctor</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Wallet</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Email</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">DOB</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {patients.map((patient: Patient) => (
                  <tr key={patient.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-mono text-gray-900">{patient.patient_id}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{patient.name || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{patient.assigned_doctor_name || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-500 font-mono">{patient.wallet_address ? patient.wallet_address.slice(0, 10) + '...' : '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{patient.email || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{patient.date_of_birth || '-'}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        patient.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {patient.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm space-x-2">
                      <button
                        onClick={() => onViewWallet(patient)}
                        className="text-emerald-600 hover:text-emerald-800 font-medium"
                      >
                        View Wallet
                      </button>
                      <button
                        onClick={() => onAssignDoctor(patient)}
                        className="text-emerald-600 hover:text-emerald-800 font-medium"
                      >
                        Assign Doctor
                      </button>
                      <button
                        onClick={() => onEdit(patient)}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => onDelete(patient.id)}
                        className="text-red-600 hover:text-red-800 font-medium"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Form Modal */}
      {isFormOpen && (
        <PatientForm
          patient={selectedItem}
          formData={formData}
          onFormChange={onFormChange}
          onSubmit={onFormSubmit}
          onClose={onFormClose}
        />
      )}
    </div>
  );
}

function AssignDoctorModal({
  patient,
  doctors,
  selectedDoctorId,
  onDoctorChange,
  loading,
  onSubmit,
  onClose,
}: any) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-xl w-full">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900">Assign Patient to Doctor</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <div className="p-6 space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded p-4 text-sm text-blue-900">
            <div><strong>Patient:</strong> {patient.name || '-'}</div>
            <div><strong>Patient ID:</strong> {patient.patient_id}</div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Assigned Doctor</label>
            <select
              value={selectedDoctorId}
              onChange={(e) => onDoctorChange(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Unassigned</option>
              {doctors.map((doctor: Doctor) => (
                <option key={doctor.id} value={doctor.id}>
                  {doctor.name} {doctor.specialization ? `(${doctor.specialization})` : ''}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={onSubmit}
            className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Save Assignment'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ==================== DOCTOR FORM ====================

function DoctorForm({ doctor, formData, onFormChange, onSubmit, onClose }: any) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900">{doctor ? 'Edit Doctor' : 'Add New Doctor'}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div className="p-6 space-y-4">
          {!doctor && (
            <div className="bg-blue-50 border border-blue-200 rounded p-4 text-sm text-blue-900">
              <strong>✓ Wallet Auto-Generation:</strong> A wallet will be automatically generated and assigned when you create this doctor. You'll see the credentials on the next screen.
            </div>
          )}
          {doctor && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Wallet Address</label>
              <input
                type="text"
                disabled
                value={formData.wallet_address || ''}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-600"
              />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
            <input
              type="text"
              value={formData.name || ''}
              onChange={(e) => onFormChange({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={formData.email || ''}
              onChange={(e) => onFormChange({ ...formData, email: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Specialization</label>
              <input
                type="text"
                value={formData.specialization || ''}
                onChange={(e) => onFormChange({ ...formData, specialization: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hospital</label>
              <input
                type="text"
                value={formData.hospital || ''}
                onChange={(e) => onFormChange({ ...formData, hospital: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          {doctor && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                value={formData.status || 'active'}
                onChange={(e) => onFormChange({ ...formData, status: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          )}
        </div>
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            onClick={onSubmit}
            className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            {doctor ? 'Update' : 'Add'} Doctor
          </button>
        </div>
      </div>
    </div>
  );
}

// ==================== PATIENT FORM ====================

function PatientForm({ patient, formData, onFormChange, onSubmit, onClose }: any) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900">{patient ? 'Edit Patient' : 'Add New Patient'}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div className="p-6 space-y-4">
          {!patient && (
            <div className="bg-blue-50 border border-blue-200 rounded p-4 text-sm text-blue-900">
              <strong>✓ Wallet Auto-Generation:</strong> A wallet will be automatically generated and assigned when you create this patient. You'll see the credentials on the next screen.
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Patient ID *</label>
            <input
              type="text"
              disabled={!!patient}
              value={formData.patient_id || ''}
              onChange={(e) => onFormChange({ ...formData, patient_id: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              value={formData.name || ''}
              onChange={(e) => onFormChange({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={formData.email || ''}
              onChange={(e) => onFormChange({ ...formData, email: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          {patient && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Wallet Address</label>
              <input
                type="text"
                disabled
                value={formData.wallet_address || ''}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-600"
              />
            </div>
          )}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
              <input
                type="date"
                value={formData.date_of_birth || ''}
                onChange={(e) => onFormChange({ ...formData, date_of_birth: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Emergency Contact</label>
              <input
                type="text"
                value={formData.emergency_contact || ''}
                onChange={(e) => onFormChange({ ...formData, emergency_contact: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          {patient && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                value={formData.status || 'active'}
                onChange={(e) => onFormChange({ ...formData, status: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          )}
        </div>
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            onClick={onSubmit}
            className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            {patient ? 'Update' : 'Add'} Patient
          </button>
        </div>
      </div>
    </div>
  );
}
