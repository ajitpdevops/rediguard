"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { 
  AlertTriangle, 
  Shield, 
  Clock, 
  Search,
  RefreshCw,
  CheckCircle,
  XCircle,
  Bell,
  User,
  MapPin,
  Activity,
  Eye
} from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import DashboardLayout from "@/components/dashboard-layout"

interface SecurityAlert {
  id: string
  title: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'investigating' | 'resolved' | 'dismissed'
  timestamp: string
  user_id?: string
  ip_address?: string
  location?: string
  event_type: string
  risk_score: number
  details: {
    detection_method: string
    confidence: number
    related_events: number
    action_taken?: string
  }
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<SecurityAlert[]>([])
  const [filteredAlerts, setFilteredAlerts] = useState<SecurityAlert[]>([])
  const [selectedAlert, setSelectedAlert] = useState<SecurityAlert | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  const [searchTerm, setSearchTerm] = useState("")
  const [filterSeverity, setFilterSeverity] = useState("all")
  const [filterStatus, setFilterStatus] = useState("all")

  // Handle alert status updates
  const handleUpdateAlert = (alertId: string, newStatus: SecurityAlert['status']) => {
    const updatedAlerts = alerts.map(alert => 
      alert.id === alertId 
        ? { ...alert, status: newStatus }
        : alert
    )
    setAlerts(updatedAlerts)
    applyFilters(updatedAlerts)
  }

