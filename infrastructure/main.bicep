// ============================================================
// Bank Marketing AI Platform — Azure Infrastructure
// Provisions all Azure services needed for the platform
// ============================================================

@description('Environment name (dev/staging/prod)')
param environment string = 'dev'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Unique suffix for globally-unique resource names')
param suffix string = uniqueString(resourceGroup().id)

@description('Azure OpenAI GPT-4o deployment name')
param openaiDeploymentName string = 'gpt-4o'

@description('Azure OpenAI embedding deployment name')
param embeddingDeploymentName string = 'text-embedding-3-large'

// ─── Variables ──────────────────────────────────────────────────────────────

var appName = 'bankmarketingai'
var tags = {
  application: 'Bank Marketing AI Platform'
  environment: environment
  managedBy: 'Bicep'
}

// ─── Azure OpenAI ───────────────────────────────────────────────────────────

resource openai 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: '${appName}-openai-${suffix}'
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: '${appName}-openai-${suffix}'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: openai
  name: openaiDeploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: 100
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-11-20'
    }
  }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: openai
  name: embeddingDeploymentName
  sku: {
    name: 'Standard'
    capacity: 120
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-3-large'
      version: '1'
    }
  }
  dependsOn: [gpt4oDeployment]
}

// ─── Azure AI Foundry Hub (Agent Service) ────────────────────────────────────

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: '${appName}-hub-${suffix}'
  location: location
  tags: tags
  kind: 'Hub'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'Bank Marketing AI Hub'
    description: 'Azure AI Foundry Hub for Bank Marketing AI Platform'
  }
}

resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: '${appName}-project-${suffix}'
  location: location
  tags: tags
  kind: 'Project'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'Bank Marketing AI Project'
    hubResourceId: aiHub.id
  }
}

// ─── Azure Cosmos DB ─────────────────────────────────────────────────────────

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: '${appName}-cosmos-${suffix}'
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
  }
}

resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: cosmosAccount
  name: 'bank_marketing_ai'
  properties: {
    resource: {
      id: 'bank_marketing_ai'
    }
  }
}

var containers = [
  { name: 'campaigns',    partitionKey: '/id' }
  { name: 'leads',        partitionKey: '/id' }
  { name: 'assets',       partitionKey: '/campaign_id' }
  { name: 'compliance',   partitionKey: '/campaign_id' }
  { name: 'messages',     partitionKey: '/session_id' }
]

resource cosmosContainers 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = [for container in containers: {
  parent: cosmosDatabase
  name: container.name
  properties: {
    resource: {
      id: container.name
      partitionKey: {
        paths: [container.partitionKey]
        kind: 'Hash'
      }
      defaultTtl: -1
    }
  }
}]

// ─── Azure Blob Storage (DAM) ────────────────────────────────────────────────

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: '${appName}stor${suffix}'
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    encryption: {
      services: {
        blob: { enabled: true }
        file: { enabled: true }
      }
      keySource: 'Microsoft.Storage'
    }
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
    deleteRetentionPolicy: {
      enabled: true
      days: 30
    }
    containerDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

var blobContainers = ['digital-assets', 'documents', 'archive', 'temp']

resource storageContainers 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = [for containerName in blobContainers: {
  parent: blobService
  name: containerName
  properties: {
    publicAccess: 'None'
  }
}]

// ─── Azure AI Search ─────────────────────────────────────────────────────────

resource searchService 'Microsoft.Search/searchServices@2024-03-01-preview' = {
  name: '${appName}-search-${suffix}'
  location: location
  tags: tags
  sku: {
    name: 'standard'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    semanticSearch: 'standard'
  }
}

// ─── Azure AI Document Intelligence ──────────────────────────────────────────

resource documentIntelligence 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: '${appName}-docintel-${suffix}'
  location: location
  tags: tags
  kind: 'FormRecognizer'
  sku: {
    name: 'S0'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

// ─── Azure Communication Services ────────────────────────────────────────────

resource communicationService 'Microsoft.Communication/communicationServices@2023-06-01-preview' = {
  name: '${appName}-acs-${suffix}'
  location: 'global'
  tags: tags
  properties: {
    dataLocation: 'United Kingdom'
  }
}

// ─── Azure Service Bus ────────────────────────────────────────────────────────

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: '${appName}-sb-${suffix}'
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
}

