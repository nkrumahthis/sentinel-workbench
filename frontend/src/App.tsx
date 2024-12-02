import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './components/ui/card';
import { Alert, AlertTitle, AlertDescription } from './components/ui/alert';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Clock, Shield, Cloud, Activity } from 'lucide-react';
import AlertList from './components/AlertList';
import { Alert as AlertType, Enrichments } from './lib/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
const App = () => {

  const [enrichments, setEnrichments] = useState<Enrichments | null>(null);
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState([]);
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<AlertType | null>(null);
  const [error, setError] = useState<string | null>(null);


  // Fetch all alerts
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        console.log(`${API_BASE_URL}/api/alerts`)
        const response = await fetch(`${API_BASE_URL}/api/alerts`);
        const data = await response.json();
        
        console.log("ok")
        setAlerts(data);
        if (data.length > 0 && !selectedAlertId) {
          setSelectedAlertId(data[0].id);
        }
      } catch (error) {
        setError('Failed to fetch alerts');
        console.error('Error:', error);
      }
    };

    fetchAlerts();
  }, []);

  // Fetch selected alert details and enrichments
  useEffect(() => {
    const fetchAlertDetails = async () => {
      if (!selectedAlertId) {
        setLoading(false)
        return
      };

      setLoading(true);
      try {
        // Fetch alert details
        const alertResponse = await fetch(`${API_BASE_URL}/api/alerts/${selectedAlertId}`);
        const alertData = await alertResponse.json();
        setSelectedAlert(alertData);

        // Fetch enrichments
        const enrichResponse = await fetch(`${API_BASE_URL}/api/enrich`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(alertData),
        });
        const enrichData = await enrichResponse.json();
        setEnrichments(enrichData);
      } catch (error) {
        setError('Failed to fetch alert details');
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAlertDetails();
  }, [selectedAlertId]);

  const transformServiceData = (services: { [key: string]: number } | undefined) => {
    return Object.entries(services || {}).map(([name, count]) => ({
      name,
      count
    }));
  };

  if (loading && !enrichments) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <div className="w-96 border-r bg-gray-50 p-4">
        <AlertList
          alerts={alerts}
          selectedAlertId={selectedAlertId}
          onSelectAlert={setSelectedAlertId}
        />
      </div>
      <div className="flex-1 overflow-auto p-6">
        {error ? (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : selectedAlert ? (
          <>
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold">AWS Alert Enrichment Workbench</h1>
            </div>

            {selectedAlert && (
              <Alert className="mb-6">
              <AlertTitle className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Alert Details
              </AlertTitle>
              <AlertDescription>
                <div className="mt-2 space-y-2">
                  <p><strong>Title:</strong> {selectedAlert.title}</p>
                  <p><strong>User:</strong> {selectedAlert.userName}</p>
                  <p><strong>Event:</strong> {selectedAlert.eventName}</p>
                  <p><strong>Time:</strong> {new Date(selectedAlert.timestamp).toLocaleString()}</p>
                  <p><strong>Source IP:</strong> {selectedAlert.sourceIP}</p>
                  <p><strong>Severity:</strong> {selectedAlert.severity}</p>
                </div>
              </AlertDescription>
            </Alert>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Assumed Role Details */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    Assumed Role Details
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {enrichments?.assumedRoleDetails?.assumedBy ? (
                    <div className="space-y-2">
                      <p><strong>Assumed By:</strong> {enrichments.assumedRoleDetails.assumedBy}</p>
                      <p><strong>Time:</strong> {enrichments.assumedRoleDetails.assumedAt}</p>
                      <p><strong>Source IP:</strong> {enrichments.assumedRoleDetails.sourceIP}</p>
                      <p><strong>Role ARN:</strong> {enrichments.assumedRoleDetails.roleArn}</p>
                    </div>
                  ) : (
                    <p>No role assumption details found</p>
                  )}
                </CardContent>
              </Card>

              {/* Recent Role Assumptions */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cloud className="h-4 w-4" />
                    Recent Role Assumptions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {(enrichments?.recentRoleAssumptions.length ?? 0) > 0 ? (
                      enrichments?.recentRoleAssumptions.map((assumption, index) => (
                        <div key={index} className="p-2 bg-gray-50 rounded">
                          <p><strong>Role:</strong> {assumption.roleArn}</p>
                          <p><strong>Time:</strong> {assumption.eventTime}</p>
                          <p><strong>IP:</strong> {assumption.sourceIP}</p>
                          <p><strong>Status:</strong>
                            <span className={assumption.successful ? 'text-green-600' : 'text-red-600'}>
                              {assumption.successful ? ' Successful' : ' Failed'}
                            </span>
                          </p>
                        </div>
                      ))
                    ) : (
                      <p>No recent role assumptions found</p>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Interesting API Calls */}
              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-4 w-4" />
                    Interesting API Calls
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {(enrichments?.interestingApiCalls.length ?? 0) > 0 ? (
                      enrichments?.interestingApiCalls.map((call, index) => (
                        <div key={index} className="p-2 bg-gray-50 rounded flex justify-between items-center">
                          <div>
                            <p className="font-medium">{call.eventName}</p>
                            <p className="text-sm text-gray-600">{call.eventSource}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm">{new Date(call.eventTime).toLocaleString()}</p>
                            <p className="text-sm text-gray-600">{call.sourceIP}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p>No interesting API calls found</p>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Service Interactions Chart */}
              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle>Service Interactions (Last 7 Days)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={transformServiceData(enrichments?.serviceInteractions)}>
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#4f46e5" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">Select an alert to view details</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;