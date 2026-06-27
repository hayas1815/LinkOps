export type FeatureFlagKey =
  | 'knowledgeGraph'
  | 'liveMonitoring'
  | 'iot'
  | 'digitalTwin'
  | 'maintenanceAI';

export type FeatureFlags = Record<FeatureFlagKey, boolean>;
