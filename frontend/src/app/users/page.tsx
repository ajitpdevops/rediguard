"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { 
  Users, 
  Search, 
  Shield, 
  AlertTriangle,
  Clock,
  MapPin,
  Activity,
  TrendingUp,
  RefreshCw,
  Eye
} from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'
import DashboardLayout from "@/components/dashboard-layout"

interface User {
  id: string
  username: string
  email: string
  last_login: string
  location: string
  risk_score: number
  total_events: number
  anomaly_count: number
  status: 'active' | 'suspended' | 'inactive'
  profile: {
    created_at: string
    role: string
    department: string
  }
}

interface UserActivity {
  user_id: string
  activity_score: number
  login_frequency: number
  risk_trend: number[]
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [filteredUsers, setFilteredUsers] = useState<User[]>([])
  const [userActivities, setUserActivities] = useState<UserActivity[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  const [searchTerm, setSearchTerm] = useState("")

  const fetchUsers = async () => {
    setIsLoading(true)
    try {
      // Mock user data
      const mockUsers: User[] = [
        {
          id: 'user_123',
          username: 'john.doe',
          email: 'john.doe@company.com',
          last_login: new Date(Date.now() - 3600000).toISOString(),
          location: 'New York, US',
          risk_score: 0.8,
          total_events: 156,
          anomaly_count: 12,
          status: 'active',
          profile: {
            created_at: '2023-01-15T10:00:00Z',
            role: 'Developer',
            department: 'Engineering'
          }
        },
        {
          id: 'user_456',
          username: 'jane.smith',
          email: 'jane.smith@company.com',
          last_login: new Date(Date.now() - 7200000).toISOString(),
          location: 'London, UK',
          risk_score: 0.3,
          total_events: 89,
          anomaly_count: 2,
          status: 'active',
          profile: {
            created_at: '2023-03-22T14:30:00Z',
            role: 'Manager',
            department: 'Marketing'
          }
        },
        {
          id: 'user_789',
          username: 'alex.wilson',
          email: 'alex.wilson@company.com',
          last_login: new Date(Date.now() - 86400000).toISOString(),
          location: 'Tokyo, JP',
          risk_score: 0.9,
          total_events: 234,
          anomaly_count: 28,
          status: 'suspended',
          profile: {
            created_at: '2022-11-08T09:15:00Z',
            role: 'Admin',
            department: 'IT'
          }
        },
        {
          id: 'user_234',
          username: 'mary.johnson',
          email: 'mary.johnson@company.com',
          last_login: new Date(Date.now() - 43200000).toISOString(),
          location: 'San Francisco, US',
          risk_score: 0.2,
          total_events: 67,
          anomaly_count: 1,
          status: 'active',
          profile: {
            created_at: '2023-06-10T11:45:00Z',
            role: 'Analyst',
            department: 'Finance'
          }
        },
        {
          id: 'user_567',
          username: 'david.brown',
          email: 'david.brown@company.com',
          last_login: new Date(Date.now() - 172800000).toISOString(),
          location: 'Berlin, DE',
          risk_score: 0.5,
          total_events: 123,
          anomaly_count: 8,
          status: 'inactive',
          profile: {
            created_at: '2023-02-28T16:20:00Z',
            role: 'Designer',
            department: 'Design'
          }
        }
      ]

      const mockActivities: UserActivity[] = [
        {
          user_id: 'user_123',
          activity_score: 85,
          login_frequency: 12,
          risk_trend: [0.2, 0.3, 0.5, 0.7, 0.8, 0.9, 0.8]
        },
        {
          user_id: 'user_456',
          activity_score: 65,
          login_frequency: 8,
          risk_trend: [0.1, 0.2, 0.2, 0.3, 0.3, 0.3, 0.3]
        },
        {
          user_id: 'user_789',
          activity_score: 95,
          login_frequency: 15,
          risk_trend: [0.4, 0.6, 0.7, 0.8, 0.9, 0.9, 0.9]
        }
      ]
      
      setUsers(mockUsers)
      setFilteredUsers(mockUsers)
      setUserActivities(mockActivities)
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
    const interval = setInterval(fetchUsers, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (searchTerm) {
      setFilteredUsers(users.filter(user => 
        user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.profile.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.profile.role.toLowerCase().includes(searchTerm.toLowerCase())
      ))
    } else {
      setFilteredUsers(users)
    }
  }, [users, searchTerm])

  // Removed unused function getRiskColor

  const getRiskBadge = (score: number): "default" | "destructive" | "secondary" => {
    if (score >= 0.7) return 'destructive'
    if (score >= 0.4) return 'default'
    return 'secondary'
  }

  const getStatusColor = (status: string): "default" | "destructive" | "secondary" => {
    switch (status) {
      case 'active': return 'default'
      case 'suspended': return 'destructive'
      case 'inactive': return 'secondary'
      default: return 'default'
    }
  }

  const formatLastLogin = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    
    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  // Mock risk trend data for charts
  const riskTrendData = [
    { day: 'Mon', high: 3, medium: 8, low: 15 },
    { day: 'Tue', high: 5, medium: 12, low: 18 },
    { day: 'Wed', high: 2, medium: 6, low: 20 },
    { day: 'Thu', high: 7, medium: 15, low: 16 },
    { day: 'Fri', high: 4, medium: 9, low: 19 },
    { day: 'Sat', high: 1, medium: 3, low: 8 },
    { day: 'Sun', high: 2, medium: 4, low: 10 },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Users</h2>
            <p className="text-muted-foreground">
              User behavior analysis and risk assessment
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
              onClick={fetchUsers}
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
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{users.length}</div>
              <p className="text-xs text-muted-foreground">
                Active in system
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High Risk Users</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {users.filter(u => u.risk_score >= 0.7).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Risk score ≥ 70%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {users.filter(u => u.status === 'active').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Currently active
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Risk Score</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {((users.reduce((sum, u) => sum + u.risk_score, 0) / users.length) * 100).toFixed(0)}%
              </div>
              <p className="text-xs text-muted-foreground">
                <TrendingUp className="inline mr-1 h-3 w-3" />
                Across all users
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="users" className="space-y-4">
          <TabsList>
            <TabsTrigger value="users">User List</TabsTrigger>
            <TabsTrigger value="analytics">Risk Analytics</TabsTrigger>
            <TabsTrigger value="activity">Activity Monitoring</TabsTrigger>
          </TabsList>

          <TabsContent value="users" className="space-y-4">
            {/* Search */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Search className="mr-2 h-4 w-4" />
                  Search Users
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="relative">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by username, email, department, or role..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Users Table */}
            <Card>
              <CardHeader>
                <CardTitle>User Directory</CardTitle>
                <CardDescription>
                  User profiles and risk assessment ({filteredUsers.length} users)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Department</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Risk Score</TableHead>
                      <TableHead>Events</TableHead>
                      <TableHead>Last Login</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{user.username}</div>
                            <div className="text-sm text-muted-foreground">{user.email}</div>
                            <div className="text-xs text-muted-foreground">{user.profile.role}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={getStatusColor(user.status)}>
                            {user.status}
                          </Badge>
                        </TableCell>
                        <TableCell>{user.profile.department}</TableCell>
                        <TableCell>
                          <div className="flex items-center">
                            <MapPin className="mr-1 h-3 w-3 text-muted-foreground" />
                            {user.location}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={getRiskBadge(user.risk_score)}>
                            {(user.risk_score * 100).toFixed(0)}%
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <div>{user.total_events} total</div>
                            <div className="text-red-500">{user.anomaly_count} anomalies</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            {formatLastLogin(user.last_login)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => console.log('View user:', user.username)}
                          >
                            <Eye className="mr-1 h-3 w-3" />
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Risk Distribution by Day</CardTitle>
                  <CardDescription>Daily risk level breakdown</CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={riskTrendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="day" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="low" stackId="a" fill="#10b981" name="Low Risk" />
                      <Bar dataKey="medium" stackId="a" fill="#f59e0b" name="Medium Risk" />
                      <Bar dataKey="high" stackId="a" fill="#ef4444" name="High Risk" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Department Risk Analysis</CardTitle>
                  <CardDescription>Risk scores by department</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {Array.from(new Set(users.map(u => u.profile.department))).map(dept => {
                    const deptUsers = users.filter(u => u.profile.department === dept)
                    const avgRisk = deptUsers.reduce((sum, u) => sum + u.risk_score, 0) / deptUsers.length
                    const highRiskCount = deptUsers.filter(u => u.risk_score >= 0.7).length
                    
                    return (
                      <div key={dept} className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm font-medium">{dept}</span>
                          <span className="text-sm text-muted-foreground">
                            {deptUsers.length} users, {highRiskCount} high risk
                          </span>
                        </div>
                        <Progress value={avgRisk * 100} className="h-2" />
                        <div className="text-xs text-muted-foreground">
                          Average risk: {(avgRisk * 100).toFixed(1)}%
                        </div>
                      </div>
                    )
                  })}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="activity" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>User Activity Patterns</CardTitle>
                <CardDescription>Real-time user behavior monitoring</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {userActivities.map((activity) => {
                    const user = users.find(u => u.id === activity.user_id)
                    if (!user) return null
                    
                    const riskTrendData = activity.risk_trend.map((risk, index) => ({
                      time: `Day ${index + 1}`,
                      risk: risk * 100
                    }))
                    
                    return (
                      <div key={activity.user_id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h4 className="font-medium">{user.username}</h4>
                            <p className="text-sm text-muted-foreground">{user.profile.role} • {user.profile.department}</p>
                          </div>
                          <div className="text-right">
                            <div className="text-sm">Activity Score</div>
                            <div className="text-lg font-bold">{activity.activity_score}%</div>
                          </div>
                        </div>
                        
                        <div className="grid gap-4 md:grid-cols-2">
                          <div>
                            <h5 className="text-sm font-medium mb-2">Risk Trend (7 days)</h5>
                            <div className="h-32">
                              <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={riskTrendData}>
                                  <XAxis dataKey="time" />
                                  <YAxis />
                                  <Tooltip />
                                  <Line type="monotone" dataKey="risk" stroke="#ef4444" strokeWidth={2} />
                                </LineChart>
                              </ResponsiveContainer>
                            </div>
                          </div>
                          
                          <div className="space-y-3">
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">Login Frequency</span>
                              <span className="text-sm font-medium">{activity.login_frequency}/day</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">Total Events</span>
                              <span className="text-sm font-medium">{user.total_events}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">Anomalies</span>
                              <span className="text-sm font-medium text-red-600">{user.anomaly_count}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">Current Risk</span>
                              <Badge variant={getRiskBadge(user.risk_score)}>
                                {(user.risk_score * 100).toFixed(0)}%
                              </Badge>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
