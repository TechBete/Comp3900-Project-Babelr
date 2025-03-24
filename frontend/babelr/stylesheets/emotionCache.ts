import createCache from '@emotion/cache';

export function createCustomCache() {
  return createCache({ key: 'css', prepend: true }); // same as MUI default
}