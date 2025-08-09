"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Shield, 
  Database, 
  Bell,
  Lock,
  Activity,
  Save,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Info
} from "lucide-react"
import DashboardLayout from "@/components/dashboard-layout"

interface SecuritySettings {
  anomaly_detection: {
    enabled: boolean
    sensitivity: 'low' | 'medium' | 'high'
    ml_threshold: number
    auto_block: boolean
  }
  alerts: {
    email_notifications: boolean
    sms_notifications: boolean
    webhook_url: string
    severity_threshold: 'low' | 'medium' | 'high' | 'critical'
  }
  authentication: {
    session_timeout: number
    max_login_attempts: number
    require_2fa: boolean
    password_complexity: 'basic' | 'medium' | 'strict'
  }
  monitoring: {
    log_retention_days: number
    real_time_monitoring: boolean
    api_rate_limiting: boolean
    geo_blocking: boolean
  }
}

interface RedisSettings {
  connection: {
    host: string
    port: number
    password: string
    ssl_enabled: boolean
  }
  performance: {
    max_memory: string
    eviction_policy: string
    save_interval: number
  }
  modules: {
    redis_json: boolean
    redis_search: boolean
    redis_timeseries: boolean
    redis_bloom: boolean
  }
}

export default function SettingsPage() {
  const [securitySettings, setSecuritySettings] = useState<SecuritySettings>({
    anomaly_detection: {
      enabled: true,
      sensitivity: 'medium',
      ml_threshold: 0.7,
      auto_block: false
    },
    alerts: {
      email_notifications: true,
      sms_notifications: false,
      webhook_url: '',
      severity_threshold: 'medium'
    },
    authentication: {
      session_timeout: 3600,
      max_login_attempts: 5,
      require_2fa: true,
      password_complexity: 'medium'
    },
    monitoring: {
      log_retention_days: 90,
      real_time_monitoring: true,
      api_rate_limiting: true,
      geo_blocking: false
    }
  })

  const [redisSettings, setRedisSettings] = useState<RedisSettings>({
    connection: {
      host: 'localhost',
      port: 6379,
      password: '••••••••',
      ssl_enabled: false
    },
    performance: {
      max_memory: '2gb',
      eviction_policy: 'allkeys-lru',
      save_interval: 900
    },
    modules: {
      redis_json: true,
      redis_search: true,
      redis_timeseries: true,
      redis_bloom: false
    }
  })

  const [isLoading, setIsLoading] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle')

  const handleSaveSettings = async () => {
    setIsLoading(true)
    setSaveStatus('saving')
    
    try {
      // Simulate API call to save settings
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      setSaveStatus('success')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } catch {
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } finally {
      setIsLoading(false)
    }
  }

  const updateSecuritySetting = (section: keyof SecuritySettings, key: string, value: string | number | boolean) => {
    setSecuritySettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }))
  }

  const updateRedisSetting = (section: keyof RedisSettings, key: string, value: string | number | boolean) => {
    setRedisSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }))
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
            <p className="text-muted-foreground">
              Configure security policies and system settings
            </p>
          </div>
          {saveStatus !== 'idle' && (
            <div className="flex items-center space-x-2">
              {saveStatus === 'saving' && (
                <Badge variant="outline">
                  <RefreshCw className="mr-1 h-3 w-3 animate-spin" />
                  Saving...
                </Badge>
              )}
              {saveStatus === 'success' && (
                <Badge variant="outline" className="text-green-600">
                  <CheckCircle className="mr-1 h-3 w-3" />
                  Saved successfully
                </Badge>
              )}
              {saveStatus === 'error' && (
                <Badge variant="outline" className="text-red-600">
                  <AlertTriangle className="mr-1 h-3 w-3" />
                  Save failed
                </Badge>
              )}
            </div>
          )}
        </div>

        {/* Main Content */}
        <Tabs defaultValue="security" className="space-y-4">
          <TabsList>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="redis">Redis Configuration</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="system">System</TabsTrigger>
          </TabsList>

          <TabsContent value="security" className="space-y-4">
            {/* Anomaly Detection Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="mr-2 h-4 w-4" />
                  Anomaly Detection
                </CardTitle>
                <CardDescription>
                  Configure machine learning-based anomaly detection settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">Enable Anomaly Detection</Label>
                    <div className="text-sm text-muted-foreground">
                      Use AI/ML algorithms to detect unusual user behavior
                    </div>
                  </div>
                  <Switch
                    checked={securitySettings.anomaly_detection.enabled}
                    onCheckedChange={(checked) => 
                      updateSecuritySetting('anomaly_detection', 'enabled', checked)
                    }
                  />
                </div>

                <Separator />

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Detection Sensitivity</Label>
                    <Select 
                      value={securitySettings.anomaly_detection.sensitivity}
                      onValueChange={(value) => 
                        updateSecuritySetting('anomaly_detection', 'sensitivity', value)
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low (Fewer false positives)</SelectItem>
                        <SelectItem value="medium">Medium (Balanced)</SelectItem>
                        <SelectItem value="high">High (More sensitive)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>ML Threshold</Label>
                    <Input
                      type="number"
                      min="0"
                      max="1"
                      step="0.1"
                      value={securitySettings.anomaly_detection.ml_threshold}
                      onChange={(e) => 
                        updateSecuritySetting('anomaly_detection', 'ml_threshold', parseFloat(e.target.value))
                      }
                    />
                    <div className="text-xs text-muted-foreground">
                      Confidence threshold for anomaly detection (0.0 - 1.0)
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">Auto-block Suspicious IPs</Label>
                    <div className="text-sm text-muted-foreground">
                      Automatically block IPs with high-confidence threats
                    </div>
                  </div>
                  <Switch
                    checked={securitySettings.anomaly_detection.auto_block}
                    onCheckedChange={(checked) => 
                      updateSecuritySetting('anomaly_detection', 'auto_block', checked)
                    }
                  />
                </div>
              </CardContent>
            </Card>

            {/* Authentication Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Lock className="mr-2 h-4 w-4" />
                  Authentication & Access Control
                </CardTitle>
                <CardDescription>
                  Configure user authentication and session management
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Session Timeout (seconds)</Label>
                    <Input
                      type="number"
                      value={securitySettings.authentication.session_timeout}
                      onChange={(e) => 
                        updateSecuritySetting('authentication', 'session_timeout', parseInt(e.target.value))
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Max Login Attempts</Label>
                    <Input
                      type="number"
                      value={securitySettings.authentication.max_login_attempts}
                      onChange={(e) => 
                        updateSecuritySetting('authentication', 'max_login_attempts', parseInt(e.target.value))
                      }
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Password Complexity</Label>
                  <Select 
                    value={securitySettings.authentication.password_complexity}
                    onValueChange={(value) => 
                      updateSecuritySetting('authentication', 'password_complexity', value)
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="basic">Basic (8+ characters)</SelectItem>
                      <SelectItem value="medium">Medium (8+ chars, mixed case, numbers)</SelectItem>
                      <SelectItem value="strict">Strict (12+ chars, mixed case, numbers, symbols)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">Require Two-Factor Authentication</Label>
                    <div className="text-sm text-muted-foreground">
                      Enforce 2FA for all user accounts
                    </div>
                  </div>
                  <Switch
                    checked={securitySettings.authentication.require_2fa}
                    onCheckedChange={(checked) => 
                      updateSecuritySetting('authentication', 'require_2fa', checked)
                    }
                  />
                </div>
              </CardContent>
            </Card>

            {/* Monitoring Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="mr-2 h-4 w-4" />
                  Monitoring & Logging
                </CardTitle>
                <CardDescription>
                  Configure system monitoring and data retention policies
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Log Retention Period (days)</Label>
                  <Input
                    type="number"
                    value={securitySettings.monitoring.log_retention_days}
                    onChange={(e) => 
                      updateSecuritySetting('monitoring', 'log_retention_days', parseInt(e.target.value))
                    }
                  />
                  <div className="text-xs text-muted-foreground">
                    How long to keep security event logs
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">Real-time Monitoring</Label>
                    <div className="text-sm text-muted-foreground">
                      Enable continuous security monitoring
                    </div>
                  </div>
                  <Switch
                    checked={securitySettings.monitoring.real_time_monitoring}
                    onCheckedChange={(checked) => 
                      updateSecuritySetting('monitoring', 'real_time_monitoring', checked)
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">API Rate Limiting</Label>
                    <div className="text-sm text-muted-foreground">
                      Protect APIs from abuse and DoS attacks
                    </div>
                  </div>
                  <Switch
                    checked={securitySettings.monitoring.api_rate_limiting}
                    onCheckedChange={(checked) => 
                      updateSecuritySetting('monitoring', 'api_rate_limiting', checked)
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">Geographic Blocking</Label>
                    <div className="text-sm text-muted-foreground">
                      Block requests from high-risk countries
                    </div>
                  </div>
                  <Switch
                    checked={securitySettings.monitoring.geo_blocking}
                    onCheckedChange={(checked) => 
                      updateSecuritySetting('monitoring', 'geo_blocking', checked)
                    }
                  />
                </div>
              </CardContent>
            </Card>

            <div className="flex justify-end">
              <Button 
                onClick={() => handleSaveSettings()}
                disabled={isLoading}
                className="w-32"
              >
                {isLoading ? (
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Save className="mr-2 h-4 w-4" />
                )}
                Save Changes
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="redis" className="space-y-4">
            {/* Redis Connection Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="mr-2 h-4 w-4" />
                  Redis Connection
                </CardTitle>
                <CardDescription>
                  Configure Redis Stack connection settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Host</Label>
                    <Input
                      value={redisSettings.connection.host}
                      onChange={(e) => 
                        updateRedisSetting('connection', 'host', e.target.value)
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Port</Label>
                    <Input
                      type="number"
                      value={redisSettings.connection.port}
                      onChange={(e) => 
                        updateRedisSetting('connection', 'port', parseInt(e.target.value))
                      }
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Password</Label>
                  <Input
                    type="password"
                    value={redisSettings.connection.password}
                    onChange={(e) => 
                      updateRedisSetting('connection', 'password', e.target.value)
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">Enable SSL/TLS</Label>
                    <div className="text-sm text-muted-foreground">
                      Use encrypted connection to Redis
                    </div>
                  </div>
                  <Switch
                    checked={redisSettings.connection.ssl_enabled}
                    onCheckedChange={(checked) => 
                      updateRedisSetting('connection', 'ssl_enabled', checked)
                    }
                  />
                </div>
              </CardContent>
            </Card>

            {/* Redis Performance Settings */}
            <Card>
              <CardHeader>
                <CardTitle>Performance Settings</CardTitle>
                <CardDescription>
                  Configure Redis performance and memory management
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Max Memory</Label>
                    <Select 
                      value={redisSettings.performance.max_memory}
                      onValueChange={(value) => 
                        updateRedisSetting('performance', 'max_memory', value)
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1gb">1 GB</SelectItem>
                        <SelectItem value="2gb">2 GB</SelectItem>
                        <SelectItem value="4gb">4 GB</SelectItem>
                        <SelectItem value="8gb">8 GB</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Eviction Policy</Label>
                    <Select 
                      value={redisSettings.performance.eviction_policy}
                      onValueChange={(value) => 
                        updateRedisSetting('performance', 'eviction_policy', value)
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="allkeys-lru">All Keys LRU</SelectItem>
                        <SelectItem value="allkeys-lfu">All Keys LFU</SelectItem>
                        <SelectItem value="volatile-lru">Volatile LRU</SelectItem>
                        <SelectItem value="volatile-lfu">Volatile LFU</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Save Interval (seconds)</Label>
                  <Input
                    type="number"
                    value={redisSettings.performance.save_interval}
                    onChange={(e) => 
                      updateRedisSetting('performance', 'save_interval', parseInt(e.target.value))
                    }
                  />
                  <div className="text-xs text-muted-foreground">
                    How often to save data to disk
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Redis Modules */}
            <Card>
              <CardHeader>
                <CardTitle>Redis Stack Modules</CardTitle>
                <CardDescription>
                  Enable or disable Redis Stack modules
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">RedisJSON</Label>
                    <div className="text-sm text-muted-foreground">
                      JSON data type support
                    </div>
                  </div>
                  <Switch
                    checked={redisSettings.modules.redis_json}
                    onCheckedChange={(checked) => 
                      updateRedisSetting('modules', 'redis_json', checked)
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">RediSearch</Label>
                    <div className="text-sm text-muted-foreground">
                      Full-text search and indexing
                    </div>
                  </div>
                  <Switch
                    checked={redisSettings.modules.redis_search}
                    onCheckedChange={(checked) => 
                      updateRedisSetting('modules', 'redis_search', checked)
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">RedisTimeSeries</Label>
                    <div className="text-sm text-muted-foreground">
                      Time series data support
                    </div>
                  </div>
                  <Switch
                    checked={redisSettings.modules.redis_timeseries}
                    onCheckedChange={(checked) => 
                      updateRedisSetting('modules', 'redis_timeseries', checked)
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">RedisBloom</Label>
                    <div className="text-sm text-muted-foreground">
                      Probabilistic data structures
                    </div>
                  </div>
                  <Switch
                    checked={redisSettings.modules.redis_bloom}
                    onCheckedChange={(checked) => 
                      updateRedisSetting('modules', 'redis_bloom', checked)
                    }
                  />
                </div>
              </CardContent>
            </Card>

            <div className="flex justify-end">
              <Button 
                onClick={() => handleSaveSettings()}
                disabled={isLoading}
                className="w-32"
              >
                {isLoading ? (
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Save className="mr-2 h-4 w-4" />
                )}
                Save Changes
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="notifications" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Bell className="mr-2 h-4 w-4" />
                  Notification Settings
                </CardTitle>
                <CardDescription>
                  Configure how and when you receive security alerts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">Email Notifications</Label>
                    <div className="text-sm text-muted-foreground">
                      Receive alerts via email
                    </div>
                  </div>
                  <Switch
                    checked={securitySettings.alerts.email_notifications}
                    onCheckedChange={(checked) => 
                      updateSecuritySetting('alerts', 'email_notifications', checked)
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">SMS Notifications</Label>
                    <div className="text-sm text-muted-foreground">
                      Receive critical alerts via SMS
                    </div>
                  </div>
                  <Switch
                    checked={securitySettings.alerts.sms_notifications}
                    onCheckedChange={(checked) => 
                      updateSecuritySetting('alerts', 'sms_notifications', checked)
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label>Webhook URL</Label>
                  <Input
                    placeholder="https://your-webhook-url.com/alerts"
                    value={securitySettings.alerts.webhook_url}
                    onChange={(e) => 
                      updateSecuritySetting('alerts', 'webhook_url', e.target.value)
                    }
                  />
                  <div className="text-xs text-muted-foreground">
                    Send alerts to external systems via webhook
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Minimum Severity for Notifications</Label>
                  <Select 
                    value={securitySettings.alerts.severity_threshold}
                    onValueChange={(value) => 
                      updateSecuritySetting('alerts', 'severity_threshold', value)
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low and above</SelectItem>
                      <SelectItem value="medium">Medium and above</SelectItem>
                      <SelectItem value="high">High and above</SelectItem>
                      <SelectItem value="critical">Critical only</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>System Information</CardTitle>
                <CardDescription>
                  Current system status and configuration
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <h4 className="font-semibold mb-2">Application</h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Version:</span>
                        <span>v1.0.0</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Build:</span>
                        <span>2025.08.09</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Environment:</span>
                        <Badge variant="outline">Production</Badge>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Redis Stack</h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Version:</span>
                        <span>8.2-rc1</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Status:</span>
                        <Badge variant="outline" className="text-green-600">Connected</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Uptime:</span>
                        <span>2d 14h 32m</span>
                      </div>
                    </div>
                  </div>
                </div>

                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    All systems are operating normally. Last health check: {new Date().toLocaleTimeString()}
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
