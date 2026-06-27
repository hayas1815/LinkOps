export type PermissionRole = 'viewer' | 'engineer' | 'manager' | 'admin';

export type PermissionKey =
  | 'workspace.read'
  | 'workspace.write'
  | 'documents.upload'
  | 'assets.edit'
  | 'settings.manage'
  | 'integrations.manage';

export type PermissionProfile = {
  role: PermissionRole;
  permissions: PermissionKey[];
};

export interface AuthorizationContext {
  userId: string;
  role: PermissionRole;
  profile: PermissionProfile;
}
