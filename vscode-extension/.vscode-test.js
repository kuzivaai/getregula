const { defineConfig } = require('@vscode/test-cli');

module.exports = defineConfig({
	files: 'out/test/**/*.test.js',
	version: '1.85.0',
	workspaceFolder: `${__dirname}/src/test/fixture`,
	mocha: { timeout: 10000 }
});
