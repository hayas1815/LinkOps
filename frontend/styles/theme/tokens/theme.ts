import { animations } from './animations';
import { colors } from './colors';
import { radius } from './radius';
import { shadows } from './shadows';
import { spacing } from './spacing';
import { typography } from './typography';
import { zIndex } from './zIndex';

export const themeTokens = {
  colors,
  spacing,
  typography,
  radius,
  shadows,
  zIndex,
  animations,
} as const;
