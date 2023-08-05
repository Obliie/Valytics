module.exports = {
  env: {
    es2021: true,
  },
  extends: [
    'universe/native',
    'universe/shared/typescript-analysis',
    'airbnb',
    'airbnb-typescript',
    'airbnb/hooks',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
  ],
  overrides: [
    {
      files: ['*.ts', '*.tsx', '*.d.ts'],
    },
  ],
  parserOptions: {
    project: ['app-web/tsconfig.json'],
  },
  rules: {
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/no-use-before-define': 'off',
  },
};