resource campaignsQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: 'campaigns-queue'
  properties: {
    maxSizeInMegabytes: 1024
    defaultMessageTimeToLive: 'P7D'
    lockDuration: 'PT30S'
    maxDeliveryCount: 5
  }
}

resource leadsQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: 'leads-queue'
  properties: {
    maxSizeInMegabytes: 1024
    defaultMessageTimeToLive: 'P1D'
    lockDuration: 'PT30S'
    maxDeliveryCount: 10
  }
}

// ─── Azure Key Vault ──────────────────────────────────────────────────────────

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${appName}-kv-${suffix}'
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enableRbacAuthorization: true
    publicNetworkAccess: 'Enabled'
  }
}

// ─── Azure Container Apps Environment ────────────────────────────────────────

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${appName}-logs-${suffix}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${appName}-cae-${suffix}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// Backend Container App
resource backendContainerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${appName}-backend-${suffix}'
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
          allowedHeaders: ['*']
        }
      }
      secrets: [
        {
          name: 'azure-openai-key'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/azure-openai-key'
          identity: 'system'
        }
        {
          name: 'cosmos-key'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/cosmos-key'
          identity: 'system'
        }
        {
          name: 'storage-key'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/storage-key'
          identity: 'system'
        }
        {
          name: 'search-key'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/search-key'
          identity: 'system'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: 'ghcr.io/bank/marketing-ai-backend:latest'
          resources: {
            cpu: json('1.0')
            memory: '2.0Gi'
          }
          env: [
            { name: 'AZURE_OPENAI_ENDPOINT', value: openai.properties.endpoint }
            { name: 'AZURE_OPENAI_DEPLOYMENT', value: openaiDeploymentName }
            { name: 'AZURE_OPENAI_API_KEY', secretRef: 'azure-openai-key' }
            { name: 'AZURE_COSMOS_ENDPOINT', value: cosmosAccount.properties.documentEndpoint }
            { name: 'AZURE_COSMOS_KEY', secretRef: 'cosmos-key' }
            { name: 'AZURE_COSMOS_DATABASE', value: cosmosDatabase.name }
            { name: 'AZURE_STORAGE_ACCOUNT_NAME', value: storageAccount.name }
            { name: 'AZURE_STORAGE_ACCOUNT_KEY', secretRef: 'storage-key' }
            { name: 'AZURE_SEARCH_ENDPOINT', value: 'https://${searchService.name}.search.windows.net' }
            { name: 'AZURE_SEARCH_API_KEY', secretRef: 'search-key' }
            { name: 'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', value: documentIntelligence.properties.endpoint }
            { name: 'AZURE_SERVICE_BUS_CONNECTION_STRING', value: listKeys(serviceBusNamespace, '2022-10-01-preview').primaryConnectionString }
            { name: 'LOG_LEVEL', value: 'INFO' }
            { name: 'CORS_ORIGINS', value: '*' }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
        rules: [
          {
            name: 'http-scale'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

// Frontend Container App (Nginx serving React build)
resource frontendContainerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${appName}-frontend-${suffix}'
  location: location
  tags: tags
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 80
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: 'ghcr.io/bank/marketing-ai-frontend:latest'
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          env: [
            { name: 'VITE_API_BASE_URL', value: 'https://${backendContainerApp.properties.configuration.ingress!.fqdn}/api' }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 5
      }
    }
  }
}

// ─── Azure Monitor & Application Insights ────────────────────────────────────

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${appName}-ai-${suffix}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    RetentionInDays: 90
  }
}

// ─── RBAC: Container App → Key Vault ────────────────────────────────────────

resource kvAccessPolicy 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, backendContainerApp.id, 'key-vault-secrets-user')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: backendContainerApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// ─── Outputs ─────────────────────────────────────────────────────────────────

output backendUrl string = 'https://${backendContainerApp.properties.configuration.ingress!.fqdn}'
output frontendUrl string = 'https://${frontendContainerApp.properties.configuration.ingress!.fqdn}'
output openaiEndpoint string = openai.properties.endpoint
output cosmosEndpoint string = cosmosAccount.properties.documentEndpoint
output storageAccountName string = storageAccount.name
output searchEndpoint string = 'https://${searchService.name}.search.windows.net'
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output keyVaultUri string = keyVault.properties.vaultUri
