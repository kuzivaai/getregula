import * as assert from 'assert';
import * as fs from 'fs/promises';
import * as os from 'os';
import * as path from 'path';
import * as vscode from 'vscode';

const RESPONSE_ENV = 'REGULA_TEST_RESPONSE';
const MARKER_ENV = 'REGULA_TEST_MARKER';

const findingEnvelope = JSON.stringify({
	format_version: '1.0',
	regula_version: '1.9.0',
	command: 'check',
	timestamp: '2026-08-12T00:00:00Z',
	exit_code: 0,
	data: {
		detector_findings: [{
			file: 'model.py',
			line: 1,
			detector_class: 'high_risk',
			category: 'test_finding',
			description: 'Extension host diagnostic fixture',
			suggested_provisions: ['Article 9'],
			detector_priority: 70,
			suppressed: false,
		}],
		decision: {
			result_type: 'insufficient_information',
			model_version: '2026-08-12.3',
			jurisdiction: 'eu',
			rule_resolution: 'unresolved',
			unresolved_predicates: [{ fact_id: 'jurisdiction_in_scope' }],
		},
	},
});

const unexpectedEnvelope = JSON.stringify({
	format_version: '1.0',
	regula_version: '1.9.0',
	command: 'check',
	timestamp: '2026-08-12T00:00:00Z',
	exit_code: 0,
	data: { valid_json_but_unexpected: true },
});

async function createFakeCli(): Promise<{ executable: string; marker: string }> {
	const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'regula-vscode-host-'));
	const script = path.join(dir, 'fake-regula.js');
	const marker = path.join(dir, 'invocations.txt');
	await fs.writeFile(script, [
		'#!/usr/bin/env node',
		"const fs = require('fs');",
		"fs.appendFileSync(process.env.REGULA_TEST_MARKER, 'called\\n');",
		"process.stdout.write(process.env.REGULA_TEST_RESPONSE || '{}');",
	].join('\n'), { mode: 0o755 });
	if (process.platform !== 'win32') {
		return { executable: script, marker };
	}
	const wrapper = path.join(dir, 'fake-regula.cmd');
	await fs.writeFile(wrapper, `@node "${script}" %*\r\n`);
	return { executable: wrapper, marker };
}

async function waitFor(
	predicate: () => Promise<boolean> | boolean,
	message: string,
	timeoutMs = 5000,
): Promise<void> {
	const deadline = Date.now() + timeoutMs;
	while (Date.now() < deadline) {
		if (await predicate()) return;
		await new Promise(resolve => setTimeout(resolve, 25));
	}
	assert.fail(message);
}

async function invocationCount(marker: string): Promise<number> {
	try {
		return (await fs.readFile(marker, 'utf8')).trim().split('\n').filter(Boolean).length;
	} catch {
		return 0;
	}
}

async function configureFakeCli(executable: string, marker: string): Promise<void> {
	process.env[RESPONSE_ENV] = findingEnvelope;
	process.env[MARKER_ENV] = marker;
	await vscode.workspace.getConfiguration('regula').update(
		'executablePath', executable, vscode.ConfigurationTarget.Global,
	);
}

async function exerciseUnexpectedEnvelope(
	command: 'regula.scanFile' | 'regula.scanWorkspace',
	uri: vscode.Uri,
	marker: string,
): Promise<void> {
	await vscode.commands.executeCommand(command);
	await waitFor(
		async () => await invocationCount(marker) === 1,
		`${command} did not invoke the fixture CLI`,
	);
	await waitFor(
		() => vscode.languages.getDiagnostics(uri).length === 1,
		`${command} did not establish the prior diagnostic`,
	);

	process.env[RESPONSE_ENV] = unexpectedEnvelope;
	await vscode.commands.executeCommand(command);
	await waitFor(
		async () => await invocationCount(marker) === 2,
		`${command} did not invoke the fixture CLI a second time`,
	);
	await new Promise(resolve => setTimeout(resolve, 1000));
	assert.strictEqual(
		vscode.languages.getDiagnostics(uri).length,
		1,
		`${command} must preserve prior diagnostics when the CLI envelope is unexpected`,
	);
}

suite('Regula Extension Test Suite', () => {
	vscode.window.showInformationMessage('Start all tests.');

	suiteSetup(async () => {
		const extension = vscode.extensions.getExtension('kuzivaai.regula-ai-act');
		assert.ok(extension, 'development extension is missing from the extension host');
		await extension.activate();
		await vscode.workspace.getConfiguration('regula').update(
			'scanOnSave', false, vscode.ConfigurationTarget.Global,
		);
	});

	test('Extension should be present', () => {
		assert.ok(vscode.extensions.getExtension('kuzivaai.regula-ai-act'));
	});

	test('Commands should be registered', async () => {
		const commands = await vscode.commands.getCommands(true);
		assert.ok(commands.includes('regula.scanFile'));
		assert.ok(commands.includes('regula.scanWorkspace'));
	});

	test('Scan file preserves prior diagnostics for an unexpected envelope', async () => {
		const fixture = vscode.Uri.joinPath(
			vscode.workspace.workspaceFolders![0].uri, 'model.py',
		);
		const document = await vscode.workspace.openTextDocument(fixture);
		await vscode.window.showTextDocument(document);
		const { executable, marker } = await createFakeCli();
		await configureFakeCli(executable, marker);
		await exerciseUnexpectedEnvelope('regula.scanFile', fixture, marker);
	});

	test('Scan workspace preserves prior diagnostics for an unexpected envelope', async () => {
		const root = vscode.workspace.workspaceFolders![0].uri;
		const fixture = vscode.Uri.joinPath(root, 'model.py');
		const { executable, marker } = await createFakeCli();
		await configureFakeCli(executable, marker);
		await exerciseUnexpectedEnvelope('regula.scanWorkspace', fixture, marker);
	});
});