  const fetchAlerts = async () => {
    setIsLoading(true)
    try {
      // Mock security alerts data
      const mockAlerts: SecurityAlert[] = [
        {
          id: 'alert_001',
          title: 'Suspicious Login Pattern Detected',
          description: 'User user_123 showing unusual login behavior from multiple locations',
          severity: 'critical',
          status: 'open',
          timestamp: new Date().toISOString(),
          user_id: 'user_123',
          ip_address: '192.168.1.100',
          location: 'New York, US',
          event_type: 'anomalous_login',
          risk_score: 0.95,
          details: {
            detection_method: 'ML Anomaly Detection',
            confidence: 95,
            related_events: 8,
          }
        },
        {
          id: 'alert_002',
          title: 'Multiple Failed Login Attempts',
          description: 'Brute force attack detected from IP 203.0.113.45',
          severity: 'high',
          status: 'investigating',
          timestamp: new Date(Date.now() - 300000).toISOString(),
          ip_address: '203.0.113.45',
          location: 'Unknown',
          event_type: 'brute_force',
          risk_score: 0.85,
          details: {
            detection_method: 'Rate Limiting',
            confidence: 90,
            related_events: 15,
            action_taken: 'IP temporarily blocked'
          }
        },
        {
          id: 'alert_003',
          title: 'Unusual Data Access Pattern',
          description: 'User user_789 accessing large volumes of sensitive data',
          severity: 'high',
          status: 'open',
          timestamp: new Date(Date.now() - 600000).toISOString(),
          user_id: 'user_789',
          ip_address: '172.16.0.10',
          location: 'Tokyo, JP',
          event_type: 'data_exfiltration',
          risk_score: 0.88,
          details: {
            detection_method: 'Behavior Analysis',
            confidence: 88,
            related_events: 12,
          }
        },
        {
          id: 'alert_004',
          title: 'Off-Hours Administrative Access',
          description: 'Administrative access detected outside normal business hours',
          severity: 'medium',
          status: 'resolved',
          timestamp: new Date(Date.now() - 1800000).toISOString(),
          user_id: 'admin_001',
          ip_address: '10.0.0.100',
          location: 'Berlin, DE',
          event_type: 'off_hours_access',
          risk_score: 0.65,
          details: {
            detection_method: 'Time-based Rules',
            confidence: 75,
            related_events: 3,
            action_taken: 'Verified with user'
          }
        },
        {
          id: 'alert_005',
          title: 'Unusual API Usage Spike',
          description: 'API calls from user_456 exceeded normal thresholds',
          severity: 'medium',
          status: 'dismissed',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          user_id: 'user_456',
          ip_address: '10.0.0.5',
          location: 'London, UK',
          event_type: 'api_abuse',
          risk_score: 0.55,
          details: {
            detection_method: 'Threshold Monitoring',
            confidence: 70,
            related_events: 6,
            action_taken: 'False positive - automated testing'
          }
        },
        {
          id: 'alert_006',
          title: 'Privilege Escalation Attempt',
          description: 'Unauthorized attempt to access admin functions',
          severity: 'critical',
          status: 'investigating',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          user_id: 'user_567',
          ip_address: '192.168.1.50',
          location: 'San Francisco, US',
          event_type: 'privilege_escalation',
          risk_score: 0.92,
          details: {
            detection_method: 'Permission Monitoring',
            confidence: 85,
            related_events: 4,
          }
        }
      ]
      
      setAlerts(mockAlerts)
      setFilteredAlerts(mockAlerts)
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Failed to fetch alerts:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
    const interval = setInterval(fetchAlerts, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    let filtered = alerts

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(alert => 
        alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.user_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.ip_address?.includes(searchTerm) ||
        alert.event_type.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Apply severity filter
    if (filterSeverity !== "all") {
      filtered = filtered.filter(alert => alert.severity === filterSeverity)
    }

    // Apply status filter
    if (filterStatus !== "all") {
      filtered = filtered.filter(alert => alert.status === filterStatus)
    }

    setFilteredAlerts(filtered)
  }, [alerts, searchTerm, filterSeverity, filterStatus])

  // Helper function to apply filters manually
  const applyFilters = (alertsToFilter = alerts) => {
    let filtered = alertsToFilter

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(alert => 
        alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.user_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.ip_address?.includes(searchTerm) ||
        alert.event_type.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Apply severity filter
    if (filterSeverity !== "all") {
      filtered = filtered.filter(alert => alert.severity === filterSeverity)
    }

    // Apply status filter
    if (filterStatus !== "all") {
      filtered = filtered.filter(alert => alert.status === filterStatus)
    }

    setFilteredAlerts(filtered)
  }

  const getSeverityColor = (severity: string): "default" | "destructive" | "secondary" => {
    switch (severity) {
      case 'critical': return 'destructive'
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'default'
    }
  }

  const getStatusColor = (status: string): "default" | "destructive" | "secondary" => {
    switch (status) {
      case 'open': return 'destructive'
      case 'investigating': return 'default'
      case 'resolved': return 'secondary'
      case 'dismissed': return 'secondary'
      default: return 'default'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <AlertTriangle className="h-5 w-5 text-red-500" />
      case 'high': return <AlertTriangle className="h-5 w-5 text-orange-500" />
      case 'medium': return <Shield className="h-5 w-5 text-yellow-500" />
      case 'low': return <Shield className="h-5 w-5 text-blue-500" />
      default: return <Shield className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open': return <Bell className="h-4 w-4 text-red-500" />
      case 'investigating': return <Activity className="h-4 w-4 text-orange-500" />
      case 'resolved': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'dismissed': return <XCircle className="h-4 w-4 text-gray-500" />
      default: return <Bell className="h-4 w-4 text-gray-500" />
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    
    if (diffMinutes < 1) return 'Just now'
    if (diffMinutes < 60) return `${diffMinutes}m ago`
    const diffHours = Math.floor(diffMinutes / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  // Mock data for charts
  const alertTrends = [
    { time: '00:00', critical: 1, high: 2, medium: 3, low: 1 },
    { time: '04:00', critical: 0, high: 1, medium: 2, low: 2 },
    { time: '08:00', critical: 2, high: 3, medium: 4, low: 3 },
    { time: '12:00', critical: 1, high: 4, medium: 6, low: 2 },
    { time: '16:00', critical: 3, high: 5, medium: 5, low: 4 },
    { time: '20:00', critical: 1, high: 2, medium: 3, low: 2 },
  ]

  const alertsByType = [
    { type: 'Login Anomaly', count: 8 },
    { type: 'Data Access', count: 6 },
    { type: 'API Abuse', count: 4 },
    { type: 'Privilege Escalation', count: 3 },
    { type: 'Brute Force', count: 2 },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Security Alerts</h2>
            <p className="text-muted-foreground">
              Real-time security alerts and incident management
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="text-xs">
              <Clock className="mr-1 h-3 w-3" />
              Last updated: {lastUpdated.toLocaleTimeString()}
            </Badge>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={fetchAlerts}
              disabled={isLoading}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Alerts</CardTitle>
              <Bell className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{alerts.length}</div>
              <p className="text-xs text-muted-foreground">
                {filteredAlerts.length} after filters
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Critical/High</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {alerts.filter(a => a.severity === 'critical' || a.severity === 'high').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Requires immediate attention
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Open Alerts</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {alerts.filter(a => a.status === 'open' || a.status === 'investigating').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Active investigations
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Resolved Today</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {alerts.filter(a => a.status === 'resolved').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Successfully handled
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="alerts" className="space-y-4">
          <TabsList>
            <TabsTrigger value="alerts">Alert List</TabsTrigger>
            <TabsTrigger value="analytics">Alert Analytics</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
          </TabsList>

          <TabsContent value="alerts" className="space-y-4">
            {/* Filters */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Search className="mr-2 h-4 w-4" />
                  Search & Filter Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search alerts by title, description, user, or IP..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-8"
                      />
                    </div>
                  </div>
                  <Select value={filterSeverity} onValueChange={setFilterSeverity}>
                    <SelectTrigger className="w-[140px]">
                      <SelectValue placeholder="Severity" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Severities</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filterStatus} onValueChange={setFilterStatus}>
                    <SelectTrigger className="w-[140px]">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Statuses</SelectItem>
                      <SelectItem value="open">Open</SelectItem>
                      <SelectItem value="investigating">Investigating</SelectItem>
                      <SelectItem value="resolved">Resolved</SelectItem>
                      <SelectItem value="dismissed">Dismissed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Alerts List */}
            <div className="space-y-4">
              {filteredAlerts.map((alert) => (
                <Card key={alert.id} className="overflow-hidden">
                  <CardContent className="p-6">
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0 mt-1">
                        {getSeverityIcon(alert.severity)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            {/* Header with title and badges */}
                            <div className="flex flex-wrap items-center gap-2 mb-3">
                              <h3 className="font-semibold text-lg leading-tight">{alert.title}</h3>
                              <Badge variant={getSeverityColor(alert.severity)} className="whitespace-nowrap">
                                {alert.severity.toUpperCase()}
                              </Badge>
                              <Badge variant={getStatusColor(alert.status)} className="whitespace-nowrap">
                                {getStatusIcon(alert.status)}
                                <span className="ml-1">{alert.status.replace('_', ' ').toUpperCase()}</span>
                              </Badge>
                            </div>
                            
                            {/* Description */}
                            <p className="text-muted-foreground mb-4 leading-relaxed">{alert.description}</p>
                            
                            {/* Details Grid */}
                            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 text-sm mb-4">
                              {alert.user_id && (
                                <div className="flex items-center gap-2 p-2 bg-muted/30 rounded">
                                  <User className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                                  <span className="text-muted-foreground">User:</span>
                                  <span className="font-medium truncate">{alert.user_id}</span>
                                </div>
                              )}
                              {alert.ip_address && (
                                <div className="flex items-center gap-2 p-2 bg-muted/30 rounded">
                                  <Activity className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                                  <span className="text-muted-foreground">IP:</span>
                                  <span className="font-mono font-medium truncate">{alert.ip_address}</span>
                                </div>
                              )}
                              {alert.location && (
                                <div className="flex items-center gap-2 p-2 bg-muted/30 rounded">
                                  <MapPin className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                                  <span className="text-muted-foreground">Location:</span>
                                  <span className="font-medium truncate">{alert.location}</span>
                                </div>
                              )}
                              <div className="flex items-center gap-2 p-2 bg-muted/30 rounded">
                                <Clock className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                                <span className="text-muted-foreground">Time:</span>
                                <span className="font-medium truncate">{formatTimestamp(alert.timestamp)}</span>
                              </div>
                            </div>

                            {/* Technical Details */}
                            <div className="grid gap-3 sm:grid-cols-3 text-sm mb-4">
                              <div className="p-2 bg-blue-50 dark:bg-blue-950/30 rounded">
                                <span className="text-blue-700 dark:text-blue-300 text-xs uppercase font-semibold">Detection</span>
                                <div className="font-medium">{alert.details.detection_method}</div>
                              </div>
                              <div className="p-2 bg-green-50 dark:bg-green-950/30 rounded">
                                <span className="text-green-700 dark:text-green-300 text-xs uppercase font-semibold">Confidence</span>
                                <div className="font-medium">{alert.details.confidence}%</div>
                              </div>
                              <div className="p-2 bg-orange-50 dark:bg-orange-950/30 rounded">
                                <span className="text-orange-700 dark:text-orange-300 text-xs uppercase font-semibold">Related Events</span>
                                <div className="font-medium">{alert.details.related_events}</div>
                              </div>
                            </div>

                            {/* Action Taken */}
                            {alert.details.action_taken && (
                              <div className="p-3 bg-muted rounded-lg border-l-4 border-green-500 mb-4">
                                <div className="flex items-center gap-2 mb-1">
                                  <CheckCircle className="h-4 w-4 text-green-600" />
                                  <span className="font-semibold text-green-700 dark:text-green-300">Action Taken</span>
                                </div>
                                <p className="text-sm">{alert.details.action_taken}</p>
                              </div>
                            )}
                          </div>
                          
                          {/* Right Side - Risk Score and Actions */}
                          <div className="flex lg:flex-col gap-4 lg:gap-2 lg:items-end">
                            <div className="text-center lg:text-right">
                              <div className="text-sm text-muted-foreground mb-1">Risk Score</div>
                              <div className="text-2xl font-bold text-red-600">
                                {(alert.risk_score * 100).toFixed(0)}%
                              </div>
                            </div>
                            
                            {/* Action Buttons */}
                            <div className="flex flex-wrap gap-2 lg:flex-col lg:w-32">
                              {alert.status === 'open' && (
                                <Button 
                                  size="sm" 
                                  onClick={() => handleUpdateAlert(alert.id, 'investigating')}
                                  className="flex-1 lg:w-full"
                                >
                                  Investigate
                                </Button>
                              )}
                              {alert.status === 'investigating' && (
                                <>
                                  <Button 
                                    size="sm" 
                                    onClick={() => handleUpdateAlert(alert.id, 'resolved')}
                                    className="flex-1 lg:w-full"
                                  >
                                    Resolve
                                  </Button>
                                  <Button 
                                    size="sm" 
                                    variant="outline"
                                    onClick={() => handleUpdateAlert(alert.id, 'dismissed')}
                                    className="flex-1 lg:w-full"
                                  >
                                    Dismiss
                                  </Button>
                                </>
                              )}
                              {(alert.status === 'resolved' || alert.status === 'dismissed') && (
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => handleUpdateAlert(alert.id, 'open')}
                                  className="flex-1 lg:w-full"
                                >
                                  Reopen
                                </Button>
                              )}
                              <Button 
                                size="sm" 
                                variant="ghost"
                                onClick={() => setSelectedAlert(alert)}
                                className="flex-1 lg:w-full"
                              >
                                <Eye className="mr-1 h-3 w-3" />
                                Details
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Alerts by Type</CardTitle>
                  <CardDescription>Most common alert categories</CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={alertsByType}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="type" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#ef4444" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Alert Severity Distribution</CardTitle>
                  <CardDescription>Current alert breakdown by severity</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {['critical', 'high', 'medium', 'low'].map(severity => {
                    const count = alerts.filter(a => a.severity === severity).length
                    const percentage = (count / alerts.length) * 100
                    
                    return (
                      <div key={severity} className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm font-medium capitalize">{severity}</span>
                          <span className="text-sm text-muted-foreground">
                            {count} alerts ({percentage.toFixed(1)}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              severity === 'critical' ? 'bg-red-600' :
                              severity === 'high' ? 'bg-orange-500' :
                              severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                            }`}
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    )
                  })}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="trends" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Alert Trends by Severity</CardTitle>
                <CardDescription>Alert volume and severity patterns over time</CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={alertTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="critical" stroke="#dc2626" strokeWidth={2} name="Critical" />
                    <Line type="monotone" dataKey="high" stroke="#ea580c" strokeWidth={2} name="High" />
                    <Line type="monotone" dataKey="medium" stroke="#ca8a04" strokeWidth={2} name="Medium" />
                    <Line type="monotone" dataKey="low" stroke="#2563eb" strokeWidth={2} name="Low" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Alert Details Dialog */}
      <Dialog open={!!selectedAlert} onOpenChange={() => setSelectedAlert(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedAlert && getSeverityIcon(selectedAlert.severity)}
              {selectedAlert?.title}
              <Badge variant={selectedAlert ? getSeverityColor(selectedAlert.severity) : "default"}>
                {selectedAlert?.severity.toUpperCase()}
              </Badge>
            </DialogTitle>
          </DialogHeader>
          
          {selectedAlert && (
            <div className="space-y-6">
              {/* Alert Overview */}
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Alert Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <span className="text-sm font-medium text-muted-foreground">Description:</span>
                      <p className="mt-1">{selectedAlert.description}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-muted-foreground">Event Type:</span>
                      <p className="mt-1 capitalize">{selectedAlert.event_type.replace('_', ' ')}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-muted-foreground">Risk Score:</span>
                      <p className="mt-1 text-lg font-bold text-red-600">
                        {(selectedAlert.risk_score * 100).toFixed(0)}%
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Context Details</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {selectedAlert.user_id && (
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">User:</span>
                        <span className="font-medium">{selectedAlert.user_id}</span>
                      </div>
                    )}
                    {selectedAlert.ip_address && (
                      <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">IP Address:</span>
                        <span className="font-mono">{selectedAlert.ip_address}</span>
                      </div>
                    )}
                    {selectedAlert.location && (
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">Location:</span>
                        <span>{selectedAlert.location}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Timestamp:</span>
                      <span>{formatTimestamp(selectedAlert.timestamp)}</span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Technical Details */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Detection Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <span className="text-sm font-medium text-muted-foreground">Detection Method:</span>
                      <p className="mt-1 font-medium">{selectedAlert.details.detection_method}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-muted-foreground">Confidence:</span>
                      <p className="mt-1 font-medium">{selectedAlert.details.confidence}%</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-muted-foreground">Related Events:</span>
                      <p className="mt-1 font-medium">{selectedAlert.details.related_events}</p>
                    </div>
                  </div>
                  
                  {selectedAlert.details.action_taken && (
                    <div className="mt-4 p-3 bg-muted rounded-lg border-l-4 border-green-500">
                      <div className="flex items-center gap-2 mb-1">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="font-semibold text-green-700 dark:text-green-300">Action Taken</span>
                      </div>
                      <p className="text-sm">{selectedAlert.details.action_taken}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Status Management */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Status Management</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-sm font-medium">Current Status:</span>
                    <Badge variant={getStatusColor(selectedAlert.status)}>
                      {getStatusIcon(selectedAlert.status)}
                      <span className="ml-1">{selectedAlert.status.replace('_', ' ').toUpperCase()}</span>
                    </Badge>
                  </div>
                  
                  <div className="flex flex-wrap gap-2">
                    {selectedAlert.status === 'open' && (
                      <Button 
                        size="sm" 
                        onClick={() => {
                          handleUpdateAlert(selectedAlert.id, 'investigating')
                          setSelectedAlert({...selectedAlert, status: 'investigating'})
                        }}
                      >
                        Start Investigation
                      </Button>
                    )}
                    {selectedAlert.status === 'investigating' && (
                      <>
                        <Button 
                          size="sm" 
                          onClick={() => {
                            handleUpdateAlert(selectedAlert.id, 'resolved')
                            setSelectedAlert({...selectedAlert, status: 'resolved'})
                          }}
                        >
                          Mark Resolved
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            handleUpdateAlert(selectedAlert.id, 'dismissed')
                            setSelectedAlert({...selectedAlert, status: 'dismissed'})
                          }}
                        >
                          Dismiss Alert
                        </Button>
                      </>
                    )}
                    {(selectedAlert.status === 'resolved' || selectedAlert.status === 'dismissed') && (
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => {
                          handleUpdateAlert(selectedAlert.id, 'open')
                          setSelectedAlert({...selectedAlert, status: 'open'})
                        }}
                      >
                        Reopen Alert
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  )
}
