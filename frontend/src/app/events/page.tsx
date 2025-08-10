"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Shield, 
  AlertTriangle, 
  Search, 
  Filter,
  Clock,
  MapPin,
  Activity,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Database,
  ShieldAlert,
  Info
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
  priority: "high" | "medium" | "low"
  location_risk: string
  details: {
    user_agent?: string
    session_id?: string
    action?: string
    resource?: string
    duration_ms?: number
  }
}

interface PaginationInfo {
  page: number
  limit: number
  total: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

interface FiltersApplied {
  priority?: string
  event_type?: string
  user_id?: string
  min_risk_score?: number
  hours_back?: number
  include_low_priority?: boolean
}

interface PriorityDistribution {
  total_events: number
  high_priority: { count: number; percentage: number }
  medium_priority: { count: number; percentage: number }
  low_priority: { count: number; percentage: number }
}

interface EventsResponse {
  events: SecurityEvent[]
  pagination: PaginationInfo
  filters_applied: FiltersApplied
  priority_distribution: PriorityDistribution
  total_all_events?: number
}

export default function Events() {
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([])
  const [allEvents, setAllEvents] = useState<SecurityEvent[]>([])
  const [securityPagination, setSecurityPagination] = useState<PaginationInfo>({
    page: 1, limit: 50, total: 0, total_pages: 0, has_next: false, has_prev: false
  })
  const [allPagination, setAllPagination] = useState<PaginationInfo>({
    page: 1, limit: 50, total: 0, total_pages: 0, has_next: false, has_prev: false
  })
  const [priorityDistribution, setPriorityDistribution] = useState<PriorityDistribution | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  const [searchTerm, setSearchTerm] = useState("")
  const [filterType, setFilterType] = useState("all")
  const [filterSeverity, setFilterSeverity] = useState("all")
  const [activeTab, setActiveTab] = useState("security")
  const [currentSecurityPage, setCurrentSecurityPage] = useState(1)
  const [currentAllPage, setCurrentAllPage] = useState(1)

  const fetchSecurityEvents = async (page: number = 1) => {
    setIsLoading(true)
    try {
      // Mock API call - replace with actual API endpoint
      const mockResponse: EventsResponse = {
        events: generateMockSecurityEvents(),
        pagination: {
          page,
          limit: 50,
          total: 127,
          total_pages: 3,
          has_next: page < 3,
          has_prev: page > 1
        },
        filters_applied: {},
        priority_distribution: {
          total_events: 127,
          high_priority: { count: 23, percentage: 18.1 },
          medium_priority: { count: 104, percentage: 81.9 },
          low_priority: { count: 0, percentage: 0 }
        }
      }
      
      setSecurityEvents(mockResponse.events)
      setSecurityPagination(mockResponse.pagination)
      setPriorityDistribution(mockResponse.priority_distribution)
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Failed to fetch security events:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchAllEvents = async (page: number = 1) => {
    setIsLoading(true)
    try {
      // Mock API call - replace with actual API endpoint
      const mockResponse: EventsResponse = {
        events: generateMockAllEvents(),
        pagination: {
          page,
          limit: 50,
          total: 1247,
          total_pages: 25,
          has_next: page < 25,
          has_prev: page > 1
        },
        filters_applied: { include_low_priority: true },
        priority_distribution: {
          total_events: 1247,
          high_priority: { count: 23, percentage: 1.8 },
          medium_priority: { count: 104, percentage: 8.3 },
          low_priority: { count: 1120, percentage: 89.9 }
        },
        total_all_events: 1247
      }
      
      setAllEvents(mockResponse.events)
      setAllPagination(mockResponse.pagination)
      setPriorityDistribution(mockResponse.priority_distribution)
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Failed to fetch all events:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateMockSecurityEvents = (): SecurityEvent[] => {
    // Generate high and medium priority events only
    const eventTypes = [
      { type: "failed_login", priority: "high" as const, risk: 0.8 },
      { type: "suspicious_login", priority: "high" as const, risk: 0.75 },
      { type: "privilege_escalation", priority: "high" as const, risk: 0.9 },
      { type: "impossible_travel", priority: "high" as const, risk: 0.95 },
      { type: "login", priority: "medium" as const, risk: 0.4 },
      { type: "admin_access", priority: "medium" as const, risk: 0.5 },
      { type: "password_change", priority: "medium" as const, risk: 0.3 },
      { type: "api_call", priority: "medium" as const, risk: 0.2 }
    ]
    
    return Array.from({ length: 50 }, (_, i) => {
      const eventConfig = eventTypes[Math.floor(Math.random() * eventTypes.length)]
      const now = new Date()
      return {
        id: `sec_${i + 1}`,
        user_id: `user_${Math.floor(Math.random() * 20) + 1}`,
        event_type: eventConfig.type,
        ip_address: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
        location: ["New York, US", "London, UK", "Tokyo, JP", "Berlin, DE"][Math.floor(Math.random() * 4)],
        timestamp: new Date(now.getTime() - Math.random() * 86400000).toISOString(),
        risk_score: eventConfig.risk + (Math.random() - 0.5) * 0.2,
        is_anomaly: eventConfig.priority === "high" ? Math.random() > 0.3 : Math.random() > 0.8,
        priority: eventConfig.priority,
        location_risk: "low",
        details: {
          user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
          session_id: `sess_${Math.random().toString(36).substr(2, 9)}`,
          action: eventConfig.type.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase()),
          resource: eventConfig.type.includes("api") ? "/api/data" : undefined
        }
      }
    })
  }

  const generateMockAllEvents = (): SecurityEvent[] => {
    // Generate events with all priorities including low priority
    const eventTypes = [
      { type: "failed_login", priority: "high" as const, risk: 0.8 },
      { type: "login", priority: "medium" as const, risk: 0.4 },
      { type: "admin_access", priority: "medium" as const, risk: 0.5 },
      { type: "routine_activity", priority: "low" as const, risk: 0.05 },
      { type: "system_maintenance", priority: "low" as const, risk: 0.1 },
      { type: "normal_api_call", priority: "low" as const, risk: 0.05 },
      { type: "file_access", priority: "low" as const, risk: 0.08 },
      { type: "session_refresh", priority: "low" as const, risk: 0.02 }
    ]
    
    return Array.from({ length: 50 }, (_, i) => {
      // Weighted random selection (more low priority events)
      const weights = [0.02, 0.08, 0.05, 0.3, 0.25, 0.2, 0.1] // Matches eventTypes order
      const rand = Math.random()
      let sum = 0
      let selectedIndex = 0
      for (let j = 0; j < weights.length; j++) {
        sum += weights[j]
        if (rand <= sum) {
          selectedIndex = j
          break
        }
      }
      
      const eventConfig = eventTypes[selectedIndex]
      const now = new Date()
      return {
        id: `all_${i + 1}`,
        user_id: `user_${Math.floor(Math.random() * 50) + 1}`,
        event_type: eventConfig.type,
        ip_address: `10.0.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
        location: ["New York, US", "London, UK", "Tokyo, JP", "Berlin, DE", "San Francisco, US"][Math.floor(Math.random() * 5)],
        timestamp: new Date(now.getTime() - Math.random() * 86400000).toISOString(),
        risk_score: Math.max(0, eventConfig.risk + (Math.random() - 0.5) * 0.3),
        is_anomaly: eventConfig.priority === "high" ? Math.random() > 0.3 : Math.random() > 0.9,
        priority: eventConfig.priority,
        location_risk: "low",
        details: {
          user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
          session_id: `sess_${Math.random().toString(36).substr(2, 9)}`,
          action: eventConfig.type.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase()),
          resource: eventConfig.type.includes("api") ? "/api/data" : undefined
        }
      }
    })
  }

  const handleSecurityPageChange = (newPage: number) => {
    setCurrentSecurityPage(newPage)
    fetchSecurityEvents(newPage)
  }

  const handleAllPageChange = (newPage: number) => {
    setCurrentAllPage(newPage)
    fetchAllEvents(newPage)
  }

  useEffect(() => {
    if (activeTab === "security") {
      fetchSecurityEvents(currentSecurityPage)
    } else {
      fetchAllEvents(currentAllPage)
    }
  }, [activeTab]) // eslint-disable-line react-hooks/exhaustive-deps

  const currentEvents = activeTab === "security" ? securityEvents : allEvents

  // Apply client-side filtering to current events
  const filteredEvents = currentEvents.filter(event => {
    const matchesSearch = !searchTerm || 
      event.user_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.ip_address.includes(searchTerm) ||
      event.event_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.location.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesType = filterType === "all" || event.event_type === filterType
    
    let matchesSeverity = true
    if (filterSeverity === "high") {
      matchesSeverity = event.risk_score >= 0.7
    } else if (filterSeverity === "medium") {
      matchesSeverity = event.risk_score >= 0.4 && event.risk_score < 0.7
    } else if (filterSeverity === "low") {
      matchesSeverity = event.risk_score < 0.4
    } else if (filterSeverity === "anomaly") {
      matchesSeverity = event.is_anomaly
    }

    return matchesSearch && matchesType && matchesSeverity
  })

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "high":
        return <Badge variant="destructive">High Priority</Badge>
      case "medium":
        return <Badge variant="default">Medium Priority</Badge>
      case "low":
        return <Badge variant="secondary">Low Priority</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

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

  const PaginationControls = ({ 
    pagination, 
    onPageChange 
  }: { 
    pagination: PaginationInfo; 
    onPageChange: (page: number) => void 
  }) => (
    <div className="flex items-center justify-between space-x-2 py-4">
      <div className="text-sm text-muted-foreground">
        Showing {((pagination.page - 1) * pagination.limit) + 1} to{" "}
        {Math.min(pagination.page * pagination.limit, pagination.total)} of{" "}
        {pagination.total} events
      </div>
      <div className="flex items-center space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(pagination.page - 1)}
          disabled={!pagination.has_prev || isLoading}
        >
          <ChevronLeft className="h-4 w-4" />
          Previous
        </Button>
        <div className="text-sm font-medium">
          Page {pagination.page} of {pagination.total_pages}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(pagination.page + 1)}
          disabled={!pagination.has_next || isLoading}
        >
          Next
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Security Events</h2>
            <p className="text-muted-foreground">
              AI-powered real-time security monitoring and threat detection
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
              onClick={() => activeTab === "security" ? fetchSecurityEvents(currentSecurityPage) : fetchAllEvents(currentAllPage)}
              disabled={isLoading}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Priority Distribution Stats */}
        {priorityDistribution && (
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Events</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{priorityDistribution.total_events}</div>
                <p className="text-xs text-muted-foreground">
                  Showing {filteredEvents.length} filtered
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">High Priority</CardTitle>
                <ShieldAlert className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {priorityDistribution.high_priority.count}
                </div>
                <p className="text-xs text-muted-foreground">
                  {priorityDistribution.high_priority.percentage}% of total
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Medium Priority</CardTitle>
                <Shield className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">
                  {priorityDistribution.medium_priority.count}
                </div>
                <p className="text-xs text-muted-foreground">
                  {priorityDistribution.medium_priority.percentage}% of total
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Low Priority</CardTitle>
                <Info className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {priorityDistribution.low_priority.count}
                </div>
                <p className="text-xs text-muted-foreground">
                  {priorityDistribution.low_priority.percentage}% of total
                </p>
              </CardContent>
            </Card>
          </div>
        )}

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
                  <SelectItem value="failed_login">Failed Login</SelectItem>
                  <SelectItem value="suspicious_login">Suspicious Login</SelectItem>
                  <SelectItem value="login">Login</SelectItem>
                  <SelectItem value="admin_access">Admin Access</SelectItem>
                  <SelectItem value="api_call">API Call</SelectItem>
                  <SelectItem value="password_change">Password Change</SelectItem>
                  <SelectItem value="routine_activity">Routine Activity</SelectItem>
                  <SelectItem value="system_maintenance">System Maintenance</SelectItem>
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

        {/* Event View Toggle */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="security" className="flex items-center space-x-2">
              <ShieldAlert className="h-4 w-4" />
              <span>Security Events</span>
              <Badge variant="secondary" className="ml-2">
                High + Medium Priority
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="all" className="flex items-center space-x-2">
              <Database className="h-4 w-4" />
              <span>All Events</span>
              <Badge variant="outline" className="ml-2">
                Forensic Analysis
              </Badge>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="security" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <ShieldAlert className="mr-2 h-4 w-4" />
                  Security-Focused Events
                </CardTitle>
                <CardDescription>
                  High and medium priority security events requiring attention ({filteredEvents.length} events)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Priority</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Event Type</TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>IP Address</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Risk Score</TableHead>
                      <TableHead>Timestamp</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredEvents.map((event) => {
                      const { date, time } = formatTimestamp(event.timestamp)
                      return (
                        <TableRow key={event.id}>
                          <TableCell>
                            {getPriorityBadge(event.priority)}
                          </TableCell>
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
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
                <PaginationControls 
                  pagination={securityPagination} 
                  onPageChange={handleSecurityPageChange}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="all" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="mr-2 h-4 w-4" />
                  All Events - Forensic Analysis
                </CardTitle>
                <CardDescription>
                  Complete event log including low priority events for detailed investigation ({filteredEvents.length} events)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-950 rounded-lg border">
                  <div className="flex items-center space-x-2 text-blue-700 dark:text-blue-300">
                    <Info className="h-4 w-4" />
                    <span className="text-sm font-medium">Forensic Analysis Mode</span>
                  </div>
                  <p className="text-sm text-blue-600 dark:text-blue-400 mt-1">
                    This view includes all events including routine activities. Use pagination and filters to navigate efficiently.
                    Low priority events are shown for baseline establishment and detailed investigation.
                  </p>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Priority</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Event Type</TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>IP Address</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Risk Score</TableHead>
                      <TableHead>Timestamp</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredEvents.map((event) => {
                      const { date, time } = formatTimestamp(event.timestamp)
                      return (
                        <TableRow key={event.id} className={event.priority === "low" ? "opacity-75" : ""}>
                          <TableCell>
                            {getPriorityBadge(event.priority)}
                          </TableCell>
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
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
                <PaginationControls 
                  pagination={allPagination} 
                  onPageChange={handleAllPageChange}
                />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
