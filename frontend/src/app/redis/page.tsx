"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Database, 
  Server, 
  Activity, 
  Clock, 
  Zap,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle
} from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import DashboardLayout from "@/components/dashboard-layout"

interface RedisStats {
  connected_clients: number
  used_memory: number
  used_memory_human: string
  total_commands_processed: number
  instantaneous_ops_per_sec: number
  keyspace_hits: number
  keyspace_misses: number
  evicted_keys: number
  expired_keys: number
  uptime_in_seconds: number
}

interface RedisModule {
  name: string
  version: string
  status: 'loaded' | 'error' | 'unavailable'
  description: string
}

export default function RedisMonitor() {
  const [stats, setStats] = useState<RedisStats>({
    connected_clients: 0,
    used_memory: 0,
    used_memory_human: "0B",
    total_commands_processed: 0,
    instantaneous_ops_per_sec: 0,
    keyspace_hits: 0,
    keyspace_misses: 0,
    evicted_keys: 0,
    expired_keys: 0,
    uptime_in_seconds: 0
  })

  const [modules, setModules] = useState<RedisModule[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  // Mock performance data
  const performanceData = [
    { time: '14:00', ops: 1200, memory: 85, connections: 45 },
    { time: '14:05', ops: 1350, memory: 87, connections: 52 },
    { time: '14:10', ops: 1180, memory: 84, connections: 48 },
    { time: '14:15', ops: 1450, memory: 89, connections: 56 },
    { time: '14:20', ops: 1320, memory: 86, connections: 51 },
    { time: '14:25', ops: 1580, memory: 91, connections: 62 },
    { time: '14:30', ops: 1420, memory: 88, connections: 58 },
  ]

  const fetchRedisData = async () => {
    setIsLoading(true)
    try {
      // Mock Redis stats (in real app, these would come from Redis INFO command)
      setStats({
        connected_clients: Math.floor(Math.random() * 100) + 20,
        used_memory: Math.floor(Math.random() * 1000000000) + 500000000,
        used_memory_human: `${(Math.random() * 500 + 250).toFixed(1)}MB`,
        total_commands_processed: Math.floor(Math.random() * 10000000) + 5000000,
        instantaneous_ops_per_sec: Math.floor(Math.random() * 2000) + 800,
        keyspace_hits: Math.floor(Math.random() * 1000000) + 500000,
        keyspace_misses: Math.floor(Math.random() * 50000) + 10000,
        evicted_keys: Math.floor(Math.random() * 1000) + 100,
        expired_keys: Math.floor(Math.random() * 5000) + 1000,
        uptime_in_seconds: Math.floor(Math.random() * 86400) + 3600
      })

      // Mock Redis modules
      setModules([
        {
          name: "RedisJSON",
          version: "2.8.9",
          status: "loaded",
          description: "JSON data type support"
        },
        {
          name: "RediSearch",
          version: "2.10.10",
          status: "loaded",
          description: "Full-text search and indexing"
        },
        {
          name: "RedisTimeSeries",
          version: "1.12.2",
          status: "loaded",
          description: "Time series data support"
        },
        {
          name: "RedisBloom",
          version: "2.8.0",
          status: "unavailable",
          description: "Probabilistic data structures"
        },
        {
          name: "RedisGraph",
          version: "2.12.15",
          status: "unavailable",
          description: "Graph database functionality"
        }
      ])

      setLastUpdated(new Date())
    } catch (error) {
      console.error('Failed to fetch Redis data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchRedisData()
    const interval = setInterval(fetchRedisData, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'loaded': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error': return <XCircle className="h-4 w-4 text-red-500" />
      case 'unavailable': return <AlertCircle className="h-4 w-4 text-yellow-500" />
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string): "default" | "destructive" | "secondary" | "outline" => {
    switch (status) {
      case 'loaded': return 'default'
      case 'error': return 'destructive'
      case 'unavailable': return 'secondary'
      default: return 'outline'
    }
  }

  const hitRate = ((stats.keyspace_hits / (stats.keyspace_hits + stats.keyspace_misses)) * 100).toFixed(1)

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Redis Monitor</h2>
            <p className="text-muted-foreground">
              Real-time Redis Stack 8 performance and health monitoring
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
              onClick={fetchRedisData}
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
              <CardTitle className="text-sm font-medium">Operations/sec</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.instantaneous_ops_per_sec.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                Total: {stats.total_commands_processed.toLocaleString()}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.used_memory_human}</div>
              <p className="text-xs text-muted-foreground">
                {((stats.used_memory / (1024 * 1024 * 1024)) * 100).toFixed(1)}% of system
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Connected Clients</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.connected_clients}</div>
              <p className="text-xs text-muted-foreground">
                Active connections
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Cache Hit Rate</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{hitRate}%</div>
              <p className="text-xs text-muted-foreground">
                {stats.keyspace_hits.toLocaleString()} hits / {stats.keyspace_misses.toLocaleString()} misses
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="performance" className="space-y-4">
          <TabsList>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="modules">Modules</TabsTrigger>
            <TabsTrigger value="keys">Key Statistics</TabsTrigger>
            <TabsTrigger value="config">Configuration</TabsTrigger>
          </TabsList>

          <TabsContent value="performance" className="space-y-4">
            <div className="grid gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Real-time Performance Metrics</CardTitle>
                  <CardDescription>Operations, memory usage, and connections over time</CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="ops" stroke="#8884d8" strokeWidth={2} name="Ops/sec" />
                      <Line type="monotone" dataKey="memory" stroke="#82ca9d" strokeWidth={2} name="Memory %" />
                      <Line type="monotone" dataKey="connections" stroke="#ffc658" strokeWidth={2} name="Connections" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Memory Usage Trend</CardTitle>
                    <CardDescription>Memory consumption over time</CardDescription>
                  </CardHeader>
                  <CardContent className="h-60">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={performanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" />
                        <YAxis />
                        <Tooltip />
                        <Area type="monotone" dataKey="memory" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.3} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>System Information</CardTitle>
                    <CardDescription>Current Redis instance details</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Uptime</span>
                      <span className="text-sm font-medium">
                        {Math.floor(stats.uptime_in_seconds / 3600)}h {Math.floor((stats.uptime_in_seconds % 3600) / 60)}m
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Evicted Keys</span>
                      <span className="text-sm font-medium">{stats.evicted_keys.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Expired Keys</span>
                      <span className="text-sm font-medium">{stats.expired_keys.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Redis Version</span>
                      <span className="text-sm font-medium">8.2-rc1</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="modules" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Redis Stack Modules</CardTitle>
                <CardDescription>Available Redis modules and their status</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {modules.map((module) => (
                    <div key={module.name} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          {getStatusIcon(module.status)}
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-medium">{module.name}</span>
                            <Badge variant={getStatusColor(module.status)}>
                              {module.status}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {module.description}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">v{module.version}</div>
                        <div className="text-xs text-muted-foreground">
                          {module.status === 'loaded' ? 'Active' : 'Inactive'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="keys" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Key Statistics</CardTitle>
                  <CardDescription>Redis keyspace analysis</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Total Keys</span>
                    <span className="text-sm font-medium">1,247,893</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Strings</span>
                    <span className="text-sm font-medium">856,234 (68.6%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Hashes</span>
                    <span className="text-sm font-medium">234,567 (18.8%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Lists</span>
                    <span className="text-sm font-medium">89,456 (7.2%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Sets</span>
                    <span className="text-sm font-medium">45,678 (3.7%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Sorted Sets</span>
                    <span className="text-sm font-medium">21,958 (1.8%)</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Command Statistics</CardTitle>
                  <CardDescription>Most frequent Redis commands</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">GET</span>
                    <span className="text-sm font-medium">2,456,789 (45.2%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">SET</span>
                    <span className="text-sm font-medium">1,234,567 (22.7%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">HGET</span>
                    <span className="text-sm font-medium">567,890 (10.4%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">HSET</span>
                    <span className="text-sm font-medium">345,678 (6.4%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">JSON.GET</span>
                    <span className="text-sm font-medium">234,567 (4.3%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">FT.SEARCH</span>
                    <span className="text-sm font-medium">123,456 (2.3%)</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="config" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Redis Configuration</CardTitle>
                <CardDescription>Current Redis instance configuration</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-4">
                    <h4 className="font-semibold">Memory Settings</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Max Memory</span>
                        <span>2GB</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Max Memory Policy</span>
                        <span>allkeys-lru</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Memory Usage</span>
                        <span>{stats.used_memory_human}</span>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-semibold">Network Settings</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Port</span>
                        <span>6379</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Bind Address</span>
                        <span>0.0.0.0</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Max Clients</span>
                        <span>10000</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
