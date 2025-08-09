"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { 
  Shield, 
  Activity, 
  Users, 
  AlertTriangle, 
  Database, 
  TrendingUp,
  RefreshCw,
  Clock,
  MapPin
} from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import DashboardLayout from "@/components/dashboard-layout"

interface SecurityEvent {
  id: string
  user_id: string
  event_type: string
  ip_address: string
  location: string
  timestamp: string
  risk_score: number
  is_anomaly: boolean
}

interface DashboardStats {
  total_events: number
  anomalies: number
  active_users: number
  security_alerts: number
  redis_operations: number
  avg_response_time: number
}

interface AlertData {
  id: string
  message: string
  severity: 'high' | 'medium' | 'low'
  timestamp: string
  user_id?: string
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    total_events: 0,
    anomalies: 0,
    active_users: 0,
    security_alerts: 0,
    redis_operations: 0,
    avg_response_time: 0
  })
  
  const [recentEvents, setRecentEvents] = useState<SecurityEvent[]>([])
  const [alerts, setAlerts] = useState<AlertData[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  // Mock data for demonstration
  const mockEventData = [
    { time: '00:00', events: 45, anomalies: 2 },
    { time: '04:00', events: 32, anomalies: 1 },
    { time: '08:00', events: 89, anomalies: 5 },
    { time: '12:00', events: 124, anomalies: 8 },
    { time: '16:00', events: 156, anomalies: 12 },
    { time: '20:00', events: 98, anomalies: 6 },
  ]

  const mockLocationData = [
    { name: 'US', value: 45, color: '#0088FE' },
    { name: 'EU', value: 32, color: '#00C49F' },
    { name: 'Asia', value: 23, color: '#FFBB28' },
    { name: 'Others', value: 12, color: '#FF8042' },
  ]

  const mockRiskData = [
    { category: 'Login Attempts', low: 45, medium: 12, high: 3 },
    { category: 'API Calls', low: 89, medium: 23, high: 8 },
    { category: 'Data Access', low: 67, medium: 15, high: 5 },
    { category: 'Admin Actions', low: 23, medium: 8, high: 2 },
  ]

  const fetchDashboardData = async () => {
    setIsLoading(true)
    try {
      // Mock real-time data
      setStats({
        total_events: Math.floor(Math.random() * 1000) + 500,
        anomalies: Math.floor(Math.random() * 50) + 10,
        active_users: Math.floor(Math.random() * 200) + 50,
        security_alerts: Math.floor(Math.random() * 20) + 5,
        redis_operations: Math.floor(Math.random() * 10000) + 5000,
        avg_response_time: Math.floor(Math.random() * 100) + 50
      })

      // Mock recent events
      const mockEvents: SecurityEvent[] = [
        {
          id: '1',
          user_id: 'user_123',
          event_type: 'login',
          ip_address: '192.168.1.100',
          location: 'New York, US',
          timestamp: new Date().toISOString(),
          risk_score: 0.8,
          is_anomaly: true
        },
        {
          id: '2',
          user_id: 'user_456',
          event_type: 'api_call',
          ip_address: '10.0.0.5',
          location: 'London, UK',
          timestamp: new Date(Date.now() - 300000).toISOString(),
          risk_score: 0.3,
          is_anomaly: false
        },
        {
          id: '3',
          user_id: 'user_789',
          event_type: 'data_access',
          ip_address: '172.16.0.10',
          location: 'Tokyo, JP',
          timestamp: new Date(Date.now() - 600000).toISOString(),
          risk_score: 0.9,
          is_anomaly: true
        }
      ]
      setRecentEvents(mockEvents)

      // Mock alerts
      const mockAlerts: AlertData[] = [
        {
          id: 'alert_1',
          message: 'Suspicious login pattern detected for user_123',
          severity: 'high',
          timestamp: new Date().toISOString(),
          user_id: 'user_123'
        },
        {
          id: 'alert_2',
          message: 'Multiple failed login attempts from IP 192.168.1.100',
          severity: 'medium',
          timestamp: new Date(Date.now() - 600000).toISOString()
        }
      ]
      setAlerts(mockAlerts)

      setLastUpdated(new Date())
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const getRiskColor = (score: number) => {
    if (score >= 0.7) return 'text-red-600 dark:text-red-400'
    if (score >= 0.4) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-green-600 dark:text-green-400'
  }

  const getSeverityColor = (severity: string): "default" | "destructive" | "secondary" => {
    switch (severity) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'default'
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Security Dashboard</h2>
            <p className="text-muted-foreground">
              Real-time monitoring powered by Redis Stack 8
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
              onClick={fetchDashboardData}
              disabled={isLoading}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Events</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_events.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                <TrendingUp className="inline mr-1 h-3 w-3" />
                +12% from last hour
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Anomalies</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.anomalies}</div>
              <p className="text-xs text-muted-foreground">
                {((stats.anomalies / stats.total_events) * 100).toFixed(1)}% of total events
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.active_users}</div>
              <p className="text-xs text-muted-foreground">
                Online in last 24h
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Redis Ops/sec</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.redis_operations.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                Avg response: {stats.avg_response_time}ms
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="events">Recent Events</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Event Timeline</CardTitle>
                  <CardDescription>Security events and anomalies over time</CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={mockEventData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="events" stroke="#8884d8" strokeWidth={2} />
                      <Line type="monotone" dataKey="anomalies" stroke="#ff6b6b" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Geographic Distribution</CardTitle>
                  <CardDescription>Events by location</CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={mockLocationData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {mockLocationData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="events" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Security Events</CardTitle>
                <CardDescription>Latest events from Redis Stream</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentEvents.map((event) => (
                    <div key={event.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          {event.is_anomaly ? (
                            <AlertTriangle className="h-5 w-5 text-red-500" />
                          ) : (
                            <Shield className="h-5 w-5 text-green-500" />
                          )}
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-medium">{event.event_type}</span>
                            <Badge variant={event.is_anomaly ? "destructive" : "secondary"}>
                              {event.is_anomaly ? "Anomaly" : "Normal"}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            User: {event.user_id} • IP: {event.ip_address}
                          </div>
                          <div className="flex items-center text-sm text-muted-foreground">
                            <MapPin className="mr-1 h-3 w-3" />
                            {event.location}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-sm font-medium ${getRiskColor(event.risk_score)}`}>
                          Risk: {(event.risk_score * 100).toFixed(0)}%
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Risk Analysis</CardTitle>
                <CardDescription>Security risk breakdown by category</CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={mockRiskData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="low" stackId="a" fill="#10b981" />
                    <Bar dataKey="medium" stackId="a" fill="#f59e0b" />
                    <Bar dataKey="high" stackId="a" fill="#ef4444" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="alerts" className="space-y-4">
            <div className="space-y-4">
              {alerts.map((alert) => (
                <Alert key={alert.id}>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription className="ml-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="font-medium">{alert.message}</span>
                        {alert.user_id && (
                          <div className="text-sm text-muted-foreground mt-1">
                            User: {alert.user_id}
                          </div>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={getSeverityColor(alert.severity)}>
                          {alert.severity.toUpperCase()}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {new Date(alert.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
