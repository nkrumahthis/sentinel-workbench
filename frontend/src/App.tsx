import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './components/ui/card';
import { Alert, AlertTitle, AlertDescription } from './components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Clock, Shield, Cloud, Activity } from 'lucide-react';

type AlertData = {
  userName: string,
  eventName: string,
  eventTime: string,
  sourceIP: string,
  userAgent: string
}

type Enrichments = {
  assumedRoleDetails: {
    assumedBy: string,
    assumedAt: string,
    sourceIP: string,
    roleArn: string,
  },
  recentRoleAssumptions: [
    {
      roleArn: string,
      eventTime: string,
      sourceIP: string,
      successful: string,
    }
  ],
  interestingApiCalls: [
    {
      eventName: string,
      eventSource: string,
      eventTime: string,
      sourceIP: string,
    }
  ],
  serviceInteractions: {
    [key: string]: number
  }
}

const AlertEnrichmentDashboard = () => {

  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState<string | undefined>(undefined);
  const [alertData, setAlertData] = useState<AlertData | null>(null);
  const [enrichments, setEnrichments] = useState<Enrichments | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch available users from mock data
    const fetchUsers = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/users');
        const data = await response.json();
        setUsers(data);
        if (data.length > 0) {
          setSelectedUser(data[0]);
        }
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    };

    fetchUsers();
  }, []);

  useEffect(() => {
    if (selectedUser) {
      setAlertData({
        userName: selectedUser,
        eventName: 'CreateKeyPair',
        eventTime: new Date().toISOString(),
        sourceIP: '192.168.1.1',
        userAgent: 'aws-cli/2.0.0'
      });
    }
  }, [selectedUser]);

  useEffect(() => {
    const fetchEnrichments = async () => {
      if (!alertData) return;

      setLoading(true);
      try {
        const response = await fetch('http://localhost:5001/api/enrich', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(alertData)
        });
        const data = await response.json();
        setEnrichments(data);
      } catch (error) {
        console.error('Error fetching enrichments:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEnrichments();
  }, [alertData]);

  const transformServiceData = (services: {[key: string]: number} | undefined) => {
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
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">AWS Alert Enrichment Workbench</h1>

        <Select value={selectedUser} onValueChange={setSelectedUser}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select user" />
          </SelectTrigger>
          <SelectContent>
            {users.map(user => (
              <SelectItem key={user} value={user}>
                {user}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {alertData && (
        <Alert className="mb-6">
          <AlertTitle className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Alert Details
          </AlertTitle>
          <AlertDescription>
            <div className="mt-2 space-y-2">
              <p><strong>User:</strong> {alertData.userName}</p>
              <p><strong>Event:</strong> {alertData.eventName}</p>
              <p><strong>Time:</strong> {alertData.eventTime}</p>
              <p><strong>Source IP:</strong> {alertData.sourceIP}</p>
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
              {(enrichments?.recentRoleAssumptions?.length ?? 0) > 0 ? (
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
                <>
                  <p>{JSON.stringify(enrichments?.serviceInteractions)}</p>
                  <BarChart data={transformServiceData(enrichments?.serviceInteractions)}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#4f46e5" />
                  </BarChart>
                </>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AlertEnrichmentDashboard;