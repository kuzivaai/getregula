import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Regula Extension Test Suite', () => {
	vscode.window.showInformationMessage('Start all tests.');

	test('Extension should be present', () => {
		assert.ok(vscode.extensions.getExtension('kuzivaai.regula-ai-act'));
	});

	test('Commands should be registered', async () => {
		const commands = await vscode.commands.getCommands(true);
		assert.ok(commands.includes('regula.scanFile'));
		assert.ok(commands.includes('regula.scanWorkspace'));
	});
});
