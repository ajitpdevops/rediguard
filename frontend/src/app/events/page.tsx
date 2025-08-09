"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { 
  Shield, 
  AlertTriangle, 
  Search, 
  Filter,
  Clock,
  MapPin,
  User,
  Activity,
  RefreshCw
} from "lucide-react"
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
  details: {
    user_agent?: string
    session_id?: string
    action?: string
    resource?: string
  }
}

export default function Events() {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [filteredEvents, setFilteredEvents] = useState<SecurityEvent[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  const [searchTerm, setSearchTerm] = useState("")
  const [filterType, setFilterType] = useState("all")
  const [filterSeverity, setFilterSeverity] = useState("all")

  const fetchEvents = async () => {
    setIsLoading(true)
    try {
      // Mock security events data
      const mockEvents: SecurityEvent[] = [
        {
          id: '1',
          user_id: 'user_123',
          event_type: 'login',
          ip_address: '192.168.1.100',
          location: 'New York, US',
          timestamp: new Date().toISOString(),
          risk_score: 0.8,
          is_anomaly: true,
          details: {
            user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            session_id: 'sess_abc123',
            action: 'successful_login'
          }
        },
        {
          id: '2',
          user_id: 'user_456',
          event_type: 'api_call',
          ip_address: '10.0.0.5',
          location: 'London, UK',
          timestamp: new Date(Date.now() - 300000).toISOString(),
          risk_score: 0.3,
          is_anomaly: false,
          details: {
            action: 'GET /api/users',
            resource: '/api/users'
          }
        },
        {
          id: '3',
          user_id: 'user_789',
          event_type: 'data_access',
          ip_address: '172.16.0.10',
          location: 'Tokyo, JP',
          timestamp: new Date(Date.now() - 600000).toISOString(),
          risk_score: 0.9,
          is_anomaly: true,
          details: {
            action: 'bulk_download',
            resource: '/sensitive/documents'
          }
        },
        {
          id: '4',
          user_id: 'user_234',
          event_type: 'failed_login',
          ip_address: '203.0.113.45',
          location: 'Unknown',
          timestamp: new Date(Date.now() - 900000).toISOString(),
          risk_score: 0.6,
          is_anomaly: true,
          details: {
            user_agent: 'curl/7.68.0',
            action: 'failed_authentication'
          }
        },
        {
          id: '5',
          user_id: 'user_567',
          event_type: 'password_change',
          ip_address: '192.168.1.50',
          location: 'San Francisco, US',
          timestamp: new Date(Date.now() - 1200000).toISOString(),
          risk_score: 0.2,
          is_anomaly: false,
          details: {
            action: 'password_updated',
            session_id: 'sess_xyz789'
          }
        },
        {
          id: '6',
          user_id: 'user_890',
          event_type: 'admin_access',
          ip_address: '10.0.0.100',
          location: 'Berlin, DE',
          timestamp: new Date(Date.now() - 1800000).toISOString(),
          risk_score: 0.4,
          is_anomaly: false,
          details: {
            action: 'admin_panel_access',
            resource: '/admin/users'
          }
        }
      ]
      
      setEvents(mockEvents)
      setFilteredEvents(mockEvents)
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Failed to fetch events:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchEvents()
    const interval = setInterval(fetchEvents, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    let filtered = events

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(event => 
        event.user_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.ip_address.includes(searchTerm) ||
        event.event_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.location.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Apply type filter
    if (filterType !== "all") {
      filtered = filtered.filter(event => event.event_type === filterType)
    }

    // Apply severity filter
    if (filterSeverity !== "all") {
      if (filterSeverity === "high") {
        filtered = filtered.filter(event => event.risk_score >= 0.7)
      } else if (filterSeverity === "medium") {
        filtered = filtered.filter(event => event.risk_score >= 0.4 && event.risk_score < 0.7)
      } else if (filterSeverity === "low") {
        filtered = filtered.filter(event => event.risk_score < 0.4)
      } else if (filterSeverity === "anomaly") {
        filtered = filtered.filter(event => event.is_anomaly)
      }
    }

    setFilteredEvents(filtered)
  }, [events, searchTerm, filterType, filterSeverity])

  // Removed unused function getRiskColor

  const getRiskBadge = (score: number): "default" | "destructive" | "secondary" => {
    if (score >= 0.7) return 'destructive'
    if (score >= 0.4) return 'default'
    return 'secondary'
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString()
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Security Events</h2>
            <p className="text-muted-foreground">
              Real-time security events and anomaly detection
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
              onClick={fetchEvents}
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
              <CardTitle className="text-sm font-medium">Total Events</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{events.length}</div>
              <p className="text-xs text-muted-foreground">
                Showing {filteredEvents.length} filtered
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Anomalies</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {events.filter(e => e.is_anomaly).length}
              </div>
              <p className="text-xs text-muted-foreground">
                {((events.filter(e => e.is_anomaly).length / events.length) * 100).toFixed(1)}% of total
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High Risk</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {events.filter(e => e.risk_score >= 0.7).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Risk score ≥ 70%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Unique Users</CardTitle>
              <User className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {new Set(events.map(e => e.user_id)).size}
              </div>
              <p className="text-xs text-muted-foreground">
                Active in events
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Filter className="mr-2 h-4 w-4" />
              Filters & Search
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by user, IP, event type, or location..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                </div>
              </div>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Event Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="login">Login</SelectItem>
                  <SelectItem value="failed_login">Failed Login</SelectItem>
                  <SelectItem value="api_call">API Call</SelectItem>
                  <SelectItem value="data_access">Data Access</SelectItem>
                  <SelectItem value="password_change">Password Change</SelectItem>
                  <SelectItem value="admin_access">Admin Access</SelectItem>
                </SelectContent>
              </Select>
              <Select value={filterSeverity} onValueChange={setFilterSeverity}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Risk Level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="high">High Risk</SelectItem>
                  <SelectItem value="medium">Medium Risk</SelectItem>
                  <SelectItem value="low">Low Risk</SelectItem>
                  <SelectItem value="anomaly">Anomalies Only</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Events Table */}
        <Card>
          <CardHeader>
            <CardTitle>Security Events</CardTitle>
            <CardDescription>
              Real-time security events from Redis Stream ({filteredEvents.length} events)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Status</TableHead>
                  <TableHead>Event Type</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Risk Score</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Details</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredEvents.map((event) => {
                  const { date, time } = formatTimestamp(event.timestamp)
                  return (
                    <TableRow key={event.id}>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {event.is_anomaly ? (
                            <AlertTriangle className="h-4 w-4 text-red-500" />
                          ) : (
                            <Shield className="h-4 w-4 text-green-500" />
                          )}
                          <Badge variant={event.is_anomaly ? "destructive" : "secondary"}>
                            {event.is_anomaly ? "Anomaly" : "Normal"}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">{event.event_type}</TableCell>
                      <TableCell>{event.user_id}</TableCell>
                      <TableCell className="font-mono text-sm">{event.ip_address}</TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <MapPin className="mr-1 h-3 w-3 text-muted-foreground" />
                          {event.location}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getRiskBadge(event.risk_score)}>
                          {(event.risk_score * 100).toFixed(0)}%
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>{date}</div>
                          <div className="text-muted-foreground">{time}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm text-muted-foreground">
                          {event.details.action && <div>Action: {event.details.action}</div>}
                          {event.details.resource && <div>Resource: {event.details.resource}</div>}
                          {event.details.user_agent && <div>UA: {event.details.user_agent.substring(0, 30)}...</div>}
                        </div>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
