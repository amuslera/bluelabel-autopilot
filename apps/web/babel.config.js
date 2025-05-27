module.exports = function (api) {
  const isTest = api.env('test');
  
  const presets = [
    ['next/babel', { 'preset-react': { runtime: 'automatic' } }],
    ['@babel/preset-typescript', { 
      isTSX: true, 
      allExtensions: true,
      allowNamespaces: true
    }],
  ];

  const plugins = [
    ['@babel/plugin-proposal-decorators', { legacy: true }],
    ['@babel/plugin-proposal-class-properties', { loose: true }],
    '@babel/plugin-transform-runtime',
    // Modern plugins that replace the deprecated ones
    ['@babel/plugin-transform-nullish-coalescing-operator', { loose: true }],
    ['@babel/plugin-transform-optional-chaining', { loose: true }],
    // Add JSX runtime for tests
    ['@babel/plugin-transform-react-jsx', { runtime: 'automatic' }],
  ];

  if (isTest) {
    presets.push(
      ['@babel/preset-env', { 
        targets: { 
          node: 'current' 
        },
        modules: 'commonjs' // Ensure CommonJS for Jest
      }],
      ['@babel/preset-react', { 
        runtime: 'automatic' 
      }]
    );
  }

  return {
    presets,
    plugins,
  };
};
