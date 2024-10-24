import { Bell } from "lucide-react";
import { ScrollArea } from "./ui/scroll-area";
import { Badge } from "./ui/badge";
import { Alert } from "@/lib/types";

// Define the props interface
interface AlertListProps {
    alerts: Alert[]; // Array of Alert objects
    selectedAlertId: string | null; // ID is a string
    onSelectAlert: (id: string) => void; // Function that handles selecting an alert
}

const AlertList: React.FC<AlertListProps> = ({ alerts, selectedAlertId, onSelectAlert }) => (
    <ScrollArea className="h-[calc(100vh-2rem)] w-full rounded-md border">
        <div className="p-4">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Alerts ({alerts.length})
            </h2>
            <div className="space-y-2">
                {alerts.map((alert: Alert) => (
                    <div
                        key={alert.id}
                        className={`p-4 rounded-lg border cursor-pointer transition-colors ${selectedAlertId === alert.id
                            ? 'bg-blue-50 border-blue-200'
                            : 'hover:bg-gray-50'
                            }`}
                        onClick={() => onSelectAlert(alert.id)}
                    >
                        <div className="flex justify-between items-start mb-2">
                            <h3 className="font-medium">{alert.title}</h3>
                            <Badge variant={alert.severity === 'HIGH' ? 'destructive' : 'default'}>
                                {alert.severity}
                            </Badge>
                        </div>
                        <div className="text-sm text-gray-500">
                            <p>{new Date(alert.timestamp).toLocaleString()}</p>
                            <p>User: {alert.userName}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    </ScrollArea>
);

export default AlertList